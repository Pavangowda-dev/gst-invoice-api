from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.formatting import amount_in_words, format_inr
from app.schemas import BankDetails, CalculatedInvoice, Party
from app.states import state_name

GREY = colors.HexColor("#f0f0f0")
LINE = colors.HexColor("#999999")

PAGE_WIDTH = 186  # mm of usable width on A4 with 12mm margins

# widths of the item table columns in mm, the description takes whatever is left
COLUMN_WIDTHS = {
    "#": 6,
    "HSN/SAC": 15,
    "Qty": 15,
    "Rate": 17,
    "Discount": 17,
    "Taxable": 17,
    "GST": 10,
    "CGST": 17,
    "SGST": 17,
    "IGST": 17,
    "Total": 19,
}

normal = ParagraphStyle("normal", fontName="Helvetica", fontSize=9, leading=12)
small = ParagraphStyle("small", parent=normal, fontSize=8, leading=10)
title = ParagraphStyle(
    "title", parent=normal, fontName="Helvetica-Bold", fontSize=16, leading=20,
    alignment=TA_CENTER,
)


def clean(text):
    # Paragraph reads its text like XML, so & and < must be escaped
    return escape(str(text))


def party_block(label, party: Party):
    address = party.address
    lines = [
        Paragraph(f"<b>{label}</b>", small),
        Paragraph(f"<b>{clean(party.name)}</b>", normal),
        Paragraph(clean(address.line1), normal),
    ]
    if address.line2:
        lines.append(Paragraph(clean(address.line2), normal))
    lines.append(Paragraph(f"{clean(address.city)} - {address.pincode}", normal))
    lines.append(
        Paragraph(f"{state_name(address.state_code)} ({address.state_code})", normal)
    )
    if party.gstin:
        lines.append(Paragraph(f"GSTIN: {party.gstin}", normal))
    return lines


def plain_number(value):
    # 2.500 -> 2.5, 100 -> 100
    return format(value.normalize(), "f")


def build_header(invoice: CalculatedInvoice):
    place = f"{state_name(invoice.place_of_supply)} ({invoice.place_of_supply})"
    left = [
        Paragraph(f"<b>Invoice No:</b> {clean(invoice.invoice_number)}", normal),
        Paragraph(f"<b>Date:</b> {invoice.invoice_date.strftime('%d-%m-%Y')}", normal),
    ]
    right_side = [Paragraph(f"<b>Place of supply:</b> {place}", normal)]

    table = Table([[left, right_side]], colWidths=[93 * mm, 93 * mm])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return table


def build_parties(invoice: CalculatedInvoice):
    table = Table(
        [[party_block("Sold by", invoice.seller), party_block("Billed to", invoice.buyer)]],
        colWidths=[93 * mm, 93 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LINEAFTER", (0, 0), (0, 0), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_items_table(invoice: CalculatedInvoice):
    intra_state = invoice.tax_type == "intra_state"
    has_discount = any(item.discount > 0 for item in invoice.items)

    # decide which columns this invoice needs
    columns = ["#", "Description", "HSN/SAC", "Qty", "Rate"]
    if has_discount:
        columns.append("Discount")
    columns += ["Taxable", "GST"]
    columns += ["CGST", "SGST"] if intra_state else ["IGST"]
    columns.append("Total")

    fixed = sum(COLUMN_WIDTHS[name] for name in columns if name != "Description")
    widths = [
        (PAGE_WIDTH - fixed if name == "Description" else COLUMN_WIDTHS[name]) * mm
        for name in columns
    ]

    rows = [columns]
    for number, item in enumerate(invoice.items, start=1):
        cells = {
            "#": str(number),
            "Description": Paragraph(clean(item.description), small),
            "HSN/SAC": item.hsn_sac,
            "Qty": f"{plain_number(item.quantity)} {item.unit}",
            "Rate": format_inr(item.unit_price),
            "Discount": format_inr(item.discount),
            "Taxable": format_inr(item.taxable_value),
            "GST": f"{plain_number(item.gst_rate)}%",
            "CGST": format_inr(item.cgst),
            "SGST": format_inr(item.sgst),
            "IGST": format_inr(item.igst),
            "Total": format_inr(item.total),
        }
        rows.append([cells[name] for name in columns])

    table = Table(rows, colWidths=widths, repeatRows=1)

    # numbers sit on the right, text on the left
    first_number_column = columns.index("Rate")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("BACKGROUND", (0, 0), (-1, 0), GREY),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("ALIGN", (first_number_column, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    return table


def build_totals(invoice: CalculatedInvoice):
    totals = invoice.totals
    rows = []

    if totals.discount > 0:
        rows.append(["Total discount", format_inr(totals.discount)])

    rows.append(["Taxable value", format_inr(totals.taxable_value)])

    if invoice.tax_type == "intra_state":
        rows.append(["CGST", format_inr(totals.cgst)])
        rows.append(["SGST", format_inr(totals.sgst)])
    else:
        rows.append(["IGST", format_inr(totals.igst)])

    if totals.round_off != 0:
        rows.append(["Round off", format_inr(totals.round_off)])

    rows.append(["Grand total (Rs.)", format_inr(totals.grand_total)])

    table = Table(rows, colWidths=[45 * mm, 35 * mm], hAlign="RIGHT")
    table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), GREY),
                ("LINEABOVE", (0, -1), (-1, -1), 0.5, LINE),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
            ]
        )
    )
    return table


def build_bank_details(bank: BankDetails):
    lines = [
        Paragraph("<b>Bank details</b>", small),
        Paragraph(f"Account name: {clean(bank.account_name)}", normal),
        Paragraph(f"Bank: {clean(bank.bank_name)}", normal),
        Paragraph(f"Account number: {bank.account_number}", normal),
        Paragraph(f"IFSC: {bank.ifsc}", normal),
    ]
    if bank.upi_id:
        lines.append(Paragraph(f"UPI ID: {clean(bank.upi_id)}", normal))

    table = Table([[lines]], colWidths=[93 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def generate_pdf(invoice: CalculatedInvoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=f"Invoice {invoice.invoice_number}",
    )

    story = [
        Paragraph("TAX INVOICE", title),
        Spacer(1, 6 * mm),
        build_header(invoice),
        Spacer(1, 3 * mm),
        build_parties(invoice),
        Spacer(1, 5 * mm),
        build_items_table(invoice),
        Spacer(1, 4 * mm),
        build_totals(invoice),
        Spacer(1, 5 * mm),
        Paragraph(
            f"<b>Amount in words:</b> {amount_in_words(invoice.totals.grand_total)}",
            normal,
        ),
    ]

    if invoice.bank_details:
        story.append(Spacer(1, 5 * mm))
        story.append(build_bank_details(invoice.bank_details))

    if invoice.notes:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(f"<b>Notes:</b> {clean(invoice.notes)}", normal))

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("This is a computer generated invoice.", small))

    doc.build(story)
    return buffer.getvalue()