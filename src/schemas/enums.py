from enum import Enum


class DiscountRule(str, Enum):
    """Available discount rules that can be applied to line items."""
    NONE = "none"
    DELEGATED_DISCOUNT = "delegated_discount"
    HOSTED = "hosted"


class Geography(str, Enum):
    """Geographic regions for pricebooks."""
    APAC = "APAC"
    EMEA = "EMEA"
    LATAM = "LATAM"
    NA = "NA"


class PricebookType(str, Enum):
    """Types of pricebooks."""
    COMMERCIAL = "Commercial"
    NAPS = "NAPS"


class CurrencyCode(str, Enum):
    """Supported currency codes."""
    USD = "USD"
    GBP = "GBP"
    EUR = "EUR"
