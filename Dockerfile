FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ ./config/
COPY src/ ./src/
COPY scripts/ ./scripts/

# Only copy models if they exist (build won't fail if missing)
COPY models/ ./models/

ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

# GEMINI_API_KEY should be injected via Cloud Run secrets, not baked in.
# Example:  gcloud run deploy ... --set-secrets=GEMINI_API_KEY=gemini-key:latest

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
