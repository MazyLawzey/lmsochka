from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from DB.db import get_db, Grade, AssignmentSubmission, Course, User
from API.schemas import GradeCreate, GradeResponse
from API.auth import get_current_user, get_current_teacher

router = APIRouter(prefix="/api/grades", tags=["grades"])


@router.post("/submissions/{submission_id}/grade", 
             response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    submission_id: int,
    grade_data: GradeCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Выставить оценку на ответ (преподаватель или администратор)
    """
    # Найти отправку
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Ответ не найден")
    
    # Проверить права доступа (преподаватель курса)
    assignment = submission.assignment
    lesson = assignment.lesson
    course = lesson.course
    
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только преподаватель курса может выставлять оценки"
        )
    
    # Проверить, не выставлена ли уже оценка
    existing_grade = db.query(Grade).filter(
        Grade.submission_id == submission_id
    ).first()
    
    if existing_grade:
        # Обновить оценку
        existing_grade.score = grade_data.score
        existing_grade.max_score = grade_data.max_score
        existing_grade.feedback = grade_data.feedback
        existing_grade.graded_by = current_user.id
        db.commit()
        db.refresh(existing_grade)
        return existing_grade
    
    # Создать новую оценку
    new_grade = Grade(
        submission_id=submission_id,
        score=grade_data.score,
        max_score=grade_data.max_score,
        feedback=grade_data.feedback,
        graded_by=current_user.id
    )
    
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    
    return new_grade


@router.get("/submissions/{submission_id}", response_model=GradeResponse)
async def get_grade(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить оценку по ответу
    """
    grade = db.query(Grade).filter(
        Grade.submission_id == submission_id
    ).first()
    
    if not grade:
        raise HTTPException(status_code=404, detail="Оценка не найдена")
    
    # Только студент или преподаватель могут просмотреть
    submission = grade.submission
    if submission.student_id != current_user.id and current_user.role != "teacher" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет прав для просмотра")
    
    return grade


@router.get("/student/{student_id}/course/{course_id}")
async def get_student_grades(
    student_id: int,
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить оценки студента по курсу
    """
    # Проверить права доступа
    if student_id != current_user.id and current_user.role == "student":
        raise HTTPException(status_code=403, detail="Нет прав для просмотра оценок")
    
    # Получить все оценки студента по курсу
    grades = db.query(Grade).join(
        AssignmentSubmission
    ).join(
        Assignment
    ).join(
        Lesson
    ).join(
        Course
    ).filter(
        AssignmentSubmission.student_id == student_id,
        Course.id == course_id
    ).all()
    
    # Подсчитать среднюю оценку
    if not grades:
        return {
            "student_id": student_id,
            "course_id": course_id,
            "grades": [],
            "average_score": 0.0
        }
    
    total_score = sum(g.score for g in grades)
    average_score = total_score / len(grades) if grades else 0.0
    
    return {
        "student_id": student_id,
        "course_id": course_id,
        "grades": [
            {
                "id": g.id,
                "submission_id": g.submission_id,
                "score": g.score,
                "max_score": g.max_score,
                "feedback": g.feedback,
                "graded_at": g.graded_at
            } for g in grades
        ],
        "average_score": average_score
    }
