from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import hashlib
import secrets
import base64

from CONFIG.config import settings
from DB.db import get_db, SessionLocal, User

# ═══════════════════════════════════════════════════════════════════════════
# PASSWORD HASHING - использует PBKDF2 с SHA256 (встроено в Python)
# ═══════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """Хэшировать пароль с использованием PBKDF2"""
    # Генерируем случайную соль
    salt = secrets.token_bytes(32)
    # PBKDF2 с SHA256, 100000 итераций
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Возвращаем соль + хэш в base64
    return base64.b64encode(salt + pwd_hash).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    try:
        # Декодируем base64
        decoded = base64.b64decode(hashed_password.encode('utf-8'))
        # Первые 32 байта - соль, остаток - хэш
        salt = decoded[:32]
        stored_hash = decoded[32:]
        # Хэшируем введённый пароль с той же солью
        pwd_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        # Сравниваем
        return pwd_hash == stored_hash
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════
# JWT TOKEN MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создать access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создать refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Декодировать токен"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer token"),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из токена"""
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не найден токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат токена - должен начинаться с 'Bearer '",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат токена - токен не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_token(token)
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise HTTPException(status_code=401, detail="Невалидный токен")
        user_id = int(user_id_raw)  # ← вот главное исправление
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен",
        )
    
    return user


async def get_current_teacher(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверить, что пользователь преподаватель или администратор"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватели и администраторы могут это делать",
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверить, что пользователь администратор"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут это делать",
        )
    return current_user


async def get_current_student(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверить, что пользователь студент"""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут это делать",
        )
    return current_user
