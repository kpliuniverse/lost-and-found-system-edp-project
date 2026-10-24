
# DO NOT USE THIS, THIS WILL BE USEFUL ONCE MAKING THE PRODUCTION DOCKERFILE
FROM python@sha256:122756f3fe72c4f5d3d71897888204ee85774bc79de952555b8a474e1d0a5d53 AS builder

COPY --from=ghcr.io/astral-sh/uv@sha256:9f130421e930bfbdc563c00740466603f8723158e90297d07957c2294640262b /uv /uvx /bin/

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_NO_DEV=1

COPY pyproject.toml ./
COPY app ./app

# Export production dependencies without the local project itself.
RUN uv export \
    --format requirements-txt \
    --no-dev \
    --no-emit-project \
    -o requirements.txt

# Build dependency wheels, including psycopg2, from source if needed.
RUN mkdir -p /wheels \
    && pip wheel \
       --no-cache-dir \
       --wheel-dir=/wheels \
       -r requirements.txt

# Build your application wheel separately.
RUN uv build --out-dir /wheels --wheel


FROM python@sha256:122756f3fe72c4f5d3d71897888204ee85774bc79de952555b8a474e1d0a5d53 AS runner

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpq5 \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app/pyproject.toml . 

RUN pip install --no-cache-dir \
    --no-index \
    --find-links=/wheels \
    /wheels/*.whl \
    && rm -rf /wheels

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
