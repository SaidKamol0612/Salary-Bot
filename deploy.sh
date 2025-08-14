#!/bin/sh
set -eu  # падать на ошибках и на необъявленных переменных

APP_NAME="salary-bot"
MAIN="src/run.py"
LOGFILE="app.log"
VENV=".venv"
PYTHON_DIR="$HOME/python"
PYTHON_BIN="$PYTHON_DIR/bin/python3"

echo "[DEPLOY] Starting deployment..."

# 1. Проверяем Python
if [ ! -x "$PYTHON_BIN" ]; then
  echo "[DEPLOY] Python не найден, скачиваем portable версию..."
  
  # Ссылка на готовый бинарник Linux x86_64 (замени версию при необходимости)
  PYTHON_ARCHIVE="python-3.11.7-x86_64-unknown-linux-gnu.tar.gz"
  PYTHON_URL="https://github.com/indygreg/python-build-standalone/releases/download/2023.3.2/$PYTHON_ARCHIVE"
  
  mkdir -p "$PYTHON_DIR"
  
  # Скачиваем через wget или curl
  if command -v curl >/dev/null 2>&1; then
    curl -L -o /tmp/$PYTHON_ARCHIVE "$PYTHON_URL"
  else
    echo "[ERROR] Нет wget или curl, загрузите архив вручную через Plesk File Manager!"
    exit 1
  fi

  tar -xvf /tmp/$PYTHON_ARCHIVE -C "$HOME"
  mv "$HOME"/python-3.11.7-*/ "$PYTHON_DIR"
fi

# 2. Создаём виртуальное окружение
if [ ! -d "$VENV" ]; then
  echo "[DEPLOY] Создаём виртуальное окружение..."
  "$PYTHON_BIN" -m venv "$VENV"
fi

# 3. Обновляем pip и ставим зависимости
echo "[DEPLOY] Устанавливаем зависимости..."
"$VENV/bin/pip" install --upgrade pip
if [ -f requirements.txt ]; then
  "$VENV/bin/pip" install -r requirements.txt --no-cache-dir
fi

# 4. Запуск приложения
if command -v pm2 >/dev/null 2>&1; then
  echo "[DEPLOY] Перезапуск через PM2..."
  pm2 start "$MAIN" --interpreter "$VENV/bin/python" --name "$APP_NAME" --restart-delay 5000 --update-env
  pm2 save || true
else
  echo "[DEPLOY] PM2 не найден. Запускаем через nohup..."
  # Убиваем старый процесс, если есть
  pkill -f "$VENV/bin/python $MAIN" 2>/dev/null || true
  nohup "$VENV/bin/python" "$MAIN" > "$LOGFILE" 2>&1 &
fi

echo "[DEPLOY] Готово!"
