# A real HTTP readiness probe without assuming curl exists in the Qdrant image.
FROM busybox:1.37.0-musl AS probe
FROM qdrant/qdrant:v1.15.5
COPY --from=probe /bin/busybox /usr/local/bin/busybox
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 CMD ["/usr/local/bin/busybox", "wget", "-q", "-O", "/dev/null", "http://127.0.0.1:6333/readyz"]
