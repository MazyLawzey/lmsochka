@echo off
REM Скрипт для запуска LMS сервера на Windows

echo.
echo 🚀 ЛМСОЧКА - LMS Backend Startup Script
echo ========================================
echo.

REM Проверить виртуальное окружение
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
)

REM Активировать виртуальное окружение
echo ⚙️ Активирую виртуальное окружение...
call venv\Scripts\activate.bat

REM Установить зависимости если нужно
if not exist "venv\Lib\site-packages\fastapi" (
    echo 📥 Установка зависимостей...
    pip install -r requirements.txt
)

REM Запустить сервер
echo 🔥 Запуск сервера...
echo 📍 API будет доступна на: http://localhost:8000
echo 📚 Документация на: http://localhost:8000/docs
echo.

cd server
python server.py

pause
