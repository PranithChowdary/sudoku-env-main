import numpy as np
from dataclasses import dataclass
import math,sys
np.random.seed(42)

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QWidget,QGridLayout,QLineEdit
from PySide6.QtGui import QIcon 
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent

@dataclass(frozen=True)
class Board_specs:
  """
    A dataclass to define specifications for the Sudoku board.

    Attributes:
        size (tuple): Dimensions of the board (rows, columns).
        low (int): Minimum value allowed in the board.
        high (int): Maximum value allowed in the board.
  """
  size: tuple = (9,9)
  low: int = 1
  high: int = 9

def Board(specs=Board_specs):
    """
      Generates a random board matrix based on the provided specifications.

      Args:
          specs (Board_specs): Specifications for the board.

      Returns:
          numpy.ndarray: A randomly generated matrix.
    """
    matrix = np.random.randint(specs.low,specs.high,specs.size)
    return matrix

def Region_Split(matrix):
    """
      Splits the board matrix into smaller subregions.

      Args:
          matrix (numpy.ndarray): The input matrix.

      Returns:
          list: A list of concatenated subregions from the matrix.
    """
  # Convert the matrix into region size (3,3) 
    ZERO = 0
    CONST = int(math.sqrt(Board_specs.high))  # Dynamically calculate region size
    MAX_COLUMN_END = Board_specs.size[1] + 1
    row_start = col_start = ZERO
    row_end = col_end = CONST
    subgrid = []
    while len(subgrid) < len(matrix) :
        subgrid.append([row[col_start:col_end] for row in matrix[row_start:row_end]])
        col_start += CONST
        col_end += CONST
        if col_end == MAX_COLUMN_END :
            col_start = ZERO
            col_end = CONST
            row_start += CONST
            row_end += CONST
    assert len(subgrid) == len(matrix)
    subgrid = [np.concatenate(line) for line in subgrid]
    return subgrid 

class Game:
    """
      Represents the Sudoku game, managing the board and player actions.

      Attributes:
          board (numpy.ndarray): The current game board.
          action (tuple): The current action in the format (row, column, value).
    """
    def __init__(self,action = None):
        """
        Initializes the game with an optional action.

        Args:
            action (tuple, optional): The action to be applied to the board.
        """
        self.board = Board()
        self.action = action
        
    def Updated_board(self):
        """
          Updates the board with the provided action.

          Returns:
              tuple: Updated board and the action applied.
        """
        if self.action is not None:
            self.action = self.action[0] if not len(self.action)== 3 else self.action
            row,column,value = self.action
            self.board[row][column] = value 
        return self.board,self.action

class Util:
    """
      Utility class containing helper methods for game processing.

      Methods:
          Utilities(gameinstance): Processes a game instance and prepares board-related data.
          unique(lisst): Checks if a list contains unique elements.
          len_dif(lisst): Computes the difference between the list's length and the set's length.
    """
    @classmethod
    def Utilities(cls,gameinstance):
        """
          Processes a game instance and extracts the matrix, action, and region data.

          Args:
              gameinstance (Game): An instance of the game.
        """
        if gameinstance is None : 
            sys.exit(f"{cls.__name__} : No Game instance was provided")
        cls.upd_matrix,cls.action = gameinstance.Updated_board()

        # TODO : just transpose the matrix then ylist will be easy to implement
        cls.y_list = [[col[y_index] for col in cls.upd_matrix] for y_index in range(Board_specs.high)]
        cls.y = [line for line in cls.upd_matrix.T]
        cls.subgrid = Region_Split(cls.upd_matrix)
        cls.subgrid = [arr.tolist() for arr in cls.subgrid]
      
    @staticmethod
    def unique(lisst):
        """
          Checks if all elements in a list are unique.

          Args:
              lisst (list): Input list.

          Returns:
              bool: True if unique, False otherwise.
        """
        return len(lisst) == len(set(lisst))
    
    @staticmethod
    def len_dif(lisst):
        """
          Computes the length difference between a list and its unique elements.

          Args:
              lisst (list): Input list.

          Returns:
              int: The difference in length.
        """
        return len(lisst) - len(set(lisst))
    
class Board_conflicts: # Heuristic component
    """
      Class for evaluating board conflicts and managing heuristic calculations.

      Attributes:
          conflicts (int): Number of conflicts in the board.
          reward_H (int): Heuristic reward.
    """
    previous_conflicts = 0

    def __init__(self,instance):
        """
          Initializes the conflict manager with a game instance.

          Args:
              instance (Game): The game instance.
        """
        Util.Utilities(instance)
        self.conflicts = 0
        self.previous_conflicts = 0
        self.reward_H = 0
    
    def count(self):
        """
          Counts conflicts in rows, columns, and regions.

          Returns:
              int: The heuristic reward.
        """
        for line in Util.upd_matrix:
            if not Util.unique(line) : self.conflicts += Util.len_dif(line)
        for col in Util.y_list:
            if not Util.unique(col) : self.conflicts += Util.len_dif(col)
        for submatrix in Util.subgrid:
            if not Util.unique(submatrix) : self.conflicts += Util.len_dif(submatrix)
        # H value
        if self.conflicts < self.previous_conflicts:
            self.reward_H = 2
        Board_conflicts.previous_conflicts = self.conflicts
        return self.reward_H

class Reward_fn:
    """
    Class for calculating the reward based on the game state.

    Attributes:
        reward (int): The calculated reward.
    """
    
    def __init__(self,instance):
        """
        Initializes the reward function.

        Args:
            instance (Game): The game instance.
        """
        Util.Utilities(instance)
        self.action = Util.action
        self.matrix = Util.upd_matrix
        self.y_list = Util.y_list
        self.reward = 0
        if not len(self.action)==3: action = action[0]
        assert len(self.action)==3
       
       
    def Reward_return(self):
        """
        Calculates the reward based on rows, columns, and regions.

        Returns:
            int: The total reward.
        """
        if self.action is None : 
            sys.exit(f"{self.__class__.__name__} : Action is None")
        # x
        x = self.matrix[self.action[0]]; assert len(x) == Board_specs.high
        self.reward += 9 if (Util.len_dif(x) == 0) else -Util.len_dif(x)
        # y
        y_index = self.action[1]
        y = self.y_list[y_index]; assert len(y) == Board_specs.high
        self.reward += 9 if (Util.len_dif(y) == 0) else -Util.len_dif(y)
        # region
        n = int(math.sqrt(Board_specs.high))
        ix,iy = (self.action[0]//n)* n , (self.action[1]//n)* n
        region = np.concatenate(self.matrix[ix:ix+n , iy:iy+n])
        assert len(region) == Board_specs.high
        self.reward += 9 if (Util.len_dif(region) == 0) else  -Util.len_dif(region)
        return self.reward

def Terminated(instance):
    """
    Checks if the game has terminated (all rows, columns, and regions are valid).

    Args:
        instance (Game): The game instance.

    Returns:
        tuple: Booleans indicating the validity of rows, columns, and regions.
    """
    Util.Utilities(instance)
    matrix = Util.upd_matrix
    y_list = Util.y_list
    subgrid = Util.subgrid
    all_uniquerow = all(Util.unique(line) for line in matrix)
    all_uniquecol = all(Util.unique(line) for line in y_list)
    all_unique_region = all(Util.unique(line) for line in subgrid)
    return all_uniquerow,all_uniquecol,all_unique_region


import gymnasium as gym
import gymnasium.spaces as spaces
from gymnasium.envs.registration import register

from gui import Gui
app = QApplication.instance()
if app is None:
    app = QApplication([])

register(
    id="sudoku",
    entry_point="__main__:ENVI"
)

class ENVI(gym.Env):
    """
    Sudoku Environment for reinforcement learning.

    This class defines the environment for the Sudoku game using the Gymnasium library. It integrates
    the game's logic, including state management, action space, and reward function, and provides an
    interface for interacting with the game in a reinforcement learning context.
    """
    
    def __init__(self):
        """
        Initializes the Sudoku environment.

        This method sets up the environment by initializing the game state, action space, observation space,
        and GUI. It also prepares the game to be used with Gym's environment interface.
        """
        super().__init__()
        self.action = None
        self.game = Game(None)
        self.updated,_ = self.game.Updated_board()

        self.gui = Gui()

        self.size = Board_specs.high
        self.action_space = spaces.Tuple((spaces.Discrete(Board_specs.high),                        # x
                                          spaces.Discrete(Board_specs.high),                        # y
                                          spaces.Discrete(Board_specs.high,start=Board_specs.low))) # value, start = 1
        self.observation_space = spaces.Box(low=Board_specs.low,
                                            high=Board_specs.high,
                                            shape=Board_specs.size,
                                            dtype=float)
        
    def reset(self,seed = None) :
        """
        Resets the environment to the initial state.

        Args:
            seed (optional): A seed for random number generation to ensure reproducibility.

        Returns:
            tuple: The initial observation and an empty dictionary.
        """
        super().reset(seed=seed)
        return np.float16(self.updated) ,{}
        
    def step(self,action):
        """
        Steps through the environment by applying the given action.

        Args:
            action (tuple): The action to apply, consisting of the row, column, and value to be set in the board.

        Returns:
            tuple: The updated observation, the reward, a boolean indicating if the game is terminated, a boolean indicating truncation, and additional info.
        """
        self.game = Game(action)
        self.updated,_ = Game(action).Updated_board()
       
        reward_base = Reward_fn(self.game).Reward_return()
        heuristic = Board_conflicts(self.game).count()
        reward = reward_base + heuristic
        terminated_list = Terminated(self.game)
        terminated = (True if all(terminated_list) else False)

        info = {
            "conflicts" : heuristic
        }
        self.action = action
        return  np.float16(self.updated),reward,terminated,False,info
    
    def render(self):
        """
        Renders the current state of the environment.

        This method updates the GUI to reflect the current state of the board and displays it.
        """
        self.gui.updated(self.action)
        self.gui.show()
   
        
if __name__=="__main__":
    class Test:
        """
        A test class for running the ENVI environment.

        This class manages the testing of the ENVI environment by sampling random actions,
        stepping through the environment, and optionally rendering the GUI. It runs the test
        for a specified number of episodes and uses a timer to control the execution flow.
        """
        
        def __init__(self, render:bool, episodes:int):
            """
            Initializes the Test class.

            Args:
                render (bool): If True, the GUI will be rendered during testing.
                episodes (int): The number of episodes to run the test for.
            """
            self.timer = QTimer()
            self.test = ENVI()
            self.terminated = False
            self.render = render
            self.counter = 0
            self.episodes = episodes
  
        def main(self):
            """
            Executes a single test step.

            This method resets the environment, samples a random action, steps through the
            environment, and optionally renders the GUI. The process continues until the 
            specified number of episodes is completed.
            """
            self.test.reset()
            if self.counter < self.episodes:
                action = self.test.action_space.sample()
                observation, reward, terminated, truncated, info = self.test.step(action)
                print("\n--------- END ---------")
                print("Observation : \n",observation)
                print("Reward : ",reward)
                print("Terminated : ",terminated)
                print("Truncated : ",truncated)
                print("Info : ",info)
                if self.render:
                    self.test.render()
                    print("Action : ",action)
                else:
                    print("Action : ",action)
                self.counter += 1
            else:
                self.timer.stop()
                sys.exit()
        
        def run(self):
                """
                Starts the test execution.

                Connects the `main` method to a QTimer signal to execute periodically
                and starts the application's event loop.
                """
                self.timer.timeout.connect(self.main)
                self.timer.start(300)
                app.exec()
                
                
    t = Test(render=True,episodes=100)
    t.run()