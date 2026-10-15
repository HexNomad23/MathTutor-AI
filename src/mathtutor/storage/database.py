"Persistent SQLite storage for MathTutor AI.\nDefault location: %LOCALAPPDATA%/MathTutorAI/mathtutor.db"

import os
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..core.models import UserProfile, StudentAttempt, SolutionResult, SolutionStep, VerificationStatus, Subject


def get_default_db_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data) / "MathTutorAI"
    else:
        base_dir = Path.home() / ".mathtutor_ai"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_default_db_path() -> Path:
    return get_default_db_dir() / "mathtutor.db"


class StorageManager:
    CURRENT_SCHEMA_VERSION = 1

    def __init__(self, db_path: Optional[str | Path] = None):
        if db_path is None:
            self.db_path = str(get_default_db_path())
            self._mem_conn = None
        else:
            self.db_path = str(db_path)
            self._mem_conn = None
            if self.db_path == ":memory:":
                self._mem_conn = sqlite3.connect(":memory:")
                self._mem_conn.row_factory = sqlite3.Row
                self._mem_conn.execute("PRAGMA foreign_keys = ON;")
            else:
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("SELECT MAX(version) FROM schema_version")
            row = cursor.fetchone()
            current_ver = row[0] if row and row[0] is not None else 0

            if current_ver < 1:
                self._migrate_v1(conn)
                cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
                conn.commit()

    def _migrate_v1(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        # Profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences_json TEXT
            )
        """)
        # Insert the initial Student profile if it does not exist
        cursor.execute("SELECT id FROM profiles WHERE id = 'default_student'")
        if not cursor.fetchone():
            cursor.execute("\n                INSERT INTO profiles (id, name, preferences_json)\n                VALUES ('default_student', 'Student', '{}')\n            ")

        # Solution history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                exercise_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                original_input TEXT NOT NULL,
                interpreted_input TEXT NOT NULL,
                domain_assumptions TEXT,
                final_answer TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                verification_reason TEXT,
                substitution_check TEXT,
                steps_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Practice attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id TEXT PRIMARY KEY,
                exercise_id TEXT,
                topic TEXT NOT NULL,
                difficulty_level INTEGER DEFAULT 1,
                seed INTEGER,
                user_answer TEXT,
                is_correct INTEGER NOT NULL,
                hints_used INTEGER DEFAULT 0,
                attempt_count INTEGER DEFAULT 1,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Adaptive progress by topic
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_progress (
                topic TEXT PRIMARY KEY,
                current_level INTEGER DEFAULT 1,
                total_attempts INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                consecutive_unassisted INTEGER DEFAULT 0,
                history_window_json TEXT DEFAULT '[]',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    # --- Profile operations ---
    def get_profile(self, profile_id: str = "default_student") -> UserProfile:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, created_at, preferences_json FROM profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            if row:
                prefs = json.loads(row["preferences_json"] or "{}")
                return UserProfile(
                    id=row["id"],
                    name=row["name"],
                    preferences=prefs
                )
            # Default fallback
            return UserProfile(id=profile_id, name="Student")

    def update_profile_name(self, name: str, profile_id: str = "default_student") -> None:
        clean_name = name.strip() or "Student"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO profiles (id, name, preferences_json)
                VALUES (?, ?, '{}')
                ON CONFLICT(id) DO UPDATE SET name = excluded.name
            """, (profile_id, clean_name))
            conn.commit()

    # --- History operations ---
    def save_solution(self, sol: SolutionResult) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            steps_data = [
                {
                    "step_number": s.step_number,
                    "previous_expr": s.previous_expr,
                    "operation": s.operation,
                    "resulting_expr": s.resulting_expr,
                    "explanation_brief": s.explanation_brief,
                    "explanation_detailed": s.explanation_detailed,
                    "restrictions": s.restrictions
                }
                for s in sol.steps
            ]
            cursor.execute("""
                INSERT INTO history (
                    id, exercise_id, subject, original_input, interpreted_input,
                    domain_assumptions, final_answer, verification_status,
                    verification_reason, substitution_check, steps_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                sol.exercise_id, sol.exercise_id, sol.subject.value, sol.original_input,
                sol.interpreted_input, sol.domain_assumptions, sol.final_answer,
                sol.verification_status.value, sol.verification_reason,
                sol.substitution_check, json.dumps(steps_data, ensure_ascii=False)
            ))
            conn.commit()
            return sol.exercise_id

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, exercise_id, subject, original_input, interpreted_input,
                       domain_assumptions, final_answer, verification_status,
                       verification_reason, substitution_check, steps_json, created_at
                FROM history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                steps_data = json.loads(r["steps_json"] or "[]")
                steps = [
                    SolutionStep(
                        step_number=sd["step_number"],
                        previous_expr=sd["previous_expr"],
                        operation=sd["operation"],
                        resulting_expr=sd["resulting_expr"],
                        explanation_brief=sd["explanation_brief"],
                        explanation_detailed=sd["explanation_detailed"],
                        restrictions=sd.get("restrictions")
                    )
                    for sd in steps_data
                ]
                results.append({
                    "id": r["id"],
                    "exercise_id": r["exercise_id"],
                    "subject": r["subject"],
                    "original_input": r["original_input"],
                    "interpreted_input": r["interpreted_input"],
                    "domain_assumptions": r["domain_assumptions"],
                    "final_answer": r["final_answer"],
                    "verification_status": r["verification_status"],
                    "verification_reason": r["verification_reason"],
                    "substitution_check": r["substitution_check"],
                    "steps": steps,
                    "created_at": r["created_at"],
                })
            return results

    def delete_history_item(self, history_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_history(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()

    # --- Practice and progress operations ---
    def record_attempt(self, attempt: StudentAttempt) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attempts (
                    id, exercise_id, topic, difficulty_level, seed,
                    user_answer, is_correct, hints_used, attempt_count, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                attempt.id, attempt.exercise_id, attempt.topic,
                attempt.difficulty_level, attempt.seed, attempt.user_answer,
                1 if attempt.is_correct else 0, attempt.hints_used,
                attempt.attempt_count
            ))
            conn.commit()

    def get_attempts_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, exercise_id, topic, difficulty_level, seed,
                       user_answer, is_correct, hints_used, attempt_count, timestamp
                FROM attempts
                WHERE topic = ?
                ORDER BY timestamp ASC
            """, (topic,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_topic_progress(self, topic: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT topic, current_level, total_attempts, total_correct,
                       consecutive_unassisted, history_window_json, updated_at
                FROM topic_progress
                WHERE topic = ?
            """, (topic,))
            row = cursor.fetchone()
            if row:
                return {
                    "topic": row["topic"],
                    "current_level": row["current_level"],
                    "total_attempts": row["total_attempts"],
                    "total_correct": row["total_correct"],
                    "consecutive_unassisted": row["consecutive_unassisted"],
                    "history_window": json.loads(row["history_window_json"] or "[]"),
                    "updated_at": row["updated_at"]
                }
            return {
                "topic": topic,
                "current_level": 1,
                "total_attempts": 0,
                "total_correct": 0,
                "consecutive_unassisted": 0,
                "history_window": [],
                "updated_at": None
            }

    def save_topic_progress(self, topic: str, current_level: int, total_attempts: int,
                            total_correct: int, consecutive_unassisted: int,
                            history_window: List[bool]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO topic_progress (
                    topic, current_level, total_attempts, total_correct,
                    consecutive_unassisted, history_window_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(topic) DO UPDATE SET
                    current_level = excluded.current_level,
                    total_attempts = excluded.total_attempts,
                    total_correct = excluded.total_correct,
                    consecutive_unassisted = excluded.consecutive_unassisted,
                    history_window_json = excluded.history_window_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                topic, current_level, total_attempts, total_correct,
                consecutive_unassisted, json.dumps(history_window)
            ))
            conn.commit()

    def get_all_topic_progress(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT topic, current_level, total_attempts, total_correct,
                       consecutive_unassisted, history_window_json, updated_at
                FROM topic_progress
                ORDER BY topic ASC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "topic": r["topic"],
                    "current_level": r["current_level"],
                    "total_attempts": r["total_attempts"],
                    "total_correct": r["total_correct"],
                    "consecutive_unassisted": r["consecutive_unassisted"],
                    "history_window": json.loads(r["history_window_json"] or "[]"),
                    "updated_at": r["updated_at"]
                }
                for r in rows
            ]
