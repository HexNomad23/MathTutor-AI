"Home view.\nShows shortcuts to four subjects, recent activity, and history-based recommendations."

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from ...storage.database import StorageManager
from ..labels import subject_name


class HomeView(QWidget):
    navigate_to = Signal(str)  # Signal for navigation to another view

    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Greeting
        profile = self.storage.get_profile()
        self.greeting_label = QLabel(f"Hello, {profile.name}!")
        self.greeting_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        layout.addWidget(self.greeting_label)

        subtitle = QLabel("Welcome to MathTutor AI. Choose a subject or pick up where you left off.")
        subtitle.setStyleSheet("font-size: 14px; color: #64748b;")
        layout.addWidget(subtitle)

        # Subject cards (grid)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(14)

        subjects = [
            ("Algebra", "Linear and quadratic equations, steps, and review.", "#2563eb", "algebra"),
            ("Geometry", "Areas, perimeters, and the Pythagorean theorem.", "#059669", "geometria"),
            ("Physics", "Uniform motion, Newton's second law, and conversions.", "#d97706", "fisica"),
            ("Calculus", "Derivatives and integrals of polynomial functions.", "#7c3aed", "calculo"),
        ]

        row, col = 0, 0
        for title, desc, color, tag in subjects:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-top: 4px solid {color};
                    border-radius: 8px;
                    padding: 14px;
                }}
            """)
            c_layout = QVBoxLayout(card)
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")
            d_lbl = QLabel(desc)
            d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet("font-size: 12px; color: #475569; margin-top: 4px;")

            btn = QPushButton("Open Subject ➔")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f8fafc;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-weight: 600;
                    font-size: 12px;
                    color: #334155;
                    margin-top: 8px;
                }}
                QPushButton:hover {{
                    background-color: #e2e8f0;
                }}
            """)
            btn.clicked.connect(lambda checked, s=tag: self.navigate_to.emit(f"resolver_{s}"))

            c_layout.addWidget(t_lbl)
            c_layout.addWidget(d_lbl)
            c_layout.addWidget(btn)
            grid_layout.addWidget(card, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(grid_layout)

        # Bottom panel: recent activity and recommendation
        info_layout = QHBoxLayout()
        info_layout.setSpacing(14)

        # Recent activity card
        self.activity_card = QFrame()
        self.activity_card.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;")
        act_layout = QVBoxLayout(self.activity_card)
        act_title = QLabel("Recent Activity")
        act_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        act_layout.addWidget(act_title)

        self.act_desc = QLabel("Loading activity...")
        self.act_desc.setWordWrap(True)
        self.act_desc.setStyleSheet("font-size: 13px; color: #475569; margin-top: 6px;")
        act_layout.addWidget(self.act_desc)
        act_layout.addStretch()
        info_layout.addWidget(self.activity_card, stretch=1)

        # Recommendation card
        self.rec_card = QFrame()
        self.rec_card.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;")
        rec_layout = QVBoxLayout(self.rec_card)
        rec_title = QLabel("Study Recommendation")
        rec_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        rec_layout.addWidget(rec_title)

        self.rec_desc = QLabel("Loading recommendation...")
        self.rec_desc.setWordWrap(True)
        self.rec_desc.setStyleSheet("font-size: 13px; color: #475569; margin-top: 6px;")
        rec_layout.addWidget(self.rec_desc)
        rec_layout.addStretch()
        info_layout.addWidget(self.rec_card, stretch=1)

        layout.addLayout(info_layout)
        layout.addStretch()

        self.refresh_data()

    def refresh_data(self):
        profile = self.storage.get_profile()
        self.greeting_label.setText(f"Hello, {profile.name}!")

        history = self.storage.get_history(limit=1)
        if history:
            last = history[0]
            self.act_desc.setText(
                f"Subject: {subject_name(last['subject'])}\n"
                f"Exercise: {last['original_input']}\n"
                f"Result: {last['final_answer']}\n"
                f"Date: {last['created_at']}"
            )
            self.rec_desc.setText(
                f"You recently worked on {subject_name(last['subject'])}. "
                f"Try similar exercises in the Practice section."
            )
        else:
            self.act_desc.setText("You have not solved any exercises yet. Get started in the Solve section!")
            self.rec_desc.setText("There are not enough exercises in your history for personalized recommendations yet.")
