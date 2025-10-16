"""Main FastAPI application for Red Hat Distributor API."""

import base64
import logging

from fastapi import FastAPI, Request

from routes.v1.app import v1
from routes import health
from util.settings import constants


logger = logging.getLogger(__name__)

app = FastAPI(title="Red Hat Distributors API")


class HealthCheckFilter(logging.Filter):
    """Logging filter to exclude health check endpoints from access logs."""

    def filter(self, record):
        """Filter out health check requests from log records.

        Args:
            record: The log record to examine.

        Returns:
            bool: False if the record contains health check paths, True otherwise.
        """
        message = record.getMessage()
        return not any(path in message for path in ["GET /livez", "GET /readyz"])


logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())


@app.middleware("http")
async def log_headers(request: Request, call_next):
    """Log x-rh-identity header if present."""
    rh_identity = request.headers.get("x-rh-identity")
    if rh_identity:
        try:
            decoded = base64.b64decode(rh_identity).decode("utf-8")
            logger.info(f"x-rh-identity: {decoded}")
        except Exception as e:
            logger.warning(f"Failed to decode x-rh-identity header: {e}")
    response = await call_next(request)
    return response


# health endpoints
app.include_router(health.router)

# create versioned api endpoints and docs
app.mount(f"/api/{constants.APP_NAME}/v1", v1)
