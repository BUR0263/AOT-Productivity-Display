"""Project Details - AOT Productivity Display
--------------------------------------------------------------------------------
Authors:
    Leo Osbrough
    Luna Burrows
Date:
    2026-08-07
Description:
    An always on top productivity display to aid in the keeping track of time,
    events, todo's, and making small temporary notes before they can be moved
    to a more permanent place. With the goal of keeping people on track and
    organised.
"""

# Imports
import sys
import time as t
from typing import NoReturn

# PyQT6 Imports
from PyQt6.QtCore import QTimer, Qt, QCoreApplication, QSize
from PyQt6.QtGui import QFontDatabase, QIcon, QAction, QPalette

## widgets
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QStyle,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QWidget,
    
)

## layouts
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QBoxLayout
)


class MainWindow(QMainWindow):
    """A class representing the main window and the widgets inside"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # set the width of the window and move it to the top left
        self.setFixedWidth(400)
        self.move(0, 0)

        # set window title and icon
        self.setWindowTitle("Productivity Display")
        ## Windows is fkn weird, so this app icon doesn't show on the taskbar, I can't figure out how to make it work tho
        ## FIXME: taskbar icon doesn't show
        icon = QIcon("./icon.ico")
        self.setWindowIcon(icon)

        # set the window "Always on Top"
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # remove window frame and make window transparent
        # TODO: REMINDER: THESE LINES COMMENTED OUT FOR EASE OF DEVELOPMENT. UNCOMMENT WHEN SUBMITTING
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # add a title bar
        self.title_bar = CustomTitleBar(self)

        # define base layout
        layout = QVBoxLayout()
        # define the widgets
        widgets = [
        ]
        # add all the widgets to the layout
        for w in widgets:
            layout.addWidget(w())
            
    def minimise(self) -> None:
        self.showMinimized
            


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.layout = QHBoxLayout()
        
        exit_button = QPushButton("X", self)
        exit_button.clicked.connect(self.quit_program)
        self.layout.addWidget(exit_button)
        
        min_button = QPushButton("-", self)
        min_button.clicked.connect(parent.minimise)
        self.layout.addWidget(min_button)



    def quit_program(exit_code: int = 0) -> NoReturn:
        QApplication.quit()
        sys.exit(exit_code)


if __name__ == "__main__":
    # define the app and pass any command line arguments
    app = QApplication(sys.argv)
    # define the window from the mainwindow class and show it
    window = MainWindow()
    window.show()
    # execute the app
    app.exec()
