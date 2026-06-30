SHELL := /bin/bash
export PATH := /usr/local/bin:$(PATH)
export

ifeq ($(OS),Windows_NT)
    PYTHON := python.exe
    ACTIVATE_VENV := venv/Scripts/activate
else
    PYTHON := python3.13
    ACTIVATE_VENV := source venv/bin/activate
endif
PIP := $(PYTHON) -m pip

ifeq ("$(wildcard .env)","")
    $(shell cp .env.example .env)
endif
include .env


.PHONY: all init activate build run tear-down pre-commit-init pre-commit-run release analyze \
		check-python python-init python-lint python-clean python-requirements python-fetch-data python-build-dataset help

# Default target executed when no arguments are given to make.
all: help

# initialize local development environment.
# takes a few minutes to complete
init:
	@echo "==============================================================================="
	@echo "Initializing local development environment. This will verify and set up your"
	@echo "Python virtual environment, install all 3rd-party package requirements."
	@echo "This may take a few minutes..."
	@echo "==============================================================================="
	@echo ""
	@echo ""
	@echo "==============================================================================="
	@echo "Initialization complete!"
	@echo "==============================================================================="
	make python-init

activate:
	./scripts/activate.sh

# run the web application from Docker
# takes around 30 seconds to complete
run:
	@echo "==============================================================================="
	@echo "Running solution ..."
	@echo "==============================================================================="
	make python-fetch-data
	make python-build-dataset

# destroy all Docker build and local artifacts
# takes around 1 minute to complete
tear-down:
	@echo "==============================================================================="
	@echo "Tearing down solution ..."
	@echo "==============================================================================="
	make python-clean

pre-commit-init:
	@echo "==============================================================================="
	@echo "Installing and configuring pre-commit ..."
	@echo "==============================================================================="
	pre-commit install
	pre-commit autoupdate

pre-commit-run:
	@echo "==============================================================================="
	@echo "Running pre-commit hooks on all files ..."
	@echo "==============================================================================="
	pre-commit run --all-files

release:
	@echo "==============================================================================="
	@echo "Forcing a new semantic release on GitHub by creating an empty commit and pushing to the repository ..."
	@echo "==============================================================================="
	git commit -m "fix: force a new release" --allow-empty && git push

analyze:
	@echo "==============================================================================="
	@echo "Generating code analysis report using cloc ..."
	@echo "==============================================================================="
	cloc . --exclude-ext=svg,zip --fullpath --not-match-d=smarter/smarter/static/assets/ --vcs=git

# ---------------------------------------------------------
# Python
# ---------------------------------------------------------
check-python:
	@echo ""
	@echo "==============================================================================="
	@echo "Verifying that Python $(PYTHON) is installed ..."
	@echo "==============================================================================="
	@echo ""
	@command -v $(PYTHON) >/dev/null 2>&1 || { \
	echo >&2 "This project requires $(PYTHON) but it's not installed.  Aborting."; \
	echo >&2 "python --version output:"; \
	python --version 2>&1; \
	exit 1; \
}

python-init:
	@echo "==============================================================================="
	@echo "Initializing Python virtual environment and installing dependencies. This may take a few minutes..."
	@echo "==============================================================================="
	rm -r -f venv && \
	mkdir -p .pypi_cache && \
	make check-python
	make python-clean && \
	npm install && \
	$(PYTHON) -m venv venv && \
	$(ACTIVATE_VENV) && \
	$(PIP) install pip==25.3 setuptools wheel pip-tools && \
	PIP_CACHE_DIR=.pypi_cache $(PIP) install -r requirements/local.txt
	$(ACTIVATE_VENV) && $(PYTHON) -m ipykernel install --user --name py311 --display-name "Python 3.13"

python-lint:
	@echo ""
	@echo "==============================================================================="
	@echo "Running Python linting using pre-commit ..."
	@echo "==============================================================================="
	@echo ""
	make check-python
	make pre-commit-run
	pylint netflix

python-clean:
	@echo ""
	@echo "==============================================================================="
	@echo "Cleaning Python virtual environment and __pycache__ directories ..."
	@echo "==============================================================================="
	@echo ""
	rm -rf venv
	find ./netflix/ -name __pycache__ -type d -exec rm -rf {} +

# FIX NOTE: mcdaniel. the pip version pin temporarily resolves a pip-compile issue.
#           AttributeError: 'PackageFinder' object has no attribute 'allow_all_prereleases'
python-requirements:
	@echo "==============================================================================="
	@echo "Compiling and updating Python dependency files using pip-compile ..."
	@echo "==============================================================================="
	pip install pip==25.3 setuptools wheel pip-tools
	pip-compile requirements/in/base.in -o requirements/base.txt
	pip-compile requirements/in/local.in -o requirements/local.txt

python-fetch-data:
	@echo "==============================================================================="
	@echo "Fetching data from external APIs and saving to local files ..."
	@echo "==============================================================================="
	$(ACTIVATE_VENV) && python -m netflix.fetch

python-build-dataset:
	@echo "==============================================================================="
	@echo "Building composite Netflix dataset from fetched data ..."
	@echo "==============================================================================="
	$(ACTIVATE_VENV) && python -m netflix.build

python-build-stories:
	@echo "==============================================================================="
	@echo "Building  ..."
	@echo "==============================================================================="
	$(ACTIVATE_VENV) && python -m netflix.build.story_codes


######################
# HELP
######################

help:
	@echo '===================================================================='
	@echo 'init                   - Initialize local and Docker environments'
	@echo 'activate               - Activate Python virtual environment'
	@echo 'build                  - Build Docker containers'
	@echo 'run                    - Run web application from Docker'
	@echo 'test                   - Run Python-Django unit tests in Docker'
	@echo 'clean                  - Delete all local artifacts, virtual environment, node_modules, and Docker containers'
	@echo 'tear-down              - Destroy all Docker build and local artifacts'
	@echo 'pre-commit-init        - Install and configure pre-commit hooks'
	@echo 'pre-commit-run         - Run pre-commit hooks on all files'
	@echo 'release                - Force a new semantic release on GitHub by creating an empty commit and pushing to the repository'
	@echo 'analyze                - Generate code analysis report using cloc'
	@echo '<************************** Python **************************>'
	@echo 'check-python           - Verify Python 3.13 is installed'
	@echo 'python-init            - Create a Python virtual environment and install dependencies'
	@echo 'python-lint            - Run Python linting using pre-commit and pylint'
	@echo 'python-clean           - Destroy the Python virtual environment and remove __pycache__ directories'
	@echo 'python-requirements    - Compile and update Python dependency files'
	@echo 'python-fetch-data      - Fetch data from external APIs and save to local files'
	@echo 'python-build-dataset   - Build composite Netflix dataset from fetched data'
	@echo '===================================================================='
