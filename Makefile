
.PHONY:
all: lint

.PHONY: lint
lint:
	flake8 --ignore=E121,E123,E126,E128,E226,E24,E704,E265,W503,W504,E501,E402 charm/timescaledb
