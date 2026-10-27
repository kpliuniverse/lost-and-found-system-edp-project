
# DO NOT USE THIS, THIS WILL BE USEFUL ONCE MAKING THE PRODUCTION DOCKERFILE
FROM python@sha256:30a34d141e34b8fbedabecb8f86b3d49a62e348d8112ad3c1289f0b2b216ad3e AS builder

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


