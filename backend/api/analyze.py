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

# URL detection regex — matches http(s):// URLs
_URL_RE = re.compile(
    r'https?://[^\s<>"{}|\\^\[\]`]+',
    re.IGNORECASE,
)


def _is_single_url(text: str) -> bool:
    """Return True if the input is a single well-formed URL and nothing else."""
    stripped = text.strip()
    if re.match(r'^https?://', stripped, re.IGNORECASE) and ' ' not in stripped:
        return True
    return False


def _extract_urls(text: str) -> list[str]:
    """Extract all http(s) URLs from free text."""
    return _URL_RE.findall(text)


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
    Full URL analysis pipeline (PLAN.md §4.3):
    Step 1: Heuristics
    Step 2: Shortener resolution (if applicable)
    Step 3: AI
    Step 4: VirusTotal
    """
    # Step 1: Heuristics on original URL
    heuristics = await asyncio.to_thread(run_all_heuristics, url)
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
                # Re-run heuristics on resolved destination
                resolved_heuristics = await asyncio.to_thread(run_all_heuristics, final_url)
                # Merge findings
                heuristics.typosquatting_detected |= resolved_heuristics.typosquatting_detected
                heuristics.homograph_detected |= resolved_heuristics.homograph_detected
                heuristics.suspicious_tld |= resolved_heuristics.suspicious_tld
                heuristics.brand_impersonation |= resolved_heuristics.brand_impersonation
                heuristics.suspicious_url_features |= resolved_heuristics.suspicious_url_features
                heuristics.notes.extend(resolved_heuristics.notes)
        except SSRFError as e:
            heuristics.notes.append(f'[Safe Fetch] SSRF-blocked redirect: {e}')
        except Exception as e:
            heuristics.notes.append(f'[Safe Fetch] Could not resolve shortener: {e}')

    # Step 3: AI
    system_prompt, user_block = build_text_analysis_prompt(
        content=final_url,
        content_type='url',
        heuristics_notes=heuristics.notes,
    )
    try:
        raw_llm = await call_llm_for_analysis(
            system_prompt=system_prompt,
            user_content_block=user_block,
        )
        ai_result = AnalysisResult.model_validate(raw_llm)
    except (LLMError, ValidationError) as e:
        logger.warning('AI analysis failed for URL: %s', e)
        ai_result = _ai_unavailable_result()

    # Step 4: VirusTotal
    vt_result = await check_url_virustotal(final_url)

    return heuristics, ai_result, vt_result


def _ai_unavailable_result() -> AnalysisResult:
    """Safe fallback when AI analysis fails (SECURITY.md §6)."""
    return AnalysisResult(
        risk_score=0,
        threat_level='Low',
        classification='Likely Safe',
        confidence=0,
        reasons=['AI analysis is currently unavailable. Heuristics and VirusTotal results are still shown.'],
        highlighted_phrases=[],
        recommendations=['Review the heuristics and VirusTotal findings for guidance.'],
    )


@router.post('/text', response_model=FullReport)
@limiter.limit('10/minute')
async def analyze_text(request: Request, response: Response, body: TextAnalysisRequest) -> FullReport:
    """
    Analyze a pasted message or URL.
    Auto-detects input type: single URL -> URL pipeline; free text -> text pipeline.
    PLAN.md §4.1, §4.2, §4.3.
    """
    content = body.content
    logger.info('Text analysis request: %s', sanitize_for_log(content))

    # Determine input type
    if _is_single_url(content):
        input_type = 'url'
        cache_key = hash_content(normalize_url(content))
    else:
        input_type = 'text'
        cache_key = hash_content(normalize_text(content))

    # Check cache first (SECURITY.md §7)
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
        # Text pipeline: analyze message, then extract and analyze any embedded URLs
        heuristics = HeuristicsResult()  # No URL heuristics for pure text
        embedded_urls = _extract_urls(content)

        # URL sub-analysis for embedded links
        url_heuristics_notes: list[str] = []
        url_vt_result = ThreatIntelFindings(available=False, notes=[])
        for embedded_url in embedded_urls[:5]:  # Cap at 5 URLs to prevent abuse
            h, _, vt = await _analyze_url_pipeline(embedded_url)
            url_heuristics_notes.extend(h.notes)
            if vt.available and (vt.malicious_votes or 0) > 0:
                url_vt_result = vt  # Surface the worst VT result

        heuristics.notes = url_heuristics_notes
        heuristics.typosquatting_detected = any('typosquat' in n.lower() for n in url_heuristics_notes)
        heuristics.brand_impersonation = any('impersonation' in n.lower() for n in url_heuristics_notes)

        # AI text analysis
        system_prompt, user_block = build_text_analysis_prompt(
            content=content,
            content_type='text',
            heuristics_notes=heuristics.notes,
        )
        try:
            raw_llm = await call_llm_for_analysis(
                system_prompt=system_prompt,
                user_content_block=user_block,
            )
            ai_result = AnalysisResult.model_validate(raw_llm)
        except (LLMError, ValidationError) as e:
            logger.warning('AI text analysis failed: %s', e)
            ai_result = _ai_unavailable_result()

        vt_result = url_vt_result

    overall_score = compute_overall_risk_score(ai_result, heuristics, vt_result)
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
    Analyze an uploaded image: attempt QR decode first, then screenshot analysis.
    PLAN.md §4.4, §4.5.
    SECURITY.md §8: upload size limit and content validation applied.
    """
    # SECURITY.md §8: enforce upload size before reading
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

    # SECURITY.md §8: validate actual image content via magic bytes / Pillow
    from PIL import Image as PILImage, UnidentifiedImageError
    import io as _io
    try:
        PILImage.MAX_IMAGE_PIXELS = 89_478_485  # Decompression-bomb protection
        with PILImage.open(_io.BytesIO(image_bytes)) as img:
            img.verify()  # Raises on corrupt/non-image
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

    # PLAN.md §4.5: attempt QR decode first
    qr_result = decode_qr(image_bytes)
    input_type = 'image'

    if qr_result.found and qr_result.payload:
        input_type = 'qr'
        if qr_result.is_url:
            # Route decoded URL through URL pipeline
            heuristics, ai_result, vt_result = await _analyze_url_pipeline(qr_result.payload)
        else:
            # Non-URL QR payload -> text pipeline
            heuristics = HeuristicsResult()
            system_prompt, user_block = build_text_analysis_prompt(
                content=qr_result.payload,
                content_type='text',
                heuristics_notes=[],
            )
            try:
                raw_llm = await call_llm_for_analysis(
                    system_prompt=system_prompt,
                    user_content_block=user_block,
                )
                ai_result = AnalysisResult.model_validate(raw_llm)
            except (LLMError, ValidationError) as e:
                logger.warning('AI QR text analysis failed: %s', e)
                ai_result = _ai_unavailable_result()
            vt_result = ThreatIntelFindings(available=False, notes=['No URL to check against VirusTotal.'])
    else:
        # PLAN.md §4.4: Screenshot analysis
        input_type = 'screenshot'
        image_b64 = base64.b64encode(image_bytes).decode()

        if supports_vision():
            system_prompt, user_block = build_screenshot_analysis_prompt()
            try:
                raw_llm = await call_llm_for_analysis(
                    system_prompt=system_prompt,
                    user_content_block=user_block,
                    image_base64=image_b64,
                    image_media_type=file.content_type or 'image/png',
                )
                ai_result = AnalysisResult.model_validate(raw_llm)
            except (LLMError, ValidationError) as e:
                logger.warning('Vision AI analysis failed: %s', e)
                ai_result = _ai_unavailable_result()
        else:
            # Fallback to Tesseract OCR
            ocr = extract_text_from_image(image_bytes)
            if ocr.available and ocr.text:
                system_prompt, user_block = build_text_analysis_prompt(
                    content=ocr.text,
                    content_type='text',
                    heuristics_notes=[],
                )
                try:
                    raw_llm = await call_llm_for_analysis(
                        system_prompt=system_prompt,
                        user_content_block=user_block,
                    )
                    ai_result = AnalysisResult.model_validate(raw_llm)
                except (LLMError, ValidationError) as e:
                    logger.warning('OCR+AI analysis failed: %s', e)
                    ai_result = _ai_unavailable_result()
            else:
                ai_result = _ai_unavailable_result()

        # Extract URLs from AI findings and run through URL pipeline
        heuristics = HeuristicsResult()
        vt_result = ThreatIntelFindings(available=False, notes=[])
        for reason in ai_result.reasons:
            for url in _extract_urls(reason):
                h, _, vt = await _analyze_url_pipeline(url)
                heuristics.notes.extend(h.notes)
                if vt.available:
                    vt_result = vt
                    break

    # VirusTotal file hash check (PLAN.md §4.6)
    hash_vt = await check_hash_virustotal(file_hash)
    if hash_vt.available and (hash_vt.malicious_votes or 0) > 0:
        # Merge hash VT findings — worst case wins
        vt_result = hash_vt

    overall_score = compute_overall_risk_score(ai_result, heuristics, vt_result)
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
