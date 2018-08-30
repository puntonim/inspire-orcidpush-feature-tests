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
TOX=$(shell "$(CMD_FROM_VENV)" "tox")
PYTHON=$(shell "$(CMD_FROM_VENV)" "python2.7")
TOX_PY_LIST="$(shell $(TOX) -l | grep ^py | xargs | sed -e 's/ /,/g')"

.PHONY: venv clean pyclean test tox docker setup.py celery-monitor

venv:
	$(VIRTUALENV) -p $(shell which python2.7) venv
	@. venv/bin/activate
	@$(PIP) install -U "pip>=18.0" -q
	@$(PIP) install -r $(DEPS)

test/%: venv pyclean
	$(TOX) -e $(TOX_PY_LIST) -- $*

celery-monitor/prod:
	$(DOCKER_COMPOSE) run --rm app make test/"-s -k test_actually_count_celery_queues --env prod"

celery-monitor/qa:
	$(DOCKER_COMPOSE) run --rm app make test/"-s -k test_actually_count_celery_queues --env qa"

docker:
	$(DOCKER_COMPOSE) run --rm app bash

docker/%:
	$(DOCKER_COMPOSE) run --rm app make $*

setup.py: venv
	$(PYTHON) setup_gen.py
	@$(PYTHON) setup.py check --restructuredtext

tox: clean venv
	$(TOX)

pyclean:
	@find . -name *.pyc -delete
	@rm -rf *.egg-info build

clean: pyclean
	@rm -rf venv
	@rm -rf .tox
