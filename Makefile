MAIN = src/run.py

VENV = .venv

PYTHON = $(VENV)/bin/python
ifeq ($(OS),Windows_NT)
	PYTHON = $(VENV)/Scripts/python.exe
endif

.PHONY: run install clean venv

venv:
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

# Установка зависимостей
install: venv
	$(PYTHON) -m pip install -r requirements.txt --no-cache-dir

run: venv
	$(PYTHON) $(MAIN)

# Очистка временных файлов
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
