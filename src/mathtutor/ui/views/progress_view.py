"Student progress view.\nShows statistics based only on SQLite records.\nDisplays an insufficient-data message when a topic has fewer than three attempts."

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QPushButton
)
from ...storage.database import StorageManager
from ...practice.adaptive import AdaptiveController
from ...practice.generator import ExerciseGenerator


class ProgressView(QWidget):
    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.adaptive = AdaptiveController(storage)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        title = QLabel("My Learning Progress")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        btn_refresh = QPushButton("Refresh Statistics")
        btn_refresh.clicked.connect(self.refresh_stats)
        header_layout.addWidget(btn_refresh)

        layout.addLayout(header_layout)

        notice = QLabel("Assessments are based only on your completed exercises saved in your local profile.")
        notice.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(notice)

        # Topic card container
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(14)
        layout.addLayout(self.grid_layout)

        layout.addStretch()

        self.refresh_stats()

    def refresh_stats(self):
        # Clear the grid
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        topic_names = {
            "algebra_lineal": "Linear Equations",
            "algebra_cuadratica": "Quadratic Equations",
            "geometria": "Geometry",
            "fisica": "Physics",
            "calculo": "Calculus",
        }

        row, col = 0, 0
        for topic_key, topic_title in topic_names.items():
            summary = self.adaptive.get_progress_summary(topic_key)
            card = self._create_topic_card(topic_title, summary)
            self.grid_layout.addWidget(card, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

    def _create_topic_card(self, title: str, summary: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(8)

        # Title and level
        header_l = QHBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e3a8a;")
        header_l.addWidget(t_lbl)

        lvl_badge = QLabel(f"Current level: {summary['current_level']}")
        lvl_badge.setStyleSheet("""
            background-color: #eff6ff;
            color: #2563eb;
            font-weight: bold;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
        """)
        header_l.addWidget(lvl_badge)
        header_l.addStretch()
        c_layout.addLayout(header_l)

        if not summary["has_enough_data"]:
            msg_lbl = QLabel(summary["message"])
            msg_lbl.setWordWrap(True)
            msg_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 13px; margin-top: 6px;")
            c_layout.addWidget(msg_lbl)

            details_lbl = QLabel(f"Recorded attempts: {summary['total_attempts']} | Correct: {summary['total_correct']}")
            details_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
            c_layout.addWidget(details_lbl)
        else:
            pct_lbl = QLabel(f"Accuracy: {summary['percentage']}% ({summary['total_correct']} correct out of {summary['total_attempts']} attempts)")
            pct_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #166534;")
            c_layout.addWidget(pct_lbl)

            blk_lbl = QLabel(f"Adaptive block progress: {summary.get('unassisted_progress', '0/5')}")
            blk_lbl.setStyleSheet("color: #475569; font-size: 12px;")
            c_layout.addWidget(blk_lbl)

        return card
