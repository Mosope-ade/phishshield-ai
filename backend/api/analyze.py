"""
api/analyze.py

FastAPI route handlers for all analysis endpoints.
Routes are thin — they validate input, call services, and return responses.
All business logic lives in services/.

SECURITY.md §2: all inputs validated before processing.
SECURITY.md §7: rate limiting applied at this layer via slowapi.
PLAN.md §4.1: input type is auto-detected; no manual mode selector.
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
import re
import os
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile, status
from pydantic import ValidationError

from ..models.schemas import (
    AnalysisResult,
    FullReport,
    HeuristicsFindings,
    ThreatIntelFindings,
    TextAnalysisRequest,
)
from ..services.heuristics import run_all_heuristics, HeuristicsResult
from ..services.llm_client import call_llm_for_analysis, LLMError, supports_vision
from ..services.virustotal import check_url_virustotal, check_hash_virustotal
from ..services.safe_fetch import safe_fetch_url, SSRFError
from ..services.qr_decode import decode_qr
from ..services.ocr_fallback import extract_text_from_image
from ..db.cache import get_cached_report, store_report, get_report_by_id
from ..utils.hashing import hash_content, normalize_url, normalize_text, generate_report_id
from ..utils.sanitize import sanitize_for_log
from ..utils.limiter import limiter
from .prompts import build_text_analysis_prompt, build_screenshot_analysis_prompt
from .scoring import compute_overall_risk_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/analyze', tags=['analysis'])

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB (SECURITY.md §8)

# Generalized protocol normalization: converts http/https with 0-2 noise chars/punctuation or backslashes into clean scheme
_PROTOCOL_TYPO_RE = re.compile(
    r'^(?:http[a-z0-9\.\,\s\:\;\-\\]*?(?://|\\\\|\\)|https[a-z0-9\.\,\s\:\;\-\\]*?(?://|\\\\|\\)|htpp[a-z0-9\.\,\s\:\;\-\\]*?(?://|\\\\|\\))',
    re.IGNORECASE,
)



# URL & IPv4 detection regex — matches explicit URLs, bare domains, and raw IPv4 addresses
_URL_RE = re.compile(
    r'(?:https?://|www\.)[^\s<>"{}|\\^\[\]`]+|'
    r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?::\d+)?(?:/[^\s<>"{}|\\^\[\]`]*)?\b|'
    r'\b[a-z0-9\-\.]+\.(?:com|org|net|xyz|info|biz|co|us|uk|ru|cn|tk|click|top|site|garden|url)(?:/[^\s<>"{}|\\^\[\]`]*)?\b',
    re.IGNORECASE,
)

def _normalize_input_url(text: str) -> str:
    """Ensure input URL has a clean http/https scheme, generalizing OCR protocol noise."""
    stripped = text.strip()
    # Normalize protocol typos like "httpr//", "http.//", "http ://", "https:\\"
    if _PROTOCOL_TYPO_RE.match(stripped):
        clean_target = _PROTOCOL_TYPO_RE.sub('', stripped)
        return f'https://{clean_target}'

    if not re.match(r'^https?://', stripped, re.IGNORECASE):
        return f'https://{stripped}'
    return stripped




# General character-level OCR confusion mapping
_OCR_CONFUSION_MAP = str.maketrans({
    '1': 'l',
    '0': 'o',
    '5': 's',
    '8': 'b',
    '2': 'z',
    '}': '-',
    '{': '-',
    '|': '-',
})

def _algorithmic_ocr_correct(text: str) -> str:
    """
    Algorithmic OCR text normalization using general confusion pairs.
    Corrects character confusions and converts space-separated domain tokens to dot notation.
    """
    words = text.split()
    corrected_words = []
    tlds = ['com', 'org', 'net', 'xyz', 'info', 'click', 'site', 'biz', 'top']

    i = 0
    while i < len(words):
        word = words[i]
        clean_word = word.translate(_OCR_CONFUSION_MAP)

        # Check if next word is a standalone TLD (e.g. "netfl1x-b1lling" "click")
        if i + 1 < len(words):
            next_word = words[i + 1].translate(_OCR_CONFUSION_MAP).lower()
            if next_word in tlds or any(next_word.endswith('.' + t) for t in tlds):
                clean_word = f"{clean_word}.{next_word}"
                i += 1  # consume TLD word

        # Check if TLD is attached without dot (e.g. "netfl1x-b1llingclick")
        for tld in tlds:
            if tld in clean_word.lower() and not clean_word.lower().endswith('.' + tld) and not ('.' + tld in clean_word.lower()):
                idx = clean_word.lower().rfind(tld)
                if idx > 0 and clean_word[idx - 1] not in ('.', '-'):
                    clean_word = clean_word[:idx] + '.' + clean_word[idx:]

        corrected_words.append(clean_word)
        i += 1

    return ' '.join(corrected_words)



def _extract_urls(text: str) -> list[str]:
    """Extract all http(s) URLs and bare domains from free text with algorithmic OCR correction."""
    matches = _URL_RE.findall(text)
    if not matches:
        # Second-pass: try algorithmic OCR confusion-pair normalization
        corrected = _algorithmic_ocr_correct(text)
        matches = _URL_RE.findall(corrected)
    return [_normalize_input_url(m) for m in matches]



def _heuristics_to_schema(result: HeuristicsResult) -> HeuristicsFindings:
    return HeuristicsFindings(
        typosquatting_detected=result.typosquatting_detected,
        homograph_detected=result.homograph_detected,
        suspicious_tld=result.suspicious_tld,
        brand_impersonation=result.brand_impersonation,
        suspicious_url_features=result.suspicious_url_features,
        resolved_final_url=result.resolved_final_url,
        notes=result.notes,
    )


async def _analyze_url_pipeline(url: str) -> tuple[HeuristicsResult, AnalysisResult, ThreatIntelFindings]:
    """
    Full URL analysis pipeline:
    Step 1: Heuristics & VirusTotal concurrently
    Step 2: Shortener resolution (if applicable)
    """
    # Step 1: Run heuristics (in worker thread) and VirusTotal concurrently
    heuristics_task = asyncio.to_thread(run_all_heuristics, url)
    vt_task = check_url_virustotal(url)
    heuristics, vt_result = await asyncio.gather(heuristics_task, vt_task)

    final_url = url

    # Step 2: Shortener resolution
    if heuristics.suspicious_url_features and any(
        'shortener' in note.lower() for note in heuristics.notes
    ):
        try:
            fetch_result = await safe_fetch_url(url, follow_redirects=True)
            final_url = fetch_result.final_url
            heuristics.resolved_final_url = final_url
            if final_url != url:
                # Re-run heuristics & VT on resolved destination concurrently
                resolved_heuristics_task = asyncio.to_thread(run_all_heuristics, final_url)
                resolved_vt_task = check_url_virustotal(final_url)
                resolved_heuristics, resolved_vt = await asyncio.gather(
                    resolved_heuristics_task, resolved_vt_task
                )

                # Merge findings
                heuristics.typosquatting_detected |= resolved_heuristics.typosquatting_detected
                heuristics.homograph_detected |= resolved_heuristics.homograph_detected
                heuristics.suspicious_tld |= resolved_heuristics.suspicious_tld
                heuristics.brand_impersonation |= resolved_heuristics.brand_impersonation
                heuristics.suspicious_url_features |= resolved_heuristics.suspicious_url_features
                heuristics.notes.extend(resolved_heuristics.notes)

                if resolved_vt.available:
                    vt_result = resolved_vt
        except SSRFError as e:
            heuristics.notes.append(f'[Safe Fetch] SSRF-blocked redirect: {e}')
        except Exception as e:
            heuristics.notes.append(f'[Safe Fetch] Could not resolve shortener: {e}')

    ai_result = _ai_unavailable_result()
    return heuristics, ai_result, vt_result


def _ai_unavailable_result() -> AnalysisResult:
    """Safe default for AI findings when AI enrichment is disabled/inactive."""
    return AnalysisResult(
        risk_score=0,
        threat_level='Low',
        classification='Likely Safe',
        confidence=0,
        reasons=['AI analysis layer is currently inactive. Verdict is computed strictly via Heuristics and Threat Intelligence.'],
        highlighted_phrases=[],
        recommendations=['Review the Heuristics and VirusTotal findings below for security guidance.'],
    )


@router.post('/text', response_model=FullReport)
@limiter.limit('10/minute')
async def analyze_text(request: Request, response: Response, body: TextAnalysisRequest) -> FullReport:
    """
    Analyze a pasted message or URL.
    Auto-detects input type: single URL -> URL pipeline; free text -> text pipeline.
    """
    content = body.content
    logger.info('Text analysis request: %s', sanitize_for_log(content))

    # Determine input type
    if _is_single_url(content):
        input_type = 'url'
        content = _normalize_input_url(content)
        cache_key = hash_content(normalize_url(content))
    else:
        input_type = 'text'
        cache_key = hash_content(normalize_text(content))


    # Check cache first
    cached = await get_cached_report(cache_key)
    if cached:
        logger.info('Cache hit for %s', sanitize_for_log(content))
        try:
            return FullReport.model_validate(cached)
        except ValidationError:
            pass  # Stale/malformed cache entry — recompute

    if input_type == 'url':
        heuristics, ai_result, vt_result = await _analyze_url_pipeline(content)
    else:
        # Text pipeline: analyze embedded URLs concurrently & run plain text scam pattern heuristics
        heuristics = run_all_heuristics(url='', text=content)
        embedded_urls = _extract_urls(content)

        url_heuristics_notes: list[str] = list(heuristics.notes)
        url_vt_result = ThreatIntelFindings(available=False, notes=[])


        if embedded_urls:
            # Process up to 5 embedded URLs concurrently
            url_tasks = [_analyze_url_pipeline(u) for u in embedded_urls[:5]]
            url_results = await asyncio.gather(*url_tasks)

            for h, _, vt in url_results:
                url_heuristics_notes.extend(h.notes)
                if vt.available and (vt.malicious_votes or 0) > 0:
                    url_vt_result = vt  # Surface worst VT finding

        heuristics.notes = url_heuristics_notes
        heuristics.typosquatting_detected = any('typosquat' in n.lower() for n in url_heuristics_notes)
        heuristics.brand_impersonation = any('impersonation' in n.lower() for n in url_heuristics_notes)
        heuristics.suspicious_tld = any('tld' in n.lower() for n in url_heuristics_notes)

        ai_result = _ai_unavailable_result()
        vt_result = url_vt_result

    overall_score = compute_overall_risk_score(heuristics, vt_result, ai_result)
    threat_level = _score_to_threat_level(overall_score)
    report_id = generate_report_id()

    report = FullReport(
        overall_risk_score=overall_score,
        threat_level=threat_level,
        ai_findings=ai_result,
        heuristics_findings=_heuristics_to_schema(heuristics),
        threat_intel_findings=vt_result,
        report_id=report_id,
    )

    await store_report(report_id, cache_key, input_type, report.model_dump())
    return report


@router.post('/image', response_model=FullReport)
@limiter.limit('10/minute')
async def analyze_image(
    request: Request,
    response: Response,
    file: Annotated[UploadFile, File(description='Screenshot or QR code image')],
) -> FullReport:
    """
    Analyze an uploaded image: attempt QR decode first, then screenshot OCR.
    """
    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='Upload exceeds maximum size of 2MB.',
        )

    image_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='Upload exceeds maximum size of 2MB.',
        )

    from PIL import Image as PILImage, UnidentifiedImageError
    import io as _io
    try:
        PILImage.MAX_IMAGE_PIXELS = 89_478_485
        with PILImage.open(_io.BytesIO(image_bytes)) as img:
            img.verify()
    except (UnidentifiedImageError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Uploaded file is not a valid image.',
        ) from e

    file_hash = hash_content(image_bytes)
    cache_key = file_hash
    cached = await get_cached_report(cache_key)
    if cached:
        try:
            return FullReport.model_validate(cached)
        except ValidationError:
            pass

    qr_result = decode_qr(image_bytes)
    input_type = 'image'
    heuristics = HeuristicsResult()
    vt_result = ThreatIntelFindings(available=False, notes=[])
    ai_result = _ai_unavailable_result()

    if qr_result.found and qr_result.payload:
        input_type = 'qr'
        if qr_result.is_url:
            heuristics, ai_result, vt_result = await _analyze_url_pipeline(qr_result.payload)
        else:
            vt_result = ThreatIntelFindings(available=False, notes=['No URL found in QR code payload.'])
    from ..services.llm_client import extract_text_via_ai
    # Screenshot analysis via Tesseract OCR (Tier 1)
    input_type = 'screenshot'
    ocr = extract_text_from_image(image_bytes)
    extracted_text = ocr.text if (ocr.available and ocr.text) else ''
    ai_assisted_ocr = False

    # Tier 2: AI Vision Fallback if Tier 1 produced no text or URL
    if not extracted_text:
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        try:
            ai_text = await extract_text_via_ai(image_b64, timeout_seconds=2.5)
            if ai_text:
                extracted_text = ai_text
                ai_assisted_ocr = True
        except Exception as err:
            logger.warning("Tier 2 AI extraction skipped/timed out: %s", err)

    # Tier 3: Graceful Unreadable State if both Tier 1 and Tier 2 failed
    if not extracted_text:
        unreadable_report = FullReport(
            overall_risk_score=None,
            threat_level='Unreadable',
            status='unreadable',
            ai_findings=_ai_unavailable_result(),
            heuristics_findings=HeuristicsFindings(
                typosquatting_detected=False,
                homograph_detected=False,
                suspicious_tld=False,
                brand_impersonation=False,
                suspicious_url_features=False,
                notes=["We couldn't clearly read this image. Try a higher-resolution screenshot, or paste the message text/URL directly instead."]
            ),
            threat_intel_findings=ThreatIntelFindings(available=False, notes=['Analysis skipped: Image content is unreadable.']),
            report_id=generate_report_id(),
        )
        return unreadable_report

    # Evaluate plain-text scam patterns on extracted OCR text
    text_heuristics = run_all_heuristics(url='', text=extracted_text)
    heuristics.text_scam_detected = text_heuristics.text_scam_detected
    heuristics.text_scam_score = text_heuristics.text_scam_score
    heuristics.notes.extend(text_heuristics.notes)
    if ai_assisted_ocr:
        heuristics.notes.append('[AI Assistance] Text extracted via vision AI due to low local image quality.')

    # Extract and analyze any embedded URLs in OCR text concurrently
    extracted_urls = list(dict.fromkeys(_extract_urls(extracted_text)))
    if extracted_urls:
        url_tasks = [_analyze_url_pipeline(u) for u in extracted_urls[:5]]
        url_results = await asyncio.gather(*url_tasks)
        for h, _, vt in url_results:
            heuristics.typosquatting_detected |= h.typosquatting_detected
            heuristics.homograph_detected |= h.homograph_detected
            heuristics.suspicious_tld |= h.suspicious_tld
            heuristics.brand_impersonation |= h.brand_impersonation
            heuristics.suspicious_url_features |= h.suspicious_url_features
            heuristics.notes.extend(h.notes)
            if vt.available and (vt.malicious_votes or 0) > 0:
                vt_result = vt

        # Deduplicate accumulated notes across multiple URL findings
        heuristics.notes = list(dict.fromkeys(heuristics.notes))


    # VirusTotal file hash check concurrently
    hash_vt = await check_hash_virustotal(file_hash)
    if hash_vt.available and (hash_vt.malicious_votes or 0) > 0:
        vt_result = hash_vt

    overall_score = compute_overall_risk_score(heuristics, vt_result, ai_result)
    threat_level = _score_to_threat_level(overall_score)
    report_id = generate_report_id()

    report = FullReport(
        overall_risk_score=overall_score,
        threat_level=threat_level,
        status='completed',
        ai_findings=ai_result,
        heuristics_findings=_heuristics_to_schema(heuristics),
        threat_intel_findings=vt_result,
        report_id=report_id,
    )

    await store_report(report_id, cache_key, input_type, report.model_dump())
    return report




@router.get('/report/{report_id}', response_model=FullReport)
@limiter.limit('30/minute')
async def get_report(request: Request, response: Response, report_id: str) -> FullReport:
    """Fetch a cached report by its public slug ID."""
    cached = await get_report_by_id(report_id)
    if not cached:
        raise HTTPException(status_code=404, detail='Report not found.')
    try:
        return FullReport.model_validate(cached)
    except ValidationError as e:
        logger.error('Malformed cached report %s: %s', report_id, e)
        raise HTTPException(status_code=500, detail='Report data is malformed.')


def _score_to_threat_level(score: int) -> str:
    if score >= 75:
        return 'Critical'
    if score >= 50:
        return 'High'
    if score >= 25:
        return 'Medium'
    return 'Low'
