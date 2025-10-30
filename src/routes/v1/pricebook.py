"""Pricebook API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Query

from services import salesforce
from schemas import (
    PricebookHeader,
    PricebookLineItem,
    NapsPricebookLineItem,
    PricebookChange,
    DiscountBand,
    # ProductDiscount,
    # ProductNote,
)

router = APIRouter(tags=["pricebook"])

# TODO: determine this from header
mdmId = "MDM-12345"


@router.get("/pricebook_list", response_model=List[PricebookHeader], operation_id="getPricebookList")
def get_pricebook_list():
    """Retrieve list of PricebookHeaders available to the partner."""
    data: dict = {"mdmId": mdmId}
    return salesforce.execute_apex("partnerpricebook/pricebooklist", "GET", data)


@router.get("/pricebook", response_model=List[PricebookLineItem], operation_id="get_pricebook")
def get_pricebook(pricebook_id: Optional[str] = Query(None, description="the Pricebook Id")):
    """Retrieve pricebook by Pricebook Id."""
    data: dict = {"mdmId": mdmId, "pricebookId": pricebook_id}
    return salesforce.execute_apex("partnerpricebook/pricebook", "GET", data)


@router.get("/naps_pricebook", response_model=List[NapsPricebookLineItem], operation_id="get_naps_pricebook")
def get_naps_pricebook(pricebook_id: Optional[str] = Query(None, description="the Pricebook Id")):
    """Retrieve NAPS pricebook by Pricebook Id."""
    data: dict = {"mdmId": mdmId, "pricebookId": pricebook_id}
    # NOTE: This endpoint may need to be verified with Salesforce API
    return salesforce.execute_apex("partnerpricebook/napspricebook", "GET", data)


@router.get("/pricebook_change_summary", response_model=List[PricebookChange], operation_id="get_pricebook_change_summary")
def get_pricebook_change_summary(pricebook_id: Optional[str] = Query(None, description="the Pricebook Id")):
    """Retrieve pricebook changes for Pricebook ID."""
    data: dict = {"mdmId": mdmId, "pricebookId": pricebook_id}
    return salesforce.execute_apex(
        "partnerpricebook/pricebookchangesummary", "GET", data
    )


@router.get("/discount_bands", response_model=List[DiscountBand], operation_id="get_discount_bands")
def get_discount_bands(pricebook_id: Optional[str] = Query(None, description="the Pricebook Id")):
    """Retrieve the discount bands."""
    data: dict = {"mdmId": mdmId, "pricebookId": pricebook_id}
    return salesforce.execute_apex("partnerpricebook/discountbands", "GET", data)


# TODO: finalize implementation
# @router.get("/product_discounts", response_model=List[ProductDiscount], operation_id="get_product_discounts")
# def get_product_discounts(pricebook_id: Optional[str] = Query(None, description="the Pricebook Id")):
#     """Retrieve the product discounts which will be applied to a set of line items on the quote."""
#     data: dict = {"mdmId": mdmId, "pricebookId": pricebook_id}
#     return salesforce.execute_apex("???", "GET", data)


# TODO: finalize implementation
# @router.get("/product_notes", response_model=List[ProductNote], operation_id="get_product_notes")
# def get_product_notes(pricebook_id: Optional[str] = Query(None, description="the Pricebook Id")):
#     """Retrieve the product notes."""
#     data: dict = {"mdmId": mdmId, "pricebookId": pricebook_id}
#     return salesforce.execute_apex("???", "GET", data)
