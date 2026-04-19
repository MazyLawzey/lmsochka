"""
Server entry point для LMS FastAPI приложения
"""
import uvicorn
import sys
import os
from pathlib import Path

# Добавить текущую директорию в sys.path для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from API.api import app
from CONFIG.config import settings
from DB.db import init_db


def main():
    """Главная функция для запуска сервера"""
    
    # Инициализировать БД
    print("🚀 Инициализация базы данных...")
    init_db()
    print("✅ База данных инициализирована")
    
    # Запустить сервер
    print(f"🌐 Запуск сервера на http://0.0.0.0:8000")
    print(f"📚 Документация доступна на http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    main()

