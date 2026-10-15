"""
Pruebas de interfaz gráfica y flujo de usuario para MathTutor AI.
Se ejecutan en modo headless/offscreen para validación continua.
"""

import os
import pytest

# Configurar plataforma offscreen para pruebas automatizadas
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from mathtutor.storage.database import StorageManager
from mathtutor.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_init(qapp):
    storage = StorageManager(":memory:")
    window = MainWindow(storage)
    assert window.windowTitle() == "MathTutor AI — Versión 0.1"
    assert window.stack.count() == 6
    window.close()


def test_main_window_solve_linear_flow(qapp):
    storage = StorageManager(":memory:")
    window = MainWindow(storage)

    # Navegar a Resolver (índice 1)
    window.nav_list.setCurrentRow(1)
    assert window.stack.currentIndex() == 1

    # Ejecutar resolución de 2x + 3 = 11
    solver = window.view_solver
    solver.alg_input.setText("2x + 3 = 11")
    solver.solve_algebra()

    assert solver.current_solution is not None
    assert solver.current_solution.final_answer == "x = 4"
    assert "Verificado" in solver.status_pill.text()

    # Comprobar que se guardó en el historial de storage
    history = storage.get_history()
    assert len(history) >= 1
    assert history[0]["original_input"] == "2x + 3 = 11"
    assert history[0]["final_answer"] == "x = 4"

    window.close()


def test_main_window_navigation_flow(qapp):
    storage = StorageManager(":memory:")
    window = MainWindow(storage)

    # Navegar por todas las pestañas
    for i in range(6):
        window.nav_list.setCurrentRow(i)
        assert window.stack.currentIndex() == i

    window.close()
