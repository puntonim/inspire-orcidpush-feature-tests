# This Makefile requires the following commands to be available:
# * virtualenv
# * python2.7
# * docker
# * docker-compose

DEPS:=requirements/requirements-base.txt
DOCKER_COMPOSE=$(shell which docker-compose)

VIRTUALENV=$(shell which virtualenv)
PIP:="venv/bin/pip"
CMD_FROM_VENV:=". venv/bin/activate; which"
PYTHON=$(shell "$(CMD_FROM_VENV)" "python2.7")
PYTEST=$(shell "$(CMD_FROM_VENV)" "pytest")

.PHONY: venv tests requirements clean pyclean pipclean

venv:
	$(VIRTUALENV) -p $(shell which python2.7) venv
	. venv/bin/activate
	$(PIP) install -U "pip>=18.0" -q
	$(PIP) install -U -r $(DEPS)

_make_venv_if_empty:
	@[ -e ./venv/bin/python ] || make venv

tests/qa: _make_venv_if_empty
	$(PYTEST) tests -s --env qa --remote false

tests/prod: _make_venv_if_empty
	$(PYTEST) tests -s --env prod --remote false

tests/qa/remote: _make_venv_if_empty
	$(PYTEST) tests -s --env qa --remote true

tests/prod/remote: _make_venv_if_empty
	$(PYTEST) tests -s --env prod --remote true

## Utilities for the venv currently active.

_ensure_active_env:
ifndef VIRTUAL_ENV
	@echo 'Error: no virtual environment active'
	@exit 1
endif

requirements: _ensure_active_env
	pip install -U "pip>=18.0" -q
	pip install -U -r $(DEPS)


## Generic utilities.

pyclean:
	find . -name *.pyc -delete
	rm -rf *.egg-info build
	rm -rf coverage.xml .coverage
	rm -rf .pytest_cache
	rm -rf __pycache__

clean: pyclean
	rm -rf venv
	rm -rf .tox
	rm -rf dist

pipclean:
	rm -rf ~/Library/Caches/pip
	rm -rf ~/.cache/pip
