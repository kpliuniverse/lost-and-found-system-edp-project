#!/bin/sh
set -eu

export OLLAMA_HOST="0.0.0.0:${PORT:-80}"
exec ollama serve
