"""
Genera capturas visuales de alta fidelidad de la interfaz de MathTutor AI
usando la plataforma nativa de Windows para renderizado perfecto de fuentes tipográficas.
"""

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

# Captura 1: Vista Inicio
pix_home = window.grab()
pix_home.save("screenshot_home.png")

# Captura 2: Vista Resolver con ejercicio 2x + 3 = 11 resuelto
window.nav_list.setCurrentRow(1)
window.view_solver.alg_input.setText("2x + 3 = 11")
window.view_solver.solve_algebra()
app.processEvents()

pix_solver = window.grab()
pix_solver.save("screenshot_solver.png")

# Captura 3: Vista Práctica
window.nav_list.setCurrentRow(2)
app.processEvents()
pix_practice = window.grab()
pix_practice.save("screenshot_practice.png")

window.close()
print("Capturas generadas con exito con tipografia real de Windows.")
