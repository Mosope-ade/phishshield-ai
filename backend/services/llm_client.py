"""
services/llm_client.py

Lightweight, direct HTTP LLM client using httpx.
Supports Gemini (Google AI Studio), OpenAI, and Anthropic directly.
Switch providers by changing LLM_PROVIDER + LLM_MODEL + LLM_API_KEY in .env.

No heavy packages like litellm required!

SECURITY.md §3: prompt injection defense is the responsibility of the CALLER.
Every call site must:
  1. Place user content in a clearly-delimited data block, never in the
     system prompt or concatenated with instructions.
  2. Explicitly instruct the model that user content is data, not instructions.

SECURITY.md §6: raw LLM output is NEVER returned to callers unvalidated.
Callers must validate against AnalysisResult (Pydantic schema) before use.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Raised when the LLM call fails unrecoverably."""


def supports_vision() -> bool:
    """
    Return True if the currently configured LLM model supports vision/image input.
    Used by the screenshot pipeline to decide whether to call the LLM with the
    image directly or fall back to Tesseract OCR.
    """
    model = os.environ.get('LLM_MODEL', '').lower()
    # Models known to support vision; extend as needed
    vision_models = (
        'gpt-4o', 'gpt-4-turbo', 'gpt-4-vision',
        'gemini-1.5', 'gemini-2', 'gemini/gemini',
        'claude-3', 'claude-3-5',
        'anthropic/claude-3',
    )
    return any(vm in model for vm in vision_models)


def _extract_json_from_response(text: str) -> Optional[dict]:
    """
    Extract a JSON object from the LLM response text.
    LLMs sometimes wrap JSON in markdown code fences — handle both:
    - Raw JSON
    - ```json ... ```
    - ``` ... ```
    """
    # Try raw JSON first
    text = text.strip()
    if text.startswith('{'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Try extracting from code fence
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try any JSON-like block
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


async def _call_gemini(
    model: str,
    api_key: str,
    system_prompt: str,
    user_content_block: str,
    image_base64: Optional[str] = None,
    image_media_type: str = 'image/png',
) -> str:
    # Google AI Studio Gemini API:
    # URL: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}
    # If model string contains a provider prefix (e.g., 'gemini/gemini-1.5-pro'), strip it
    clean_model = model.split('/')[-1] if '/' in model else model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"

    parts = []
    if image_base64 and supports_vision():
        parts.append({
            "inlineData": {
                "mimeType": image_media_type,
                "data": image_base64
            }
        })
    parts.append({"text": user_content_block})

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": parts
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise LLMError(f"Gemini API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected response structure from Gemini API: {data}") from exc


async def _call_openai(
    model: str,
    api_key: str,
    system_prompt: str,
    user_content_block: str,
    image_base64: Optional[str] = None,
    image_media_type: str = 'image/png',
) -> str:
    # OpenAI Chat Completions API
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    clean_model = model.split('/')[-1] if '/' in model else model

    user_content: Any = user_content_block
    if image_base64 and supports_vision():
        user_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_media_type};base64,{image_base64}"
                }
            },
            {
                "type": "text",
                "text": user_content_block
            }
        ]

    payload = {
        "model": clean_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise LLMError(f"OpenAI API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        try:
            return data['choices'][0]['message']['content']
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected response structure from OpenAI API: {data}") from exc


async def _call_anthropic(
    model: str,
    api_key: str,
    system_prompt: str,
    user_content_block: str,
    image_base64: Optional[str] = None,
    image_media_type: str = 'image/png',
) -> str:
    # Anthropic Messages API
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    clean_model = model.split('/')[-1] if '/' in model else model

    user_content: Any = user_content_block
    if image_base64 and supports_vision():
        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_media_type,
                    "data": image_base64
                }
            },
            {
                "type": "text",
                "text": user_content_block
            }
        ]

    payload = {
        "model": clean_model,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1,
        "max_tokens": 2048
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise LLMError(f"Anthropic API returned status {response.status_code}: {response.text}")
        
        data = response.json()
        try:
            return data['content'][0]['text']
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected response structure from Anthropic API: {data}") from exc


async def call_llm_for_analysis(
    *,
    system_prompt: str,
    user_content_block: str,
    image_base64: Optional[str] = None,
    image_media_type: str = 'image/png',
    retry_with_format_reminder: bool = True,
) -> dict[str, Any]:
    """
    Call the LLM for phishing analysis.

    Parameters
    ----------
    system_prompt : str
        The instruction prompt. MUST NOT contain raw user content.
    user_content_block : str
        The user content block, clearly delimited. This is the content
        being analyzed — the system_prompt must tell the model to treat
        this as data, not instructions.
    image_base64 : str, optional
        Base64-encoded image for vision calls (screenshot analysis).
    retry_with_format_reminder : bool
        If True, retry once with a strict format reminder on JSON parse failure.

    Returns
    -------
    dict
        Raw parsed JSON dict from LLM. Caller MUST validate against
        AnalysisResult schema before use (SECURITY.md §6).
    """
    provider = os.environ.get('LLM_PROVIDER', '').lower()
    model = os.environ.get('LLM_MODEL', '')
    api_key = os.environ.get('LLM_API_KEY', '')

    if not model:
        raise LLMError('LLM_MODEL environment variable not set.')
    if not api_key:
        raise LLMError('LLM_API_KEY environment variable not set.')

    # Auto-detect provider from model name if LLM_PROVIDER is not set
    if not provider:
        if 'gemini' in model.lower():
            provider = 'gemini'
        elif 'claude' in model.lower():
            provider = 'anthropic'
        elif 'gpt' in model.lower():
            provider = 'openai'
        else:
            raise LLMError(f"Could not auto-detect LLM provider from model name '{model}'. Set LLM_PROVIDER.")

    async def _attempt(sys_p: str, user_p: str) -> Optional[dict]:
        try:
            if provider == 'gemini':
                raw_text = await _call_gemini(model, api_key, sys_p, user_p, image_base64, image_media_type)
            elif provider == 'openai':
                raw_text = await _call_openai(model, api_key, sys_p, user_p, image_base64, image_media_type)
            elif provider == 'anthropic':
                raw_text = await _call_anthropic(model, api_key, sys_p, user_p, image_base64, image_media_type)
            else:
                raise LLMError(f"Unsupported LLM provider: {provider}")

            parsed = _extract_json_from_response(raw_text)
            if parsed is None:
                logger.warning('LLM returned non-JSON output (provider=%s model=%s): %r', provider, model, raw_text[:200])
            return parsed
        except Exception as exc:
            logger.warning('LLM call failed (provider=%s model=%s): %s', provider, model, exc, exc_info=True)
            return None

    result = await _attempt(system_prompt, user_content_block)

    if result is None and retry_with_format_reminder:
        # Retry once with an explicit format reminder (SECURITY.md §6)
        retry_reminder = (
            "\n\nIMPORTANT: You must respond with ONLY a valid JSON object matching "
            "the schema specified. No prose, no markdown fences, no explanation — "
            "just the raw JSON object."
        )
        result = await _attempt(system_prompt, user_content_block + retry_reminder)

    if result is None:
        raise LLMError(
            'LLM returned non-JSON output after retry. Analysis unavailable.'
        )

    return result

