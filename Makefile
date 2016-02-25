SHELL := /bin/bash

help:
	@echo "Usage:"
	@echo " make test    | Run the tests."
	@echo " make run-doc | Run the docs locally."

test:
	@coverage run ./user_management/tests/run.py
	@coverage report --show-missing --fail-under=100
	@flake8

run-doc:
	@mkdocs serve

release:
	@(git diff --quiet && git diff --cached --quiet) || (echo "You have uncommitted changes - stash or commit your changes"; exit 1)
	@git clean -dxf
	@python setup.py register sdist bdist_wheel upload
