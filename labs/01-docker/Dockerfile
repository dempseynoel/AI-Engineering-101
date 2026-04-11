# Stage 1: Build + export model ------------------------------------------------

FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

# Install build deps (includes torch for ONNX export)
COPY requirements-build.txt .
RUN uv pip install --system --no-cache -r requirements-build.txt

# Download and export model to ONNX
RUN python -c "\
from optimum.onnxruntime import ORTModelForSequenceClassification; \
from transformers import AutoTokenizer; \
model_name = 'distilbert-base-uncased-finetuned-sst-2-english'; \
ORTModelForSequenceClassification.from_pretrained(model_name, export=True).save_pretrained('./model'); \
AutoTokenizer.from_pretrained(model_name).save_pretrained('./model')"

# Install runtime-only deps into a clean prefix (no torch)
COPY requirements-runtime.txt .
RUN uv pip install --no-cache --prefix=/runtime -r requirements-runtime.txt

# Stage 2: Runtime image ------------------------------------------------------

FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home appuser

# Copy only runtime packages (no torch)
COPY --from=builder /runtime/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /runtime/bin/uvicorn /usr/local/bin/uvicorn

# Copy exported ONNX model
COPY --from=builder /build/model ./model/

# Copy application code
COPY app/ ./app/

# Fix ownership of the model
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Document the port the app listens on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]