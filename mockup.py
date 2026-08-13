import sys
import time as t
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, Qt, QElapsedTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QWidget,
    QLineEdit, QPushButton, QGridLayout, QVBoxLayout, QTabWidget, QHBoxLayout

)

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
    def update_label(self):
        self.time_elapsed += 10
        seconds, ms = divmod(self.time_elapsed, 1000)
        self.timed.setText(f"{seconds:02d}:{ms // 10:02d}")
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.move(0, 0)
        self.setStyleSheet("""
        QLabel {
            font: 30pt, "Arial";
            }
        """)
        self.header_layout = QVBoxLayout()
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(30)
        self.layout.setVerticalSpacing(10)

        container = QWidget()
        container.setLayout(self.header_layout)
        self.setCentralWidget(container)


        self.setWindowTitle("Productivity Display")
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.time_tabs = QTabWidget()
        self.time_tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.clock_tab = QWidget()
        self.clock_layout = QHBoxLayout()
        self.clock_layout.addWidget(Clock(), alignment=Qt.AlignmentFlag.AlignCenter)
        self.clock_tab.setLayout(self.clock_layout)




        # self.stopwatch_layout = QHBoxLayout()
        # self.stopwatch_layout.addWidget(Stopwatch())
        # self.stopwatch_tab.setLayout(self.stopwatch_layout)

        self.time_tabs.addTab(self.clock_tab, "Clock")
        self.time_tabs.addTab(Stopwatch(), "Stopwatch")

        self.tempwidg = QPushButton("ABC123")

        self.new_note_button = QPushButton("Add a new note")
        self.new_note_button.clicked.connect(self.add_note)

        self.header_layout.addWidget(self.time_tabs)
        self.layout.addWidget(self.new_note_button, 0, 1)
        self.layout.addWidget(self.tempwidg, 0, 2)

        self.header_layout.addLayout(self.layout)
        self.current_note_row = 2



    def add_note(self):
        new_note = QLineEdit()
        new_note.setPlaceholderText("Type something here...")
        self.layout.addWidget(new_note, self.current_note_row, 1)

        self.current_note_row += 1


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
