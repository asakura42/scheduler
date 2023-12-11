# Weekly Schedule Generator

The Weekly Schedule Generator is a Python program that allows you to create and visualize your weekly schedule. It provides a graphical user interface (GUI) where you can input tasks, their respective days, start and end times, and colors. The program then generates a schedule plot using matplotlib, displaying your tasks in a visually appealing way.

## Installation

To use the Weekly Schedule Generator, follow these steps:

```
$ git clone https://github.com/asakura42/scheduler
# pacman -Syu python-matplotlib python-pyqt5 python-pyqt5-sip
``` 

## Usage

To run the Weekly Schedule Generator, execute the following command in your terminal or command prompt:

```bash
python schedule.py [INPUT_FILE]
```

This will launch the application and open the main window.

## Adding Tasks

To add a task to your schedule, follow these steps:

1. Enter the task name in the "Task" input field.
2. Select the day of the week for the task from the dropdown menu.
3. Enter the start time of the task in the "Start Time" input field. Use the format HH:mm (e.g., 09:30).
4. Enter the end time of the task in the "End Time" input field. Use the same format as the start time.
5. Click the "Pick Color" button to choose a color for the task.
6. Click the "Add Task" button to add the task to the schedule.

   **Note:** You can also press the Enter key in any of the input fields to add the task.

## Editing Tasks

To edit a task in your schedule, follow these steps:

1. Click on the task in the task list on the right side of the window.
2. The task details will be populated in the input fields.
3. Modify the task details as desired.
4. Click the "Add Task" button to save the changes.

   **Note:** Editing a task will update its details in the schedule.

## Rendering the Schedule

To generate and view the schedule plot, follow these steps:

1. Click the "Render" button.
2. The program will generate the schedule plot using the entered tasks.
3. The plot will be saved as a PNG image in the "outputs" directory.
4. The generated image will be opened automatically.

   **Note:** The "outputs" directory will be created if it doesn't exist.

## Importing a Task List

You can import a task list from a text file. The file should contain one task per line, with each task formatted as follows:

```
Task Name, Day of the Week, Start Time - End Time, Color
```

For example:

```
Meeting, Monday, 09:00 - 10:30, #FF0000
Study at home, Tuesday, 14:00 - 16:00, red
```

To import a task list, follow these steps:

1. Place your task list text file in a convenient location.
2. Launch the Weekly Schedule Generator with the file name as first argument.
3. The program will automatically detect the file argument and import the task list.

   **Note:** If no file argument is provided, a file dialog will appear for you to select the file. If you will reject this dialog, empty document will open.

## Contributing

If you would like to contribute to the Weekly Schedule Generator, feel free to submit a pull request on the GitHub repository. Your contributions are greatly appreciated!

## Acknowledgements

The Weekly Schedule Generator was inspired by the https://github.com/ftorres16/my_weekly_schedule. Some lines were initially took from that project. Because of it, this program has GPL-3.0 license too.
