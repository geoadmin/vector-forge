VENV = venv
PYTHON_CMD = $(VENV)/bin/python
USER = $(shell whoami)

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- install            Install the app"
	@echo "- template           Create templates"
	@echo "- lint               Linter for python code"
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
	virtualenv $(VENV)
	$(PYTHON_CMD) setup.py develop

.PHONY: template	
template:
	@ if [ -z "$$DEV_PORT" ]; then \
		echo "ERROR: Environment variables for DEV_PORT is not set"; exit 2; \
	else true; fi
	sed -e 's/$$DEV_PORT/$(DEV_PORT)/' development.ini.in > development.ini
	cp production.ini.in production.ini

.PHONY: lint
lint:
	venv/bin/pyflakes vectorforge/

.PHONY: dev
dev:
	$(VENV)/bin/pserve development.ini --reload

.PHONY: clean
clean:
	rm -rf venv
	rm -rf vector_forge.egg-info
	rm -f *.ini
