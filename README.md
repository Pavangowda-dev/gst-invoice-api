# GST Invoice API

An open-source API that generates GST-compliant invoices (CGST, SGST, IGST) for freelancers and small businesses in India.

Work in progress. Being built step by step.

## Run locally

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs