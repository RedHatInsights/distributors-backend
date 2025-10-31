"""Main FastAPI application for Red Hat Distributor API."""

import base64
import logging
import time
from typing import Optional

from fastapi import FastAPI, Request

from routes.v1.app import v1
from routes import health
from util.settings import constants
from util.logger import get_logger, log_with_context, log_debug


logger = get_logger(__name__)

app = FastAPI(title="Red Hat Distributors API")


# Disable uvicorn's default access logging (we have our own structured logging)
logging.getLogger("uvicorn.access").disabled = True


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, checking proxy headers.

    Args:
        request: The FastAPI request object.

    Returns:
        The client IP address.
    """
    # Check X-Forwarded-For header (proxy/load balancer)
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # Return the first IP (original client)
        return x_forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header (nginx proxy)
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip

    # Fallback to direct client
    if request.client:
        return request.client.host

    return "unknown"


def decode_rh_identity(request: Request) -> Optional[dict]:
    """Decode x-rh-identity header if present.

    Args:
        request: The FastAPI request object.

    Returns:
        Decoded identity dict or None.
    """
    rh_identity = request.headers.get("x-rh-identity")
    if rh_identity:
        try:
            import json
            decoded = base64.b64decode(rh_identity).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            return None
    return None


@app.middleware("http")
async def access_logging_middleware(request: Request, call_next):
    """Log detailed access information for each request.

    Logs:
    - Timestamp (ISO 8601 with timezone)
    - HTTP method and path
    - Client IP (with proxy support)
    - X-Forwarded-For chain
    - User/partner identification
    - Response status code
    - Response time
    - Request ID (if available)
    """
    start_time = time.time()

    # Skip health check endpoints
    if request.url.path in ["/livez", "/readyz"]:
        return await call_next(request)

    # Extract request context
    client_ip = get_client_ip(request)
    forwarded_chain = request.headers.get("x-forwarded-for")
    rh_identity = decode_rh_identity(request)

    # Debug: Log request headers (only in DEBUG_MODE)
    log_debug(
        logger,
        "Incoming request headers",
        path=request.url.path,
        headers=dict(request.headers),
    )

    # Process request
    response = await call_next(request)

    # Calculate response time
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Build structured log context
    log_context = {
        "action": "http_request",
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params) if request.query_params else None,
        "client_ip": client_ip,
        "client_port": request.client.port if request.client else None,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }

    # Add optional fields
    if forwarded_chain:
        log_context["x_forwarded_for"] = forwarded_chain

    if rh_identity:
        # Extract relevant identity fields
        identity_data = rh_identity.get("identity", {})
        if "account_number" in identity_data:
            log_context["account_number"] = identity_data["account_number"]
        if "org_id" in identity_data:
            log_context["org_id"] = identity_data["org_id"]
        if "user" in identity_data:
            user_data = identity_data["user"]
            if "username" in user_data:
                log_context["user"] = user_data["username"]

    # Add request ID if present
    request_id = request.headers.get("x-request-id")
    if request_id:
        log_context["request_id"] = request_id

    # Add user agent
    user_agent = request.headers.get("user-agent")
    if user_agent:
        log_context["user_agent"] = user_agent

    # Determine log level based on status code (hybrid approach)
    if response.status_code >= 500:
        level = "error"  # Server errors = actual problems
    elif response.status_code in [401, 403]:
        level = "warning"  # Potential security/auth issues
    else:
        level = "info"  # All client errors and successes

    # Log the request
    log_with_context(
        logger,
        level,
        f"{request.method} {request.url.path} - {response.status_code}",
        **log_context
    )

    return response


# health endpoints
app.include_router(health.router)

# create versioned api endpoints and docs
app.mount(f"/api/{constants.APP_NAME}/v1", v1)
