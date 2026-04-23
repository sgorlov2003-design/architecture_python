# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=15 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
COPY wheels/ /wheels/

ARG INSTALL_MODE=online
ARG PIP_INDEX_URL=

RUN --mount=type=cache,target=/root/.cache/pip \
    set -eux; \
    pip_install() { pip install --prefer-binary --retries 10 --timeout 120 "$@"; }; \
    if [ "$INSTALL_MODE" = "offline" ]; then \
      pip_install --no-index --find-links=/wheels -r requirements.txt; \
    elif [ -n "$PIP_INDEX_URL" ]; then \
      pip_install --index-url "$PIP_INDEX_URL" -r requirements.txt; \
    else \
      pip_install \
        -i https://pypi.tuna.tsinghua.edu.cn/simple \
        --trusted-host pypi.tuna.tsinghua.edu.cn \
        -r requirements.txt \
      || pip_install \
        -i https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        -r requirements.txt \
      || pip_install -r requirements.txt; \
    fi; \
    rm -rf /wheels/*

COPY app ./app
COPY main.py .
COPY openapi.yaml ./openapi.yaml

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=5s --start-period=25s --retries=8 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
