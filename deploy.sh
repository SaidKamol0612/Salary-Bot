#!/bin/bash
set -e  # если любая команда упадёт — скрипт сразу завершится

APP_NAME="salary-bot"   # имя процесса в pm2
MAIN="src/run.py"       # точка входа бота
PYTHON_BIN="python3"    # какой Python использовать (убедись что python3 доступен)
VENV=".venv"

echo "[DEPLOY] Starting deployment..."

if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "[ERROR] Python3 не найден! Проверь, что он установлен на сервере."
    exit 1
fi

if [ ! -d "$VENV" ]; then
    echo "[DEPLOY] Creating virtual environment..."
    $PYTHON_BIN -m venv $VENV
fi

echo "[DEPLOY] Installing dependencies..."
$VENV/bin/pip install --upgrade pip
$VENV/bin/pip install -r requirements.txt --no-cache-dir

if command -v pm2 &> /dev/null; then
    echo "[DEPLOY] Restarting app with PM2..."
    pm2 start $MAIN --interpreter $VENV/bin/python --name $APP_NAME --restart-delay 5000
    pm2 save
else
    echo "[WARN] PM2 не найден. Запускаю напрямую (бот остановится при закрытии сессии)."
    nohup $VENV/bin/python $MAIN > app.log 2>&1 &
fi

echo "[DEPLOY] Done!"
