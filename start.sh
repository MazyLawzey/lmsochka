#!/bin/bash

# Скрипт для запуска LMS сервера

echo "🚀 ЛМСОЧКА - LMS Backend Startup Script"
echo "========================================"

# Проверить виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активировать виртуальное окружение
echo "⚙️ Активирую виртуальное окружение..."
source venv/bin/activate

# Установить зависимости если нужно
if [ ! -d "venv/lib/python3.14/site-packages/fastapi" ]; then
    echo "📥 Установка зависимостей..."
    pip install -r requirements.txt
fi

# Запустить сервер
echo "🔥 Запуск сервера..."
echo "📍 API будет доступна на: http://localhost:8000"
echo "📚 Документация на: http://localhost:8000/docs"
echo ""

cd server
python3 server.py
