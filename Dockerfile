# syntax=docker/dockerfile:1
FROM node:22.12-alpine AS web-build
WORKDIR /build
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BOUNDARYLAB_DATA_DIR=/data
WORKDIR /app

RUN groupadd --system boundarylab && useradd --system --gid boundarylab --home-dir /nonexistent boundarylab
COPY apps/service/ /app/apps/service/
COPY contracts/ /app/contracts/
COPY examples/ /app/examples/
COPY --from=web-build /build/dist/ /app/apps/web/dist/
RUN python -m pip install --no-cache-dir --disable-pip-version-check -e /app/apps/service \
    && mkdir -p /data \
    && chown boundarylab:boundarylab /data

USER boundarylab
EXPOSE 8080
VOLUME ["/data"]
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import json,urllib.request; assert json.load(urllib.request.urlopen('http://127.0.0.1:8080/api/healthz', timeout=2))['status']=='ok'"]
CMD ["python", "-m", "boundarylab.devserver", "--host", "0.0.0.0", "--data-dir", "/data"]
