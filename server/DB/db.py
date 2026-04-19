from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

from CONFIG.config import settings

# Создание движка БД
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class RoleEnum(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    courses_created = relationship("Course", back_populates="teacher", foreign_keys="Course.teacher_id")
    course_enrollments = relationship("CourseEnrollment", back_populates="student")
    assignments_submitted = relationship("AssignmentSubmission", back_populates="student")
    grades = relationship("Grade", back_populates="grader")
    progress = relationship("StudentProgress", back_populates="student")


class Course(Base):
    """Модель курса"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    teacher = relationship("User", back_populates="courses_created", foreign_keys=[teacher_id])
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """Модель урока"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String, index=True)
    content = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    course = relationship("Course", back_populates="lessons")
    assignments = relationship("Assignment", back_populates="lesson", cascade="all, delete-orphan")


class Assignment(Base):
    """Модель задания"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    title = Column(String, index=True)
    description = Column(Text)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    lesson = relationship("Lesson", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    """Модель ответа на задание"""
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="assignments_submitted")
    grade = relationship("Grade", back_populates="submission", uselist=False, cascade="all, delete-orphan")


class Grade(Base):
    """Модель оценки"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("assignment_submissions.id"), unique=True)
    score = Column(Float)
    max_score = Column(Float, default=100.0)
    feedback = Column(Text)
    graded_by = Column(Integer, ForeignKey("users.id"))
    graded_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    submission = relationship("AssignmentSubmission", back_populates="grade")
    grader = relationship("User", back_populates="grades", foreign_keys=[graded_by])


class CourseEnrollment(Base):
    """Модель записи студента на курс"""
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('course_id', 'student_id', name='_course_student_uc'),)
    
    # Отношения
    course = relationship("Course", back_populates="enrollments")
    student = relationship("User", back_populates="course_enrollments")


class StudentProgress(Base):
    """Модель прогресса студента"""
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    lessons_completed = Column(Integer, default=0)
    total_lessons = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    student = relationship("User", back_populates="progress")


def init_db():
    """Инициализация БД с созданием всех таблиц"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
