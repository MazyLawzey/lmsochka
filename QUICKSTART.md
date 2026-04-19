# 🎯 QUICK START GUIDE - LMS Backend

## Быстрый старт за 5 минут

### 📋 Требования
- Python 3.10+
- pip или poetry
- Git

### 🚀 Установка и запуск

#### 1️⃣ **macOS / Linux**
```bash
cd /Users/mazylawzey/Documents/C/LMS

# Сделать скрипт исполняемым
chmod +x start.sh

# Запустить
./start.sh
```

#### 2️⃣ **Windows**
```bash
cd C:\Users\<YourUser>\Documents\C\LMS
start.bat
```

#### 3️⃣ **Вручную (все ОС)**
```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
cd server
python3 server.py
```

### ✅ Успешный запуск выглядит так:
```
🚀 Инициализация базы данных...
✅ База данных инициализирована
🌐 Запуск сервера на http://0.0.0.0:8000
📚 Документация доступна на http://0.0.0.0:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🔗 Доступные endpoints

### 🔐 Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `POST /api/auth/refresh` - Обновить токен
- `GET /api/auth/me` - Текущий пользователь

### 📚 Курсы
- `POST /api/courses` - Создать курс
- `GET /api/courses` - Получить все курсы
- `GET /api/courses/{course_id}` - Получить курс
- `PUT /api/courses/{course_id}` - Обновить курс
- `DELETE /api/courses/{course_id}` - Удалить курс

### 📖 Уроки
- `POST /api/courses/{course_id}/lessons` - Создать урок
- `GET /api/courses/{course_id}/lessons` - Получить уроки
- `GET /api/courses/{course_id}/lessons/{lesson_id}` - Получить урок

### ✏️ Задания
- `POST /api/courses/{course_id}/lessons/{lesson_id}/assignments` - Создать задание
- `POST /api/courses/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submit` - Отправить ответ

### ⭐ Оценки
- `POST /api/grades/submissions/{submission_id}/grade` - Выставить оценку
- `GET /api/grades/student/{student_id}/course/{course_id}` - Получить оценки

### 👥 Пользователи
- `POST /api/users/{course_id}/enroll` - Записать на курс
- `GET /api/users/my-courses` - Мои курсы

---

## 📊 Полная документация API

Откройте **http://localhost:8000/docs** в браузере для интерактивной Swagger документации

---

## 🧪 Примеры использования

### Регистрация через curl
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student1@example.com",
    "full_name": "Student One",
    "password": "password123",
    "role": "student"
  }'
```

### Вход через curl
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "password123"
  }'
```

### Python примеры
```bash
# Запустить примеры
cd /Users/mazylawzey/Documents/C/LMS
source venv/bin/activate
python3 examples.py
```

---

## 🗂️ Структура проекта

```
LMS/
├── server/
│   ├── API/               # FastAPI приложение
│   │   ├── entity/        # Роутеры (auth, courses, etc)
│   │   ├── auth.py        # JWT логика
│   │   ├── schemas.py     # Pydantic модели
│   │   └── api.py         # Главное приложение
│   ├── DB/                # База данных
│   │   ├── db.py          # SQLAlchemy модели
│   │   └── migrations/    # Миграции
│   ├── CONFIG/
│   │   └── config.py      # Конфигурация
│   └── server.py          # Точка входа
├── public/
│   └── index.html         # Фронтенд
├── venv/                  # Виртуальное окружение
├── .env                   # Переменные окружения
├── requirements.txt       # Зависимости
├── README.md             # Полная документация
├── QUICKSTART.md         # Этот файл
├── examples.py           # Примеры использования
├── start.sh              # Скрипт для macOS/Linux
└── start.bat             # Скрипт для Windows
```

---

## 🔧 Отладка

### Ошибка: "Модуль не найден"
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Переустановите зависимости
pip install -r requirements.txt
```

### Ошибка: "PORT 8000 уже используется"
```bash
# Измените порт в server.py:
# Найдите строку: uvicorn.run(app, host="0.0.0.0", port=8000)
# Измените на: uvicorn.run(app, host="0.0.0.0", port=8001)
```

### База данных повреждена
```bash
# Удалите файл БД
rm lms.db

# При следующем запуске она будет пересоздана автоматически
```

---

## 📝 Переменные окружения (.env)

```env
# Database
DATABASE_URL=sqlite:///./lms.db

# JWT (СМЕНИТЕ ЭТО В PRODUCTION!)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
ALLOWED_ORIGINS=["*"]

# App
APP_NAME=LMS API
DEBUG=True
```

---

## 🚨 Важно для Production

1. **Измените SECRET_KEY** на безопасный ключ
2. **Используйте PostgreSQL** вместо SQLite
3. **Установите DEBUG=False**
4. **Ограничьте CORS** (не используйте "*")
5. **Используйте HTTPS**
6. **Установите Rate Limiting**

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте версию Python: `python3 --version` (должна быть 3.10+)
2. Проверьте файл `README.md` для полной документации
3. Смотрите логи запуска сервера

---

**Last Updated**: 19.04.2026
