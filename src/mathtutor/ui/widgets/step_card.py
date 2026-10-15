"""
Widget de tarjeta de paso pedagógico (StepCard).
Muestra la operación realizada, la expresión resultante y la explicación
con alternador entre modo 'Breve' y 'Detallado'.
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt
from ...core.models import SolutionStep


class StepCardWidget(QFrame):
    def __init__(self, step: SolutionStep, is_detailed: bool = False, parent=None):
        super().__init__(parent)
        self.step = step
        self.is_detailed = is_detailed
        self._init_ui()

    def _init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            StepCardWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #3b82f6;
                border-radius: 6px;
                margin-bottom: 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Encabezado: Paso X y Botón Breve/Detallado
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        step_title = QLabel(f"Paso {self.step.step_number}: {self.step.operation}")
        step_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e3a8a;")
        header_layout.addWidget(step_title, stretch=1)

        self.toggle_btn = QPushButton("Detalle ▼" if not self.is_detailed else "Breve ▲")
        self.toggle_btn.setFixedWidth(80)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 4px;
                color: #1d4ed8;
                font-size: 11px;
                font-weight: 600;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: #dbeafe;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_detail)
        header_layout.addWidget(self.toggle_btn)
        layout.addLayout(header_layout)

        # Expresión resultante destacada
        res_label = QLabel(f"➔  {self.step.resulting_expr}")
        res_label.setStyleSheet("""
            background-color: #f8fafc;
            border: 1px solid #f1f5f9;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 15px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-weight: bold;
            color: #0f172a;
        """)
        layout.addWidget(res_label)

        # Explicación
        self.explanation_label = QLabel(
            self.step.explanation_detailed if self.is_detailed else self.step.explanation_brief
        )
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("color: #475569; font-size: 13px; line-height: 1.4;")
        layout.addWidget(self.explanation_label)

        # Restricciones si las hay
        if self.step.restrictions:
            rest_label = QLabel(f"Restricciones: {self.step.restrictions}")
            rest_label.setStyleSheet("color: #b45309; font-size: 12px; font-style: italic;")
            layout.addWidget(rest_label)

    def _toggle_detail(self):
        self.is_detailed = not self.is_detailed
        if self.is_detailed:
            self.toggle_btn.setText("Breve ▲")
            self.explanation_label.setText(self.step.explanation_detailed)
        else:
            self.toggle_btn.setText("Detalle ▼")
            self.explanation_label.setText(self.step.explanation_brief)

    def set_detailed_mode(self, detailed: bool):
        self.is_detailed = detailed
        self.toggle_btn.setText("Breve ▲" if detailed else "Detalle ▼")
        self.explanation_label.setText(
            self.step.explanation_detailed if detailed else self.step.explanation_brief
        )
