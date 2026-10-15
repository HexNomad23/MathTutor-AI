"Settings and profile view.\nConfigures the local student name and displays system information."

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Signal
from ...storage.database import StorageManager, get_default_db_path


class SettingsView(QWidget):
    profile_updated = Signal(str)

    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Settings and Profile")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)

        # Profile card
        profile_card = QFrame()
        profile_card.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;")
        p_layout = QVBoxLayout(profile_card)
        p_layout.setSpacing(10)

        p_title = QLabel("User Profile")
        p_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        p_layout.addWidget(p_title)

        desc = QLabel("Customize your student name. No online account is required.")
        desc.setStyleSheet("color: #64748b; font-size: 13px;")
        p_layout.addWidget(desc)

        name_layout = QHBoxLayout()
        name_lbl = QLabel("Name:")
        name_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        name_layout.addWidget(name_lbl)

        self.name_input = QLineEdit()
        profile = self.storage.get_profile()
        self.name_input.setText(profile.name)
        self.name_input.setStyleSheet("background-color: #ffffff; color: #0f172a; padding: 6px 10px; font-size: 14px; border: 1px solid #cbd5e1; border-radius: 4px;")
        name_layout.addWidget(self.name_input)

        save_btn = QPushButton("Save Name")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        save_btn.clicked.connect(self._save_name)
        name_layout.addWidget(save_btn)

        p_layout.addLayout(name_layout)
        layout.addWidget(profile_card)

        # System and privacy card
        sys_card = QFrame()
        sys_card.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;")
        s_layout = QVBoxLayout(sys_card)
        s_layout.setSpacing(8)

        s_title = QLabel("System and Privacy")
        s_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        s_layout.addWidget(s_title)

        mode_lbl = QLabel("Status: Local mode active (no telemetry or required external connection).")
        mode_lbl.setStyleSheet("color: #166534; font-weight: 600; font-size: 13px;")
        s_layout.addWidget(mode_lbl)

        db_lbl = QLabel(f"Local storage location:\n{get_default_db_path()}")
        db_lbl.setWordWrap(True)
        db_lbl.setStyleSheet("color: #475569; font-size: 12px; font-family: monospace; background-color: #f8fafc; padding: 8px; border-radius: 4px;")
        s_layout.addWidget(db_lbl)

        ver_lbl = QLabel("MathTutor AI — Version 0.1 (Windows x64)")
        ver_lbl.setStyleSheet("color: #64748b; font-size: 12px; margin-top: 4px;")
        s_layout.addWidget(ver_lbl)

        layout.addWidget(sys_card)
        layout.addStretch()

    def _save_name(self):
        new_name = self.name_input.text().strip()
        if not new_name:
            new_name = "Student"
            self.name_input.setText(new_name)

        self.storage.update_profile_name(new_name)
        self.profile_updated.emit(new_name)
        QMessageBox.information(self, "Profile Updated", f"Name updated to: '{new_name}'")
