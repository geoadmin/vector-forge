VENV = .venv
PYTHON_CMD = $(VENV)/bin/python
PYFLAKES_CMD = $(VENV)/bin/pyflakes
AUTOPEP8_CMD = $(VENV)/bin/autopep8
USER = $(shell whoami)
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
	@echo "- autolint						Autolint all python files"
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
		virtualenv $(VENV) --distribute; \
	fi; \
	$(PYTHON_CMD) setup.py develop
	npm install

.PHONY: template	
template:
	@ if [ -z "$$DEV_PORT" ]; then \
		echo "ERROR: Environment variables for DEV_PORT is not set"; exit 2; \
	else true; fi
	sed -e 's/$$DEV_PORT/$(DEV_PORT)/' development.ini.in > development.ini
	cp production.ini.in production.ini

.PHONY: lint
lint:
	$(PYFLAKES_CMD) $(PYTHON_FILES)

.PHONY: autolint
autolint:
	$(AUTOPEP8_CMD) --in-place --aggressive --aggressive --verbose $(PYTHON_FILES)

.PHONY: dev
dev:
	$(VENV)/bin/pserve development.ini --reload

.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf vector_forge.egg-info
	rm -f *.ini
	rm -rf node_modules
