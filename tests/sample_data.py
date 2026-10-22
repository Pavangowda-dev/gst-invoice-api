SAMPLE_GSTIN = "29ABCDE1234F1ZW"
BUYER_GSTIN = "33AAACR1234A1ZA"

SAMPLE_BANK = {
    "account_name": "Test Seller",
    "bank_name": "Test Bank",
    "account_number": "50100123456789",
    "ifsc": "TEST0001234",
    "upi_id": "testseller@testbank",
}


def sample_invoice(
    seller_gstin=SAMPLE_GSTIN,
    gst_rate=18,
    items=None,
    buyer_state_code="33",
    place_of_supply=None,
    bank_details=None,
):
    if items is None:
        items = [
            {
                "description": "Website development",
                "hsn_sac": "998314",
                "quantity": 1,
                "unit_price": 50000,
                "gst_rate": gst_rate,
            }
        ]

    invoice = {
        "invoice_number": "INV-001",
        "seller": {
            "name": "Test Seller",
            "gstin": seller_gstin,
            "address": {
                "line1": "12 MG Road",
                "city": "Bengaluru",
                "state_code": "29",
                "pincode": "560001",
            },
        },
        "buyer": {
            "name": "Test Buyer",
            "address": {
                "line1": "45 Anna Salai",
                "city": "Chennai",
                "state_code": buyer_state_code,
                "pincode": "600002",
            },
        },
        "items": items,
    }

    if place_of_supply:
        invoice["place_of_supply"] = place_of_supply

    if bank_details:
        invoice["bank_details"] = bank_details

    return invoice