# Inspire ORCID push feature tests

Usage:
```bash
# Create config/config.ini (see config/config.ini-template).
$ pip install -r requirements/requirements-base.txt
$ pytest tests -s --env qa
$ pytest tests -s --env qa --remote true
$ pytest tests -s --env qa --headless true
# Or with the Makefile:
$ make tests/qa
$ make tests/qa/remote
$ make tests/qa/headless
```
