FROM alpine/ollama@sha256:d81e4e3a38eefb991891fd1a19e3e34832e239ea4b0c211cdde9a70c13b882e6

COPY vercel_entrypoint.sh /model_files/vercel_entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/bin/sh", "/model_files/vercel_entrypoint.sh"]
