"""
Vista completa del Solucionador Multimateria de MathTutor AI.
Organizado en pestañas:
1. Álgebra (Ecuaciones lineales y cuadráticas, teclado virtual, pistas y revisión línea a línea).
2. Geometría (Pitágoras, Triángulos, Rectángulos, Círculos con validación dimensional).
3. Física (MRU, Ley de Newton y conversiones con comprobación física).
4. Cálculo (Derivadas e Integrales indefinidas polinómicas paso a paso).
"""

from typing import Optional, List
import sympy as sp

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QRadioButton, QButtonGroup, QMessageBox,
    QDialog, QTextEdit, QSplitter, QTabWidget, QComboBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal

from ...core.models import Subject, SolutionResult, SolutionStep, VerificationStatus
from ...math_engine.safe_parser import parse_equation, parse_expression, SafeParserError
from ...math_engine.algebra_solver import solve_linear_equation, solve_quadratic_equation
from ...math_engine.geometry_solver import (
    solve_pythagoras, solve_triangle_area, solve_rectangle, solve_circle
)
from ...math_engine.physics_solver import (
    solve_mru, solve_newton_second_law, convert_units
)
from ...math_engine.calculus_solver import (
    solve_polynomial_derivative, solve_polynomial_integral
)
from ...tutor.step_reviewer import review_student_procedure
from ...storage.database import StorageManager
from ..widgets.math_keyboard import MathKeyboardWidget
from ..widgets.step_card import StepCardWidget
from ..widgets.plot_widget import PolynomialPlotWidget


class StudentProcedureDialog(QDialog):
    """Diálogo para revisión línea a línea del procedimiento del alumno."""
    def __init__(self, initial_problem: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Revisa mi procedimiento - Álgebra")
        self.setMinimumSize(560, 420)
        self.initial_problem = initial_problem
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        lbl = QLabel("Escribe tu procedimiento paso a paso, una ecuación por línea:")
        lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #1e293b;")
        layout.addWidget(lbl)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(f"{self.initial_problem}\n...\n...")
        self.editor.setText(f"{self.initial_problem}\n")
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #0f172a;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.editor)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("padding: 8px; border-radius: 6px; font-size: 13px;")
        self.result_label.hide()
        layout.addWidget(self.result_label)

        btn_layout = QHBoxLayout()
        check_btn = QPushButton("Comprobar pasos")
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        check_btn.clicked.connect(self._check_steps)
        btn_layout.addWidget(check_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _check_steps(self):
        text = self.editor.toPlainText().strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if len(lines) < 2:
            self.result_label.setText("Por favor ingresa al menos 2 líneas para poder comparar un paso.")
            self.result_label.setStyleSheet("background-color: #fef3c7; color: #92400e; padding: 8px; border-radius: 6px;")
            self.result_label.show()
            return

        reviews = review_student_procedure(lines)
        if not reviews:
            self.result_label.setText("No se encontraron transiciones válidas.")
            self.result_label.show()
            return

        has_error = False
        feedback_lines = []
        for r in reviews:
            if not r.is_valid:
                has_error = True
                feedback_lines.append(f"❌ Transición {r.step_index} ('{r.previous_line}' ➔ '{r.current_line}'):")
                feedback_lines.append(f"   {r.message}")
                if r.suggested_correction:
                    feedback_lines.append(f"   Sugerencia: {r.suggested_correction}")
                break
            else:
                extra = " (Paso alternativo válido)" if r.is_alternative_valid else ""
                feedback_lines.append(f"✓ Paso {r.step_index}: '{r.current_line}' correcto.{extra}")

        if not has_error:
            feedback_lines.append("\n¡Excelente! Todos los pasos analizados son matemáticamente correctos.")
            self.result_label.setStyleSheet("background-color: #dcfce7; color: #166534; padding: 10px; border-radius: 6px; font-size: 13px;")
        else:
            self.result_label.setStyleSheet("background-color: #fee2e2; color: #991b1b; padding: 10px; border-radius: 6px; font-size: 13px;")

        self.result_label.setText("\n".join(feedback_lines))
        self.result_label.show()


class SolverView(QWidget):
    request_practice = Signal(str)

    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.current_solution: Optional[SolutionResult] = None
        self.revealed_steps_count = 0
        self.guided_mode = False
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        header = QLabel("Resolver ejercicios paso a paso")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        main_layout.addWidget(header)

        # Tabs de materias
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-weight: 600;
                font-size: 13px;
                padding: 8px 16px;
                color: #475569;
            }
            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }
        """)

        # Tab 1: Álgebra
        self.tab_algebra = self._create_algebra_tab()
        self.tabs.addTab(self.tab_algebra, "Álgebra")

        # Tab 2: Geometría
        self.tab_geometry = self._create_geometry_tab()
        self.tabs.addTab(self.tab_geometry, "Geometría")

        # Tab 3: Física
        self.tab_physics = self._create_physics_tab()
        self.tabs.addTab(self.tab_physics, "Física")

        # Tab 4: Cálculo
        self.tab_calculus = self._create_calculus_tab()
        self.tabs.addTab(self.tab_calculus, "Cálculo")

        main_layout.addWidget(self.tabs)

        # Opciones de detalle
        action_bar = QHBoxLayout()
        self.radio_brief = QRadioButton("Explicación Breve")
        self.radio_detailed = QRadioButton("Explicación Detallada")
        self.radio_brief.setChecked(True)
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_brief)
        self.radio_group.addButton(self.radio_detailed)
        self.radio_brief.toggled.connect(self._on_detail_mode_changed)

        action_bar.addWidget(QLabel("Modo de explicación:"))
        action_bar.addWidget(self.radio_brief)
        action_bar.addWidget(self.radio_detailed)
        action_bar.addStretch()

        self.btn_practice_similar = QPushButton("Practicar algo parecido ➔")
        self.btn_practice_similar.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_practice_similar.clicked.connect(self._on_practice_similar_clicked)
        action_bar.addWidget(self.btn_practice_similar)

        main_layout.addLayout(action_bar)

        # Splitter inferior: Pasos y Panel de Verificación
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        steps_scroll = QScrollArea()
        steps_scroll.setWidgetResizable(True)
        steps_scroll.setMinimumWidth(440)
        steps_scroll.setStyleSheet("QScrollArea { border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc; }")

        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_container)
        self.steps_layout.setContentsMargins(12, 12, 12, 12)
        self.steps_layout.setSpacing(8)
        self.steps_layout.addStretch()
        steps_scroll.setWidget(self.steps_container)
        content_splitter.addWidget(steps_scroll)

        # Panel lateral: Verificación y Gráfica
        side_panel = QFrame()
        side_panel.setMinimumWidth(350)
        side_panel.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;")
        side_layout = QVBoxLayout(side_panel)
        side_layout.setSpacing(8)

        verif_title = QLabel("Resultado y Comprobación")
        verif_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        side_layout.addWidget(verif_title)

        self.status_pill = QLabel("Esperando ejercicio")
        self.status_pill.setStyleSheet("""
            background-color: #e2e8f0;
            color: #475569;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
        """)
        self.status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(self.status_pill)

        self.answer_label = QLabel("Ingresa un ejercicio y pulsa 'Resolver paso a paso'")
        self.answer_label.setWordWrap(True)
        self.answer_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a;")
        side_layout.addWidget(self.answer_label)

        self.check_label = QLabel("")
        self.check_label.setWordWrap(True)
        self.check_label.setStyleSheet("font-size: 12px; color: #334155; background-color: #f1f5f9; padding: 8px; border-radius: 4px;")
        side_layout.addWidget(self.check_label)

        self.plot_widget = PolynomialPlotWidget()
        side_layout.addWidget(self.plot_widget, stretch=1)

        content_splitter.addWidget(side_panel)
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 2)
        content_splitter.setSizes([600, 420])

        main_layout.addWidget(content_splitter, stretch=1)

    # --- Pestaña Álgebra ---
    def _create_algebra_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        self.alg_input = QLineEdit()
        self.alg_input.setPlaceholderText("Ejemplo: 2x + 3 = 11  o  3(x - 2) = 12  o  x^2 - 5x + 6 = 0")
        self.alg_input.setText("2x + 3 = 11")
        self.alg_input.setStyleSheet("background-color: #ffffff; color: #0f172a; font-size: 15px; padding: 7px 10px; border: 1px solid #cbd5e1; border-radius: 6px;")
        self.alg_input.textChanged.connect(self._on_alg_input_changed)
        self.alg_input.returnPressed.connect(self.solve_algebra)
        layout.addWidget(self.alg_input)

        # Teclado matemático
        self.keyboard = MathKeyboardWidget(self.alg_input)
        layout.addWidget(self.keyboard)

        # Vista previa de interpretación
        self.alg_preview = QLabel("Interpreté tu ejercicio como: 2*x + 3 = 11")
        self.alg_preview.setStyleSheet("color: #166534; font-size: 12px; font-weight: 500;")
        layout.addWidget(self.alg_preview)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_solve = QPushButton("Resolver paso a paso")
        btn_solve.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_algebra)
        btn_layout.addWidget(btn_solve)

        btn_hint = QPushButton("Dame una pista")
        btn_hint.setStyleSheet("background-color: #f59e0b; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        btn_hint.clicked.connect(self.give_algebra_hint)
        btn_layout.addWidget(btn_hint)

        btn_review = QPushButton("Revisa mi procedimiento")
        btn_review.setStyleSheet("background-color: #0ea5e9; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        btn_review.clicked.connect(self._open_procedure_reviewer)
        btn_layout.addWidget(btn_review)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return tab

    def _on_alg_input_changed(self, text: str):
        t = text.strip()
        if not t:
            self.alg_preview.setText("Escribe una ecuación arriba para ver la interpretación.")
            return
        try:
            lhs, rhs, var = parse_equation(t)
            self.alg_preview.setText(f"Interpreté tu ejercicio como: {lhs} = {rhs}  (Incógnita: {var})")
            self.alg_preview.setStyleSheet("color: #166534; font-size: 12px; font-weight: 500;")
        except Exception as e:
            self.alg_preview.setText(f"Interpretación pendiente: {e}")
            self.alg_preview.setStyleSheet("color: #b45309; font-size: 12px; font-style: italic;")

    def solve_algebra(self):
        text = self.alg_input.text().strip()
        if not text:
            return
        try:
            lhs, rhs, var = parse_equation(text)
            diff = sp.expand(lhs - rhs)
            poly = sp.Poly(diff, var)
            deg = poly.degree()

            if deg == 1:
                sol = solve_linear_equation(text)
            elif deg == 2:
                sol = solve_quadratic_equation(text)
            else:
                QMessageBox.warning(self, "Fuera de alcance", f"Ecuación de grado {deg} fuera del alcance v0.1.")
                return

            self._apply_solution(sol)
            self.plot_widget.plot_polynomial(diff, var, title=f"f({var}) = {diff}")
        except Exception as e:
            QMessageBox.warning(self, "Error al resolver", str(e))

    def give_algebra_hint(self):
        text = self.alg_input.text().strip()
        if not text:
            return
        if not self.current_solution or self.current_solution.original_input != text:
            self.solve_algebra()
            self.revealed_steps_count = 0

        total_steps = len(self.current_solution.steps)
        if self.revealed_steps_count < total_steps:
            self.revealed_steps_count += 1
            self._render_solution()
        else:
            QMessageBox.information(self, "Pistas completas", "Ya se han revelado todos los pasos de este ejercicio.")

    def _open_procedure_reviewer(self):
        text = self.alg_input.text().strip()
        dlg = StudentProcedureDialog(text, self)
        dlg.exec()

    # --- Pestaña Geometría ---
    def _create_geometry_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        form_l = QHBoxLayout()
        form_l.addWidget(QLabel("Problema:"))
        self.geom_type = QComboBox()
        self.geom_type.addItems([
            "Teorema de Pitágoras (a² + b² = c²)",
            "Área de Triángulo (A = b·h / 2)",
            "Rectángulo (Área y Perímetro)",
            "Círculo (Área y Circunferencia)"
        ])
        self.geom_type.currentIndexChanged.connect(self._on_geom_type_changed)
        form_l.addWidget(self.geom_type)

        form_l.addWidget(QLabel("Unidad:"))
        self.geom_unit = QLineEdit("cm")
        self.geom_unit.setFixedWidth(50)
        form_l.addWidget(self.geom_unit)
        form_l.addStretch()
        layout.addLayout(form_l)

        # Campos de parámetros
        inputs_layout = QHBoxLayout()
        self.geom_lbl1 = QLabel("Cateto a:")
        self.geom_val1 = QDoubleSpinBox()
        self.geom_val1.setRange(0, 10000)
        self.geom_val1.setValue(3)

        self.geom_lbl2 = QLabel("Cateto b:")
        self.geom_val2 = QDoubleSpinBox()
        self.geom_val2.setRange(0, 10000)
        self.geom_val2.setValue(4)

        self.geom_lbl3 = QLabel("Hipotenusa c (0 si es incógnita):")
        self.geom_val3 = QDoubleSpinBox()
        self.geom_val3.setRange(0, 10000)
        self.geom_val3.setValue(0)

        inputs_layout.addWidget(self.geom_lbl1)
        inputs_layout.addWidget(self.geom_val1)
        inputs_layout.addWidget(self.geom_lbl2)
        inputs_layout.addWidget(self.geom_val2)
        inputs_layout.addWidget(self.geom_lbl3)
        inputs_layout.addWidget(self.geom_val3)
        inputs_layout.addStretch()
        layout.addLayout(inputs_layout)

        btn_solve = QPushButton("Resolver Geometría paso a paso")
        btn_solve.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_geometry)
        layout.addWidget(btn_solve)
        return tab

    def _on_geom_type_changed(self, idx: int):
        if idx == 0:  # Pitágoras
            self.geom_lbl1.setText("Cateto a:")
            self.geom_lbl2.setText("Cateto b:")
            self.geom_lbl3.setText("Hipotenusa c (0 para incógnita):")
            self.geom_lbl3.show()
            self.geom_val3.show()
        elif idx == 1:  # Triángulo
            self.geom_lbl1.setText("Base b:")
            self.geom_lbl2.setText("Altura h:")
            self.geom_lbl3.hide()
            self.geom_val3.hide()
        elif idx == 2:  # Rectángulo
            self.geom_lbl1.setText("Base b:")
            self.geom_lbl2.setText("Altura h:")
            self.geom_lbl3.hide()
            self.geom_val3.hide()
        elif idx == 3:  # Círculo
            self.geom_lbl1.setText("Radio r:")
            self.geom_lbl2.hide()
            self.geom_val2.hide()
            self.geom_lbl3.hide()
            self.geom_val3.hide()

    def solve_geometry(self):
        idx = self.geom_type.currentIndex()
        unit = self.geom_unit.text().strip() or "cm"
        try:
            if idx == 0:  # Pitágoras
                a = self.geom_val1.value() if self.geom_val1.value() > 0 else None
                b = self.geom_val2.value() if self.geom_val2.value() > 0 else None
                c = self.geom_val3.value() if self.geom_val3.value() > 0 else None
                sol = solve_pythagoras(a, b, c, unit)
            elif idx == 1:  # Triángulo
                sol = solve_triangle_area(self.geom_val1.value(), self.geom_val2.value(), unit)
            elif idx == 2:  # Rectángulo
                sol = solve_rectangle(self.geom_val1.value(), self.geom_val2.value(), unit)
            elif idx == 3:  # Círculo
                sol = solve_circle(self.geom_val1.value(), unit)
            else:
                return

            self._apply_solution(sol)
        except Exception as e:
            QMessageBox.warning(self, "Error en geometría", str(e))

    # --- Pestaña Física ---
    def _create_physics_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        form_l = QHBoxLayout()
        form_l.addWidget(QLabel("Modelo de Física:"))
        self.phys_type = QComboBox()
        self.phys_type.addItems([
            "MRU (d = v · t)",
            "Segunda Ley de Newton (F = m · a)",
            "Conversión de unidades (km/h ⇄ m/s)"
        ])
        self.phys_type.currentIndexChanged.connect(self._on_phys_type_changed)
        form_l.addWidget(self.phys_type)
        form_l.addStretch()
        layout.addLayout(form_l)

        # Contenedor de inputs
        self.phys_inputs_l = QHBoxLayout()
        self.phys_lbl1 = QLabel("Distancia d (m):")
        self.phys_val1 = QDoubleSpinBox()
        self.phys_val1.setRange(0, 100000)
        self.phys_val1.setValue(150)

        self.phys_lbl2 = QLabel("Rapidez v (m/s) [0 si es incógnita]:")
        self.phys_val2 = QDoubleSpinBox()
        self.phys_val2.setRange(0, 10000)
        self.phys_val2.setValue(0)

        self.phys_lbl3 = QLabel("Tiempo t (s):")
        self.phys_val3 = QDoubleSpinBox()
        self.phys_val3.setRange(0, 10000)
        self.phys_val3.setValue(10)

        self.phys_inputs_l.addWidget(self.phys_lbl1)
        self.phys_inputs_l.addWidget(self.phys_val1)
        self.phys_inputs_l.addWidget(self.phys_lbl2)
        self.phys_inputs_l.addWidget(self.phys_val2)
        self.phys_inputs_l.addWidget(self.phys_lbl3)
        self.phys_inputs_l.addWidget(self.phys_val3)
        self.phys_inputs_l.addStretch()
        layout.addLayout(self.phys_inputs_l)

        btn_solve = QPushButton("Resolver Física paso a paso")
        btn_solve.setStyleSheet("background-color: #d97706; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_physics)
        layout.addWidget(btn_solve)
        return tab

    def _on_phys_type_changed(self, idx: int):
        if idx == 0:  # MRU
            self.phys_lbl1.setText("Distancia d (m):")
            self.phys_lbl2.setText("Rapidez v (m/s):")
            self.phys_lbl3.setText("Tiempo t (s):")
            self.phys_lbl3.show()
            self.phys_val3.show()
        elif idx == 1:  # Newton
            self.phys_lbl1.setText("Fuerza F (N) [0 incógnita]:")
            self.phys_lbl2.setText("Masa m (kg):")
            self.phys_lbl3.setText("Aceleración a (m/s²):")
            self.phys_lbl3.show()
            self.phys_val3.show()
        elif idx == 2:  # Conversión
            self.phys_lbl1.setText("Valor:")
            self.phys_lbl2.setText("De (km/h):")
            self.phys_lbl3.hide()
            self.phys_val3.hide()

    def solve_physics(self):
        idx = self.phys_type.currentIndex()
        try:
            if idx == 0:  # MRU
                d = self.phys_val1.value() if self.phys_val1.value() > 0 else None
                v = self.phys_val2.value() if self.phys_val2.value() > 0 else None
                t = self.phys_val3.value() if self.phys_val3.value() > 0 else None
                sol = solve_mru(d=d, v=v, t=t)
            elif idx == 1:  # Newton
                F = self.phys_val1.value() if self.phys_val1.value() > 0 else None
                m = self.phys_val2.value() if self.phys_val2.value() > 0 else None
                a = self.phys_val3.value() if self.phys_val3.value() > 0 else None
                sol = solve_newton_second_law(F=F, m=m, a=a)
            elif idx == 2:  # Conversión
                val = self.phys_val1.value()
                sol = convert_units(val, "km/h", "m/s")
            else:
                return

            self._apply_solution(sol)
        except Exception as e:
            QMessageBox.warning(self, "Error en física", str(e))

    # --- Pestaña Cálculo ---
    def _create_calculus_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        mode_l = QHBoxLayout()
        mode_l.addWidget(QLabel("Operación de Cálculo:"))
        self.calc_mode = QComboBox()
        self.calc_mode.addItems(["Derivada de polinomio: d/dx [P(x)]", "Integral indefinida de polinomio: ∫ P(x) dx"])
        mode_l.addWidget(self.calc_mode)
        mode_l.addStretch()
        layout.addLayout(mode_l)

        self.calc_input = QLineEdit("3x^2 + 2x - 5")
        self.calc_input.setPlaceholderText("Ejemplo: 3x^2 + 2x - 5  o  2x + 3")
        self.calc_input.setStyleSheet("background-color: #ffffff; color: #0f172a; font-size: 15px; padding: 7px 10px; border: 1px solid #cbd5e1; border-radius: 6px;")
        layout.addWidget(self.calc_input)

        btn_solve = QPushButton("Resolver Cálculo paso a paso")
        btn_solve.setStyleSheet("background-color: #7c3aed; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_calculus)
        layout.addWidget(btn_solve)
        return tab

    def solve_calculus(self):
        text = self.calc_input.text().strip()
        if not text:
            return
        idx = self.calc_mode.currentIndex()
        try:
            if idx == 0:
                sol = solve_polynomial_derivative(text)
            else:
                sol = solve_polynomial_integral(text)

            self._apply_solution(sol)

            # Graficar función original si es posible
            expr = parse_expression(text)
            symbols = list(expr.free_symbols)
            var = symbols[0] if symbols else sp.Symbol("x", real=True)
            self.plot_widget.plot_polynomial(expr, var, title=f"f({var}) = {expr}")
        except Exception as e:
            QMessageBox.warning(self, "Error en cálculo", str(e))

    # --- Renderizado común ---
    def _apply_solution(self, sol: SolutionResult):
        self.current_solution = sol
        self.revealed_steps_count = len(sol.steps)
        self.guided_mode = False
        self._render_solution()
        self.storage.save_solution(sol)

    def _clear_steps_layout(self):
        while self.steps_layout.count() > 1:
            item = self.steps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_solution(self):
        if not self.current_solution:
            return

        self._clear_steps_layout()
        is_detailed = self.radio_detailed.isChecked()

        steps_to_show = self.current_solution.steps[:self.revealed_steps_count]
        for step in steps_to_show:
            card = StepCardWidget(step, is_detailed=is_detailed)
            self.steps_layout.insertWidget(self.steps_layout.count() - 1, card)

        if self.revealed_steps_count >= len(self.current_solution.steps):
            self.status_pill.setText(f"✓ {self.current_solution.verification_status.value}")
            self.status_pill.setStyleSheet("""
                background-color: #dcfce7;
                color: #15803d;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
            """)
            self.answer_label.setText(f"Solución: {self.current_solution.final_answer}")
            self.check_label.setText(self.current_solution.substitution_check or self.current_solution.verification_reason)
        else:
            self.status_pill.setText(f"Pista {self.revealed_steps_count} de {len(self.current_solution.steps)}")
            self.status_pill.setStyleSheet("""
                background-color: #fef3c7;
                color: #b45309;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
            """)
            self.answer_label.setText("Modo guiado en progreso...")
            self.check_label.setText("Pulsa 'Dame una pista' para el siguiente paso.")

    def _on_detail_mode_changed(self):
        is_detailed = self.radio_detailed.isChecked()
        for i in range(self.steps_layout.count() - 1):
            w = self.steps_layout.itemAt(i).widget()
            if isinstance(w, StepCardWidget):
                w.set_detailed_mode(is_detailed)

    def _on_practice_similar_clicked(self):
        tab_idx = self.tabs.currentIndex()
        topic_map = {0: "algebra_lineal", 1: "geometria", 2: "fisica", 3: "calculo"}
        self.request_practice.emit(topic_map.get(tab_idx, "algebra_lineal"))
