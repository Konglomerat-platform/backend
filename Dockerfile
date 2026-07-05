# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.14.5-slim-bookworm
ARG PYPI_INDEX_URL=https://pypi.org/simple
ARG UV_VERSION=0.11.20

FROM ${PYTHON_IMAGE} AS builder

ARG PYPI_INDEX_URL
ARG UV_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --index-url "${PYPI_INDEX_URL}" --no-cache-dir "uv==${UV_VERSION}"

COPY ./pyproject.toml ./uv.lock /app/

RUN uv venv "${VIRTUAL_ENV}" && \
    uv export \
      --locked \
      --no-dev \
      --format requirements-txt \
      > /tmp/requirements.lock.txt && \
    uv pip install \
      --index-url "${PYPI_INDEX_URL}" \
      --no-cache \
      -r /tmp/requirements.lock.txt && \
    rm /tmp/requirements.lock.txt

FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    TZ=Asia/Tashkent \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY . /app

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
