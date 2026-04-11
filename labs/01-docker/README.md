# AI Engineering Demo

A companion repository for the **AI Engineering Seminar Series** — teaching data scientists the infrastructure skills they need to deploy ML models to production.

## Seminar Series

| Seminar | Topic | Key Files |
|---------|-------|-----------|
| **1 — Docker** | Containerising a DistilBERT model endpoint | `app/`, `Dockerfile`, `.dockerignore` |
| **2 — Terraform** | Infrastructure as Code for Azure | `infra/` |

The repo also includes a simple CI/CD pipeline (`.github/workflows/`) that ties everything together: running tests, building the Docker image, and deploying to Azure on merge to main.

## Project Structure

```
ai-engineering-demo/
├── app/
│   ├── main.py              # FastAPI application
│   └── model.py             # DistilBERT sentiment model wrapper
├── tests/
│   └── test_api.py          # API test suite
├── infra/
│   ├── main.tf              # Azure infrastructure
│   ├── variables.tf         # Terraform variables
│   ├── outputs.tf           # Terraform outputs
│   └── terraform.tfvars.example
├── .github/workflows/
│   ├── ci.yml               # CI: test + Docker build on every push
│   └── deploy.yml           # CD: push to ACR + Terraform apply on main
├── Dockerfile               # Multi-stage build with uv (pre-downloads model weights)
├── .dockerignore
├── requirements.txt
└── .gitignore
```

## The Model

This demo uses **DistilBERT** (`distilbert-base-uncased-finetuned-sst-2-english`), a
distilled version of BERT fine-tuned for sentiment analysis. It's a real transformer
model with 66M parameters that runs on CPU in under a second — no GPU needed.

It is **not** an LLM. It's an encoder-only classifier that takes text in and outputs
a sentiment label (positive/negative) with a confidence score.

## Quick Start

### Run locally (no Docker)

```bash
cd ai-engineering-demo
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload
# Open http://localhost:8000/docs
```

### Run with Docker

```bash
docker build -t ai-demo:local .
docker run -p 8000:8000 ai-demo:local
# Open http://localhost:8000/docs
```

### Run tests

```bash
uv pip install pytest httpx
pytest tests/ -v
```

### Deploy infrastructure

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

## CI/CD Pipeline

The GitHub Actions pipeline automates the full lifecycle:

- **CI** (`ci.yml`): On every push — installs dependencies with uv, runs pytest, then builds the Docker image and verifies the container starts and passes a health check.
- **CD** (`deploy.yml`): On merge to main (after CI passes) — builds and pushes the image to ACR, runs Terraform to update the Container App, and runs a smoke test against the live endpoint.

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Azure service principal credentials (JSON) |

The ACR name is configured as an environment variable in `deploy.yml`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns model loaded status |
| `POST` | `/predict` | Sentiment prediction — accepts `{"text": "..."}` |
| `GET` | `/docs` | Interactive Swagger UI |

### Example Request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I absolutely love this product!"}'
```

```json
{
  "text": "I absolutely love this product!",
  "label": "positive",
  "score": 0.9998
}
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop
- Terraform 1.5+
- Azure CLI (logged in)
- An Azure subscription
