import random
import numpy as np

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLineEdit
from PySide6.QtGui import QIcon

# Ensure a QApplication instance is available
app = QApplication.instance()
if app is None:
    app = QApplication([])


class Gui(QWidget):
    """
    The Gui class creates a graphical interface for a Sudoku-like grid.
    It allows the creation of cells in a grid, updating cell values, 
    and retrieving the grid's current state as a matrix.
    """

    def __init__(self, size=9):
        """
        Initialize the GUI with a specified grid size.

        Args:
            size (int): The number of rows and columns in the grid (default: 9).
        """
        super().__init__()

        self.setWindowTitle("Sudoku")
        self.setWindowIcon(QIcon("icon.png"))
        self.setMaximumSize(size * 30, size * 30)

        # Initialize variables
        self.grid = QGridLayout(self)
        self.grid.setSpacing(0)
        self.size = size  # Grid size
        self.action = None
        self.cells = [
            [QLineEdit(self) for _ in range(self.size)] 
            for _ in range(self.size)
        ]

        # Create and style grid cells
        for x in range(self.size):
            for y in range(self.size):
                self.cells[x][y].setMaximumSize(30, 30)  # Adjust for visibility
                self.cells[x][y].setReadOnly(True)
                self.cells[x][y].setStyleSheet(
                    f"background-color: #{''.join([random.choice('0123456789ABCDEF') for _ in range(6)])};"
                    "border: 1px solid black; color: white;"
                )
                self.cells[x][y].setText(str(random.randint(1, self.size)))
                self.cells[x][y].setAlignment(QtCore.Qt.AlignCenter)
                self.grid.addWidget(self.cells[x][y], x, y)

    def updated(self, action=None) -> list[list[int]]:
        """
        Update the grid cells based on the given action and return the updated grid as a matrix.

        Args:
            action (tuple or list): A tuple/list containing (row, column, value) to update.
        
        Returns:
            matrix (list of list of int): The updated grid as a matrix.
            action (tuple): The last performed action.
        """
        if action is not None:
            self.action = action
            if not isinstance(action, (tuple, list, np.ndarray)):
                print(f"action : {action} : {type(action)} should be a list, a tuple or a numpy array")
            else:
                if not len(action) == 3:
                    action = action[0]
                assert len(action) == 3, "Action must contain three elements: (row, column, value)"
                row, column, value = action
                self.cells[row][column].setText(str(value))
                self.cells[row][column].setStyleSheet(
                    f"background-color: #{''.join([random.choice('0123456789ABCDEF') for _ in range(6)])};"
                    "border: 1px solid black; color: white;"
                )

        # Collect all cell values
        list_text = []
        for rw in self.cells:
            for cell in rw:
                list_text.append(cell.text())
        list_text = [int(element) for element in list_text]

        # Create a matrix from the flat list
        matrix = [
            list_text[i:i + self.size] 
            for i in range(0, len(list_text), self.size)
        ]
        return matrix, self.action


class Test:
    """
    The Test class provides functionality to simulate actions on the GUI grid
    and manage rendering updates.
    """

    def __init__(self, render=True, episodes=100):
        """
        Initialize the test with rendering and episode options.

        Args:
            render (bool): Whether to render the GUI during testing.
            episodes (int): Number of episodes to run (default: 100).
        """
        self.render = render
        self.episodes = episodes
        self.timer = QtCore.QTimer()

    def main(self):
        """
        The main logic to be executed during each timer tick. 
        Updates grid values or performs testing logic.
        """
        # Example logic to update the GUI or execute steps in your test
        pass

    def run(self):
        """
        Start the test execution and manage GUI updates based on timer.
        """
        self.timer.timeout.connect(self.main)
        self.timer.start(500)  # Set update interval to 500 ms
        app.exec()


if __name__ == "__main__":
    """
    Entry point of the application. Initializes and displays the GUI,
    and starts the test logic.
    """
    grid_size = 9  # Define the Sudoku grid size (e.g., 9x9, 16x16)
    gui = Gui(size=grid_size)
    gui.show()

    # Test rendering with slower update speed
    t = Test(render=True, episodes=100)
    t.run()