
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


