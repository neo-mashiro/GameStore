"""
Clone of 2048 game.
"""

import poc_2048_gui
import random

# Directions, DO NOT MODIFY
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

# Offsets for computing tile indices in each direction.
# DO NOT MODIFY this dictionary.
OFFSETS = {UP: (1, 0),
           DOWN: (-1, 0),
           LEFT: (0, 1),
           RIGHT: (0, -1)}

def merge(line):
    """
    Function that merges a single row or column in 2048.
    """
    
    # slide zeros to the end of the list
    slide_zero = [num for num in line if num != 0]
    slide_zero.extend([0] * (len(line) - len(slide_zero)))
    
    # merge adjacent numbers
    merged = [False] * len(slide_zero)
    for curr_tile in range(len(slide_zero) - 1):
        if slide_zero[curr_tile] == slide_zero[curr_tile + 1] \
        and slide_zero[curr_tile] != 0 \
        and not merged[curr_tile]:
            slide_zero[curr_tile] *= 2
            for next_tile in range(curr_tile + 1, len(slide_zero)):
                try:
                    slide_zero[next_tile] = slide_zero[next_tile + 1]
                except:
                    slide_zero[next_tile] = 0
            merged[curr_tile] = True
        else:
            continue

    return slide_zero

class TwentyFortyEight:
    """
    Class to run the game logic.
    """

    def __init__(self, grid_height, grid_width):
        self.__height__ = grid_height
        self.__width__ = grid_width
        self.reset()
        self.__init_tiles_dict__ = {UP: [(0, col) for col in range( self.__width__)],
                                    DOWN: [( self.__height__ - 1, col) for col in range( self.__width__)],
                                    LEFT: [(row, 0) for row in range( self.__height__)],
                                    RIGHT: [(row,  self.__width__ - 1) for row in range( self.__height__)]}

    def reset(self):
        """
        Reset the game so the grid is empty except for two
        initial tiles.
        """
        self.__grid__ = [[0 for col in range( self.__width__)]
                            for row in range( self.__height__)]
        self.new_tile()
        self.new_tile()

    def __str__(self):
        """
        Return a string representation of the grid for debugging.
        """
        output = ""
        for row in self.__grid__:
            output += str(row) + "\n"
        return output

    def get_grid_height(self):
        """
        Get the height of the board.
        """
        return self.__height__

    def get_grid_width(self):
        """
        Get the width of the board.
        """
        return self.__width__

    def move(self, direction):
        """
        Move all tiles in the given direction and add
        a new tile if any tiles moved.
        """
        legal = False
        init_tiles = self.__init_tiles_dict__[direction]
        step = OFFSETS[direction]
        
        # merge list one by one
        for tile in init_tiles:
            if step[0] == 0:
                index_tuples = [(tile[0], tile[1] + step[1] * col)
                                for col in range(self.__width__)
                               ]
            else:
                index_tuples = [(tile[0] + step[0] * row, tile[1])
                                for row in range(self.__height__)
                               ]
            tile_list = [self.__grid__[tup[0]][tup[1]] for tup in index_tuples]
            merged_list = merge(tile_list)
            # replace with merged list
            for idx, tup in enumerate(index_tuples):
                self.__grid__[tup[0]][tup[1]] = merged_list[idx]
            # check if any tiles changed
            for idx in range(len(tile_list)):
                if tile_list[idx] != merged_list[idx]:
                    legal = True
        
        # check if move is legal
        if legal:
            exp_val = [2048 for row in range(self.__height__)
                            for col in range(self.__width__)
                            if self.__grid__[row][col] == 2048]
            if len(exp_val) > 0:
                print "You win!"
                self.reset()
            else:
                self.new_tile()

    def new_tile(self):
        """
        Create a new tile in a randomly selected empty
        square.  The tile should be 2 90% of the time and
        4 10% of the time.
        """
        zeros = [(row, col) for row in range(self.__height__)
                            for col in range(self.__width__)
                            if self.__grid__[row][col] == 0]
        if len(zeros) != 0:
            random_tile = random.choice(zeros)
            random_list = [2] * 9 + [4] * 1
            self.__grid__[random_tile[0]][random_tile[1]] = random.choice(random_list)

    def set_tile(self, row, col, value):
        """
        Set the tile at position row, col to have the given value.
        """
        self.__grid__[row][col] = value

    def get_tile(self, row, col):
        """
        Return the value of the tile at position row, col.
        """
        return self.__grid__[row][col]


poc_2048_gui.run_gui(TwentyFortyEight(4, 4))