from decimal import ROUND_HALF_UP, Decimal

from app.schemas import (
    CalculatedInvoice,
    CalculatedItem,
    InvoiceRequest,
    InvoiceTotals,
    LineItem,
)

PAISA = Decimal("0.01")
RUPEE = Decimal("1")
ZERO = Decimal("0.00")


def to_paisa(amount):
    return amount.quantize(PAISA, rounding=ROUND_HALF_UP)


def get_place_of_supply(invoice: InvoiceRequest):
    # for services this is usually the buyer's state
    return invoice.place_of_supply or invoice.buyer.address.state_code


def is_intra_state(invoice: InvoiceRequest):
    seller_state = invoice.seller.gstin[:2]
    return seller_state == get_place_of_supply(invoice)


def calculate_item(item: LineItem, intra_state: bool):
    taxable_value = to_paisa(item.quantity * item.unit_price)

    cgst = sgst = igst = ZERO
    if intra_state:
        # half the rate each, so divide by 200 instead of 100
        cgst = to_paisa(taxable_value * item.gst_rate / 200)
        sgst = cgst
    else:
        igst = to_paisa(taxable_value * item.gst_rate / 100)

    return CalculatedItem(
        description=item.description,
        hsn_sac=item.hsn_sac,
        quantity=item.quantity,
        unit=item.unit,
        unit_price=item.unit_price,
        gst_rate=item.gst_rate,
        taxable_value=taxable_value,
        cgst=cgst,
        sgst=sgst,
        igst=igst,
        total=taxable_value + cgst + sgst + igst,
    )


def calculate_invoice(invoice: InvoiceRequest):
    intra_state = is_intra_state(invoice)
    items = [calculate_item(item, intra_state) for item in invoice.items]

    taxable_value = sum((i.taxable_value for i in items), ZERO)
    cgst = sum((i.cgst for i in items), ZERO)
    sgst = sum((i.sgst for i in items), ZERO)
    igst = sum((i.igst for i in items), ZERO)
    total_tax = cgst + sgst + igst

    exact_total = taxable_value + total_tax
    grand_total = to_paisa(exact_total.quantize(RUPEE, rounding=ROUND_HALF_UP))
    round_off = grand_total - exact_total

    totals = InvoiceTotals(
        taxable_value=taxable_value,
        cgst=cgst,
        sgst=sgst,
        igst=igst,
        total_tax=total_tax,
        round_off=round_off,
        grand_total=grand_total,
    )

    return CalculatedInvoice(
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        seller=invoice.seller,
        buyer=invoice.buyer,
        place_of_supply=get_place_of_supply(invoice),
        tax_type="intra_state" if intra_state else "inter_state",
        items=items,
        totals=totals,
        notes=invoice.notes,
    )