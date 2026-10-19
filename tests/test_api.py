from fastapi.testclient import TestClient

from app.main import app
from tests.sample_data import sample_invoice

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_calculate_endpoint():
    response = client.post("/invoices/calculate", json=sample_invoice())
    assert response.status_code == 200
    body = response.json()
    assert body["tax_type"] == "inter_state"
    assert body["totals"]["igst"] == "9000.00"
    assert body["totals"]["grand_total"] == "59000.00"


def test_pdf_endpoint_returns_a_pdf():
    response = client.post("/invoices/pdf", json=sample_invoice())
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "invoice-INV-001.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_pdf_endpoint_rejects_bad_input():
    response = client.post("/invoices/pdf", json=sample_invoice(seller_gstin="123"))
    assert response.status_code == 422