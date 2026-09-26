import typing

from NeoTrellisGame import NeoTrellisGame, AbstractNeoTrellisGame, Action
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis

class ConnectFour:
    def __init__(self, board: typing.Optional[AbstractNeoTrellisGame] = None):
        self.board = board if board is not None else NeoTrellisGame()
        super().__init__()
        self.width = 8
        self.height = 6 # 8x6 board
        self.game_state = [] # multi-dimensional list
        for i in range(self.height):
            self.game_state = [0] * self.width 
        self.column_heights = [0] * self.width
        self.num_placed = 0
        self.current_player = 1

    def reset_game(self):
        #TODO reset the game state to its original empty state
        pass

    def register_callbacks(self):
        #TODO: Register callbacks that will be run when buttons are pressed and released
        self.board.set_callback(0, 0, self.handle_button_event) # Example of how to register a callback (function) for button 0, 0. Must be done for every button that runs a function
        self.board.activate_key(0, 0, Action.BUTTON_PRESSED) # Even though the callback is set, if the key is not enabled it will not be run. This is how you enable

        pass
  
    def handle_button_event(self, x:int, y: int, action: Action):
        """
        This is an example of how a callback function will look. It takes an x value, y value, and action, which will indicate what button activated the callback and what action the user did to run it.
        See NeoTrellisGame.set_callback() for info about callbacks.
        """
        #TODO: Implement what will happen when the button at position x,y is pressed or released
  
        pass

    # Returns -1 if row is full.
    def find_lowest_empty_row(self, col: int):
        return self.height - self.column_heights[col] - 1

    # False if failure, true if success
    def place_piece(self, col: int):
        row = self.find_lowest_empty_row(col)
        if row == -1:
            return False
        self.gamestate[col][row] = self.current_player
        self.column_heights[col] += 1
        self.num_placed += 1
        if self.current_player == 1:
            set_cell_color(self, col, row, (255, 40 , 40)) # turns the color of the latest placed square to red for player 1
        if self.current_player == 2:
            set_cell_color(self, col, row, (40, 40, 255)) # turns the color of the latest placed square to blue for player 2
        return True

    def update_board_colors(self):
        #TODO: DON'T NEED THIS, CAN DELETE LATER BECAUSE OF INCORPORATION IN PLACE_PIECE
        pass

    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1

    def show_current_player(self):
        #TODO: Function to indicate on the board which player is currently placing a piece
        pass

    def is_board_full(self):
        #TODO: Return whether or not the game state has no more legal moves
        pass  

    def get_player_color(self, player) -> tuple[int, int, int]:
        #TODO: Return the color for the given player 
        pass

    def is_column_full(self, col: int):
        #TODO: Return if the given column is currently full
        pass

    def check_win(self, x: int, y: int) -> bool:
        #TODO: Check the game state to see if any player has won or if there is a draw
        pass

    def show_winner(self):
        #TODO: Display on the board who won
        pass

    def show_tie_game(self):
        #TODO: Display on the board that there was a draw
        pass


