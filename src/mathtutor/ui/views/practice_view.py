"Adaptive practice view.\nGenerates reproducible exercises and manages hints, difficulty, and immediate feedback."

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt

from ...practice.generator import ExerciseGenerator, GeneratedExercise
from ...practice.adaptive import AdaptiveController
from ...core.models import StudentAttempt
from ...storage.database import StorageManager


class PracticeView(QWidget):
    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.adaptive = AdaptiveController(storage)
        self.current_exercise: Optional[GeneratedExercise] = None
        self.hints_used_count = 0
        self.current_hint_idx = 0
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QLabel("Adaptive Exercise Practice")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        layout.addWidget(header)

        # Topic and difficulty selection
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;")
        c_layout = QHBoxLayout(controls_frame)
        c_layout.setSpacing(12)

        c_layout.addWidget(QLabel("Subject / Topic:"))
        self.topic_combo = QComboBox()
        self.topic_combo.addItem("Linear Equations", "algebra_lineal")
        self.topic_combo.addItem("Quadratic Equations", "algebra_cuadratica")
        self.topic_combo.addItem("Geometry", "geometria")
        self.topic_combo.addItem("Physics", "fisica")
        self.topic_combo.addItem("Calculus", "calculo")
        self.topic_combo.currentIndexChanged.connect(self._on_topic_changed)
        c_layout.addWidget(self.topic_combo)

        c_layout.addWidget(QLabel("Difficulty:"))
        self.level_combo = QComboBox()
        self.level_combo.addItem("Level 1 (Basic)", 1)
        self.level_combo.addItem("Level 2 (Intermediate)", 2)
        self.level_combo.addItem("Level 3 (Advanced)", 3)
        self.level_combo.currentIndexChanged.connect(self.new_exercise)
        c_layout.addWidget(self.level_combo)

        c_layout.addStretch()

        self.btn_new = QPushButton("Generate New Exercise ↻")
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
                color: #334155;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_new.clicked.connect(self.new_exercise)
        c_layout.addWidget(self.btn_new)

        layout.addWidget(controls_frame)

        # Exercise panel
        exercise_frame = QFrame()
        exercise_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px;")
        e_layout = QVBoxLayout(exercise_frame)
        e_layout.setSpacing(12)

        # Level and block indicators
        info_header = QHBoxLayout()
        self.lbl_level_badge = QLabel("Level 1")
        self.lbl_level_badge.setStyleSheet("""
            background-color: #dbeafe;
            color: #1e40af;
            font-weight: bold;
            font-size: 12px;
            padding: 3px 8px;
            border-radius: 10px;
        """)
        info_header.addWidget(self.lbl_level_badge)

        self.lbl_block_info = QLabel("Adaptive block: 0/5 exercises without hints")
        self.lbl_block_info.setStyleSheet("color: #64748b; font-size: 12px;")
        info_header.addWidget(self.lbl_block_info)
        info_header.addStretch()
        e_layout.addLayout(info_header)

        # Question statement
        self.lbl_statement = QLabel("Loading exercise...")
        self.lbl_statement.setWordWrap(True)
        self.lbl_statement.setStyleSheet("font-size: 17px; font-weight: bold; color: #0f172a; margin: 8px 0;")
        e_layout.addWidget(self.lbl_statement)

        # Student answer field
        ans_layout = QHBoxLayout()
        ans_layout.setSpacing(8)

        self.ans_input = QLineEdit()
        self.ans_input.setPlaceholderText("Type your answer here...")
        self.ans_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #0f172a;
                font-size: 15px;
                padding: 8px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
            }
            QLineEdit:focus { border-color: #2563eb; }
        """)
        self.ans_input.returnPressed.connect(self.check_answer)
        ans_layout.addWidget(self.ans_input, stretch=1)

        self.btn_submit = QPushButton("Check Answer")
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_submit.clicked.connect(self.check_answer)
        ans_layout.addWidget(self.btn_submit)

        self.btn_hint = QPushButton("Give Me a Hint 💡")
        self.btn_hint.setStyleSheet("""
            QPushButton {
                background-color: #fef3c7;
                border: 1px solid #fde68a;
                color: #b45309;
                font-weight: 600;
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #fde68a; }
        """)
        self.btn_hint.clicked.connect(self.request_hint)
        ans_layout.addWidget(self.btn_hint)

        e_layout.addLayout(ans_layout)

        # Expandable hint area
        self.hint_box = QLabel("")
        self.hint_box.setWordWrap(True)
        self.hint_box.setStyleSheet("background-color: #fffbeb; border: 1px solid #fef3c7; color: #92400e; padding: 10px; border-radius: 6px; font-size: 13px;")
        self.hint_box.hide()
        e_layout.addWidget(self.hint_box)

        # Feedback area
        self.feedback_box = QLabel("")
        self.feedback_box.setWordWrap(True)
        self.feedback_box.setStyleSheet("padding: 12px; border-radius: 6px; font-size: 14px;")
        self.feedback_box.hide()
        e_layout.addWidget(self.feedback_box)

        layout.addWidget(exercise_frame)
        layout.addStretch()

        self.new_exercise()

    def _on_topic_changed(self):
        topic = self.topic_combo.currentData()
        prog = self.storage.get_topic_progress(topic)
        level = prog["current_level"]
        idx = self.level_combo.findData(level)
        if idx >= 0:
            self.level_combo.setCurrentIndex(idx)
        else:
            self.new_exercise()

    def new_exercise(self):
        topic = self.topic_combo.currentData() or "algebra_lineal"
        level = self.level_combo.currentData() or 1

        self.current_exercise = ExerciseGenerator.generate(topic, difficulty_level=level)
        self.hints_used_count = 0
        self.current_hint_idx = 0

        self.lbl_statement.setText(self.current_exercise.statement)
        self.lbl_level_badge.setText(f"Level {level}")
        self.ans_input.clear()
        self.ans_input.setEnabled(True)
        self.btn_submit.setEnabled(True)
        self.hint_box.hide()
        self.feedback_box.hide()

        # Update the block indicator
        prog = self.storage.get_topic_progress(topic)
        count_unassisted = prog["consecutive_unassisted"]
        self.lbl_block_info.setText(f"Adaptive block: {count_unassisted}/5 exercises without hints")

    def request_hint(self):
        if not self.current_exercise or not self.current_exercise.hints:
            return

        total_hints = len(self.current_exercise.hints)
        if self.current_hint_idx < total_hints:
            hint_text = self.current_exercise.hints[self.current_hint_idx]
            self.current_hint_idx += 1
            self.hints_used_count += 1

            self.hint_box.setText(f"💡 Hint {self.current_hint_idx}/{total_hints}:\n{hint_text}")
            self.hint_box.show()
        else:
            QMessageBox.information(self, "No More Hints", "All hints for this exercise have already been shown.")

    def check_answer(self):
        if not self.current_exercise:
            return

        user_ans = self.ans_input.text().strip().lower()
        if not user_ans:
            return

        # Normalized comparison
        correct = False
        for acc in self.current_exercise.acceptable_answers:
            if user_ans == acc.strip().lower():
                correct = True
                break

        # Process with the adaptive controller
        attempt = StudentAttempt(
            exercise_id=self.current_exercise.exercise_id,
            topic=self.current_exercise.topic,
            difficulty_level=self.current_exercise.difficulty_level,
            seed=self.current_exercise.seed,
            user_answer=user_ans,
            is_correct=correct,
            hints_used=self.hints_used_count,
            attempt_count=1
        )
        res = self.adaptive.process_attempt(attempt)

        self.ans_input.setEnabled(False)
        self.btn_submit.setEnabled(False)

        if correct:
            fb = f"✓ Great answer! That is correct.\n\nExplanation: {self.current_exercise.explanation}"
            if res["level_changed"] or res["action_message"]:
                fb += f"\n\n{res['action_message']}"
            self.feedback_box.setStyleSheet("background-color: #dcfce7; color: #166534; padding: 12px; border-radius: 6px; font-size: 14px;")
        else:
            fb = (
                f"✗ Incorrect answer.\n"
                f"Your answer: '{user_ans}'  |  Expected answer: '{self.current_exercise.correct_answer}'.\n\n"
                f"Explanation: {self.current_exercise.explanation}"
            )
            if res["level_changed"] or res["action_message"]:
                fb += f"\n\n{res['action_message']}"
            self.feedback_box.setStyleSheet("background-color: #fee2e2; color: #991b1b; padding: 12px; border-radius: 6px; font-size: 14px;")

        self.feedback_box.setText(fb)
        self.feedback_box.show()

        # Update the difficulty selector if the level changed automatically
        if res["level_changed"]:
            idx = self.level_combo.findData(res["new_level"])
            if idx >= 0:
                self.level_combo.blockSignals(True)
                self.level_combo.setCurrentIndex(idx)
                self.level_combo.blockSignals(False)

        self.lbl_block_info.setText(f"Adaptive block: {res['unassisted_in_current_block']}/5 exercises without hints")
