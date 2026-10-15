"Virtual mathematical keyboard for entering expressions.\nInserts symbols into the active input field without requiring special keyboard characters."

from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt


class MathKeyboardWidget(QWidget):
    def __init__(self, target_input: QLineEdit, parent=None):
        super().__init__(parent)
        self.target_input = target_input
        self._init_ui()

    def _init_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        # Button definitions (display text, inserted text)
        buttons = [
            ("x", "x"), ("+", " + "), ("−", " - "), ("·", "*"),
            ("÷", "/"), ("=", " = "), ("(", "("), (")", ")"),
            ("x²", "^2"), ("xⁿ", "^"), ("√", "sqrt("), (",", ",")
        ]

        row, col = 0, 0
        for label, insert_text in buttons:
            btn = QPushButton(label)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5f9;
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    min-height: 28px;
                    min-width: 36px;
                    color: #1e293b;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                    border-color: #94a3b8;
                }
                QPushButton:pressed {
                    background-color: #cbd5e1;
                }
            """)
            btn.clicked.connect(lambda checked, text=insert_text: self._insert(text))
            layout.addWidget(btn, row, col)
            col += 1
            if col > 5:
                col = 0
                row += 1

    def _insert(self, text: str):
        if not self.target_input:
            return
        self.target_input.insert(text)
        self.target_input.setFocus()
