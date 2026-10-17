import pytest
from pydantic import ValidationError

from app.schemas import InvoiceRequest
from tests.sample_data import sample_invoice


def test_valid_invoice_is_accepted():
    invoice = InvoiceRequest(**sample_invoice())
    assert invoice.seller.gstin == "29ABCDE1234F1Z5"
    assert invoice.buyer.gstin is None
    assert len(invoice.items) == 1


def test_gstin_is_cleaned_up():
    invoice = InvoiceRequest(**sample_invoice(seller_gstin=" 29abcde1234f1z5 "))
    assert invoice.seller.gstin == "29ABCDE1234F1Z5"


def test_bad_gstin_is_rejected():
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(seller_gstin="12345"))


def test_old_gst_rate_is_rejected():
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(gst_rate=28))


def test_invoice_needs_at_least_one_item():
    with pytest.raises(ValidationError):
        InvoiceRequest(**sample_invoice(items=[]))