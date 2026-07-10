"""
PhishShield AI — FastAPI application entry point.

SECURITY.md §10: CORS locked to ALLOWED_ORIGIN; security headers set.
SECURITY.md §7: rate limiting via slowapi.
PLAN.md §6: no accounts, no login, anonymous IP-scoped requests.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .api.analyze import router as analyze_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────
# SECURITY.md §7: per-IP rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title='PhishShield AI',
    description='Analyze messages, links, screenshots, and QR codes for phishing and scams.',
    version='1.0.0',
    docs_url='/docs',  # Disable in production if desired
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
# SECURITY.md §10: no wildcard * in production
allowed_origin = os.environ.get('ALLOWED_ORIGIN', 'http://localhost:5173')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)

# ── Security headers middleware ───────────────────────────────────────────────
# SECURITY.md §10
@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # SECURITY.md §14: never return stack traces to client
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze_router)


@app.get('/health')
async def health_check():
    """Basic health check endpoint."""
    return {'status': 'ok', 'service': 'PhishShield AI'}


# ── Global exception handler ──────────────────────────────────────────────────
# SECURITY.md §14: never return raw stack traces to client
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception('Unhandled exception: %s', exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'An internal error occurred. Please try again.'},
    )
