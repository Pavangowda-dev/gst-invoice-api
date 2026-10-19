import re

from fastapi import FastAPI, Response

from app.calculator import calculate_invoice
from app.pdf_generator import generate_pdf
from app.schemas import CalculatedInvoice, InvoiceRequest

app = FastAPI(
    title="GST Invoice API",
    description="Open-source API to generate GST-compliant invoices for Indian businesses.",
    version="0.1.0",
)


@app.get("/")
def home():
    return {"message": "GST Invoice API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/invoices/calculate", response_model=CalculatedInvoice)
def calculate(invoice: InvoiceRequest):
    return calculate_invoice(invoice)


@app.post("/invoices/pdf")
def invoice_pdf(invoice: InvoiceRequest):
    calculated = calculate_invoice(invoice)
    pdf_bytes = generate_pdf(calculated)

    # invoice numbers like 2026/27/001 are common, but "/" is not safe in a file name
    safe_number = re.sub(r"[^A-Za-z0-9_-]", "-", calculated.invoice_number)
    headers = {"Content-Disposition": f'attachment; filename="invoice-{safe_number}.pdf"'}

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)