"""Pricebook API endpoints."""

from fastapi import APIRouter

from services import salesforce

router = APIRouter(tags=["pricebook"])

# TODO: determine this from header
mdmId = "MDM-12345"


@router.get("/PricebookList")
def get_pricebook_list():
    """Retrieve list of PricebookHeaders available to the partner."""
    data: dict = {"mdmId": mdmId}
    return salesforce.execute_apex("partnerpricebook/pricebooklist", "GET", data)


@router.get("/Pricebook")
def get_pricebook(pricebookId: str):
    """Retrieve pricebook by ID."""
    data: dict = {"mdmId": mdmId, "pricebookId": pricebookId}
    return salesforce.execute_apex("partnerpricebook/pricebook", "GET", data)


@router.get("/PricebookChangeSummary")
def get_pricebook_change_summary(pricebookId: str):
    """Retrieve changes for pricebook by ID."""
    data: dict = {"mdmId": mdmId, "pricebookId": pricebookId}
    return salesforce.execute_apex(
        "partnerpricebook/pricebookchangesummary", "GET", data
    )


@router.get("/DiscountBands")
def get_discount_bands():
    """Retrieve discount bands."""
    data: dict = {"mdmId": mdmId}
    return salesforce.execute_apex("partnerpricebook/discountbands", "GET", data)
