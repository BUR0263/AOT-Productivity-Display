import sys
import time as t
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFontDatabase
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
    QTextEdit,
    QCheckBox,
)

note_list = []
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
class RemoveButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("color: red")
        self.setText("X")
        self.setMaximumWidth(20)


class NoteTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(45, 45, 45, 0.2)")

    def focusOutEvent(self, e):
        self.setStyleSheet("background-color: rgba(45, 45, 45, 0.2)")

    def focusInEvent(self, e):
        self.setStyleSheet("background-color: rgba(45, 45, 45, 1)")

class Clock(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.update_clock()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def update_clock(self) -> None:
        """Updates the clock"""
        self.setText(self.clock_system())

    def clock_system(self) -> str:
        """Returns the current time in a user friendly format as a string"""
        # pythons time module "string formatted time" which returns the current time using the specified format
        # <hours>:<minutes>:<seconds>
        return t.strftime("%H:%M:%S")


def create_stopwatch_string(h: int, m: int, s: int, ms: int) -> str:
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
            self.timed.setText(create_stopwatch_string(hours, mins, secs, self.ms))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(400)
        self.move(0, 0)
        # this adds the following ttf file font to the environment if the file exists
        QFontDatabase.addApplicationFont("LCD5X8H.TTF")
        # otherwise, it the font isn't installed to system or present at project root,
        # this css will fallback to a bunch of other likely monospace fonts, ranked preferentially.
        self.setStyleSheet("""
        Stopwatch QLabel, Clock {
            font-size: 30pt;
            font-family: LCD5x8H, Consolas, "Cascadia Code", "Cascadia Mono", Inconsolata, "Lucida Console", "Courier New", Courier, monospace;
            }
        """)
        # header_layout holds the clock tabs and layouts and holds the note functions fixed underneath
        self.header_layout = QVBoxLayout()
        # this layout holds two other layouts underneath the two 'add' buttons to give flexibility to the overall look of the program
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(10)

        self.todo_layout = QGridLayout()
        self.todo_layout.setVerticalSpacing(10)
        self.todo_layout.setHorizontalSpacing(10)

        self.note_layout = QGridLayout()
        self.note_layout.setVerticalSpacing(10)
        self.note_layout.setHorizontalSpacing(10)

        container = QWidget()
        container.setLayout(self.header_layout)
        self.setCentralWidget(container)

        self.setWindowTitle("Productivity Display")
        # Windows is fkn weird, so this app icon doesn't show on the taskbar, I can't figure out how to make it work
        icon = QtGui.QIcon("./icon.ico")
        self.setWindowIcon(icon)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        #  NOTE: THESE LINES COMMENTED OUT FOR EASE OF DEVELOPMENT. UNCOMMENT WHEN SUBMITTING
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

        self.add_todo_button = QPushButton("Add To-Do")
        self.add_todo_button.clicked.connect(self.add_todo)

        self.new_note_button = QPushButton("Add a new note")
        self.new_note_button.clicked.connect(self.add_note)

        self.header_layout.addWidget(self.time_tabs)
        self.layout.addWidget(self.new_note_button, 0, 0)
        self.layout.addWidget(self.add_todo_button, 0, 1)

        self.header_layout.addLayout(self.layout)
        self.layout.addLayout(self.todo_layout, 1, 1, -1, 1)
        self.layout.addLayout(self.note_layout, 1, 0, -1, 1)

        self.current_note_row = 0
        self.current_todo_row = 0
    
    def add_note(self) -> None:
        new_note = NoteTextEdit()
        new_note.setPlaceholderText("Type something here...")

        remove_button = RemoveButton()
        remove_button.clicked.connect(self.remove_note)
        self.note_layout.addWidget(new_note, self.current_note_row, 1)
        self.note_layout.addWidget(remove_button, self.current_note_row, 0)

        note_list.append(remove_button)
        note_list.append(new_note)
        self.current_note_row += 1

    def add_todo(self) -> None:
        new_checkbox = QCheckBox()
        new_line = NoteTextEdit()
        self.todo_layout.addWidget(new_checkbox, self.current_todo_row, 0)

        self.todo_layout.addWidget(new_line, self.current_todo_row, 1)
        self.current_todo_row += 1

    def remove_note(self) -> None:
        button_pressed = self.sender()
        index = self.note_layout.indexOf(button_pressed)
        row, _, _, _ = self.note_layout.getItemPosition(index)

        for i in reversed(range(self.note_layout.count())):
            r, _, _, _ = self.layout.getItemPosition(i)
            if r == row:
                item = self.note_layout.takeAt(i)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.current_note_row -= 1
        print(row)
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
