SHELL := /bin/bash

keepdb=1 

help:
	@echo "Usage:"
	@echo " make test           | Run the tests."
	@echo " make test keepdb=0  | Run the tests without keeping the db."
	@echo " make run-doc        | Run the docs locally."

test: export KEEPDB=$(keepdb)
test:
	@coverage run ./user_management/tests/run.py
	@coverage report
	@flake8

run-doc:
	@mkdocs serve

release:
	@(git diff --quiet && git diff --cached --quiet) || (echo "You have uncommitted changes - stash or commit your changes"; exit 1)
	@git clean -dxf
	@python setup.py register sdist bdist_wheel
	@twine upload dist/*
