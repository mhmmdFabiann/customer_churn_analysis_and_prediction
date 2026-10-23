# Multi-stage or slim python container for serving XGBoost Churn Prediction API
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code, deliverables, and data
COPY src/ ./src/
COPY deliverables/ ./deliverables/
COPY data/ ./data/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI service using uvicorn
CMD ["uvicorn", "deliverables.prediction.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
