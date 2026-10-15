"""
Vista de Historial de Actividades (HistoryView).
Permite ver resoluciones anteriores, inspeccionar pasos guardados y eliminar registros con confirmación.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from ...storage.database import StorageManager
from ..widgets.step_card import StepCardWidget


class HistoryDetailDialog(QDialog):
    """Muestra el detalle completo de un ejercicio del historial."""
    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Ejercicio - {item['original_input']}")
        self.setMinimumSize(600, 500)
        self.item = item
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel(f"Materia: {self.item['subject'].capitalize()} | {self.item['original_input']}")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(header)

        status_lbl = QLabel(f"Estado: {self.item['verification_status']} — {self.item['final_answer']}")
        status_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #059669;")
        layout.addWidget(status_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setSpacing(8)

        for step in self.item.get("steps", []):
            card = StepCardWidget(step, is_detailed=True)
            c_layout.addWidget(card)

        c_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        if self.item.get("substitution_check"):
            chk_box = QLabel(f"Comprobación:\n{self.item['substitution_check']}")
            chk_box.setStyleSheet("background-color: #f1f5f9; padding: 8px; border-radius: 4px; font-size: 12px;")
            chk_box.setWordWrap(True)
            layout.addWidget(chk_box)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class HistoryView(QWidget):
    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title = QLabel("Historial de ejercicios")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.btn_refresh = QPushButton("Actualizar")
        self.btn_refresh.clicked.connect(self.load_history)
        header_layout.addWidget(self.btn_refresh)

        self.btn_clear = QPushButton("Borrar todo")
        self.btn_clear.setStyleSheet("background-color: #fee2e2; color: #b91c1c; font-weight: bold;")
        self.btn_clear.clicked.connect(self._clear_all)
        header_layout.addWidget(self.btn_clear)

        layout.addLayout(header_layout)

        # Tabla de historial
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Fecha", "Materia", "Ejercicio", "Resultado", "Estado", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                gridline-color: #f1f5f9;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                font-weight: bold;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #cbd5e1;
            }
        """)
        layout.addWidget(self.table)

        self.load_history()

    def load_history(self):
        items = self.storage.get_history(limit=100)
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["created_at"])[:19]))
            self.table.setItem(row, 1, QTableWidgetItem(item["subject"].capitalize()))
            self.table.setItem(row, 2, QTableWidgetItem(item["original_input"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["final_answer"]))
            self.table.setItem(row, 4, QTableWidgetItem(item["verification_status"]))

            # Acciones
            action_widget = QWidget()
            a_layout = QHBoxLayout(action_widget)
            a_layout.setContentsMargins(2, 2, 2, 2)
            a_layout.setSpacing(4)

            view_btn = QPushButton("Ver")
            view_btn.setStyleSheet("padding: 2px 8px; font-size: 11px;")
            view_btn.clicked.connect(lambda ch, it=item: self._view_detail(it))
            a_layout.addWidget(view_btn)

            del_btn = QPushButton("Eliminar")
            del_btn.setStyleSheet("padding: 2px 8px; font-size: 11px; color: #dc2626;")
            del_btn.clicked.connect(lambda ch, hid=item["id"]: self._delete_item(hid))
            a_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def _view_detail(self, item: dict):
        dlg = HistoryDetailDialog(item, self)
        dlg.exec()

    def _delete_item(self, history_id: str):
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este ejercicio del historial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.delete_history_item(history_id)
            self.load_history()

    def _clear_all(self):
        reply = QMessageBox.question(
            self,
            "Confirmar borrado completo",
            "¿Deseas vaciar todo el historial de ejercicios?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.clear_history()
            self.load_history()
