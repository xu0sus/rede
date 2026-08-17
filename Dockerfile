# Khul3awiyah V171 - Render Free Web Service runtime
# Source baseline: Red 3.5.24-60-g61484f28f7f
FROM python:3.11.15-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    RED_INSTANCE=khul3awiyah \
    RED_DATA_DIR=/data/khul3awiyah

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        openjdk-21-jre-headless \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements/base.txt requirements/extra-test.txt /tmp/requirements/
RUN python -m pip install --no-cache-dir -r /tmp/requirements/base.txt \
    && python -m pip install --no-cache-dir -r /tmp/requirements/extra-test.txt

COPY . /app
RUN python -m pip install --no-cache-dir --no-deps -e .

COPY docker/render-entrypoint.sh docker/render-health.py docker/render-keepalive.py /usr/local/bin/
RUN chmod +x /usr/local/bin/render-entrypoint.sh /usr/local/bin/render-health.py /usr/local/bin/render-keepalive.py \
    && mkdir -p /data

EXPOSE 10000
ENTRYPOINT ["/usr/local/bin/render-entrypoint.sh"]
