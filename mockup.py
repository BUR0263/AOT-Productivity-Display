import sys
import time as t

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QApplication,
    QLabel,
    QWidget,
    QLineEdit, QPushButton, QGridLayout, QHBoxLayout

)

def clock_system():
    return t.strftime("%H:%M:%S")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.setWindowTitle("Productivity Display")
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.show_time = QLabel()



        # Update clock every second
        self.update_clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        # add the widgets


        self.new_note_button = QPushButton("Add a new note")
        self.new_note_button.clicked.connect(self.add_note)


        self.layout.addWidget(self.show_time, 0, 0)
        self.layout.addWidget(self.new_note_button, 0, 1)

        self.current_note_row = 1

    def update_clock(self):
        self.show_time.setText(clock_system())

    def add_note(self):
        new_note = QLineEdit()
        new_note.setPlaceholderText("Type something here...")
        self.layout.addWidget(new_note, self.current_note_row, 1)

        self.current_note_row += 1


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
