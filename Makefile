SHELL := /bin/bash

help:
	@echo "Usage:"
	@echo " make release | Release to pypi."

release:
	python setup.py register sdist bdist_wheel upload
