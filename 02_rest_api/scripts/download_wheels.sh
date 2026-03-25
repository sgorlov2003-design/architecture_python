#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p wheels
rm -f wheels/*.whl wheels/*.tar.gz wheels/*.zip 2>/dev/null || true

PLAT="${WHEEL_PLATFORM:-manylinux_2_28_x86_64}"
if [[ "$(uname -m)" == "aarch64" ]] || [[ "${WHEEL_PLATFORM:-}" == *aarch64* ]]; then
  PLAT="manylinux_2_28_aarch64"
fi

INDEX="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"
pip download -r requirements.txt -d wheels \
  -i "$INDEX" --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com \
  --python-version 311 \
  --platform "$PLAT" \
  --implementation cp \
  --abi cp311 \
  --only-binary=:all:

echo "OK: wheels в $ROOT/wheels — INSTALL_MODE=offline docker compose build"
