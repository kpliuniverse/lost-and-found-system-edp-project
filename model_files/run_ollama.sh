#!/bin/bash

echo "Starting Ollama server..."
ollama serve &  # Start Ollama in the background

echo "Ollama is ready, creating the model..."

ollama serve & SERVER_PID=$!
ollama pull nomic-embed-text
wait $SERVER_PID