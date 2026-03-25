# Скачивает wheel'ы под Linux x86_64 (образ python:3.11-slim-bookworm), чтобы Docker-сборка
# не ходила в PyPI. Запускать на Windows/macOS/Linux, где pip видит PyPI.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
New-Item -ItemType Directory -Force -Path "wheels" | Out-Null
Get-ChildItem "wheels" -Include *.whl,*.tar.gz,*.zip -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

$plat = "manylinux_2_28_x86_64"
if ($env:DOCKER_DEFAULT_PLATFORM -match "arm64" -or $env:WHEEL_PLATFORM -match "aarch64") {
    $plat = "manylinux_2_28_aarch64"
}

$index = if ($env:PIP_INDEX_URL) { $env:PIP_INDEX_URL } else { "https://pypi.tuna.tsinghua.edu.cn/simple" }
pip download -r requirements.txt -d wheels `
    -i $index --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com `
    --python-version 311 `
    --platform $plat `
    --implementation cp `
    --abi cp311 `
    --only-binary=:all:

Write-Host "OK: wheels в $root\wheels — соберите образ: INSTALL_MODE=offline docker compose build"
