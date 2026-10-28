FROM ollama/ollama@sha256:dea72d1e22270fe095b68fdf756d2b489d615643c5a2eaebbc5f569181e322d8

COPY vercel_entrypoint.sh /model_files/vercel_entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/bin/sh", "/model_files/vercel_entrypoint.sh"]
