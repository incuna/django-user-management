SHELL := /bin/bash

help:
	@echo "Usage:"
	@echo " make test    | Run the tests."

test:
	@coverage run ./user_management/tests/run.py
	@coverage report --show-missing --fail-under=100
	@flake8
