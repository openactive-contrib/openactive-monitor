# Makefile to set up virtual environments and install requirements
# for all subdirectories under jobs/ and services/ (except volume-1/)

# Detect which python command works
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

# Directories to process (excluding volume-1)
JOB_DIRS := $(filter-out jobs/volume-1, $(wildcard jobs/*))
SERVICE_DIRS := $(filter-out services/volume-1, $(wildcard services/*))
ALL_DIRS := $(JOB_DIRS) $(SERVICE_DIRS)

.PHONY: all setup clean check-python help

help:
	@echo "Available targets:"
	@echo "  all         - Set up virtual environments and install requirements for all directories"
	@echo "  setup       - Same as 'all'"
	@echo "  clean       - Remove all virtual environments"
	@echo "  check-python - Check which Python is available"
	@echo ""
	@echo "Directories that will be processed:"
	@for dir in $(ALL_DIRS); do echo "  - $$dir"; done

check-python:
	@if [ -z "$(PYTHON)" ]; then \
		echo "Error: Neither python nor python3 found in PATH"; \
		exit 1; \
	fi
	@echo "Using Python: $(PYTHON)"
	@$(PYTHON) --version

all: check-python setup

setup: check-python
	@echo "Setting up virtual environments..."
	@for dir in $(ALL_DIRS); do \
		if [ -d "$$dir" ] && [ -f "$$dir/requirements.txt" ]; then \
			echo ""; \
			echo "========================================"; \
			echo "Processing: $$dir"; \
			echo "========================================"; \
			cd $$dir && \
			echo "Creating virtual environment..." && \
			$(PYTHON) -m venv virt && \
			echo "Activating virtual environment..." && \
			. virt/bin/activate && \
			echo "Installing requirements..." && \
			pip install -r requirements.txt && \
			echo "Deactivating virtual environment..." && \
			deactivate && \
			cd - > /dev/null; \
			echo "Done with $$dir"; \
		else \
			echo "Skipping $$dir (no requirements.txt found)"; \
		fi \
	done
	@echo ""
	@echo "========================================"
	@echo "All virtual environments set up!"
	@echo "========================================"

clean:
	@echo "Removing virtual environments..."
	@for dir in $(ALL_DIRS); do \
		if [ -d "$$dir/virt" ]; then \
			echo "Removing $$dir/virt"; \
			rm -rf $$dir/virt; \
		fi \
	done
	@echo "Done cleaning up virtual environments."
