"Main entry point for MathTutor AI.\nSupports module execution (-m mathtutor.main) and PyInstaller executables."

import sys
import os
from pathlib import Path

# Ensure the src or package directory is on sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

try:
    from mathtutor.storage.database import StorageManager
    from mathtutor.ui.main_window import MainWindow
except ImportError:
    from storage.database import StorageManager
    from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MathTutor AI")
    app.setOrganizationName("MathTutor")

    storage = StorageManager()
    window = MainWindow(storage)
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
