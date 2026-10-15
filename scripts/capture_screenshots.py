"""Capture the MathTutor AI interface using native Windows font rendering."""

from PySide6.QtWidgets import QApplication
from mathtutor.storage.database import StorageManager
from mathtutor.ui.main_window import MainWindow

app = QApplication.instance()
if app is None:
    app = QApplication([])

storage = StorageManager(":memory:")
window = MainWindow(storage)
window.show()
app.processEvents()

# Screenshot 1: Home view
pix_home = window.grab()
pix_home.save("screenshot_home.png")

# Screenshot 2: Solver view with 2x + 3 = 11 solved
window.nav_list.setCurrentRow(1)
window.view_solver.alg_input.setText("2x + 3 = 11")
window.view_solver.solve_algebra()
app.processEvents()

pix_solver = window.grab()
pix_solver.save("screenshot_solver.png")

# Screenshot 3: Practice view
window.nav_list.setCurrentRow(2)
app.processEvents()
pix_practice = window.grab()
pix_practice.save("screenshot_practice.png")

window.close()
print("Screenshots generated successfully using native Windows font rendering.")
