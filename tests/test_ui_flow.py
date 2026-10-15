"UI and user-flow tests for MathTutor AI.\nRuns headless/offscreen for automated validation."

import os
import pytest

# Configure the offscreen platform for automated tests
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
    assert window.windowTitle() == "MathTutor AI — Version 0.1"
    assert window.stack.count() == 6
    assert storage.get_profile().name == "Student"
    assert [window.nav_list.item(i).text().strip() for i in range(6)] == [
        "Home", "Solve", "Practice", "My Progress", "History", "Settings"
    ]
    window.close()


@pytest.mark.parametrize("old_status, expected_status", [
    ("Verificado", "Verified"),
    ("Comprobación numérica", "Numerical check"),
    ("No se pudo verificar", "Could not verify"),
    ("Fuera del alcance", "Out of scope"),
])
def test_english_views_preserve_legacy_records(qapp, tmp_path, old_status, expected_status):
    """Display legacy records in English without rewriting history or progress."""
    from mathtutor.math_engine.geometry_solver import solve_rectangle
    from mathtutor.ui.views.history_view import HistoryDetailDialog
    from PySide6.QtWidgets import QLabel

    db_path = tmp_path / "existing.db"
    original = StorageManager(db_path)
    original.update_profile_name("María")
    original.save_topic_progress("geometria", 2, 7, 6, 2, [True, False])
    solution = solve_rectangle(3, 4)
    original.save_solution(solution)
    with original._get_connection() as conn:
        conn.execute("UPDATE history SET verification_status = ?", (old_status,))

    reopened = StorageManager(db_path)
    window = MainWindow(reopened)
    try:
        window.nav_list.setCurrentRow(4)
        assert window.view_history.table.item(0, 1).text() == "Geometry"
        assert window.view_history.table.item(0, 4).text() == expected_status
        assert "Subject: Geometry" in window.view_home.act_desc.text()
        assert "Geometry" in window.view_home.rec_desc.text()
        item = reopened.get_history()[0]
        dialog = HistoryDetailDialog(item)
        try:
            labels = [label.text() for label in dialog.findChildren(QLabel)]
            assert any("Subject: Geometry" in label for label in labels)
            assert any(f"Status: {expected_status}" in label for label in labels)
        finally:
            dialog.close()
        assert item["verification_status"] == old_status
        assert item["final_answer"] == solution.final_answer
        assert reopened.get_profile().name == "María"
        progress = reopened.get_topic_progress("geometria")
        assert progress["current_level"] == 2
        assert progress["total_attempts"] == 7
        assert progress["history_window"] == [True, False]
    finally:
        window.close()


def test_main_window_solve_linear_flow(qapp):
    storage = StorageManager(":memory:")
    window = MainWindow(storage)

    # Navigate to Solve (index 1)
    window.nav_list.setCurrentRow(1)
    assert window.stack.currentIndex() == 1

    # Solve 2x + 3 = 11
    solver = window.view_solver
    solver.alg_input.setText("2x + 3 = 11")
    solver.solve_algebra()

    assert solver.current_solution is not None
    assert solver.current_solution.final_answer == "x = 4"
    assert "Verified" in solver.status_pill.text()

    # Check that the solution was saved in the history
    history = storage.get_history()
    assert len(history) >= 1
    assert history[0]["original_input"] == "2x + 3 = 11"
    assert history[0]["final_answer"] == "x = 4"

    window.close()


def test_main_window_navigation_flow(qapp):
    storage = StorageManager(":memory:")
    window = MainWindow(storage)

    # Navigate through every tab
    for i in range(6):
        window.nav_list.setCurrentRow(i)
        assert window.stack.currentIndex() == i

    window.close()
