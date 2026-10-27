FROM python:3.14.9-slim AS build

COPY --from=ghcr.io/astral-sh/uv@sha256:9f130421e930bfbdc563c00740466603f8723158e90297d07957c2294640262b /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    HF_HOME=/opt/huggingface

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY app ./app
RUN uv sync --locked --no-dev --no-editable \
    && uv run --no-sync python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/clip-ViT-B-32')"

FROM python:3.14.9-slim

WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY --from=build /opt/huggingface /opt/huggingface
COPY app ./app

ENV PATH="/app/.venv/bin:$PATH" \
    HF_HOME=/opt/huggingface \
    HF_HUB_DISABLE_TELEMETRY=1

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
