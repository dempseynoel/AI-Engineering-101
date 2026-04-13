# Docker for AI Engineers

Docker from scratch: build, containerise, and deploy a real sentiment analysis model end to end.

**AI Engineering Training — Lab 1**

## Overview

This lab walks through packaging a FastAPI sentiment analysis API (serving a DistilBERT model via ONNX Runtime) into a Docker container, then deploying it to Azure Container Apps as a live endpoint.

You'll write a multi-stage Dockerfile from scratch, optimise image size from 9.4GB down to 1.5GB, and learn why each decision matters in production AI/ML work.

## Prerequisites

- **Docker Desktop** installed and running
- **Python 3.11+** for local development
- **VS Code** (or any editor with a terminal)
- **Azure CLI** (`az`) installed and authenticated with an active Azure subscription
- **Git** installed, to clone the repo containing the demo source files

No prior Docker or Azure experience is needed.

## What You'll Learn

- What Docker is and why it matters for AI engineering
- How a real model is integrated into a serving application
- How to write a Dockerfile for an AI/ML application with model dependencies
- How to build, run, and deploy a containerised FastAPI model endpoint to Azure

Full documentation with added explanations is available [here](https://dempseynoel.github.io/AI-Engineering-101/labs/01-docker/docs/01-docker.html).

## Project Structure

```
.
├── Dockerfile
├── .dockerignore
├── requirements-build.txt      # Build-stage dependencies (PyTorch, optimum, etc.)
├── requirements-runtime.txt    # Runtime dependencies (onnxruntime, fastapi, etc.)
├── app/
│   ├── main.py                 # FastAPI app with POST /predict endpoint
│   └── model.py                # DistilBERT model wrapper (ONNX inference)
└── images/                     # Lab documentation images
```

## Quick Start

### Build the image

```bash
docker build -t bert-sentiment-api:version1 .
```

The first build takes a few minutes (downloading the base image, installing dependencies, exporting the model to ONNX). Subsequent builds are much faster thanks to layer caching.

### Run locally

```bash
docker run --rm --name bert-api -p 8000:8000 bert-sentiment-api:version1
```

Once you see the Uvicorn startup message, open [http://localhost:8000/docs](http://localhost:8000/docs) to access the Swagger UI and test the `/predict` endpoint.

### Stop the container

```bash
docker stop bert-api
```

## Deploy to Azure

### 1. Push to Azure Container Registry

```bash
az login
az acr create --name <yourregistryname> --resource-group <yourresourcegroup> --sku Basic
az acr login --name <yourregistryname>
docker tag bert-sentiment-api:version1 <yourregistryname>.azurecr.io/bert-sentiment-api:version1
docker push <yourregistryname>.azurecr.io/bert-sentiment-api:version1
```

### 2. Deploy to Azure Container Apps

```bash
az containerapp env create \
  --name <yourenvname> \
  --resource-group <yourresourcegroup> \
  --location uksouth

az containerapp create \
  --name bert-sentiment-api \
  --resource-group <yourresourcegroup> \
  --environment <yourenvname> \
  --image <yourregistryname>.azurecr.io/bert-sentiment-api:version1 \
  --target-port 8000 \
  --ingress external \
  --registry-server <yourregistryname>.azurecr.io
```

Once deployed, append `/docs` to the URL Azure provides to access the Swagger UI.

### 3. Clean up resources

```bash
az group delete --name <yourresourcegroup> --yes --no-wait
```

> **Warning:** Delete your resources when you're done to avoid incurring costs.

## Dockerfile Design

The Dockerfile uses a **multi-stage build** with `uv` for fast dependency installs:

- **Stage 1 (builder):** Installs PyTorch and Hugging Face tooling, downloads the DistilBERT model, exports it to ONNX format, and installs runtime dependencies into an isolated prefix.
- **Stage 2 (runtime):** Starts from a clean `python:3.11-slim` base, copies only the ONNX model, runtime packages, and application code. Runs as a non-root user.

This approach reduced the final image from **9.4GB** (full PyTorch + CUDA) → **2.5GB** (CPU-only PyTorch) → **1.5GB** (ONNX Runtime, multi-stage).

## Scanning for Vulnerabilities

```bash
docker scout quickview bert-sentiment-api:version1
docker scout cves bert-sentiment-api:version1
```

## What's Next

**Lab 2** covers deploying the same API using **Terraform** for infrastructure as code — version-controlled, reviewable, and reproducible across environments.

## Author

Noel Dempsey | April 2026
