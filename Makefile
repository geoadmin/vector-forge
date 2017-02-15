VENV = .venv
DEV_PORT ?= 9040
PYTHON_CMD = $(VENV)/bin/python
PIP_CMD = $(VENV)/bin/pip
PYFLAKES_CMD = $(VENV)/bin/pyflakes
AUTOPEP8_CMD = $(VENV)/bin/autopep8
MAKO_CMD = $(VENV)/bin/mako-render
USER = $(shell whoami)
DBHOST ?= pg-0.dev.bgdi.ch
PYTHON_FILES = $(shell find vectorforge/ -type f -name "*.py" -print)

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- install            Install the app"
	@echo "- template           Create templates"
	@echo "- lint               Linter for python code"
	@echo "- autolint           Autolint all python files"
	@echo "- all                All of the above"
	@echo "- dev                Enter dev shell"
	@echo "- clean              Clean all generated files and folders"
	@echo
	@echo "Variables:"
	@echo
	@echo "- USER (current value: $(USER))"
	@echo "- PYTHON_CMD (current value: $(PYTHON_CMD))"

	@echo

.PHONY: all
all: install template lint

.PHONY: install
install:
	@if [ ! -d $(VENV) ]; \
	then \
		virtualenv $(VENV); \
		$(PIP_CMD) install --upgrade pip setuptools; \
	fi; \
	$(PIP_CMD) install -e .
	npm install

.PHONY: template
template: development.ini production.ini

.PHONY: lint
lint:
	$(PYFLAKES_CMD) $(PYTHON_FILES)

.PHONY: autolint
autolint:
	$(AUTOPEP8_CMD) --in-place --aggressive --aggressive --verbose $(PYTHON_FILES)

.PHONY: dev
dev:
	$(VENV)/bin/pserve development.ini --reload

development.ini: development.ini.in
	${MAKO_CMD} \
		--var "dev_port=$(DEV_PORT)" $< > $@

production.ini: production.ini.in
	${MAKO_CMD} \
		--var "dbhost=$(DBHOST)" $< > $@

.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf vector_forge.egg-info
	rm -f *.ini
	rm -rf node_modules
