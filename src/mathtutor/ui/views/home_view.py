"""
Vista de Inicio (HomeView).
Muestra accesos directos a las cuatro materias, última actividad y recomendaciones basadas en el historial.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from ...storage.database import StorageManager


class HomeView(QWidget):
    navigate_to = Signal(str)  # Señal para navegar a otra vista

    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Saludo
        profile = self.storage.get_profile()
        self.greeting_label = QLabel(f"¡Hola, {profile.name}!")
        self.greeting_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        layout.addWidget(self.greeting_label)

        subtitle = QLabel("Bienvenido a MathTutor AI. Selecciona una materia o continúa donde lo dejaste.")
        subtitle.setStyleSheet("font-size: 14px; color: #64748b;")
        layout.addWidget(subtitle)

        # Tarjetas de Materias (Grid)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(14)

        subjects = [
            ("Álgebra", "Ecuaciones lineales y cuadráticas, pasos y revisión.", "#2563eb", "algebra"),
            ("Geometría", "Áreas, perímetros y Teorema de Pitágoras.", "#059669", "geometria"),
            ("Física", "MRU, Segunda Ley de Newton y conversiones.", "#d97706", "fisica"),
            ("Cálculo", "Derivadas e integrales de funciones polinómicas.", "#7c3aed", "calculo"),
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

            btn = QPushButton("Abrir materia ➔")
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

        # Panel inferior: Última actividad y Recomendación
        info_layout = QHBoxLayout()
        info_layout.setSpacing(14)

        # Tarjeta Última Actividad
        self.activity_card = QFrame()
        self.activity_card.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;")
        act_layout = QVBoxLayout(self.activity_card)
        act_title = QLabel("Última actividad")
        act_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        act_layout.addWidget(act_title)

        self.act_desc = QLabel("Cargando actividad...")
        self.act_desc.setWordWrap(True)
        self.act_desc.setStyleSheet("font-size: 13px; color: #475569; margin-top: 6px;")
        act_layout.addWidget(self.act_desc)
        act_layout.addStretch()
        info_layout.addWidget(self.activity_card, stretch=1)

        # Tarjeta Recomendación
        self.rec_card = QFrame()
        self.rec_card.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;")
        rec_layout = QVBoxLayout(self.rec_card)
        rec_title = QLabel("Recomendación de estudio")
        rec_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        rec_layout.addWidget(rec_title)

        self.rec_desc = QLabel("Cargando recomendación...")
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
        self.greeting_label.setText(f"¡Hola, {profile.name}!")

        history = self.storage.get_history(limit=1)
        if history:
            last = history[0]
            self.act_desc.setText(
                f"Materia: {last['subject'].capitalize()}\n"
                f"Ejercicio: {last['original_input']}\n"
                f"Resultado: {last['final_answer']}\n"
                f"Fecha: {last['created_at']}"
            )
            self.rec_desc.setText(
                f"Has trabajado recientemente en {last['subject']}. "
                f"Te recomendamos practicar ejercicios similares en la sección 'Practicar'."
            )
        else:
            self.act_desc.setText("Aún no has resuelto ningún ejercicio. ¡Comienza ahora ingresando uno en 'Resolver'!")
            self.rec_desc.setText("Aún no hay suficientes ejercicios en tu historial para generar recomendaciones personalizadas.")
