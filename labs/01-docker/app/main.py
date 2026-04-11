"""FastAPI application for serving ML model predictions."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.model import SentimentModel

app = FastAPI(
    title="AI Engineering Demo API",
    description="A simple model-serving API for the AI Engineering seminar series.",
    version="1.0.0",
)

# Initialise the model once at startup
model = SentimentModel()

class PredictionRequest(BaseModel):
    """Input schema for the /predict endpoint."""

    text: str
    model_config = {"json_schema_extra": {"examples": [{"text": "I love this product!"}]}}


class PredictionResponse(BaseModel):
    """Output schema for the /predict endpoint."""

    text: str
    label: str
    score: float


class HealthResponse(BaseModel):
    """Output schema for the /health endpoint."""

    status: str
    is_model_loaded: bool


@app.get("/health", response_model=HealthResponse)
def health_check():
    if not model.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return HealthResponse(status="healthy", is_model_loaded=True)


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if not model.is_loaded:
        raise HTTPException(status_code=503, detail="Model not available")
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")
    result = model.predict(request.text)
    return PredictionResponse(text=request.text, **result)
