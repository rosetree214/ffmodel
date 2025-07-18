"""
Security middleware and utilities for FFModel API
"""

import hashlib
import logging
import os
import time
from collections import defaultdict, deque
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


# Rate limiting storage
class RateLimiter:
    def __init__(self):
        self.clients = defaultdict(lambda: deque())
        self.max_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        client_requests = self.clients[client_id]

        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()

        # Check if client has exceeded the limit
        if len(client_requests) >= self.max_requests:
            return False

        # Add current request
        client_requests.append(now)
        return True

    def get_client_id(self, request: Request) -> str:
        """Generate client ID from request"""
        # Use IP address as client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Hash the IP for privacy
        return hashlib.sha256(client_ip.encode()).hexdigest()[:16]


rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/api/health", "/api/metrics"]:
            return await call_next(request)

        client_id = rate_limiter.get_client_id(request)

        if not rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds",
                },
            )

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


class CSRFProtection:
    """CSRF protection utilities"""

    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this")

    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()

    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        try:
            # For now, we'll implement a basic validation
            # In production, you'd want more sophisticated token validation
            expected_token = self.generate_token(session_id)
            return token == expected_token
        except Exception as e:
            logger.error(f"CSRF token validation error: {e}")
            return False


csrf_protection = CSRFProtection()


def sanitize_log_data(data: Any) -> Any:
    """Sanitize sensitive data from logs"""
    if isinstance(data, dict):
        sanitized = {}
        sensitive_keys = ["password", "token", "secret", "key", "auth", "credential"]

        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = sanitize_log_data(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]
    elif isinstance(data, str):
        # Check if string looks like sensitive data
        if (
            len(data) > 20
            and any(char in data for char in ["=", "+", "/", "-"])
            and data.replace("=", "").replace("+", "").replace("/", "").replace("-", "").isalnum()
        ):
            return "***REDACTED***"
        return data
    else:
        return data


def get_trusted_hosts() -> list:
    """Get list of trusted hosts from environment"""
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
    return [host.strip() for host in trusted_hosts if host.strip()]


def setup_security_middleware(app):
    """Setup security middleware for FastAPI app"""

    # Add trusted host middleware
    trusted_hosts = get_trusted_hosts()
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

    # Add rate limiting
    app.add_middleware(RateLimitMiddleware)

    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    logger.info("Security middleware configured")
    return app
