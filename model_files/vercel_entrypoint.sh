#!/bin/sh
set -eu

export OLLAMA_HOST="0.0.0.0:${PORT:-80}"

ollama serve &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT

attempt=0
until ollama list >/dev/null 2>&1; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        echo "Ollama server exited before becoming ready." >&2
        wait "$server_pid"
        exit 1
    fi

    attempt=$((attempt + 1))
    if [ "$attempt" -ge 60 ]; then
        echo "Timed out waiting for Ollama to become ready." >&2
        exit 1
    fi
    sleep 1
done

ollama pull nomic-embed-text
wait "$server_pid"
