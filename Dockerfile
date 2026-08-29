FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VULCAN_INTELLIGENCE_MODE=auto \
    VULCAN_MODEL_NAME=Qwen/Qwen3.8-27B \
    VULCAN_MODEL_BASE_URL=http://host.docker.internal:8001/v1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "vulcan.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
