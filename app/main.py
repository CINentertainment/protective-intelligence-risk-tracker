from fastapi import FastAPI


app = FastAPI(
    title="Protective Intelligence Risk Tracker",
    description=(
        "A portfolio application for documenting protective intelligence "
        "cases, indicators, assessments, and mitigation actions."
    ),
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "application": "Protective Intelligence Risk Tracker",
        "status": "operational",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}