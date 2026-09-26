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
            self.game_state.append([0] * self.width) 
        self.column_heights = [0] * self.width
        self.num_placed = 0
        self.current_player = 1
        self.register_callbacks()

    def reset_game(self):
        #TODO reset the game state to its original empty state
        pass

    def register_callbacks(self):
        #TODO: Register callbacks that will be run when buttons are pressed and released
        for col in range(8):
            self.board.set_callback(col, 0, self.handle_button_event) # Example of how to register a callback (function) for button 0, 0. Must be done for every button that runs a function
            self.board.activate_key(col, 0, Action.BUTTON_PRESSED) # Even though the callback is set, if the key is not enabled it will not be run. This is how you enable

        pass
  
    def handle_button_event(self, x:int, y: int, action: Action):
        """
        This is an example of how a callback function will look. It takes an x value, y value, and action, which will indicate what button activated the callback and what action the user did to run it.
        See NeoTrellisGame.set_callback() for info about callbacks.
        """
        #TODO: Implement what will happen when the button at position x,y is pressed or released
        if Action.BUTTON_PRESSED:
            if self.place_piece(x):
                self.switch_player()

    # Returns -1 if row is full.
    def find_lowest_empty_row(self, col: int):
        return self.height - self.column_heights[col] - 1

    # False if failure, true if success
    def place_piece(self, col: int):
        row = self.find_lowest_empty_row(col)
        if row == -1:
            return False
        self.game_state[row][col] = self.current_player
        self.column_heights[col] += 1
        self.num_placed += 1
        if self.current_player == 1:
            self.board.set_cell_color(col, row + 2, (255, 40 , 40)) # turns the color of the latest placed square to red for player 1
            self.board.update_display()
        if self.current_player == 2:
            self.board.set_cell_color(col, row + 2, (40, 40, 255)) # turns the color of the latest placed square to blue for player 2
            self.board.update_display()
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
        directions = [
            [0, 1],
            [1, 0],
            [1, 1],
            [1, -1]
        ]
        ourColor = self.game_state[y][x]
        for direction in directions:
            curX = x
            curY = y

            # Bookkeeping variable: how many of the same color in this direction?
            counterPositiveDirection = 1

            # Go in one direction until it either goes out of the board or hits a non-self tile
            while True:
                curX += direction[0]
                curY += direction[1]

                # Out of bounds check
                if curX < 0 or curX >= self.width or curY < 0 or curY >= self.height:
                    break

                # Color check
                if self.game_state[curY][curX] != ourColor:
                    break

                # Increase bookkeeping variable
                counterPositiveDirection += 1

                # If 4 or more in this direction, we need not bother checking more
                if counterPositiveDirection >= 4:
                    return True
            
            # Go the other way
            counterNegativeDirection = 1
            while True:
                curX -= direction[0]
                curY -= direction[1]

                if curX < 0 or curX >= self.width or curY < 0 or curY >= self.height:
                    break

                if self.game_state[curY][curX] != ourColor:
                    break

                counterNegativeDirection += 1

                # Same logic as earlier check, but subtract one since the center tile is counted twice
                # Checks for if the most recently placed tile is in the middle of the winning match
                if counterPositiveDirection + counterNegativeDirection - 1 >= 4:
                    return True
        
        # If no direction won, then return failure
        return False
            


    def show_winner(self):
        #TODO: Display on the board who won
        #if counterPositiveDirection >= 4:
        #if self.current_player == 1:
        #    winner = 'Player 1'
        #    print(winner)
        pass

    def show_tie_game(self):
        #TODO: Display on the board that there was a draw
        pass


