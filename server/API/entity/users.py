from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from DB.db import get_db, User, CourseEnrollment, Course
from API.schemas import UserResponse
from API.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Получить список всех пользователей (только администраторы)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить информацию о пользователе
    """
    # Только пользователь или администратор может просмотреть профиль
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете просмотреть этот профиль"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.post("/{course_id}/enroll", status_code=status.HTTP_200_OK)
async def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Записать студента на курс
    """
    # Проверить, существует ли курс
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден"
        )
    
    # Проверить, не записан ли уже студент
    existing_enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже записаны на этот курс"
        )
    
    # Записать студента
    new_enrollment = CourseEnrollment(
        course_id=course_id,
        student_id=current_user.id
    )
    
    db.add(new_enrollment)
    db.commit()
    
    return {"message": "Успешно записаны на курс"}


@router.delete("/{course_id}/unenroll", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отписать студента от курса
    """
    # Найти и удалить запись
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы не записаны на этот курс"
        )
    
    db.delete(enrollment)
    db.commit()


@router.get("/my-courses", response_model=list)
async def get_my_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список курсов, на которые записан текущий пользователь
    """
    if current_user.role == "student":
        enrollments = db.query(CourseEnrollment).filter(
            CourseEnrollment.student_id == current_user.id
        ).all()
        courses = [e.course for e in enrollments]
    else:
        # Преподаватели видят свои курсы
        courses = db.query(Course).filter(
            Course.teacher_id == current_user.id
        ).all()
    
    result = []
    for c in courses:
        teacher = db.query(User).filter(User.id == c.teacher_id).first()
        result.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "teacher_name": teacher.full_name if teacher else "Unknown"
        })
    return result
