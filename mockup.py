import sys
import time as t
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QTabWidget,
    QHBoxLayout,
    QTextEdit, QCheckBox, QLineEdit, QStackedWidget, QSpinBox
)


# class TodoLineEdit(QLineEdit):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#     def enterEvent(self, event):
#         font_metrics = QFontMetrics(self.font())
#         text_width = font_metrics.horizontalAdvance(self.text())
#
#         visible_width = self.rect().width() - 8
#
#         if text_width > visible_width:
#             self.setToolTip(self.text())
#         else:
#             self.setToolTip("")
class NoteTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(45, 45, 45, 0.2)")

    def focusOutEvent(self, e):
        self.setStyleSheet("background-color: rgba(45, 45, 45, 0.2)")
    def focusInEvent(self, e):
        self.setStyleSheet("background-color: rgba(45, 45, 45, 1)")
# class TimerWindow(QWidget):
#     def __init__(self):
#         super.__init__()
#         pass

class Clock(QLabel):
    def __init__(self):
        super().__init__()
        self.update_clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def update_clock(self):
            self.setText(self.clock_system())

    def clock_system(self):
        return t.strftime("%H:%M:%S")
class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(20)
        self.is_running = False

        self.time_elapsed = 0
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_label)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.control)

        self.timed = QLabel("00:00")

        self.restart_button = QPushButton("Reset")
        self.restart_button.clicked.connect(self.reset)

        self.start_button.setMaximumSize(50, 50)
        self.restart_button.setMaximumSize(50, 50)

        layout.addWidget(self.start_button)
        layout.addWidget(self.timed, alignment=Qt.AlignmentFlag.AlignCenter, stretch=2)
        layout.addWidget(self.restart_button, 1)

        self.setLayout(layout)
    def control(self):
        if not self.is_running:
            self.timer.start()
            self.start_button.setText("Stop")
            self.is_running = True
        elif self.is_running:
            self.timer.stop()
            self.start_button.setText("Start")
            self.is_running = False
    def reset(self):
        self.time_elapsed = 0
        self.timed.setText("00:00")
        self.timer.stop()
        self.is_running = False
        self.start_button.setText("Start")
    def update_label(self):
        self.time_elapsed += 10
        seconds, ms = divmod(self.time_elapsed, 1000)
        self.timed.setText(f"{seconds:02d}:{ms // 10:02d}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(400)
        self.move(0, 0)
        self.setStyleSheet("""
        QLabel {
            font: 30pt, "Arial";
            }
        """)
        self.header_layout = QVBoxLayout()
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(10)

        self.todo_layout = QGridLayout()
        self.todo_layout.setVerticalSpacing(10)
        self.todo_layout.setHorizontalSpacing(10)
        container = QWidget()
        container.setLayout(self.header_layout)
        self.setCentralWidget(container)


        self.setWindowTitle("Productivity Display")
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # REMINDER: THESE LINES COMMENTED OUT FOR EASE OF DEVELOPMENT. UNCOMMENT WHEN SUBMITTING
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.time_tabs = QTabWidget()
        self.time_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.time_tabs.setMaximumHeight(100)

        self.clock_tab = QWidget()
        self.clock_layout = QHBoxLayout()
        self.clock_layout.addWidget(Clock(), alignment=Qt.AlignmentFlag.AlignCenter)
        self.clock_tab.setLayout(self.clock_layout)

        self.time_tabs.addTab(self.clock_tab, "Clock")
        self.time_tabs.addTab(Stopwatch(), "Stopwatch")
        # self.time_tabs.addTab(TimerWindow(), "Timer")

        self.todo_column = QPushButton("Add To-Do")
        self.todo_column.clicked.connect(self.add_todo)

        self.new_note_button = QPushButton("Add a new note")
        self.new_note_button.clicked.connect(self.add_note)

        self.header_layout.addWidget(self.time_tabs)
        self.layout.addWidget(self.new_note_button, 0, 0)
        self.layout.addWidget(self.todo_column, 0, 1)

        self.header_layout.addLayout(self.layout)
        self.layout.addLayout(self.todo_layout, 1, 1, -1, 1)

        self.current_note_row = 1
        self.current_todo_row = 0


    def add_note(self):
        new_note = NoteTextEdit()
        new_note.setPlaceholderText("Type something here...")
        self.layout.addWidget(new_note, self.current_note_row, 0)

        self.current_note_row += 1

    def add_todo(self):
        new_checkbox = QCheckBox()
        new_line = NoteTextEdit()
        self.todo_layout.addWidget(new_checkbox, self.current_todo_row, 0)

        self.todo_layout.addWidget(new_line, self.current_todo_row, 1)
        self.current_todo_row += 1
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
