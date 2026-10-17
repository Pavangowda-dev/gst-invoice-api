from fastapi import FastAPI

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