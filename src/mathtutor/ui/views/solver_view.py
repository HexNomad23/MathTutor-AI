"Multi-subject solver view for MathTutor AI.\nTabs: algebra, geometry, physics, and calculus.\nIncludes step-by-step solutions, hints, procedure review, and verification."

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
    "Dialog for reviewing a student's procedure line by line."
    def __init__(self, initial_problem: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review My Work - Algebra")
        self.setMinimumSize(560, 420)
        self.initial_problem = initial_problem
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        lbl = QLabel("Enter your work step by step, with one equation per line:")
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
        check_btn = QPushButton("Check Steps")
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

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _check_steps(self):
        text = self.editor.toPlainText().strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if len(lines) < 2:
            self.result_label.setText("Enter at least two lines to compare a step.")
            self.result_label.setStyleSheet("background-color: #fef3c7; color: #92400e; padding: 8px; border-radius: 6px;")
            self.result_label.show()
            return

        reviews = review_student_procedure(lines)
        if not reviews:
            self.result_label.setText("No valid transitions were found.")
            self.result_label.show()
            return

        has_error = False
        feedback_lines = []
        for r in reviews:
            if not r.is_valid:
                has_error = True
                feedback_lines.append(f"❌ Transition {r.step_index} ('{r.previous_line}' ➔ '{r.current_line}'):")
                feedback_lines.append(f"   {r.message}")
                if r.suggested_correction:
                    feedback_lines.append(f"   Suggestion: {r.suggested_correction}")
                break
            else:
                extra = " (Valid alternative step)" if r.is_alternative_valid else ""
                feedback_lines.append(f"✓ Step {r.step_index}: '{r.current_line}' is correct.{extra}")

        if not has_error:
            feedback_lines.append("\nExcellent! All reviewed steps are mathematically correct.")
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

        header = QLabel("Solve Exercises Step by Step")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        main_layout.addWidget(header)

        # Subject tabs
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

        # Tab 1: Algebra
        self.tab_algebra = self._create_algebra_tab()
        self.tabs.addTab(self.tab_algebra, "Algebra")

        # Tab 2: Geometry
        self.tab_geometry = self._create_geometry_tab()
        self.tabs.addTab(self.tab_geometry, "Geometry")

        # Tab 3: Physics
        self.tab_physics = self._create_physics_tab()
        self.tabs.addTab(self.tab_physics, "Physics")

        # Tab 4: Calculus
        self.tab_calculus = self._create_calculus_tab()
        self.tabs.addTab(self.tab_calculus, "Calculus")

        main_layout.addWidget(self.tabs)

        # Explanation detail options
        action_bar = QHBoxLayout()
        self.radio_brief = QRadioButton("Brief Explanation")
        self.radio_detailed = QRadioButton("Detailed Explanation")
        self.radio_brief.setChecked(True)
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_brief)
        self.radio_group.addButton(self.radio_detailed)
        self.radio_brief.toggled.connect(self._on_detail_mode_changed)

        action_bar.addWidget(QLabel("Explanation mode:"))
        action_bar.addWidget(self.radio_brief)
        action_bar.addWidget(self.radio_detailed)
        action_bar.addStretch()

        self.btn_practice_similar = QPushButton("Practice Something Similar ➔")
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

        # Bottom splitter: steps and verification panel
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

        # Side panel: verification and graph
        side_panel = QFrame()
        side_panel.setMinimumWidth(350)
        side_panel.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;")
        side_layout = QVBoxLayout(side_panel)
        side_layout.setSpacing(8)

        verif_title = QLabel("Result and Verification")
        verif_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1e293b;")
        side_layout.addWidget(verif_title)

        self.status_pill = QLabel("Waiting for an Exercise")
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

        self.answer_label = QLabel("Enter an exercise and click 'Solve Step by Step'")
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

    # --- Algebra tab ---
    def _create_algebra_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        self.alg_input = QLineEdit()
        self.alg_input.setPlaceholderText("Example: 2x + 3 = 11  or  3(x - 2) = 12  or  x^2 - 5x + 6 = 0")
        self.alg_input.setText("2x + 3 = 11")
        self.alg_input.setStyleSheet("background-color: #ffffff; color: #0f172a; font-size: 15px; padding: 7px 10px; border: 1px solid #cbd5e1; border-radius: 6px;")
        self.alg_input.textChanged.connect(self._on_alg_input_changed)
        self.alg_input.returnPressed.connect(self.solve_algebra)
        layout.addWidget(self.alg_input)

        # Mathematical keyboard
        self.keyboard = MathKeyboardWidget(self.alg_input)
        layout.addWidget(self.keyboard)

        # Interpretation preview
        self.alg_preview = QLabel("Your exercise is interpreted as: 2*x + 3 = 11")
        self.alg_preview.setStyleSheet("color: #166534; font-size: 12px; font-weight: 500;")
        layout.addWidget(self.alg_preview)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_solve = QPushButton("Solve Step by Step")
        btn_solve.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_algebra)
        btn_layout.addWidget(btn_solve)

        btn_hint = QPushButton("Give Me a Hint")
        btn_hint.setStyleSheet("background-color: #f59e0b; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        btn_hint.clicked.connect(self.give_algebra_hint)
        btn_layout.addWidget(btn_hint)

        btn_review = QPushButton("Review My Work")
        btn_review.setStyleSheet("background-color: #0ea5e9; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        btn_review.clicked.connect(self._open_procedure_reviewer)
        btn_layout.addWidget(btn_review)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return tab

    def _on_alg_input_changed(self, text: str):
        t = text.strip()
        if not t:
            self.alg_preview.setText("Enter an equation above to see its interpretation.")
            return
        try:
            lhs, rhs, var = parse_equation(t)
            self.alg_preview.setText(f"Your exercise is interpreted as: {lhs} = {rhs}  (Unknown: {var})")
            self.alg_preview.setStyleSheet("color: #166534; font-size: 12px; font-weight: 500;")
        except Exception as e:
            self.alg_preview.setText(f"Interpretation pending: {e}")
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
                QMessageBox.warning(self, "Out of Scope", f"An equation of degree {deg} is outside the scope of v0.1.")
                return

            self._apply_solution(sol)
            self.plot_widget.plot_polynomial(diff, var, title=f"f({var}) = {diff}")
        except Exception as e:
            QMessageBox.warning(self, "Unable to Solve", str(e))

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
            QMessageBox.information(self, "All Hints Shown", "All steps for this exercise have already been revealed.")

    def _open_procedure_reviewer(self):
        text = self.alg_input.text().strip()
        dlg = StudentProcedureDialog(text, self)
        dlg.exec()

    # --- Geometry tab ---
    def _create_geometry_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        form_l = QHBoxLayout()
        form_l.addWidget(QLabel("Problem:"))
        self.geom_type = QComboBox()
        self.geom_type.addItems([
            "Pythagorean Theorem (a² + b² = c²)",
            "Triangle Area (A = b·h / 2)",
            "Rectangle (Area and Perimeter)",
            "Circle (Area and Circumference)"
        ])
        self.geom_type.currentIndexChanged.connect(self._on_geom_type_changed)
        form_l.addWidget(self.geom_type)

        form_l.addWidget(QLabel("Unit:"))
        self.geom_unit = QLineEdit("cm")
        self.geom_unit.setFixedWidth(50)
        form_l.addWidget(self.geom_unit)
        form_l.addStretch()
        layout.addLayout(form_l)

        # Parameter fields
        inputs_layout = QHBoxLayout()
        self.geom_lbl1 = QLabel("Leg a:")
        self.geom_val1 = QDoubleSpinBox()
        self.geom_val1.setRange(0, 10000)
        self.geom_val1.setValue(3)

        self.geom_lbl2 = QLabel("Leg b:")
        self.geom_val2 = QDoubleSpinBox()
        self.geom_val2.setRange(0, 10000)
        self.geom_val2.setValue(4)

        self.geom_lbl3 = QLabel("Hypotenuse c (0 if unknown):")
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

        btn_solve = QPushButton("Solve Geometry Step by Step")
        btn_solve.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_geometry)
        layout.addWidget(btn_solve)
        return tab

    def _on_geom_type_changed(self, idx: int):
        if idx == 0:  # Pythagorean theorem
            self.geom_lbl1.setText("Leg a:")
            self.geom_lbl2.setText("Leg b:")
            self.geom_lbl3.setText("Hypotenuse c (0 if unknown):")
            self.geom_lbl3.show()
            self.geom_val3.show()
        elif idx == 1:  # Triangle
            self.geom_lbl1.setText("Base b:")
            self.geom_lbl2.setText("Height h:")
            self.geom_lbl3.hide()
            self.geom_val3.hide()
        elif idx == 2:  # Rectangle
            self.geom_lbl1.setText("Base b:")
            self.geom_lbl2.setText("Height h:")
            self.geom_lbl3.hide()
            self.geom_val3.hide()
        elif idx == 3:  # Circle
            self.geom_lbl1.setText("Radius r:")
            self.geom_lbl2.hide()
            self.geom_val2.hide()
            self.geom_lbl3.hide()
            self.geom_val3.hide()

    def solve_geometry(self):
        idx = self.geom_type.currentIndex()
        unit = self.geom_unit.text().strip() or "cm"
        try:
            if idx == 0:  # Pythagorean theorem
                a = self.geom_val1.value() if self.geom_val1.value() > 0 else None
                b = self.geom_val2.value() if self.geom_val2.value() > 0 else None
                c = self.geom_val3.value() if self.geom_val3.value() > 0 else None
                sol = solve_pythagoras(a, b, c, unit)
            elif idx == 1:  # Triangle
                sol = solve_triangle_area(self.geom_val1.value(), self.geom_val2.value(), unit)
            elif idx == 2:  # Rectangle
                sol = solve_rectangle(self.geom_val1.value(), self.geom_val2.value(), unit)
            elif idx == 3:  # Circle
                sol = solve_circle(self.geom_val1.value(), unit)
            else:
                return

            self._apply_solution(sol)
        except Exception as e:
            QMessageBox.warning(self, "Geometry Error", str(e))

    # --- Physics tab ---
    def _create_physics_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        form_l = QHBoxLayout()
        form_l.addWidget(QLabel("Physics Model:"))
        self.phys_type = QComboBox()
        self.phys_type.addItems([
            "Uniform Motion (d = v · t)",
            "Newton's Second Law (F = m · a)",
            "Unit Conversion (km/h ⇄ m/s)"
        ])
        self.phys_type.currentIndexChanged.connect(self._on_phys_type_changed)
        form_l.addWidget(self.phys_type)
        form_l.addStretch()
        layout.addLayout(form_l)

        # Input container
        self.phys_inputs_l = QHBoxLayout()
        self.phys_lbl1 = QLabel("Distance d (m):")
        self.phys_val1 = QDoubleSpinBox()
        self.phys_val1.setRange(0, 100000)
        self.phys_val1.setValue(150)

        self.phys_lbl2 = QLabel("Speed v (m/s) [0 if unknown]:")
        self.phys_val2 = QDoubleSpinBox()
        self.phys_val2.setRange(0, 10000)
        self.phys_val2.setValue(0)

        self.phys_lbl3 = QLabel("Time t (s):")
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

        btn_solve = QPushButton("Solve Physics Step by Step")
        btn_solve.setStyleSheet("background-color: #d97706; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_solve.clicked.connect(self.solve_physics)
        layout.addWidget(btn_solve)
        return tab

    def _on_phys_type_changed(self, idx: int):
        if idx == 0:  # Uniform motion
            self.phys_lbl1.setText("Distance d (m):")
            self.phys_lbl2.setText("Speed v (m/s):")
            self.phys_lbl3.setText("Time t (s):")
            self.phys_lbl3.show()
            self.phys_val3.show()
        elif idx == 1:  # Newton
            self.phys_lbl1.setText("Force F (N) [0 if unknown]:")
            self.phys_lbl2.setText("Mass m (kg):")
            self.phys_lbl3.setText("Acceleration a (m/s²):")
            self.phys_lbl3.show()
            self.phys_val3.show()
        elif idx == 2:  # Conversion
            self.phys_lbl1.setText("Value:")
            self.phys_lbl2.setText("From (km/h):")
            self.phys_lbl3.hide()
            self.phys_val3.hide()

    def solve_physics(self):
        idx = self.phys_type.currentIndex()
        try:
            if idx == 0:  # Uniform motion
                d = self.phys_val1.value() if self.phys_val1.value() > 0 else None
                v = self.phys_val2.value() if self.phys_val2.value() > 0 else None
                t = self.phys_val3.value() if self.phys_val3.value() > 0 else None
                sol = solve_mru(d=d, v=v, t=t)
            elif idx == 1:  # Newton
                F = self.phys_val1.value() if self.phys_val1.value() > 0 else None
                m = self.phys_val2.value() if self.phys_val2.value() > 0 else None
                a = self.phys_val3.value() if self.phys_val3.value() > 0 else None
                sol = solve_newton_second_law(F=F, m=m, a=a)
            elif idx == 2:  # Conversion
                val = self.phys_val1.value()
                sol = convert_units(val, "km/h", "m/s")
            else:
                return

            self._apply_solution(sol)
        except Exception as e:
            QMessageBox.warning(self, "Physics Error", str(e))

    # --- Calculus tab ---
    def _create_calculus_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        mode_l = QHBoxLayout()
        mode_l.addWidget(QLabel("Calculus Operation:"))
        self.calc_mode = QComboBox()
        self.calc_mode.addItems(["Polynomial Derivative: d/dx [P(x)]", "Indefinite Polynomial Integral: ∫ P(x) dx"])
        mode_l.addWidget(self.calc_mode)
        mode_l.addStretch()
        layout.addLayout(mode_l)

        self.calc_input = QLineEdit("3x^2 + 2x - 5")
        self.calc_input.setPlaceholderText("Example: 3x^2 + 2x - 5  or  2x + 3")
        self.calc_input.setStyleSheet("background-color: #ffffff; color: #0f172a; font-size: 15px; padding: 7px 10px; border: 1px solid #cbd5e1; border-radius: 6px;")
        layout.addWidget(self.calc_input)

        btn_solve = QPushButton("Solve Calculus Step by Step")
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

            # Plot the original function when possible
            expr = parse_expression(text)
            symbols = list(expr.free_symbols)
            var = symbols[0] if symbols else sp.Symbol("x", real=True)
            self.plot_widget.plot_polynomial(expr, var, title=f"f({var}) = {expr}")
        except Exception as e:
            QMessageBox.warning(self, "Calculus Error", str(e))

    # --- Shared rendering ---
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
            self.answer_label.setText(f"Solution: {self.current_solution.final_answer}")
            self.check_label.setText(self.current_solution.substitution_check or self.current_solution.verification_reason)
        else:
            self.status_pill.setText(f"Hint {self.revealed_steps_count} of {len(self.current_solution.steps)}")
            self.status_pill.setStyleSheet("""
                background-color: #fef3c7;
                color: #b45309;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
            """)
            self.answer_label.setText("Guided mode in progress...")
            self.check_label.setText("Click 'Give Me a Hint' for the next step.")

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
