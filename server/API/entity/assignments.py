from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from DB.db import (
    get_db, Assignment, Lesson, Course, User, AssignmentSubmission
)
from API.schemas import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentSubmissionCreate, AssignmentSubmissionResponse
)
from API.auth import get_current_user, get_current_teacher, get_current_student

router = APIRouter(prefix="/api/courses", tags=["assignments"])


@router.post("/{course_id}/lessons/{lesson_id}/assignments", 
             response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    course_id: int,
    lesson_id: int,
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Создать новое задание (только преподаватель или администратор)
    """
    # Проверить курс
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверить права доступа
    if course.teacher_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет прав для добавления заданий")
    
    # Проверить урок
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # Создать задание
    new_assignment = Assignment(
        lesson_id=lesson_id,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=assignment_data.due_date
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return new_assignment


@router.get("/{course_id}/lessons/{lesson_id}/assignments", 
            response_model=List[AssignmentResponse])
async def get_assignments(
    course_id: int,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список заданий в уроке
    """
    # Проверить урок
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.course_id == course_id
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    assignments = db.query(Assignment).filter(
        Assignment.lesson_id == lesson_id
    ).all()
    
    return assignments


@router.get("/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}",
            response_model=AssignmentResponse)
async def get_assignment(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить подробную информацию о задании
    """
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.lesson_id == lesson_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    return assignment


@router.post("/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submit",
             response_model=AssignmentSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_data: AssignmentSubmissionCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Отправить ответ на задание (студент)
    """
    # Проверить задание
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.lesson_id == lesson_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    # Проверить, не отправлено ли уже
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if existing_submission:
        # Обновить существующую отправку
        existing_submission.content = submission_data.content
        db.commit()
        db.refresh(existing_submission)
        return existing_submission
    
    # Создать новую отправку
    new_submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=submission_data.content
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return new_submission


@router.get("/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submissions",
            response_model=List[AssignmentSubmissionResponse])
async def get_submissions(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Получить список всех ответов на задание (преподаватель)
    """
    # Проверить права доступа
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course or (course.teacher_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Нет прав для просмотра ответов")
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()
    
    return submissions


@router.get("/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submissions/{submission_id}",
            response_model=AssignmentSubmissionResponse)
async def get_submission(
    course_id: int,
    lesson_id: int,
    assignment_id: int,
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить конкретный ответ на задание
    """
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id,
        AssignmentSubmission.assignment_id == assignment_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Ответ не найден")
    
    # Только студент или преподаватель могут просмотреть
    if submission.student_id != current_user.id and current_user.role != "teacher" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет прав для просмотра")
    
    return submission
