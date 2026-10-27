#!/bin/sh
set -eu

echo "Starting Ollama server..."
ollama serve &
SERVER_PID=$!

echo "Waiting for Ollama to become ready..."
attempt=0
until ollama list >/dev/null 2>&1; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Ollama server exited before becoming ready." >&2
        wait "$SERVER_PID"
        exit 1
    fi

    attempt=$((attempt + 1))
    if [ "$attempt" -ge 60 ]; then
        echo "Timed out waiting for Ollama to become ready." >&2
        exit 1
    fi
    sleep 1
done

echo "Pulling nomic-embed-text..."
ollama pull nomic-embed-text
wait "$SERVER_PID"
