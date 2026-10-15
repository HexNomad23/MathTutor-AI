"""
Widget de visualización de gráficas de polinomios integrado en Qt mediante Matplotlib.
Incluye ejes coordenados, cuadrícula y renderizado de escala.
"""

from typing import Optional
import numpy as np
import sympy as sp
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PolynomialPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3.5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self._style_axes()

    def _style_axes(self):
        self.ax.clear()
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')
        self.ax.grid(True, which='both', linestyle='--', alpha=0.5)
        self.ax.set_title("Gráfica ilustrativa", fontsize=10, color='#475569')
        self.canvas.draw()

    def plot_polynomial(self, poly_expr: sp.Expr, var: sp.Symbol, x_min: float = -10, x_max: float = 10, title: Optional[str] = None):
        """Grafica una función polinómica f(var) en el intervalo [x_min, x_max]."""
        self.ax.clear()
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')
        self.ax.grid(True, which='both', linestyle='--', alpha=0.5)

        # Generar puntos numéricos seguros
        x_vals = np.linspace(x_min, x_max, 400)
        try:
            f = sp.lambdify(var, poly_expr, modules=['numpy'])
            y_vals = f(x_vals)
            # Manejar constantes
            if np.isscalar(y_vals):
                y_vals = np.full_like(x_vals, y_vals)

            self.ax.plot(x_vals, y_vals, label=f"y = {poly_expr}", color="#2563eb", linewidth=2)
            if title:
                self.ax.set_title(title, fontsize=10, color='#1e293b')
            else:
                self.ax.set_title(f"f({var}) = {poly_expr}", fontsize=10, color='#1e293b')
            self.ax.legend(loc="upper right", fontsize=9)
        except Exception:
            self.ax.text(0.5, 0.5, "No se pudo generar la gráfica", horizontalalignment='center', verticalalignment='center')

        self.canvas.draw()
