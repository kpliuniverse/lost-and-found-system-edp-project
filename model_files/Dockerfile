FROM ollama/ollama@sha256:dea72d1e22270fe095b68fdf756d2b489d615643c5a2eaebbc5f569181e322d8

ENV OLLAMA_HOST=127.0.0.1:11434

RUN set -eu; \
    ollama serve >/tmp/ollama-build.log 2>&1 & server_pid=$!; \
    trap 'kill "$server_pid" 2>/dev/null || true' EXIT; \
    attempt=0; \
    until ollama list >/dev/null 2>&1; do \
        attempt=$((attempt + 1)); \
        if [ "$attempt" -ge 60 ]; then \
            cat /tmp/ollama-build.log >&2; \
            exit 1; \
        fi; \
        sleep 1; \
    done; \
    ollama pull nomic-embed-text

COPY vercel_entrypoint.sh /model_files/vercel_entrypoint.sh

ENV OLLAMA_HOST=0.0.0.0:80
EXPOSE 80
ENTRYPOINT ["/bin/sh", "/model_files/vercel_entrypoint.sh"]
