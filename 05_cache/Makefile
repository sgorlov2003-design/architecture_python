.PHONY: build build-offline wheels test build-tests clean

build:
	docker compose build

wheels:
	pip download -r requirements.txt -d wheels \
		-i https://pypi.tuna.tsinghua.edu.cn/simple \
		--trusted-host pypi.tuna.tsinghua.edu.cn \
		--python-version 311 --platform manylinux_2_28_x86_64 \
		--implementation cp --abi cp311 --only-binary=:all:

build-offline:
	INSTALL_MODE=offline docker compose build

# Требуется PostgreSQL (см. README): docker compose up -d postgres
test:
	python -m pytest tests/ -v

build-tests: build test

clean:
	docker compose down
