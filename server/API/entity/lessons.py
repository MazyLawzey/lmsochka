from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from DB.db import get_db, Lesson, Course, User
from API.schemas import LessonCreate, LessonUpdate, LessonResponse
from API.auth import get_current_user, get_current_teacher

router = APIRouter(prefix="/api/courses", tags=["lessons"])


@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Создать новый урок в курсе (только преподаватель или администратор)
    """
    # Проверить, существует ли курс
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    # Проверить права доступа
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только создатель курса или администратор может добавлять уроки"
        )
    
    new_lesson = Lesson(
        course_id=course_id,
        title=lesson_data.title,
        content=lesson_data.content,
        order=lesson_data.order
    )
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return new_lesson


@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
async def get_lessons(
    course_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список уроков в курсе
    """
    # Проверить, существует ли курс
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id
    ).order_by(Lesson.order).offset(skip).limit(limit).all()
    
    return lessons


@router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    course_id: int,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить подробную информацию об уроке
    """
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    return lesson


@router.put("/{course_id}/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    course_id: int,
    lesson_id: int,
    lesson_data: LessonUpdate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Обновить информацию об уроке (только преподаватель или администратор)
    """
    # Проверить курс
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    # Проверить права доступа
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только создатель курса может редактировать уроки"
        )
    
    # Найти урок
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    if lesson_data.title:
        lesson.title = lesson_data.title
    if lesson_data.content:
        lesson.content = lesson_data.content
    if lesson_data.order is not None:
        lesson.order = lesson_data.order
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.delete("/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    course_id: int,
    lesson_id: int,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Удалить урок (только преподаватель или администратор)
    """
    # Проверить курс
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    # Проверить права доступа
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только создатель курса может удалять уроки"
        )
    
    # Найти и удалить урок
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден"
        )
    
    db.delete(lesson)
    db.commit()
