from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.gstin import has_valid_checksum, has_valid_format

# GST rates currently in use. Update this when the GST Council changes rates.
ALLOWED_GST_RATES = {
    Decimal("0"),
    Decimal("0.25"),
    Decimal("3"),
    Decimal("5"),
    Decimal("18"),
    Decimal("40"),
}


class Address(BaseModel):
    line1: str = Field(min_length=1)
    line2: str | None = None
    city: str = Field(min_length=1)
    state_code: str = Field(pattern=r"^[0-9]{2}$")
    pincode: str = Field(pattern=r"^[1-9][0-9]{5}$")


class Party(BaseModel):
    name: str = Field(min_length=1)
    gstin: str | None = None
    address: Address

    @field_validator("gstin", mode="before")
    @classmethod
    def clean_gstin(cls, value):
        if value is None:
            return None
        value = str(value).strip().upper()
        if not has_valid_format(value):
            raise ValueError("GSTIN format is not valid")
        if not has_valid_checksum(value):
            raise ValueError("GSTIN check digit does not match, please check for a typo")
        return value


class LineItem(BaseModel):
    description: str = Field(min_length=1)
    hsn_sac: str = Field(pattern=r"^[0-9]{4,8}$")
    quantity: Decimal = Field(gt=0)
    unit: str = "NOS"
    unit_price: Decimal = Field(ge=0)
    gst_rate: Decimal
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    @field_validator("gst_rate")
    @classmethod
    def check_gst_rate(cls, value):
        if value not in ALLOWED_GST_RATES:
            allowed = sorted(ALLOWED_GST_RATES)
            raise ValueError(f"GST rate must be one of {allowed}")
        return value


class BankDetails(BaseModel):
    account_name: str = Field(min_length=1)
    bank_name: str = Field(min_length=1)
    account_number: str = Field(pattern=r"^[0-9]{9,18}$")
    ifsc: str = Field(pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")
    upi_id: str | None = None

    @field_validator("ifsc", mode="before")
    @classmethod
    def clean_ifsc(cls, value):
        return str(value).strip().upper()


class InvoiceRequest(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=16)
    invoice_date: date = Field(default_factory=date.today)
    seller: Party
    buyer: Party
    place_of_supply: str | None = Field(default=None, pattern=r"^[0-9]{2}$")
    items: list[LineItem] = Field(min_length=1)
    bank_details: BankDetails | None = None
    notes: str | None = None

    @field_validator("seller")
    @classmethod
    def seller_needs_gstin(cls, seller):
        if seller.gstin is None:
            raise ValueError("Seller GSTIN is required for a tax invoice")
        return seller


class CalculatedItem(BaseModel):
    description: str
    hsn_sac: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    gst_rate: Decimal
    discount: Decimal
    taxable_value: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    total: Decimal


class InvoiceTotals(BaseModel):
    discount: Decimal
    taxable_value: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    total_tax: Decimal
    round_off: Decimal
    grand_total: Decimal


class CalculatedInvoice(BaseModel):
    invoice_number: str
    invoice_date: date
    seller: Party
    buyer: Party
    place_of_supply: str
    tax_type: Literal["intra_state", "inter_state"]
    items: list[CalculatedItem]
    totals: InvoiceTotals
    bank_details: BankDetails | None = None
    notes: str | None = None