"""Pricebook-related Pydantic models."""

from typing import Optional, List
from pydantic import BaseModel, Field

from .enums import DiscountRule, Geography, PricebookType, CurrencyCode


class PricebookHeader(BaseModel):
    pricebook_id: str = Field(
        description="the unique pricebook identifier",
        examples=["D000001"]
    )
    geo: Geography = Field(
        description="Geography; APAC, EMEA, LATAM, NA",
        examples=[Geography.NA]
    )
    pricebook_type: PricebookType = Field(
        description="Commercial or NAPS",
        examples=[PricebookType.COMMERCIAL]
    )
    currency_code: CurrencyCode = Field(
        description="Pricebook currency; USD, GBP, EUR",
        examples=[CurrencyCode.USD]
    )
    name: str = Field(
        description="Pricebook name",
        examples=["Commercial - Distributor NA USD Q3 2025"]
    )
    version: str = Field(
        description="Pricebook version",
        examples=["1"]
    )
    effective_start_date: str = Field(
        description="the effective start date for this pricebook in MM/DD/YYYY format",
        examples=["07/01/2025"]
    )
    effective_end_date: str = Field(
        description="the effective end date for this pricebook in MM/DD/YYYY format",
        examples=["10/01/2025"]
    )


class PricebookLineItem(BaseModel):
    sku: Optional[str] = Field(default=None, description="product SKU", examples=["RH00025"])
    sku_description: Optional[str] = Field(
        default=None, description="SKU short description", examples=["High Availability"]
    )
    product: Optional[str] = Field(default=None, description="product line", examples=["High Availability"])
    category: Optional[str] = Field(
        default=None, description="product category", examples=["SUBSCRIPTIONS_ELS"]
    )
    region: Optional[str] = Field(
        default=None, description="regional restriction of offering", examples=["NA"]
    )
    country: Optional[str] = Field(
        default=None, description="country restriction of offering", examples=["ALL"]
    )
    currency_code: Optional[str] = Field(
        default=None, description="currency of list price", examples=["USD"]
    )
    list_price: Optional[float] = Field(default=None, description="MSRP", examples=[439.0])
    training_unit: Optional[str] = Field(
        default=None, description="Value of training offering in training units"
    )
    training_modality: Optional[str] = Field(
        default=None, description="The channel which training is delivered"
    )
    included_course_and_exam_sku: Optional[str] = Field(
        default=None, description="semi-colon delimited list of course and exam SKUs"
    )
    billing_type: Optional[str] = Field(default=None, description="billing type")
    service_term: Optional[str] = Field(
        default=None, description="service term", examples=["1 YEARS"]
    )
    support_level: Optional[str] = Field(
        default=None, description="support level", examples=["L1-L3"]
    )
    support_type: Optional[str] = Field(
        default=None, description="support type", examples=["Layered"]
    )
    unit_of_measure: Optional[str] = Field(
        default=None, description="the Unit of Measure", examples=["SYSTEM"]
    )
    cores: Optional[str] = Field(default=None, description="number of cores")
    nodes: Optional[str] = Field(default=None, description="number of Nodes")
    sockets: Optional[str] = Field(default=None, description="number of sockets", examples=["2"])
    virtual_guests: Optional[str] = Field(
        default=None, description="number of virtual guests", examples=["0"]
    )
    discount_rule: Optional[List[DiscountRule]] = Field(
        default=None,
        description="array of discount names that indicates if any discount rule should be applied; can be none, delegated_discount, hosted",
        examples=[[DiscountRule.NONE]],
    )


class NapsPricebookLineItem(BaseModel):
    sku: Optional[str] = Field(default=None, description="product SKU", examples=["MW03330"])
    sku_description: Optional[str] = Field(
        default=None,
        description="SKU short description",
        examples=["Red Hat Advanced Cluster Management for Kubernetes Extended Update Support Long-Life Add-On - Term 1 Confirmed Stateside Support (2 Cores or 4 vCPUs)"]
    )
    product: Optional[str] = Field(
        default=None, description="the Product family", examples=["ACM - Advanced Cluster Management"]
    )
    category: Optional[str] = Field(
        default=None, description="the Category of the SKU", examples=["SUBSCRIPTIONS - EUS"]
    )
    region: Optional[str] = Field(
        default=None, description="the Region in which the SKU is offered", examples=["NA"]
    )
    country: Optional[str] = Field(
        default=None,
        description="2-letter iso country code in which the SKU is offered; ALL if all countries within the region are applicable",
        examples=["ALL"]
    )
    currency_code: Optional[str] = Field(
        default=None, description="the 3-letter iso currency code for the prices", examples=["USD"]
    )
    list_price: Optional[float] = Field(default=None, description="the MSRP", examples=[241.0])
    esi_standard_price: Optional[float] = Field(
        default=None, description="the ESI standard price", examples=[183.16]
    )
    esi_price: Optional[float] = Field(default=None, description="the ESI price", examples=[159.06])
    sled_standard_price: Optional[float] = Field(
        default=None, description="the State Local and Education (SLED) standard price", examples=[228.95]
    )
    sled_preferred_price: Optional[float] = Field(
        default=None, description="the SLED preferred price", examples=[204.85]
    )
    federal_standard_price: Optional[float] = Field(
        default=None, description="the standard price for Federal customers", examples=[200.03]
    )
    federal_preferred_price: Optional[float] = Field(
        default=None, description="the preferred price for preferred Federal customers", examples=[163.88]
    )
    service_term: Optional[str] = Field(
        default=None, description="the service term", examples=["1 YEARS"]
    )
    support_level: Optional[str] = Field(
        default=None, description="the support level for the offering", examples=["CSS"]
    )
    support_type: Optional[str] = Field(
        default=None, description="the support type for the offering (CSS, L1-L3)", examples=["Layered"]
    )
    unit_of_measure: Optional[str] = Field(
        default=None, description="the unit of measure for the offering", examples=["CORE BAND"]
    )
    cores: Optional[str] = Field(
        default=None, description="the number of cores for which a unit of the offering is sold", examples=["2"]
    )
    nodes: Optional[str] = Field(
        default=None, description="the number of nodes for which a unit of the offering is sold"
    )
    sockets: Optional[str] = Field(
        default=None, description="the number of sockets for which a unit of the offering is sold"
    )
    virtual_guests: Optional[str] = Field(
        default=None,
        description="the number of virtual guests for which a unit of the offering is sold",
    )
    discount_rule: Optional[List[DiscountRule]] = Field(
        default=None,
        description="array of discount names that indicates if any discount rule should be applied; can be None, DelegatedDiscount, Hosted",
        examples=[[DiscountRule.NONE]],
    )


class PricebookChange(BaseModel):
    sku: Optional[str] = Field(default=None, description="product SKU", examples=["AD438"])
    sku_description: Optional[str] = Field(
        default=None,
        description="SKU short description",
        examples=["Build and Manage Cloud-native Workflows with Red Hat OpenShift Pipelines and OpenShift GitOps Classroom Training"]
    )
    product: Optional[str] = Field(
        default=None, description="product line", examples=["OCP - OpenShift Container Platform"]
    )
    category: Optional[str] = Field(
        default=None, description="product category", examples=["TRAINING - OPEN ENROLLMENT"]
    )
    region: Optional[str] = Field(
        default=None, description="regional restriction of offering", examples=["NA"]
    )
    country: Optional[str] = Field(
        default=None, description="country restriction of offering", examples=["GU"]
    )
    currency_code: Optional[str] = Field(
        default=None, description="currency of list price", examples=["USD"]
    )
    list_price: Optional[float] = Field(default=None, description="MSRP", examples=[2350.0])
    training_unit: Optional[str] = Field(
        default=None, description="Value of training offering in training units", examples=["8"]
    )
    training_modality: Optional[str] = Field(
        default=None, description="The channel which training is delivered", examples=["CLASSROOM TRAINING"]
    )
    included_course_and_exam_sku: Optional[str] = Field(
        default=None, description="semi-colon delimited list of course and exam SKUs"
    )
    billing_type: Optional[str] = Field(default=None, description="billing type")
    service_term: Optional[str] = Field(
        default=None, description="service term", examples=["2 DAYS"]
    )
    support_level: Optional[str] = Field(default=None, description="support level")
    support_type: Optional[str] = Field(default=None, description="support type")
    unit_of_measure: Optional[str] = Field(
        default=None, description="UOM", examples=["NAMED PARTICIPANT"]
    )
    cores: Optional[str] = Field(default=None, description="number of cores")
    nodes: Optional[str] = Field(default=None, description="number of Nodes")
    sockets: Optional[str] = Field(default=None, description="number of sockets")
    virtual_guests: Optional[str] = Field(default=None, description="number of virtual guests")
    discount_rule: Optional[List[DiscountRule]] = Field(
        default=None,
        description="array of discount names that indicates if any discount rule should be applied; can be None, DelegatedDiscount, Hosted",
        examples=[[DiscountRule.NONE]],
    )
    change_type: Optional[str] = Field(
        default=None,
        description="Pricebook line item change type {SKU Added, SKU Removed, SKU Updated [List Price], SKU Updated [Product, List Price], SKU Updated [SKU Description, List Price], SKU Updated [SKU Description, Product]}",
        examples=["SKU Added"]
    )
    effective_date: Optional[str] = Field(
        default=None, description="The effective date of this change in MM/DD/YYYY format", examples=["07/01/2025"]
    )


class DiscountBand(BaseModel):
    discount_band_name: Optional[str] = Field(
        default=None,
        description="the name of the discount band",
        examples=["Delegated Distributor Discount Band 1"]
    )
    applicable_countries: Optional[str] = Field(
        default=None,
        description="ALL countries in a geography or a comma-delimited list of applicable 2-character ISO country codes",
        examples=["ALL"]
    )
    one_year_deal_size_msrp_low: Optional[float] = Field(
        default=None, description="the one year deal size MSRP", examples=[0]
    )
    one_year_deal_size_msrp_high: Optional[float] = Field(default=None, examples=[50000])
    discount_percentage: Optional[float] = Field(
        default=None, description="the discount percentage", examples=[15]
    )


class ProductDiscount(BaseModel):
    product_discount_name: Optional[str] = Field(
        default=None,
        description="the unique name of the product discount",
        examples=["Hosted Product Discount"]
    )
    applicable_countries: Optional[str] = Field(
        default=None,
        description="ALL countries in a geography or a comma-delimited list of applicable 2-character ISO country codes",
        examples=["ALL"]
    )
    percentage: Optional[str] = Field(
        default=None,
        description="the percentage (whole number in string format) to apply to the set of products in the quote",
        examples=["15"]
    )
    product_category: Optional[str] = Field(
        default=None,
        description="the product category to which this product discount will be applied. sku_lisst should be null if the product_category is used",
        examples=["CLOUD SERVICES"]
    )
    sku_list: Optional[str] = Field(
        default=None,
        description="the comma-delimited list of SKUs to which this product discount will be applied.  product_category should be null if the sku_list is used",
    )
    effective_start_date: Optional[str] = Field(
        default=None,
        description="the effective start date of the discount in MMDDYYYY format.  An empty effective start date indicates the start date in which the pricebook becomes valid.",
    )
    effective_end_date: Optional[str] = Field(
        default=None,
        description="the effective end date of the discout in MMDDYYYY format.  An empty effective end date indicates the end date in which the pricebook is no longer valid.",
    )


class ProductNote(BaseModel):
    product_name: Optional[str] = Field(default=None, description="the name of the Product")
    notes: Optional[str] = Field(default=None, description="notes related to the Product")