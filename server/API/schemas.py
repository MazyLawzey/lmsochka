from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# USER SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)
    role: str = Field(default="student")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ["student", "teacher", "admin"]:
            raise ValueError("Роль должна быть: student, teacher или admin")
        return v


class UserResponse(BaseModel):
    """Схема ответа с информацией о пользователе"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для входа"""
    username: str
    password: str


# ═══════════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str


# ═══════════════════════════════════════════════════════════════════════════
# COURSE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class CourseCreate(BaseModel):
    """Схема для создания курса"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)


class CourseUpdate(BaseModel):
    """Схема для обновления курса"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)


class CourseResponse(BaseModel):
    """Схема ответа с информацией о курсе"""
    id: int
    title: str
    description: str
    teacher_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """Детальная информация о курсе с преподавателем"""
    teacher: UserResponse


# ═══════════════════════════════════════════════════════════════════════════
# LESSON SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class LessonCreate(BaseModel):
    """Схема для создания урока"""
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    order: int = Field(default=0, ge=0)


class LessonUpdate(BaseModel):
    """Схема для обновления урока"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    order: Optional[int] = Field(None, ge=0)


class LessonResponse(BaseModel):
    """Схема ответа с информацией об уроке"""
    id: int
    course_id: int
    title: str
    content: str
    order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# ASSIGNMENT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class AssignmentCreate(BaseModel):
    """Схема для создания задания"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    due_date: datetime


class AssignmentUpdate(BaseModel):
    """Схема для обновления задания"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    due_date: Optional[datetime] = None


class AssignmentResponse(BaseModel):
    """Схема ответа с информацией о задании"""
    id: int
    lesson_id: int
    title: str
    description: str
    due_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# ASSIGNMENT SUBMISSION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class AssignmentSubmissionCreate(BaseModel):
    """Схема для отправки ответа на задание"""
    content: str = Field(..., min_length=1)


class AssignmentSubmissionResponse(BaseModel):
    """Схема ответа с информацией об ответе на задание"""
    id: int
    assignment_id: int
    student_id: int
    content: str
    submitted_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# GRADE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class GradeCreate(BaseModel):
    """Схема для создания оценки"""
    score: float = Field(..., ge=0, le=100)
    max_score: float = Field(default=100.0, ge=0)
    feedback: Optional[str] = None


class GradeResponse(BaseModel):
    """Схема ответа с информацией об оценке"""
    id: int
    submission_id: int
    score: float
    max_score: float
    feedback: Optional[str]
    graded_by: int
    graded_at: datetime
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESS SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class StudentProgressResponse(BaseModel):
    """Схема ответа с прогрессом студента"""
    id: int
    student_id: int
    course_id: int
    lessons_completed: int
    total_lessons: int
    average_score: float
    last_accessed: datetime
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# ENROLLMENT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class EnrollmentCreate(BaseModel):
    """Схема для записи на курс"""
    course_id: int


class EnrollmentResponse(BaseModel):
    """Схема ответа с информацией о записи"""
    id: int
    course_id: int
    student_id: int
    enrolled_at: datetime
    
    class Config:
        from_attributes = True
