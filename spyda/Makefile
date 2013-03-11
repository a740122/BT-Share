.PHONY: help clean docs tests

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean     to cleanup build and temporary files"
	@echo "  docs      to build the documentation"
	@echo "  tests     to run the test suite"

clean:
	@rm -rf build dist spyda.egg-info
	@rm -rf .coverage coverage
	@rm -rf docs/build
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete
	@find . -name "__pycache__" -delete

docs:
	@make -C docs clean html

tests:
	@python -m tests.main
