.PHONY: test test-tox audit clean-pyc docs venv-activate venv

all: clean-pyc test

MODE?=dev

venv-activate:
	$(eval PWD := $(shell pwd))
	test -d $(PWD)/.venv || virtualenv $(PWD)/.venv --no-site-packages --distribute
	. $(PWD)/.venv/bin/activate; pip install -Ur $(PWD)/requirements/requirements-$(MODE).txt
	touch $(PWD)/.venv/bin/activate

venv: venv-activate

test: venv
	$(eval PWD := $(shell pwd))
	. $(PWD)/.venv/bin/activate; python run_tests.py

run: venv
	$(eval PWD := $(shell pwd))
	. $(PWD)/.venv/bin/activate; python scatter/tests/main.py

test-tox:
	tox

audit:
	python setup.py audit

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -rf {} +

docs:
	$(MAKE) -C docs html
