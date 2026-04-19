"""
Примеры использования LMS API с Python requests

Запуск: python examples.py
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api"

class LMSClient:
    """Клиент для работы с LMS API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[int] = None
    
    def _headers(self) -> dict:
        """Получить заголовки с токеном"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    # ═══════════════════════════════════════════════════════════════════════════
    # АУТЕНТИФИКАЦИЯ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def register(self, username: str, email: str, full_name: str, password: str, role: str = "student") -> dict:
        """Зарегистрироваться"""
        data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password,
            "role": role
        }
        response = requests.post(f"{self.base_url}/auth/register", json=data)
        return response.json()
    
    def login(self, username: str, password: str) -> dict:
        """Войти в систему"""
        data = {"username": username, "password": password}
        response = requests.post(f"{self.base_url}/auth/login", json=data)
        result = response.json()
        
        if response.status_code == 200:
            self.access_token = result["access_token"]
            self.refresh_token = result["refresh_token"]
            self.user_id = result["user"]["id"]
            print(f"✅ Успешно вошли как {result['user']['username']}")
        
        return result
    
    def refresh_token_method(self) -> dict:
        """Обновить access token"""
        if not self.refresh_token:
            raise Exception("Refresh token не найден")
        
        data = {"refresh_token": self.refresh_token}
        response = requests.post(f"{self.base_url}/auth/refresh", json=data)
        result = response.json()
        
        if response.status_code == 200:
            self.access_token = result["access_token"]
            self.refresh_token = result["refresh_token"]
            print("✅ Токен обновлен")
        
        return result
    
    def get_me(self) -> dict:
        """Получить текущего пользователя"""
        response = requests.get(f"{self.base_url}/auth/me", headers=self._headers())
        return response.json()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # КУРСЫ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_course(self, title: str, description: str) -> dict:
        """Создать курс"""
        data = {"title": title, "description": description}
        response = requests.post(f"{self.base_url}/courses", json=data, headers=self._headers())
        return response.json()
    
    def get_courses(self, skip: int = 0, limit: int = 10) -> dict:
        """Получить список курсов"""
        response = requests.get(
            f"{self.base_url}/courses?skip={skip}&limit={limit}",
            headers=self._headers()
        )
        return response.json()
    
    def get_course(self, course_id: int) -> dict:
        """Получить курс"""
        response = requests.get(f"{self.base_url}/courses/{course_id}", headers=self._headers())
        return response.json()
    
    def update_course(self, course_id: int, title: str = None, description: str = None) -> dict:
        """Обновить курс"""
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        
        response = requests.put(f"{self.base_url}/courses/{course_id}", json=data, headers=self._headers())
        return response.json()
    
    def delete_course(self, course_id: int) -> None:
        """Удалить курс"""
        response = requests.delete(f"{self.base_url}/courses/{course_id}", headers=self._headers())
        if response.status_code == 204:
            print(f"✅ Курс {course_id} удален")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # УРОКИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_lesson(self, course_id: int, title: str, content: str, order: int = 0) -> dict:
        """Создать урок"""
        data = {"title": title, "content": content, "order": order}
        response = requests.post(
            f"{self.base_url}/courses/{course_id}/lessons",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def get_lessons(self, course_id: int, skip: int = 0, limit: int = 100) -> dict:
        """Получить уроки курса"""
        response = requests.get(
            f"{self.base_url}/courses/{course_id}/lessons?skip={skip}&limit={limit}",
            headers=self._headers()
        )
        return response.json()
    
    def get_lesson(self, course_id: int, lesson_id: int) -> dict:
        """Получить урок"""
        response = requests.get(
            f"{self.base_url}/courses/{course_id}/lessons/{lesson_id}",
            headers=self._headers()
        )
        return response.json()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ЗАДАНИЯ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_assignment(self, course_id: int, lesson_id: int, title: str, description: str, due_date: str) -> dict:
        """Создать задание"""
        data = {
            "title": title,
            "description": description,
            "due_date": due_date
        }
        response = requests.post(
            f"{self.base_url}/courses/{course_id}/lessons/{lesson_id}/assignments",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def submit_assignment(self, course_id: int, lesson_id: int, assignment_id: int, content: str) -> dict:
        """Отправить ответ на задание"""
        data = {"content": content}
        response = requests.post(
            f"{self.base_url}/courses/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submit",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def get_submissions(self, course_id: int, lesson_id: int, assignment_id: int) -> dict:
        """Получить все ответы на задание"""
        response = requests.get(
            f"{self.base_url}/courses/{course_id}/lessons/{lesson_id}/assignments/{assignment_id}/submissions",
            headers=self._headers()
        )
        return response.json()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ОЦЕНКИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def grade_submission(self, submission_id: int, score: float, max_score: float = 100.0, feedback: str = None) -> dict:
        """Выставить оценку"""
        data = {
            "score": score,
            "max_score": max_score
        }
        if feedback:
            data["feedback"] = feedback
        
        response = requests.post(
            f"{self.base_url}/grades/submissions/{submission_id}/grade",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def get_student_grades(self, student_id: int, course_id: int) -> dict:
        """Получить оценки студента по курсу"""
        response = requests.get(
            f"{self.base_url}/grades/student/{student_id}/course/{course_id}",
            headers=self._headers()
        )
        return response.json()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ПОЛЬЗОВАТЕЛИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def enroll_course(self, course_id: int) -> dict:
        """Записать на курс"""
        response = requests.post(
            f"{self.base_url}/users/{course_id}/enroll",
            headers=self._headers()
        )
        return response.json()
    
    def get_my_courses(self) -> dict:
        """Получить мои курсы"""
        response = requests.get(
            f"{self.base_url}/users/my-courses",
            headers=self._headers()
        )
        return response.json()


def main():
    """Примеры использования API"""
    
    client = LMSClient()
    
    print("\n" + "="*80)
    print("🎓 LMS API ПРИМЕРЫ")
    print("="*80)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. РЕГИСТРАЦИЯ И ВХОД
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n📝 1. Регистрация студента...")
    student_reg = client.register(
        username="student_demo",
        email="student_demo@example.com",
        full_name="Demo Student",
        password="password123",
        role="student"
    )
    print(json.dumps(student_reg, indent=2, ensure_ascii=False))
    
    print("\n📝 2. Регистрация преподавателя...")
    teacher_reg = client.register(
        username="teacher_demo",
        email="teacher_demo@example.com",
        full_name="Demo Teacher",
        password="password123",
        role="teacher"
    )
    print(json.dumps(teacher_reg, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. ВХОД КАК ПРЕПОДАВАТЕЛЬ
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n🔐 3. Вход как преподаватель...")
    client.login("teacher_demo", "password123")
    
    me = client.get_me()
    print(json.dumps(me, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. СОЗДАНИЕ КУРСА И КОНТЕНТА
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n📚 4. Создание курса...")
    course = client.create_course(
        title="Python для начинающих",
        description="Полный курс Python: основы, функции, классы, работа с файлами"
    )
    course_id = course["id"]
    print(json.dumps(course, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. ДОБАВЛЕНИЕ УРОКОВ
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n📖 5. Добавление уроков...")
    lesson1 = client.create_lesson(
        course_id=course_id,
        title="Урок 1: Введение в Python",
        content="Python - это язык программирования...\n\n# Основные концепции:\n- Переменные\n- Типы данных\n- Операции",
        order=1
    )
    lesson1_id = lesson1["id"]
    print(json.dumps(lesson1, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. ДОБАВЛЕНИЕ ЗАДАНИЙ
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n✏️ 6. Добавление задания...")
    assignment = client.create_assignment(
        course_id=course_id,
        lesson_id=lesson1_id,
        title="Задание 1: Первая программа",
        description="Напишите программу, которая выводит 'Hello, World!' на экран",
        due_date="2026-05-01T23:59:59"
    )
    assignment_id = assignment["id"]
    print(json.dumps(assignment, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 6. ВХОД КАК СТУДЕНТ И ЗАПИСЬ НА КУРС
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n🔐 7. Вход как студент...")
    client.login("student_demo", "password123")
    student_id = client.user_id
    
    print("\n📝 8. Запись на курс...")
    enrollment = client.enroll_course(course_id)
    print(json.dumps(enrollment, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 7. ПРОСМОТР КУРСОВ И ОТПРАВКА ЗАДАНИЯ
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n📚 9. Получение моих курсов...")
    my_courses = client.get_my_courses()
    print(json.dumps(my_courses, indent=2, ensure_ascii=False))
    
    print("\n✏️ 10. Отправка ответа на задание...")
    submission = client.submit_assignment(
        course_id=course_id,
        lesson_id=lesson1_id,
        assignment_id=assignment_id,
        content="print('Hello, World!')"
    )
    submission_id = submission["id"]
    print(json.dumps(submission, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 8. ВХОД КАК ПРЕПОДАВАТЕЛЬ И ВЫСТАВЛЕНИЕ ОЦЕНКИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n🔐 11. Вход как преподаватель для выставления оценок...")
    client.login("teacher_demo", "password123")
    
    print("\n🔍 12. Получение ответов на задание...")
    submissions = client.get_submissions(course_id, lesson1_id, assignment_id)
    print(json.dumps(submissions, indent=2, ensure_ascii=False))
    
    print("\n⭐ 13. Выставление оценки...")
    grade = client.grade_submission(
        submission_id=submission_id,
        score=95.0,
        max_score=100.0,
        feedback="Отличная работа! Код правильный и хорошо оформлен."
    )
    print(json.dumps(grade, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 9. ПОЛУЧЕНИЕ ОЦЕНОК СТУДЕНТА
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n📊 14. Получение оценок студента по курсу...")
    student_grades = client.get_student_grades(student_id, course_id)
    print(json.dumps(student_grades, indent=2, ensure_ascii=False))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 10. ПОЛУЧЕНИЕ СПИСКА КУРСОВ
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("\n📚 15. Получение всех курсов...")
    all_courses = client.get_courses()
    print(json.dumps(all_courses, indent=2, ensure_ascii=False))
    
    print("\n" + "="*80)
    print("✅ Все примеры успешно выполнены!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
