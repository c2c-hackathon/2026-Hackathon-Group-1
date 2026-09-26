import typing

from NeoTrellisGame import NeoTrellisGame, AbstractNeoTrellisGame, Action
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from Colors import RED, GREEN, BLUE, WHITE, OFF
from dataclasses import dataclass
from time import sleep
# freesound_community-hard-slap-46388.mp3
@dataclass
class WinningRow:
    startX: int
    startY: int
    stepX: int
    stepY: int
    num_cells: int

class ConnectFour:
    def __init__(self, board: typing.Optional[AbstractNeoTrellisGame] = None):
        # This defines the hardware interface
        self.board = board if board is not None else NeoTrellisGame()
        super().__init__()
        self.width = 8
        self.height = 6 # 8x6 board
        self.game_state = [] # multi-dimensional list
        self.reset_game()
        self.register_callbacks()

    def reset_game(self, animate=False):
        if animate:
            for decrement in range(self.height + 1):
                for col in range(self.width):
                    for row in range(self.height):
                        if row - decrement < 0:
                            self.board.set_cell_color(col, row + 2, OFF)
                        else:
                            self.board.set_cell_color(col, row + 2, self.get_color(self.game_state[row - decrement][col]))
                self.board.update_display()
                sleep(0.05)
                self.board.play_sound("slap.mp3")
            
            self.board.clear_keypad_buffer()
        else:
            self.board.clear_board()

        self.game_state = [] # multi-dimensional list
        for i in range(self.height):
            self.game_state.append([0] * self.width) 
        self.column_heights = [0] * self.width
        self.num_placed = 0
        self.current_player = 1
        self.game_ended = False
        self.top_row(RED)
        self.board.update_display()

    def top_row(self, color):
        for col in range(self.width):
            self.board.set_cell_color(col, 0, color)
        self.board.update_display()

    def register_callbacks(self):
        #TODO: Register callbacks that will be run when buttons are pressed and released
        for col in range(self.width):
            self.board.set_callback(col, 0, self.handle_button_event) # Example of how to register a callback (function) for button 0, 0. Must be done for every button that runs a function
            self.board.activate_key(col, 0, Action.BUTTON_PRESSED) # Even though the callback is set, if the key is not enabled it will not be run. This is how you enable
  
    def current_color(self):
        return self.get_color(self.current_player)
    
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
        #TODO: Implement what will happen when the button at position x,y is pressed or released
        if Action.BUTTON_PRESSED:
            if self.game_ended:
                if x == self.width - 1:
                    self.reset_game(True)
                return
            
            result = self.place_piece(x)
            if result is None:
                self.board.play_sound("error.mp3")
                return
            
            # No win
            if len(result) == 0:
                self.switch_player()
            
            # Draw or win
            if self.is_board_full() or len(result) > 0:
                self.game_ended = True

                color = self.current_color()

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
                
                self.board.set_cell_color(6, 0, OFF)
                self.board.set_cell_color(7, 0, GREEN)
                self.board.update_display()

                for i in range(21):
                    for row in result:
                        for j in range(row.num_cells):
                            self.board.set_cell_color(
                                row.startX + j * row.stepX,
                                row.startY + j * row.stepY + 2,
                                color if i % 2 == 0 else OFF
                            )
                    self.board.update_display()
                    sleep(0.05)
                self.board.clear_keypad_buffer()

    # Returns -1 if row is full.
    def find_lowest_empty_row(self, col: int):
        return self.height - self.column_heights[col] - 1

    # None if failure, empty array if success, array containing win information if win
    def place_piece(self, col: int):
        row = self.find_lowest_empty_row(col)
        if row == -1:
            return None
        self.game_state[row][col] = self.current_player
        self.column_heights[col] += 1
        self.num_placed += 1

        color = self.current_color()

        y = 0
        while y <= row:
            self.board.set_cell_color(col, y + 1, OFF)
            self.board.set_cell_color(col, y + 2, color)
            self.board.update_display()
            sleep(0.05)
            y += 1

        self.board.play_sound("slap.mp3")

        self.board.clear_keypad_buffer()

        return self.check_win(col, row)

    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1
        self.top_row(self.current_color())

    def is_board_full(self):
        return self.num_placed >= self.width * self.height

    def check_win(self, x: int, y: int):
        directions = [
            [0, 1],
            [1, 0],
            [1, 1],
            [1, -1]
        ]
        our_color = self.game_state[y][x]
        out = []
        for direction in directions:
            # Current X and Y
            curX = x
            curY = y

            # Bookkeeping variable: how many cells in winning row?
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

                # Increase bookkeeping variable
                num_cells += 1
            
            curX = x
            curY = y

            # Go the other way
            while True:
                curX -= direction[0]
                curY -= direction[1]

                if curX < 0 or curX >= self.width or curY < 0 or curY >= self.height or self.game_state[curY][curX] != our_color:
                    curX += direction[0]
                    curY += direction[1]
                    break

                num_cells += 1

            if num_cells >= 4:
                out.append(WinningRow(curX, curY, direction[0], direction[1], num_cells))
            
        return out


