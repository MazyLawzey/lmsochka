import sqlite3
import bcrypt
from contextlib import contextmanager

class Database:
    """
    Thread-safe обёртка над SQLite для LMS.
    Каждый вызов _get_conn() создаёт соединение для текущего потока.
    Для Flask используй get_db() / close_db() через app context.
    """

    def __init__(self, db_name: str = 'lms.db'):
        self.db_name = db_name
        # Инициализируем схему через отдельное соединение
        with self._connect() as conn:
            self._create_tables(conn)

    # ──────────────────────────── СОЕДИНЕНИЕ ────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _get_conn(self):
        """Context manager: одно соединение на вызов — thread-safe."""
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ──────────────────────────── СХЕМА ────────────────────────────

    def _create_tables(self, conn: sqlite3.Connection):
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                teacher_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                position INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            );
        """)
        conn.commit()

    # ──────────────────────────── USERS ────────────────────────────

    def add_user(self, username: str, password: str, role: str) -> int | None:
        """
        Добавить пользователя.
        Возвращает id новой записи или None если username занят.
        """
        if role not in ('student', 'teacher', 'admin'):
            raise ValueError(f"Недопустимая роль: {role}")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed, role)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # username уже занят

    def authenticate_user(self, username: str, password: str) -> dict | None:
        """
        Аутентификация.
        Возвращает безопасный dict (без хэша пароля) или None.
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id, username, password, role, created_at FROM users WHERE username = ?",
                (username,)
            ).fetchone()
        if row and bcrypt.checkpw(password.encode('utf-8'), row['password'].encode('utf-8')):
            # Явно исключаем password — чтобы случайный jsonify() не утёк хэш
            return {'id': row['id'], 'username': row['username'], 'role': row['role'], 'created_at': row['created_at']}
        return None

    def get_user_by_id(self, user_id: int) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id, username, role, created_at FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_user_by_username(self, username: str) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id, username, role, created_at FROM users WHERE username = ?",
                (username,)
            ).fetchone()
        return dict(row) if row else None

    # ──────────────────────────── COURSES ────────────────────────────

    def add_course(self, title: str, description: str, teacher_id: int) -> int | None:
        """Создать курс. Возвращает id или None если teacher_id не существует."""
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "INSERT INTO courses (title, description, teacher_id) VALUES (?, ?, ?)",
                    (title, description, teacher_id)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_courses(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT c.id, c.title, c.description, c.created_at, u.username AS teacher "
                "FROM courses c JOIN users u ON c.teacher_id = u.id"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_course_by_id(self, course_id: int) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT c.id, c.title, c.description, c.created_at, u.username AS teacher "
                "FROM courses c JOIN users u ON c.teacher_id = u.id WHERE c.id = ?",
                (course_id,)
            ).fetchone()
        return dict(row) if row else None

    def update_course(self, course_id: int, title: str, description: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "UPDATE courses SET title = ?, description = ? WHERE id = ?",
                (title, description, course_id)
            )
            return cursor.rowcount > 0

    def delete_course(self, course_id: int) -> bool:
        with self._get_conn() as conn:
            return conn.execute(
                "DELETE FROM courses WHERE id = ?", (course_id,)
            ).rowcount > 0

    # ──────────────────────────── LESSONS ────────────────────────────

    def add_lesson(self, course_id: int, title: str, content: str, position: int = 0) -> int | None:
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "INSERT INTO lessons (course_id, title, content, position) VALUES (?, ?, ?, ?)",
                    (course_id, title, content, position)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_lessons(self, course_id: int) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT id, title, content, position, created_at FROM lessons "
                "WHERE course_id = ? ORDER BY position, id",
                (course_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_lesson_by_id(self, lesson_id: int) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id, course_id, title, content, position, created_at "
                "FROM lessons WHERE id = ?",
                (lesson_id,)
            ).fetchone()
        return dict(row) if row else None

    def update_lesson(self, lesson_id: int, title: str, content: str, position: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "UPDATE lessons SET title = ?, content = ?, position = ? WHERE id = ?",
                (title, content, position, lesson_id)
            )
            return cursor.rowcount > 0

    def delete_lesson(self, lesson_id: int) -> bool:
        with self._get_conn() as conn:
            return conn.execute(
                "DELETE FROM lessons WHERE id = ?", (lesson_id,)
            ).rowcount > 0

    # ──────────────────────────── ENROLLMENTS ────────────────────────────

    def enroll_student(self, student_id: int, course_id: int) -> bool:
        """Записать студента на курс. False если уже записан."""
        try:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                    (student_id, course_id)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def unenroll_student(self, student_id: int, course_id: int) -> bool:
        """Отписать студента от курса."""
        with self._get_conn() as conn:
            return conn.execute(
                "DELETE FROM enrollments WHERE student_id = ? AND course_id = ?",
                (student_id, course_id)
            ).rowcount > 0

    def get_student_courses(self, student_id: int) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT c.id, c.title, c.description, e.enrolled_at "
                "FROM enrollments e JOIN courses c ON e.course_id = c.id "
                "WHERE e.student_id = ?",
                (student_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_course_students(self, course_id: int) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT u.id, u.username, u.role, e.enrolled_at "
                "FROM enrollments e JOIN users u ON e.student_id = u.id "
                "WHERE e.course_id = ?",
                (course_id,)
            ).fetchall()
        return [dict(r) for r in rows]
