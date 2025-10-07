"""Main FastAPI application for Red Hat Distributor API."""

import base64
import logging

from fastapi import FastAPI, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from routes import health, pricebook
from util.settings import constants


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Red Hat Distributor API",
    docs_url=f"/api/{constants.APP_NAME}/docs",
    openapi_url=f"/api/{constants.APP_NAME}/openapi.json",
)


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


def basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """Basic auth dependency for OpenAPI spec, handled by ConsoleDot."""
    return credentials


app.include_router(health.router)
app.include_router(
    pricebook.router,
    prefix=f"/api/{constants.APP_NAME}",
    dependencies=[Depends(basic_auth)],
)
