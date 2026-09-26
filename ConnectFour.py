import typing

from NeoTrellisGame import NeoTrellisGame, AbstractNeoTrellisGame, Action
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from Colors import RED, GREEN, BLUE, WHITE, OFF
from dataclasses import dataclass
from time import sleep

# Encode information about winning row
# startX and startY represent the first square of the row
# stepX and stepY represent which direction it is in. We call them stepX/Y because they represent the "step" between consecutive squares
# num_cells is quite obvious
@dataclass
class WinningRow:
    startX: int
    startY: int
    stepX: int
    stepY: int
    num_cells: int

class ConnectFour:
    def __init__(self, board: typing.Optional[AbstractNeoTrellisGame] = None):
        super().__init__()

        # This defines the hardware interface
        self.board = board if board is not None else NeoTrellisGame()

        # 8x6 board
        self.width = 8
        self.height = 6

        # Initialize game
        self.reset_game()
        self.register_callbacks()

    def reset_game(self, animate=False):
        if animate:
            # Board dropping animation
            # Decrement is how much the board drops by
            for decrement in range(self.height + 1):
                # Draw the board, but moved down
                for col in range(self.width):
                    for row in range(self.height):
                        if row - decrement < 0:
                            self.board.set_cell_color(col, row + 2, OFF)
                        else:
                            self.board.set_cell_color(col, row + 2, self.get_color(self.game_state[row - decrement][col]))
                self.board.update_display()
                sleep(0.05)
                self.board.play_sound("slap.mp3")
            
            # Ignore any key events that happened during animation
            self.board.clear_keypad_buffer()
        else:
            # Standard clear board
            self.board.clear_board()

        # Multi-dimensional list representing board state
        # 0 = none, 1 = player 1 tile, 2 = player 2 tile
        self.game_state = [] 
        for i in range(self.height):
            self.game_state.append([0] * self.width) 
        
        # How many tiles are in each column
        self.column_heights = [0] * self.width
        
        # How many tiles have been placed (draw detection)
        self.num_placed = 0

        self.current_player = 1

        # Has game ended? (Convenient for the button handler to know)
        self.game_ended = False

        # Make the top row the color of the first player
        self.top_row(self.get_color(1))
        self.board.update_display()

    # Set color of top row.
    def top_row(self, color):
        for col in range(self.width):
            self.board.set_cell_color(col, 0, color)
        self.board.update_display()

    # Attach behaviors to certain buttons
    def register_callbacks(self):
        for col in range(self.width):
            self.board.set_callback(col, 0, self.handle_button_event)
            self.board.activate_key(col, 0, Action.BUTTON_PRESSED)
    
    # Color corresponding to current player
    def current_color(self):
        return self.get_color(self.current_player)
    
    # Color corresponding to player given in argument; returns OFF if not a recognized player
    def get_color(self, player):
        if player == 1:
            return RED
        elif player == 2:
            return BLUE
        else:
            return OFF

    def handle_button_event(self, x: int, y: int, action: Action):
        """
        This is an example of how a callback function will look. It takes an x value, y value, and action, which will indicate what button activated the callback and what action the user did to run it.
        See NeoTrellisGame.set_callback() for info about callbacks.
        """
        # Safeguard: only run if the button is pressed, not if the button is released or any other behavior
        if Action.BUTTON_PRESSED:
            # Implement a reset button, or ignore other button presses after win
            if self.game_ended:
                if x == self.width - 1:
                    self.reset_game(True)
                return
            
            # Attempt to place piece. If that fails, it plays the error sound and exits function.
            result = self.place_piece(x)
            if result is None:
                self.board.play_sound("error.mp3")
                return
            
            # Switch player, unless there's a win
            if len(result) == 0:
                self.switch_player()
            
            # In case of draw or win
            if self.is_board_full() or len(result) > 0:
                self.game_ended = True

                color = self.current_color()

                # Display winning player at first 6 squares of top row
                # Or alternating red and blue if draw
                if len(result) > 0:
                    self.top_row(color)
                    self.board.play_sound("cheer.mp3")
                else:
                    col = 0
                    while col < 6:
                        self.board.set_cell_color(col, 0, RED)
                        self.board.set_cell_color(col + 1, 0, BLUE)
                        col += 2
                    self.board.play_sound("aww.mp3")
                
                # Separator square at seventh, then reset button at eighth
                self.board.set_cell_color(6, 0, OFF)
                self.board.set_cell_color(7, 0, GREEN)
                self.board.update_display()

                # Flashing winning row animation
                for i in range(21):
                    # Multiple rows may be winning rows at the same time, so this flashes all of them simultaneously
                    for row in result:
                        for j in range(row.num_cells):
                            self.board.set_cell_color(
                                row.startX + j * row.stepX,
                                row.startY + j * row.stepY + 2,
                                color if i % 2 == 0 else OFF
                            )
                    self.board.update_display()
                    sleep(0.05)
                
                # Get rid of key events that happened during animation
                self.board.clear_keypad_buffer()

    # Finds the lowest empty row of a column. Returns -1 if row is full.
    def find_lowest_empty_row(self, col: int):
        return self.height - self.column_heights[col] - 1

    # Returns None if failure, empty list if success, list containing win information if win
    def place_piece(self, col: int):
        # Attempt to find lowest empty row of col
        row = self.find_lowest_empty_row(col)
        if row == -1:
            return None

        # Update state
        self.game_state[row][col] = self.current_player
        self.column_heights[col] += 1
        self.num_placed += 1

        color = self.current_color()

        # Animates the square falling down
        y = 0
        while y <= row:
            self.board.set_cell_color(col, y + 1, OFF)
            self.board.set_cell_color(col, y + 2, color)
            self.board.update_display()
            sleep(0.05)
            y += 1

        self.board.play_sound("slap.mp3")

        # Clear any events that occured during animation
        self.board.clear_keypad_buffer()

        # Return win information (this is an empty list if no win)
        return self.check_win(col, row)

    # Switch player, and set top row color
    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1
        self.top_row(self.current_color())

    # Use the num_placed state variable to check if board is full
    def is_board_full(self):
        return self.num_placed >= self.width * self.height

    # Check win function
    # Returns empty list if no win
    # Returns an list of one or more WinningRow objects if win
    def check_win(self, x: int, y: int):
        # Encodes the four directions to check in terms of displacements
        # Horizontal, vertical, two diagonals
        directions = [
            [0, 1], # Vertical
            [1, 0], # Horizontal
            [1, 1], # Top left <-> bottom right
            [1, -1] # Bottom left <-> top right
        ]

        # Color of the tile that was just placed
        our_color = self.game_state[y][x]

        # List that we will return
        out = []

        # Check for wins in each direction
        for direction in directions:
            # Current X and Y
            curX = x
            curY = y

            # How many cells in winning row?
            num_cells = 1

            # Go in one direction until it either goes out of the board or hits a non-self tile
            while True:
                curX += direction[0]
                curY += direction[1]

                # Out of bounds check
                if curX < 0 or curX >= self.width or curY < 0 or curY >= self.height:
                    break

                # Color check
                if self.game_state[curY][curX] != our_color:
                    break

                # More distance has been covered
                num_cells += 1
            
            # Reset these
            curX = x
            curY = y

            # Go the opposite direction
            while True:
                curX -= direction[0]
                curY -= direction[1]

                if curX < 0 or curX >= self.width or curY < 0 or curY >= self.height or self.game_state[curY][curX] != our_color:
                    # We step back here because we need these for the winning row
                    curX += direction[0]
                    curY += direction[1]
                    break

                num_cells += 1

            # Add the winning row if four in a row or more
            if num_cells >= 4:
                out.append(WinningRow(curX, curY, direction[0], direction[1], num_cells))
            
        # Return our list
        return out


