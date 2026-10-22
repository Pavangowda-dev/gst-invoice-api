import pytest
from pydantic import ValidationError

from app.schemas import InvoiceRequest
from tests.sample_data import SAMPLE_BANK, SAMPLE_GSTIN, sample_invoice


def test_valid_invoice_is_accepted():
    invoice = InvoiceRequest(**sample_invoice())
    assert invoice.seller.gstin == SAMPLE_GSTIN
    assert invoice.buyer.gstin is None
    assert len(invoice.items) == 1


def test_gstin_is_cleaned_up():
    invoice = InvoiceRequest(**sample_invoice(seller_gstin=f" {SAMPLE_GSTIN.lower()} "))
    assert invoice.seller.gstin == SAMPLE_GSTIN


def test_bad_gstin_is_rejected():
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(seller_gstin="12345"))


def test_gstin_with_a_typo_is_rejected():
    # right format, but the last character does not match the others
    with pytest.raises(ValidationError, match="check digit"):
        InvoiceRequest(**sample_invoice(seller_gstin="29ABCDE1234F1Z5"))


def test_old_gst_rate_is_rejected():
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(gst_rate=28))


def test_invoice_needs_at_least_one_item():
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(items=[]))


def test_discount_over_100_percent_is_rejected():
    items = [
        {
            "description": "Design work",
            "hsn_sac": "998314",
            "quantity": 1,
            "unit_price": 1000,
            "gst_rate": 18,
            "discount_percent": 150,
        }
    ]
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(items=items))


def test_bank_details_are_accepted():
    invoice = InvoiceRequest(**sample_invoice(bank_details=SAMPLE_BANK))
    assert invoice.bank_details.ifsc == "TEST0001234"


def test_ifsc_is_cleaned_up():
    bank = {**SAMPLE_BANK, "ifsc": " test0001234 "}
    invoice = InvoiceRequest(**sample_invoice(bank_details=bank))
    assert invoice.bank_details.ifsc == "TEST0001234"


def test_bad_ifsc_is_rejected():
    bank = {**SAMPLE_BANK, "ifsc": "TEST1234567"}
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(bank_details=bank))


def test_bad_account_number_is_rejected():
    bank = {**SAMPLE_BANK, "account_number": "12AB"}
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(bank_details=bank))