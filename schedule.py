import sys
import re
import os
import datetime
from pathlib import Path
from enum import Enum
from math import ceil

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QColorDialog,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QProcess

import typing as T
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class WeekdayEnum(Enum):
    mon = 0
    tue = 1
    wed = 2
    thu = 3
    fri = 4
    sat = 5
    sun = 6
    пн = 0
    вт = 1
    ср = 2
    чт = 3
    пт = 4
    сб = 5
    вс = 6
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6


class Event:
    def __init__(self, title: str, day: WeekdayEnum, start: datetime.time, end: datetime.time, color: str):
        self.title = title
        self.day = day
        self.start = start
        self.end = end
        self.color = color

    @staticmethod
    def get_enum_from_str(v):
        if isinstance(v, str):
            v_lower = v.strip().lower()
            if v_lower in WeekdayEnum.__members__:
                return WeekdayEnum[v_lower]
            else:
                raise ValueError("Day must be one of: Mon, Tue, Wed, Thu, Fri, Sat, Sun")
        return v

    @staticmethod
    def get_start_time(v):
        if isinstance(v, str) and len(v.split("-")) == 2:
            return datetime.datetime.strptime(v.split("-")[0].strip(), "%H:%M").time()
        return v

    @staticmethod
    def get_end_time(v):
        if isinstance(v, str) and len(v.split("-")) == 2:
            return datetime.datetime.strptime(v.split("-")[1].strip(), "%H:%M").time()
        return v

    @staticmethod
    def ends_after_start(v, values, **kwargs):
        if "start" in values and values["start"] >= v:
            raise ValueError("Event must end after it starts")
        return v

    @staticmethod
    def validate_color(v):
        try:
            # Convert any valid color format to RGBA tuple
            rgba = mcolors.to_rgba(v)
            # Return the hex representation of the RGBA tuple
            return mcolors.to_hex(rgba)
        except ValueError:
            # If the conversion fails, raise a custom error message
            raise ValueError("Invalid color format. Please provide a valid hex or CSS color name.")
        return v


def parse_txt(in_path: Path) -> list[Event]:
    with open(in_path) as f:
        lines = f.readlines()

    events = []

    for line in lines:
        try:
            parts = line.strip().split(", ")
            title = parts[0]
            day = WeekdayEnum[parts[1].lower()]
            start, end = parts[2].split(" - ")
            color = parts[3]
            event = Event(
                title=title,
                day=day,
                start=datetime.datetime.strptime(start, "%H:%M").time(),
                end=datetime.datetime.strptime(end, "%H:%M").time(),
                color=color,
            )
            events.append(event)
        except (ValueError, KeyError):
            continue

    return events


def time_to_hours(time: datetime.time) -> float:
    return time.hour + time.minute / 60


def plot_events(
    events: list[Event],
    show: bool,
    with_weekends: bool,
    save_img: bool,
    out_path: T.Optional[Path] = None,
):
    """
    Generate the schedule as a matplotlib plot.
    """
    if save_img and out_path is None:
        raise ValueError("Attempted to save image, but no output path was given.")

    fig = plt.figure(figsize=(18, 9))

    for event in events:
        min_x = event.day.value + 0.5
        max_x = min_x + 0.96

        min_y = time_to_hours(event.start)
        max_y = time_to_hours(event.end)

        plt.fill_between(
            [min_x, max_x], [min_y, min_y], [max_y, max_y], color=event.color
        )
        plt.text(
            min_x + 0.02,
            min_y + 0.02,
            f"{event.start.strftime('%H:%M')} - {event.end.strftime('%H:%M')}",
            va="top",
            fontsize=8,
        )

        plt.text(
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            event.title,
            ha="center",
            va="center",
            fontsize=10,
        )

    plt.title("Weekly Schedule", y=1, fontsize=14)

    [ax] = fig.axes

    days = [day.name.title() for day in WeekdayEnum if with_weekends or day.value < 5]

    ax.set_xlim(0.5, len(days) + 0.5)
    ax.set_xticks(range(1, len(days) + 1))
    ax.set_xticklabels(days)

    earliest = min(time_to_hours(event.start) for event in events)
    latest = max(time_to_hours(event.end) for event in events)

    earliest = ceil(earliest)
    latest = ceil(latest)

    ax.set_ylim(latest, earliest)
    ax.set_yticks(range(earliest, latest))
    ax.set_yticklabels([f"{h}:00" for h in range(earliest, latest)])

    ax.grid(axis="y", linestyle="--", linewidth=0.5)

    if save_img:
        plt.savefig(
            out_path,
            dpi=200,
            bbox_inches="tight",
        )

    if show:
        plt.show()


class WeeklyScheduleGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weekly Schedule Generator")

        # Create labels
        task_label = QLabel("Task:")
        day_label = QLabel("Day of the Week:")
        start_time_label = QLabel("Start Time:")
        end_time_label = QLabel("End Time:")
        color_label = QLabel("Color:")

        # Create input fields
        self.task_input = QLineEdit()
        self.day_input = QComboBox()
        self.day_input.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.start_time_input = QLineEdit()
        self.end_time_input = QLineEdit()

        # Create color picker button
        self.color_button = QPushButton("Pick Color")
        self.color_button.clicked.connect(self.pick_color)

        # Create buttons
        add_task_button = QPushButton("Add Task")
        render_button = QPushButton("Render")

        # Create task list
        self.task_list = QListWidget()
        self.task_list.itemClicked.connect(self.select_task)

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(task_label)
        layout.addWidget(self.task_input)
        layout.addWidget(day_label)
        layout.addWidget(self.day_input)
        layout.addWidget(start_time_label)
        layout.addWidget(self.start_time_input)
        layout.addWidget(end_time_label)
        layout.addWidget(self.end_time_input)
        layout.addWidget(color_label)
        layout.addWidget(self.color_button)
        layout.addWidget(add_task_button)
        layout.addWidget(self.task_list)
        layout.addWidget(render_button)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect button signals to functions
        add_task_button.clicked.connect(self.add_task)
        render_button.clicked.connect(self.render_schedule)

        # Connect returnPressed signal of input fields to add_task function
        self.task_input.returnPressed.connect(self.add_task)
        self.start_time_input.returnPressed.connect(self.add_task)
        self.end_time_input.returnPressed.connect(self.add_task)

        # Initialize tasks list
        self.tasks = []
        self.selected_task = None

        # Import the task list from a file argument or a file dialog
        self.import_task_list()

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()};")

    def add_task(self):
        task = self.task_input.text()
        day = self.day_input.currentText()
        start_time = self.convert_time_input(self.start_time_input.text())
        end_time = self.convert_time_input(self.end_time_input.text())
        color = self.color_button.palette().button().color().name()

        if not self.is_valid_time(start_time) or not self.is_valid_time(end_time):
            QMessageBox.critical(self, "Invalid Time", "Please enter a valid time in the format HH:mm.")
            return

        if not self.is_valid_time_range(start_time, end_time):
            QMessageBox.critical(self, "Invalid Time Range", "The end time must be later than the start time.")
            return

        if self.selected_task is not None:
            # Edit the selected task
            self.selected_task.setText(f"{task}, {day}, {start_time} - {end_time}, {color}")
            self.selected_task = None
        else:
            # Create a new task item
            task_item = QListWidgetItem(f"{task}, {day}, {start_time} - {end_time}, {color}")
            self.task_list.addItem(task_item)

        # Clear the input fields
        self.task_input.clear()
        self.start_time_input.clear()
        self.end_time_input.clear()

    def select_task(self, item):
        self.selected_task = item
        task_text = item.text()
        task_info = re.split(r",\s*", task_text)
        task = task_info[0]
        day = task_info[1]
        time_range = task_info[2].split(" - ")
        start_time = time_range[0]
        end_time = time_range[1]
        color = task_info[3]

        # Set the selected task details in the input fields
        self.task_input.setText(task)
        self.day_input.setCurrentText(day)
        self.start_time_input.setText(start_time)
        self.end_time_input.setText(end_time)
        self.color_button.setStyleSheet(f"background-color: {color};")

    def convert_time_input(self, time_input):
        # Remove non-digit characters
        time_input = re.sub(r"\D", "", time_input)

        # Check if the input is empty
        if not time_input:
            return ""

        # Pad the input with zeros if necessary
        if len(time_input) < 4:
            time_input = time_input.zfill(4)

        # Extract hours and minutes
        hours = time_input[:2]
        minutes = time_input[2:]

        # Format the time as "HH:mm"
        return f"{hours}:{minutes}"

    def is_valid_time(self, time):
        return re.match(r"\d{2}:\d{2}", time) is not None

    def is_valid_time_range(self, start_time, end_time):
        return start_time < end_time

    def render_schedule(self):
        input_file_content = self.generate_input_file()
        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file_path = f"outputs/{current_datetime}.txt"
        png_file_path = f"outputs/{current_datetime}.png"

        # Create the "outputs" directory if it doesn't exist
        if not os.path.exists("outputs"):
            os.makedirs("outputs")

        with open(temp_file_path, "w") as file:
            file.write(input_file_content)

        events = parse_txt(Path(temp_file_path))

        plot_events(
            events,
            with_weekends=True,
            show=False,
            save_img=True,
            out_path=Path(png_file_path),
        )

        self.open_png_file(png_file_path)

    def open_png_file(self, file_path):
        if sys.platform == "darwin":  # macOS
            os.system(f"open {file_path}")
        elif sys.platform == "win32":  # Windows
            os.system(f"start {file_path}")
        else:  # Linux
            os.system(f"xdg-open {file_path}")

    def generate_input_file(self):
        input_file_content = ""
        for i in range(self.task_list.count()):
            task_text = self.task_list.item(i).text()
            input_file_content += f"{task_text}\n"
        return input_file_content

    def import_task_list(self):
        # Check if there is a file argument passed to the program
        if len(sys.argv) > 1:
            # Read the task list from the file
            file_path = sys.argv[1]
            self.read_task_list(file_path)
        else:
            # Show a file dialog to let the user select a file
            file_path, _ = QFileDialog.getOpenFileName(self, "Import Task List", "", "Text Files (*.txt)")
            if file_path:
                self.read_task_list(file_path)

    def read_task_list(self, file_path):
        # Clear the current task list
        self.task_list.clear()

        # Read the task list from the file
        with open(file_path, "r") as file:
            for line in file:
                # Create a new task item from the line
                task_item = QListWidgetItem(line.strip())
                self.task_list.addItem(task_item)


# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = WeeklyScheduleGenerator()

# Show the main window
window.show()

# Execute the application
sys.exit(app.exec_())
