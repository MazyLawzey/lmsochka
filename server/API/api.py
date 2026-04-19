from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from DB.db import init_db
from CONFIG.config import settings

# Импортируем все роутеры
from API.entity import auth, courses, lessons, users, assignments, roles

# ═══════════════════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API для Learning Management System (LMS)",
    version="1.0.0",
    debug=settings.DEBUG
)

# ═══════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# ═══════════════════════════════════════════════════════════════════════════
# ИНИЦИАЛИЗАЦИЯ БД
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Инициализировать БД при запуске приложения"""
    init_db()
    print("✅ База данных инициализирована")


# ═══════════════════════════════════════════════════════════════════════════
# ROUTERS
# ═══════════════════════════════════════════════════════════════════════════

# Подключаем все роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(assignments.router)
app.include_router(roles.router)

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    """Проверка статуса приложения"""
    return {"status": "ok", "app": settings.APP_NAME}


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/docs")
async def get_docs():
    """Документация API"""
    return {
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_schema": "/openapi.json"
    }


# ═══════════════════════════════════════════════════════════════════════════
# STATIC FILES & FRONTEND
# ═══════════════════════════════════════════════════════════════════════════

# Путь к статическим файлам (относительно файла server.py)
# server.py находится в /server/
# public находится в /public/ (на уровень выше)
PUBLIC_DIR = Path(__file__).parent.parent.parent / "public"

# Попытаемся найти papку, если её нет там, пробуем альтернативный путь
if not PUBLIC_DIR.exists():
    # Альтернативный путь - относительно текущей рабочей директории
    PUBLIC_DIR = Path("../../public").resolve()

print(f"📁 Public directory: {PUBLIC_DIR}")
print(f"📁 Exists: {PUBLIC_DIR.exists()}")

# Проверяем, существует ли папка public
if PUBLIC_DIR.exists():
    # Монтируем статические файлы
    app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")
    print(f"✅ Static files mounted at /static")
    
    @app.get("/")
    async def serve_frontend():
        """Обслуживание главной страницы"""
        index_path = PUBLIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse(
            status_code=404,
            content={"detail": "Frontend not found", "path": str(index_path)}
        )
else:
    print(f"⚠️  Public directory not found at {PUBLIC_DIR}")


# ═══════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Общий обработчик ошибок"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error": str(exc) if settings.DEBUG else "Internal Server Error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
