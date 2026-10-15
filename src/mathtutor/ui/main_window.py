"Main MathTutor AI window (PySide6 / Qt).\nUses sidebar navigation with layouts for 1366x768 and Windows display scaling."

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QLabel, QStatusBar, QFrame
)
from PySide6.QtCore import Qt, QSize, QLocale
from PySide6.QtGui import QIcon, QFont

from ..storage.database import StorageManager
from .views.home_view import HomeView
from .views.solver_view import SolverView
from .views.practice_view import PracticeView
from .views.progress_view import ProgressView
from .views.history_view import HistoryView
from .views.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self, storage: StorageManager, parent=None):
        QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("MathTutor AI — Version 0.1")
        self.resize(1366, 768)
        self.setMinimumSize(960, 640)
        self._init_ui()
        self._apply_global_styles()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Navigation sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
            }
        """)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(12, 18, 12, 14)
        side_layout.setSpacing(12)

        # Logo / brand
        brand_label = QLabel("MathTutor AI")
        brand_label.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; padding-left: 6px;")
        side_layout.addWidget(brand_label)

        ver_label = QLabel("v0.1 • Local Mode")
        ver_label.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: 600; padding-left: 6px; margin-bottom: 8px;")
        side_layout.addWidget(ver_label)

        # Navigation menu
        self.nav_list = QListWidget()
        self.nav_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #94a3b8;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 12px;
                border-radius: 6px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background-color: #1e293b;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #2563eb;
                color: #ffffff;
            }
        """)

        nav_items = [
            ("Home", "home"),
            ("Solve", "solver"),
            ("Practice", "practice"),
            ("My Progress", "progress"),
            ("History", "history"),
            ("Settings", "settings"),
        ]

        for text, tag in nav_items:
            item = QListWidgetItem(f"  {text}")
            item.setData(Qt.ItemDataRole.UserRole, tag)
            item.setSizeHint(QSize(200, 42))
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        side_layout.addWidget(self.nav_list)
        side_layout.addStretch()

        # Sidebar profile
        self.lbl_profile_sidebar = QLabel("👤 Student")
        self.lbl_profile_sidebar.setStyleSheet("color: #cbd5e1; font-size: 13px; font-weight: 600; padding: 6px;")
        side_layout.addWidget(self.lbl_profile_sidebar)

        root_layout.addWidget(sidebar)

        # Stacked view container (QStackedWidget)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f8fafc;")

        # Views
        self.view_home = HomeView(self.storage)
        self.view_home.navigate_to.connect(self._handle_home_navigation)
        self.stack.addWidget(self.view_home)  # 0

        self.view_solver = SolverView(self.storage)
        self.view_solver.request_practice.connect(self._handle_request_practice)
        self.stack.addWidget(self.view_solver)  # 1

        self.view_practice = PracticeView(self.storage)
        self.stack.addWidget(self.view_practice)  # 2

        self.view_progress = ProgressView(self.storage)
        self.stack.addWidget(self.view_progress)  # 3

        self.view_history = HistoryView(self.storage)
        self.stack.addWidget(self.view_history)  # 4

        self.view_settings = SettingsView(self.storage)
        self.view_settings.profile_updated.connect(self._on_profile_updated)
        self.stack.addWidget(self.view_settings)  # 5

        root_layout.addWidget(self.stack, stretch=1)

        # Bottom status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #f1f5f9; color: #475569; font-size: 12px; border-top: 1px solid #e2e8f0;")
        self.setStatusBar(self.status_bar)

        self._update_status_bar()
        self.nav_list.setCurrentRow(0)

    def _on_nav_changed(self, row: int):
        self.stack.setCurrentIndex(row)
        # Refresh data in views that need it
        if row == 0:
            self.view_home.refresh_data()
        elif row == 3:
            self.view_progress.refresh_stats()
        elif row == 4:
            self.view_history.load_history()

    def _handle_home_navigation(self, route: str):
        if route.startswith("resolver_"):
            subject = route.replace("resolver_", "")
            self.nav_list.setCurrentRow(1)
            # Switch to the corresponding tab
            sub_to_tab = {"algebra": 0, "geometria": 1, "fisica": 2, "calculo": 3}
            if subject in sub_to_tab:
                self.view_solver.tabs.setCurrentIndex(sub_to_tab[subject])
        else:
            self.nav_list.setCurrentRow(1)

    def _handle_request_practice(self, topic: str):
        self.nav_list.setCurrentRow(2)
        idx = self.view_practice.topic_combo.findData(topic)
        if idx >= 0:
            self.view_practice.topic_combo.setCurrentIndex(idx)

    def _on_profile_updated(self, new_name: str):
        self.lbl_profile_sidebar.setText(f"👤 {new_name}")
        self.view_home.refresh_data()
        self._update_status_bar()

    def _update_status_bar(self):
        profile = self.storage.get_profile()
        self.lbl_profile_sidebar.setText(f"👤 {profile.name}")
        self.status_bar.showMessage(f"Local mode active | Profile: {profile.name} | Ready")

    def _apply_global_styles(self):
        from PySide6.QtGui import QPalette, QColor

        # Force a light palette to keep text readable in Windows dark mode
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f1f5f9"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#f1f5f9"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("#dc2626"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563eb"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
                color: #0f172a;
            }
            QMainWindow {
                background-color: #f8fafc;
            }
            QLabel {
                color: #1e293b;
            }
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 7px 10px;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #2563eb;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 5px 8px;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
                border: 1px solid #cbd5e1;
            }
            QRadioButton {
                color: #334155;
                font-weight: 500;
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QTabBar::tab {
                font-weight: 600;
                font-size: 13px;
                padding: 8px 16px;
                color: #475569;
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                color: #1d4ed8;
                background-color: #ffffff;
                border-bottom: 2px solid #2563eb;
            }
        """)
