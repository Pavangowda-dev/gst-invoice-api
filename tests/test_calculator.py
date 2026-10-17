from decimal import Decimal

from app.calculator import calculate_invoice
from app.schemas import InvoiceRequest
from tests.sample_data import sample_invoice


def run(**kwargs):
    return calculate_invoice(InvoiceRequest(**sample_invoice(**kwargs)))


def test_inter_state_uses_igst():
    result = run()  # Karnataka seller, Tamil Nadu buyer
    assert result.tax_type == "inter_state"
    assert result.totals.igst == Decimal("9000.00")
    assert result.totals.cgst == Decimal("0.00")
    assert result.totals.sgst == Decimal("0.00")
    assert result.totals.grand_total == Decimal("59000.00")


def test_intra_state_splits_into_cgst_and_sgst():
    result = run(buyer_state_code="29")
    assert result.tax_type == "intra_state"
    assert result.totals.cgst == Decimal("4500.00")
    assert result.totals.sgst == Decimal("4500.00")
    assert result.totals.igst == Decimal("0.00")


def test_place_of_supply_overrides_buyer_state():
    result = run(place_of_supply="29")
    assert result.tax_type == "intra_state"
    assert result.place_of_supply == "29"


def test_multiple_items_with_different_rates():
    items = [
        {
            "description": "Development",
            "hsn_sac": "998314",
            "quantity": 1,
            "unit_price": 50000,
            "gst_rate": 18,
        },
        {
            "description": "Printed manual",
            "hsn_sac": "4901",
            "quantity": 2,
            "unit_price": 1000,
            "gst_rate": 5,
        },
    ]
    result = run(items=items)
    assert result.totals.taxable_value == Decimal("52000.00")
    assert result.totals.igst == Decimal("9100.00")
    assert result.totals.grand_total == Decimal("61100.00")
    assert result.totals.round_off == Decimal("0.00")


def test_rounding_to_paisa_and_rupee():
    items = [
        {
            "description": "Odd priced item",
            "hsn_sac": "998314",
            "quantity": 3,
            "unit_price": "33.33",
            "gst_rate": 18,
        }
    ]
    result = run(items=items, buyer_state_code="29")
    assert result.totals.taxable_value == Decimal("99.99")
    assert result.totals.cgst == Decimal("9.00")
    assert result.totals.sgst == Decimal("9.00")
    assert result.totals.grand_total == Decimal("118.00")
    assert result.totals.round_off == Decimal("0.01")