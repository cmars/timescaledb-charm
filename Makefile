
all: lint charm

.PHONY: lint
lint:
	flake8 --ignore=E121,E123,E126,E128,E226,E24,E704,E265,W503,W504 charm/timescaledb

.PHONY: charm
charm: charm/builds/timescaledb

charm/builds/timescaledb:
	charm build -o ./charm ./charm/timescaledb

.PHONY: clean-charm
clean-charm:
	$(RM) -r charm/builds/timescaledb

.PHONY: clean
clean: clean-charm
