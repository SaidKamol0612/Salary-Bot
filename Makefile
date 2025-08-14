MAIN = src/run.py

VENV = .venv

PYTHON = $(VENV)/bin/python
PIP = $(PYTHON) -m pip

ifeq ($(OS),Windows_NT)
	PYTHON = $(VENV)/Scripts/python.exe
	PIP = $(PYTHON) -m pip
	CLEAN_CMD = del /S /Q *.pyc & for /d %%p in (__pycache__) do rmdir /S /Q "%%p"
else
	CLEAN_CMD = find . -type f -name '*.pyc' -delete && find . -type d -name '__pycache__' -exec rm -rf {} +
endif

.PHONY: run install clean venv deploy freeze

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt --no-cache-dir

run: venv
	$(PYTHON) $(MAIN)

deploy: install
	@echo "Project ready for deployment."

freeze: venv
	$(PIP) freeze > requirements.txt

clean:
	$(CLEAN_CMD)
