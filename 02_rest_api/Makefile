.PHONY: build build-offline wheels test build-tests clean

# Сборка Docker-образа (PyPI из контейнера; лучше с DOCKER_BUILDKIT=1)
build:
	docker compose build

# Колёса под Linux для офлайн-сборки (на хосте должен работать pip → PyPI)
wheels:
	pip download -r requirements.txt -d wheels \
		-i https://pypi.tuna.tsinghua.edu.cn/simple \
		--trusted-host pypi.tuna.tsinghua.edu.cn \
		--python-version 311 --platform manylinux_2_28_x86_64 \
		--implementation cp --abi cp311 --only-binary=:all:

# Сборка без обращения к PyPI из Docker (сначала: make wheels)
build-offline:
	INSTALL_MODE=offline docker compose build

# Локальные тесты (pytest; зависимости: pip install -r requirements-dev.txt)
test:
	python -m pytest tests/ -v

# Сборка + тесты
build-tests: build test

# Остановка контейнеров
clean:
	docker compose down
