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
import ctypes

# PyQT6 Imports
from PyQt6.QtCore import QTimer, Qt, QSize, QEvent
from PyQt6.QtGui import QFontDatabase, QIcon, QFontMetrics, QPalette, QPixmap

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
    QStyle,
)

## layouts
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QBoxLayout

# TODO: add styling for transparency and add background contrast detection to make sure stuff is readable

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

        # this adds the following ttf file font to the environment if the file exists
        QFontDatabase.addApplicationFont("LCD5X8H.TTF")
        # otherwise, it the font isn't installed to system or present at project root,
        # the css (or rather qss) will fallback to a bunch of other likely monospace fonts, ranked preferentially.

        # TODO: Add a development mode bool flag, and;
        # TODO: check transparent styling to make sure eveything is actually transparent

        # remove window frame and make window transparent (if not in dev mode)
        if not DEVELOPMENT_MODE:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # TODO: add a title bar (see commented code near bottom of file)
        # self.title_bar = CustomTitleBar(self)

        # define vertical layout
        layout = QVBoxLayout()

        # define title bar variable - won't work without it??
        self.title_bar = CustomTitleBar(self)

        # add widgets to layout
        layout.addWidget(self.title_bar, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(clock_display(), alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(notes(), alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(todos(), alignment=Qt.AlignmentFlag.AlignTop)


        # create a widget, set its layout to the main layout, and place it in the centre of the main widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    # Tells the titlebar when the window state has been changed, (minimize, maximized
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

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
        self.start_button = QPushButton()
        self.start_icon = QIcon("./icons/play.svg")
        self.stop_icon = QIcon("./icons/pause.svg")
        self.start_button.setIcon(self.start_icon)
        self.start_button.clicked.connect(self.control)

        # define the default "zero" state of the stopwatch
        self.default_timer_text = "00.00"
        self.timed = QLabel(self.default_timer_text)

        # define a restart button and connect it to the reset function
        reset_icon = QIcon("./icons/refresh.svg")
        self.restart_button = QPushButton()
        self.restart_button.setIcon(reset_icon)
        self.restart_button.clicked.connect(self.reset)

        # define button sizes
        self.start_button.setFixedSize(50, 50)
        self.restart_button.setFixedSize(50, 50)

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
            self.start_button.setIcon(self.stop_icon)
            self.is_running = True
        elif self.is_running:
            self.start_button.setIcon(self.start_icon)
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
        self.start_button.setIcon(self.start_icon)

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
        self.layout().addWidget(note(""))


class note_base(QWidget):
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

        # add to layout
        layout.addWidget(self.text_edit, 0, 0)

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


class note(note_base):
    def __init__(self, text=""):
        super().__init__(text)

        layout = QHBoxLayout()

        # add delete button
        delete_icon = QIcon("./icons/delete.svg")
        self.delete_button = QPushButton(self)
        self.delete_button.setIcon(delete_icon)
        self.delete_button.setFixedSize(QSize(20, 20))
        self.delete_button.clicked.connect(self.delete_note)

        # add note
        self.note = note_base(text="")

        # add to layout
        layout.addWidget(self.delete_button)
        layout.addWidget(self.note)

        # I dont know why but this line causes a warning when adding new notes, but commenting it out has no consequences, so...
        # the warning:
        #   QWidget::setLayout: Attempting to set QLayout "" on note "", which already has a layout

        # self.setLayout(layout)

    def delete_note(self) -> None:
        self.deleteLater()
        set_window_to_min_height()


class todos(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        new_todo_button = QPushButton()
        new_todo_button.setText("Add New Todo")
        new_todo_button.clicked.connect(self.create_new_todo)

        layout.addWidget(new_todo_button)

        self.setLayout(layout)

    def create_new_todo(self):
        self.layout().addWidget(todo())


class todo(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        # add delete button
        delete_icon = QIcon("./icons/delete.svg")
        self.delete_button = QPushButton(self)
        self.delete_button.setIcon(delete_icon)
        self.delete_button.setFixedSize(QSize(20, 20))
        self.delete_button.clicked.connect(self.delete_todo)

        # add note
        self.note = note_base(text="")

        # add check box

        self.check_box = QCheckBox(self)

        # add to layout
        layout.addWidget(self.delete_button)
        layout.addWidget(self.check_box)
        layout.addWidget(self.note)

        self.setLayout(layout)

    def delete_todo(self) -> None:
        self.deleteLater()
        set_window_to_min_height()


# Unable to get custom title bar working as of now

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # used when moving window around screen
        self.initial_pos = None

        # declaring layout for titlebar
        title_layout = QHBoxLayout(self)
        title_layout.setContentsMargins(1, 1, 1, 1)
        title_layout.setSpacing(2)

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)

        # defining a title for the window
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # defining an icon for thw window
        self.window_icon_label = QLabel()
        window_icon = QPixmap("./icons/icon.ico")
        self.window_icon_label.setContentsMargins(5, 1, 5, 1)
        self.window_icon_label.setPixmap(window_icon)
        title_layout.addWidget(self.window_icon_label)
        # if the window has a title, set the title widget to that title
        if title := parent.windowTitle():
            self.title.setText(title)
        title_layout.addWidget(self.title)

        # MINIMIZE BUTTON
        self.minimize = QToolButton(self)
        # Using QStyle's default minimise icon
        min_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton)
        self.minimize.setIcon(min_icon)
        # when clicked minimize the parent window
        self.minimize.clicked.connect(self.window().showMinimized)

        # MAXIMIZE BUTTON
        self.maximize = QToolButton(self)
        # using QStyle's default maximize icon
        max_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        self.maximize.setIcon(max_icon)
        # when clicked maximize the parent window
        self.maximize.clicked.connect(self.window().showMaximized)

        # EXIT BUTTON
        self.exit = QToolButton(self)
        # using QStyle's default close icon
        exit_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.exit.setIcon(exit_icon)
        # when clicked exit the program
        self.exit.clicked.connect(self.window().close)

        # NORMAL BUTTON
        self.normal = QToolButton(self)
        # using QStyle's default normal icon
        normal_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
        self.normal.setIcon(normal_icon)
        # when clicked return to normal state
        self.normal.clicked.connect(self.window().showNormal)
        self.normal.setVisible(False)

        # using the list of buttons we make it so it doesn't allow the buttons to take focus
        # away from other widges, sets their size and adds them to the layout
        buttons = [
            self.minimize,
            self.normal,
            self.maximize,
            self.exit,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(28, 28))
            title_layout.addWidget(button)


    # Let you mazimise the window and then return it to the set state
    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal.setVisible(True)
            self.maximize.setVisible(False)
        else:
            self.normal.setVisible(False)
            self.maximize.setVisible(True)
    # allows user to move window across screen
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()
    # resets the initial position variable so the window moves accurately
    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()

# allows custom icon to be shown in taskbar
myappid = u'AOTDisplay.2026.woah' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
if __name__ == "__main__":
    # NOTE: If you would like to force development mode, you can change this to True
    DEVELOPMENT_MODE = False
    for arg in sys.argv:
        if arg == "--development-mode" or arg == "-d":
            DEVELOPMENT_MODE = True
    # define the app
    app = QApplication([])
    # define and show window
    window = MainWindow()
    window.show()
    # execute the app
    app.exec()
