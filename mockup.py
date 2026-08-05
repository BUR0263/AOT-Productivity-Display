import sys
import time as t

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QApplication,
    QLabel,
    QWidget

)

def clock_system():
    return t.strftime("%H:%M:%S")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity Display")
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.show_time = QLabel()

        # Update clock every second
        self.update_clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        # add the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.show_time)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_clock(self):
        self.show_time.setText(clock_system())


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
