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
import json
from typing import NoReturn

# PyQT6 Imports
from PyQt6.QtCore import QTimer, Qt, QCoreApplication, QSize
from PyQt6.QtGui import QFontDatabase, QIcon, QAction, QPalette, QFontMetrics

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
    QPlainTextEdit,
)

## layouts
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QBoxLayout


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
        icon = QIcon("./icons/icon.ico")
        self.setWindowIcon(icon)

        # set the window "Always on Top"
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # TODO: Add a development mode bool flag, and;
        # TODO: check transparent styling to make sure eveything is actually transparent
        
        # remove window frame and make window transparent
        # TODO: REMINDER: THESE LINES COMMENTED OUT FOR EASE OF DEVELOPMENT. UNCOMMENT WHEN SUBMITTING
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # TODO: add a title bar (see commented code near bottom of file)
        # self.title_bar = CustomTitleBar(self)

        # define vertical layout
        layout = QVBoxLayout()

        # add widgets to layout
        layout.addWidget(clock_display(), alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(notes(), alignment=Qt.AlignmentFlag.AlignTop)

        # create a widget, set its layout to the main layout, and place it in the centre of the main widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


def set_window_to_min_height() -> None:
    """A function that when called sets the window,
    assuming it exists as a global variable named "window",
    to it's minimum height and returns None
    """
    if "window" in globals() and type(window) == MainWindow:
        # set max height to an arbitrarily large number, in this case, the max value allowed without errors
        # we do to practically "unset" the max height before measuring the min,
        # because if min wants to be larger than max, but max is set, the min height will be as large as
        # possible without exceeding the max, and thus measuring it won't yield anything useful
        window.setMaximumHeight(16777215)
        window.setMaximumHeight(window.minimumHeight())
        # FIXME: window height and widget position is glitchy
        # whenever a note is deleted, we call this function to resize the window, but for some reason,
        # it doesn't resize to the minimum like we'd like it to, which causes problems.


class clock_display(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        self.time_tabs = QTabWidget()
        self.time_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.time_tabs.setFixedHeight(100)

        self.time_tabs.addTab(Clock(), "Clock")
        self.time_tabs.addTab(Stopwatch(), "Stopwatch")

        layout.addWidget(self.time_tabs)


class Clock(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.setStyleSheet("""
        Clock {
            font-size: 30pt;
            font-family: LCD5x8H, Consolas, "Cascadia Code", "Cascadia Mono", Inconsolata, "Lucida Console", "Courier New", Courier, monospace;
            }
        """)

    def update_clock(self) -> None:
        """Updates the clock"""
        self.setText(self.clock_system())

    def clock_system(self) -> str:
        """Returns the current time in a user friendly format as a string"""
        # pythons time module "string formatted time" which returns the current time using the specified format
        # <hours>:<minutes>:<seconds>
        return t.strftime("%H:%M:%S")


class Stopwatch(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(20)
        self.is_running = False

        # define a bunch of variables and set them all to 0
        (
            self.ms,
            self.current_secs,
            self.start_secs,
            self.last_secs,
            self.offset_secs,
            self.elapsed_secs,
            self.last_offset_secs,
        ) = (0, 0, 0, 0, 0, 0, 0)

        # Every 10ms update the stopwatch display
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_label)

        # Define a start/stop button for the stopwatch, and connect it to the control function
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.control)

        # define the default "zero" state of the stopwatch
        self.default_timer_text = "00.00"
        self.timed = QLabel(self.default_timer_text)

        # define a restart button and connect it to the reset function
        self.restart_button = QPushButton("Reset")
        self.restart_button.clicked.connect(self.reset)

        # define button sizes
        self.start_button.setMaximumSize(50, 50)
        self.restart_button.setMaximumSize(50, 50)

        # add the widgets
        layout.addWidget(self.start_button)
        layout.addWidget(self.timed, alignment=Qt.AlignmentFlag.AlignCenter, stretch=2)
        layout.addWidget(self.restart_button, 1)

        self.setStyleSheet("""
        QLabel {
            font-size: 30pt;
            font-family: LCD5x8H, Consolas, "Cascadia Code", "Cascadia Mono", Inconsolata, "Lucida Console", "Courier New", Courier, monospace;
            }
        """)

        self.setLayout(layout)

    def control(self) -> None:
        """Stops the stopwatch if it's running, starts it if it's not"""
        if not self.is_running:
            if self.start_secs == 0:
                # if start secs is zero, this function is being called after resetting the stopwatch, and we should define the start time
                # if we didn't do this conditionally, pausing and playing the timer (which calls this function where start secs is already defined) would reset it
                self.start_secs = int(t.time())
            self.timer.start()
            self.start_button.setText("Stop")
            self.is_running = True
        elif self.is_running:
            self.start_button.setText("Start")
            self.is_running = False

    def reset(self) -> None:
        # reset all the dependent variables
        (
            self.ms,
            self.current_secs,
            self.start_secs,
            self.last_secs,
            self.offset_secs,
            self.elapsed_secs,
            self.last_offset_secs,
        ) = (0, 0, 0, 0, 0, 0, 0)

        # reset the stopwatch display
        self.timed.setText(self.default_timer_text)
        self.timer.stop()
        self.is_running = False
        self.start_button.setText("Start")

    def update_label(self) -> None:
        # this is the core timer logic
        # the logic works by defining when we started the timer as seconds since epoch,
        # and then comparing that to what time it is now, finding the difference,
        # and then converting that time delta from seconds to hours, minutes, and seconds.
        # we get milliseconds by realising that this function is called every 10ms,
        # so we can count every time this function is called.
        # playing and pausing is handled by, when the stopwatch is paused,
        # counting how long its been paused along with how long its been active
        # and then we can find out what time to display by subtracting time spent paused from time active.

        # we do all this instead of just counting up every 10ms, as the time between cycles is
        # the 10ms spent sleeping plus however long this logic takes, which might be up to a ms or 2.
        # because of this, little inaccuracies build up and we get a slow stopwatch.
        # we can't just sleep 9ms and count on 1ms of logic, as this logic will run faster or slower on different machines.

        # this function called every 10ms, so add 10 to ms every 10(ish)ms

        # FIXME: flawed stopwatch logic.
        # stopwatch logic is flawed it forces itself to be in sync with system seconds. The ideal logic would be as follows.
        # wait 10ms, advance the stopwatch by 10ms, while doing this measure how long it actually took to do that,
        # and then adjust the next period to take that into account that difference.
        # Ie if waiting 10 ms and advancing the timer actually took 10.5ms,
        # the next period should wait for 2*10-10.5 or 9.5ms to account for that disparity.
        #   (desired time - time difference)
        #   (desired time - (actual time - desired time))
        # simplifies to:
        #   (2 * desired time - actual time)

        self.ms = (self.ms + 10) % 1000

        # find out what time were currently at
        self.current_secs = int(t.time())

        # if the timer isn't running (is paused), count the running total of how long it's spent paused
        if not self.is_running:
            self.offset_secs = (
                self.current_secs
                - self.elapsed_secs
                - self.start_secs
                + self.last_offset_secs
            )
        else:
            # we have to keep track of the running total of time spent paused, thus this logic
            self.last_offset_secs = self.offset_secs

            # elapsed time equals what time since epoch we're currently at minus when we started
            self.elapsed_secs = self.current_secs - self.start_secs

        # take into account the offset given by the stopwatch being paused, and modulo 60 to convert say 100s to 40s and 1m
        secs = (self.elapsed_secs - self.offset_secs) % 60

        # remove any compounding inaccuracy in ms by setting ms to 0 at every change in number of seconds
        if self.last_secs != secs:
            self.ms = 0

        self.last_secs = secs

        # 60 seconds in a minute, taking into account offset, modulo 60 to get minutes and hours
        mins = ((self.elapsed_secs - self.offset_secs) // 60) % 60
        # 3600 seconds in an hour, taking into account offset,
        # no modulo as we dont have logic for days, so seeing values >23 hrs is fine
        hours = (self.elapsed_secs - self.offset_secs) // 3600

        # only update stopwatch if it's running
        if self.is_running:
            self.timed.setText(self.create_stopwatch_string(hours, mins, secs, self.ms))

    def create_stopwatch_string(self, h: int, m: int, s: int, ms: int) -> str:
        """takes 4 ints; hours, minutes, seconds, and milliseconds, and formats them into an appropriate string for display

        Args:
            h (int): Hours
            m (int): Minutes
            s (int): Seconds
            ms (int): Milliseconds

        Returns:
            str: A user friendly formatted string
        """
        hours = False
        string = ""
        if h:
            string += f"{h}:"
            hours = True
        if m:
            # if there are hours, use trailing zeros on seconds
            if hours:
                string += f"{m:02d}:"
            else:
                string += f"{m}:"
        # remove ms to make room for hours
        if hours:
            string += f"{s:02d}"
        else:
            string += f"{s:02d}.{(ms // 10):02d}"

        return string


# TODO: add note and todo saving, and save loading at start up


class notes(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        new_note_button = QPushButton()
        new_note_button.setText("Add New Note")
        new_note_button.clicked.connect(self.create_new_note)

        layout.addWidget(new_note_button)

        self.setLayout(layout)

    def create_new_note(self):
        self.layout().addWidget(note())


class note(QWidget):
    def __init__(self, text: str = "") -> None:
        super().__init__()

        layout = QGridLayout()

        self.text_edit = QTextEdit()
        self.text = text

        self.text_edit.setText(self.text)
        self.text_edit.setPlaceholderText("Start typing here...")

        # update the note without saving
        self.text = self.text_edit.toPlainText()

        ## define the font used, this must be changed if we use a different font
        font = self.text_edit.document().defaultFont()
        ## get details on that font
        fontMetrics = QFontMetrics(font)
        textSize = fontMetrics.size(0, self.text)

        ## this constant (+ c) may need to be tweaked to define the size of one line
        textHeight = textSize.height() + 34

        ## set the widget and then the window to their minimum heights
        self.setFixedHeight(textHeight)
        set_window_to_min_height()

        # connect text changes to note update function
        self.text_edit.textChanged.connect(self.update_note)

        # add delete button
        delete_icon = QIcon("./icons/delete.svg")
        self.delete_button = QPushButton()
        self.delete_button.setIcon(delete_icon)
        self.delete_button.setFixedSize(QSize(20, 20))
        self.delete_button.clicked.connect(self.delete_note)

        # add everything to layout
        layout.addWidget(self.delete_button, 0, 0)
        layout.addWidget(self.text_edit, 0, 1)

        self.setLayout(layout)

    def update_note(self) -> None:
        # get the text content of the widget
        self.text = self.text_edit.toPlainText()

        # define the font used, this must be changed if we use a different font
        font = self.text_edit.document().defaultFont()
        # get details on that font
        fontMetrics = QFontMetrics(font)
        textSize = fontMetrics.size(0, self.text)

        # this constant (+ c) may need to be tweaked to define the size of one line
        textHeight = textSize.height() + 34

        # set the widget and then the window to their minimum heights
        self.setFixedHeight(textHeight)
        set_window_to_min_height()

    def delete_note(self) -> None:
        self.deleteLater()
        set_window_to_min_height()


class todos:
    pass


class todo:
    pass


# Unable to get custom title bar working as of now

# class CustomTitleBar(QWidget):
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.layout = QHBoxLayout()

#         exit_button = QPushButton("X", self)
#         exit_button.clicked.connect(self.quit_program)
#         self.layout.addWidget(exit_button)

#         min_button = QPushButton("-", self)
#         min_button.clicked.connect(parent.minimise)
#         self.layout.addWidget(min_button)

#     def quit_program(exit_code: int = 0) -> NoReturn:
#         QApplication.quit()
#         sys.exit(exit_code)


if __name__ == "__main__":
    # define the app and pass any command line arguments
    app = QApplication(sys.argv)
    # define and show window
    window = MainWindow()
    window.show()
    # execute the app
    app.exec()
