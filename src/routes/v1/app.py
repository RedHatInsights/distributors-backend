"""FastAPI app for API v1."""

from fastapi import FastAPI

from routes.v1 import pricebook

v1 = FastAPI(
    title="Red Hat Distributors API v1",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

v1.include_router(pricebook.router)
