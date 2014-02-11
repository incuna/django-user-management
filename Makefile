SHELL := /bin/bash

help:
	@echo "Usage:"
	@echo " make release | Release to pypi."
	@echo " make test | Run the tests."

release:
	python setup.py register sdist upload
	python setup.py bdist_wheel upload

test:
	./user_management/tests/run.py
