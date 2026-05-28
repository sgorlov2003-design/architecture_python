FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    cmake \
    pkg-config \
    g++ \
    libssl-dev \
    zlib1g-dev \
    libpoco-dev \
    librdkafka-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY includes/ ./includes/
COPY src/ ./src/
COPY CMakeLists.txt ./CMakeLists.txt

RUN mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libssl3 \
    zlib1g \
    libpocofoundation80 \
    libpocojson80 \
    libpocoutil80 \
    libpoconet80 \
    librdkafka1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY --from=builder /usr/lib/x86_64-linux-gnu/librdkafka*.so* /usr/lib/x86_64-linux-gnu/
RUN ldconfig

COPY --from=builder /build/build/fitness_events_demo /app/fitness_events_demo
COPY openapi.yaml /app/openapi.yaml

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

CMD ["/app/fitness_events_demo"]
