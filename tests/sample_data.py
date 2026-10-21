SAMPLE_GSTIN = "29ABCDE1234F1ZW"
BUYER_GSTIN = "33AAACR1234A1ZA"

SAMPLE_BANK = {
    "account_name": "Pavan Dev Studio",
    "bank_name": "HDFC Bank",
    "account_number": "50100123456789",
    "ifsc": "HDFC0001234",
    "upi_id": "pavan@okhdfcbank",
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
            "name": "Pavan Dev Studio",
            "gstin": seller_gstin,
            "address": {
                "line1": "12 MG Road",
                "city": "Bengaluru",
                "state_code": "29",
                "pincode": "560001",
            },
        },
        "buyer": {
            "name": "Acme Traders",
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