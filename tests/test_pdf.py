from app.calculator import calculate_invoice
from app.pdf_generator import generate_pdf
from app.schemas import InvoiceRequest
from tests.sample_data import sample_invoice


def make_pdf(data):
    calculated = calculate_invoice(InvoiceRequest(**data))
    return generate_pdf(calculated)


def test_inter_state_pdf_is_generated():
    pdf = make_pdf(sample_invoice())
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_intra_state_pdf_is_generated():
    pdf = make_pdf(sample_invoice(buyer_state_code="29"))
    assert pdf.startswith(b"%PDF")


def test_special_characters_do_not_break_the_pdf():
    data = sample_invoice()
    data["buyer"]["name"] = "Sharma & Sons <Traders>"
    data["notes"] = "Pay within 7 days & quote the invoice number"
    pdf = make_pdf(data)
    assert pdf.startswith(b"%PDF")