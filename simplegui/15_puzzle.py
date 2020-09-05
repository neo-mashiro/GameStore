"""
Loyd's Fifteen puzzle - solver and visualizer
Note that solved configuration has the blank (zero) tile in upper left
Use the arrows key to swap this tile with its neighbors
"""

import poc_fifteen_gui


class Puzzle:
    """
    Class representation for the Fifteen puzzle
    """

    def __init__(self, puzzle_height, puzzle_width, initial_grid=None):
        """
        Initialize puzzle with default height and width
        Returns a Puzzle object
        """
        self._height = puzzle_height
        self._width = puzzle_width
        self._grid = [[col + puzzle_width * row
                       for col in range(self._width)]
                      for row in range(self._height)]

        if initial_grid != None:
            for row in range(puzzle_height):
                for col in range(puzzle_width):
                    self._grid[row][col] = initial_grid[row][col]

    def __str__(self):
        """
        Generate string representaion for puzzle
        Returns a string
        """
        ans = ""
        for row in range(self._height):
            ans += str(self._grid[row])
            ans += "\n"
        return ans

    #####################################
    # GUI methods

    def get_height(self):
        """
        Getter for puzzle height
        Returns an integer
        """
        return self._height

    def get_width(self):
        """
        Getter for puzzle width
        Returns an integer
        """
        return self._width

    def get_number(self, row, col):
        """
        Getter for the number at tile position pos
        Returns an integer
        """
        return self._grid[row][col]

    def set_number(self, row, col, value):
        """
        Setter for the number at tile position pos
        """
        self._grid[row][col] = value

    def clone(self):
        """
        Make a copy of the puzzle to update during solving
        Returns a Puzzle object
        """
        new_puzzle = Puzzle(self._height, self._width, self._grid)
        return new_puzzle

    ########################################################
    # Core puzzle methods

    def current_position(self, solved_row, solved_col):
        """
        Locate the current position of the tile that will be at
        position (solved_row, solved_col) when the puzzle is solved
        Returns a tuple of two integers        
        """
        solved_value = (solved_col + self._width * solved_row)

        for row in range(self._height):
            for col in range(self._width):
                if self._grid[row][col] == solved_value:
                    return (row, col)
        assert False, "Value " + str(solved_value) + " not found"

    def update_puzzle(self, move_string):
        """
        Updates the puzzle state based on the provided move string
        """
        zero_row, zero_col = self.current_position(0, 0)
        for direction in move_string:
            if direction == "l":
                assert zero_col > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col - 1]
                self._grid[zero_row][zero_col - 1] = 0
                zero_col -= 1
            elif direction == "r":
                assert zero_col < self._width - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col + 1]
                self._grid[zero_row][zero_col + 1] = 0
                zero_col += 1
            elif direction == "u":
                assert zero_row > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row - 1][zero_col]
                self._grid[zero_row - 1][zero_col] = 0
                zero_row -= 1
            elif direction == "d":
                assert zero_row < self._height - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row + 1][zero_col]
                self._grid[zero_row + 1][zero_col] = 0
                zero_row += 1
            else:
                assert False, "invalid direction: " + direction

    ##################################################################
    # Phase one methods

    def lower_row_invariant(self, target_row, target_col):
        """
        Check whether the puzzle satisfies the specified invariant
        at the given position in the bottom rows of the puzzle (target_row > 1)
        Returns a boolean
        """
        # Tile zero is positioned at (i,j).
        if self.get_number(target_row, target_col) != 0:
            print "target tile is not zero"
            return False
            
        # All tiles in rows i+1 or below are positioned at their solved location.
        for lower_row in range(target_row + 1, self._height):
            for lower_col in range(self._width):
                if self.get_number(lower_row, lower_col) != (lower_col + self._width * lower_row):
                    print "tile (" + str(lower_row) + ", " + str(lower_col) + ") is not solved"
                    return False
                    
        # All tiles in row i to the right of position (i,j) are positioned at their solved location.
        for right_col in range(target_col + 1, self._width):
            if self.get_number(target_row, right_col) != (right_col + self._width * target_row):
                print "tile (" + str(target_row) + ", " + str(right_col) + ") is not solved"
                return False
        return True
        
    def position_tile(self, target_row, target_col, tile_row = None, tile_col = None):
        """
        Move the correct tile at (tile_row, tile_col) to the target position (target_row, target_col)
        Updates puzzle and returns a move string
        """
        if tile_row == None and tile_col == None:
            tile_row = target_row
            tile_col = target_col
        
        move = ''
        while self.current_position(tile_row, tile_col) != (target_row, target_col):
            curr_pos = self.current_position(tile_row, tile_col)
        
            # target tile's current position above the target position
            if curr_pos[0] < target_row:
                # move 0 tile to curr_pos
                step = (target_row - curr_pos[0]) * 'u'
                if curr_pos[1] <= target_col:
                    step += (target_col - curr_pos[1]) * 'l'
                else:
                    step += (curr_pos[1] - target_col) * 'r'
                self.update_puzzle(step)
                move += step
                
                # move 0 back to target position
                if self.current_position(tile_row, tile_col)[0] == target_row:
                    # if curr_pos == target, 0 must be right above it, so reset tile 0 and we're done
                    self.update_puzzle('ld')
                    move += 'ld'
                    break
                if curr_pos[1] == target_col:
                    step = 'l' + (target_row - curr_pos[0]) * 'd' + 'r'
                elif curr_pos[1] < target_col:
                    step = (target_row - curr_pos[0]) * 'd' + (target_col - curr_pos[1]) * 'r'
                else:
                    if curr_pos[0] == 0:
                        step = 'd' + (curr_pos[1] - target_col + 1) * 'l' + (target_row - curr_pos[0] - 1) * 'd' + 'r'
                    elif curr_pos[0] == 1:
                        step = 'u' + (curr_pos[1] - target_col + 1) * 'l' + (target_row - curr_pos[0] + 1) * 'd' + 'r'
                    elif curr_pos[0] == 2:
                        step = 'u' + (curr_pos[1] - target_col + 1) * 'l' + (target_row - curr_pos[0] + 1) * 'd' + 'r'
                self.update_puzzle(step)
                move += step
            
            # target tile's current position on the same row to the left
            if curr_pos[0] == target_row and curr_pos[1] < target_col:
                # move 0 tile to curr_pos
                step = (target_col - curr_pos[1]) * 'l'
                self.update_puzzle(step)
                move += step
                
                # move 0 back to target position
                if self.current_position(tile_row, tile_col)[1] == target_col:
                    # if curr_pos == target, 0 must be to its left, so just break out of the loop
                    break
                step = 'u' + (target_col - curr_pos[1]) * 'r' + 'd'
                self.update_puzzle(step)
                move += step
                
            # target tile's current position on the same row to the right
            if curr_pos[0] == target_row and curr_pos[1] > target_col:
                # move 0 tile to curr_pos
                step = (curr_pos[1] - target_col) * 'r'
                self.update_puzzle(step)
                move += step
                
                # move 0 back to target position
                if self.current_position(tile_row, tile_col)[1] == target_col:
                    # if curr_pos == target, 0 must be to its right
                    self.update_puzzle('ulld')
                    move += 'ulld'
                    break
                step = 'u' + (curr_pos[1] - target_col) * 'l' + 'd'
                self.update_puzzle(step)
                move += step
        
        return move

    def solve_interior_tile(self, target_row, target_col):
        """
        Place correct tile at target position
        Updates puzzle and returns a move string
        """
        assert self.lower_row_invariant(target_row, target_col), "checkpoint 1"
        move = self.position_tile(target_row, target_col)
        assert self.lower_row_invariant(target_row, target_col - 1), "checkpoint 2"

        return move

    def solve_col0_tile(self, target_row):
        """
        Solve tile in column zero on specified row (> 1)
        Updates puzzle and returns a move string
        """
        assert self.lower_row_invariant(target_row, 0), "checkpoint 3"
        
        # move the zero tile from (i,0) to (i−1,1)
        self.update_puzzle('ur')
        move = 'ur'
        if self.current_position(target_row, 0) == (target_row, 0):
            step = (self._width - 2) * 'r'
            self.update_puzzle(step)
            move += step
            assert self.lower_row_invariant(target_row - 1, self._width - 1), "checkpoint 4"
            return move
        
        # move the target tile to (i−1,1)
        step = self.position_tile(target_row - 1, 1, target_row, 0)
        move += step
        
        # apply the move string for a 3×2 puzzle
        step = 'ruldrdlurdluurddlur' + (self._width - 2) * 'r'
        self.update_puzzle(step)
        move += step

        assert self.lower_row_invariant(target_row - 1, self._width - 1), "checkpoint 5"
        return move

    #############################################################
    # Phase two methods

    def row0_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row zero invariant
        at the given column (col > 1)
        Returns a boolean
        """
        # Tile zero is positioned at (0,j).
        if self.get_number(0, target_col) != 0:
            print "target tile is not zero"
            return False
            
        # All tiles in row 0 but to the right of (0,j) are positioned at their solved location.
        for right_col in range(target_col + 1, self._width):
            if self.get_number(0, right_col) != right_col:
                print "tile (" + str(0) + ", " + str(right_col) + ") is not solved"
                return False
                    
        # All tiles in row 1 to the right of position (i,j-1) are positioned at their solved location.
        for right_col in range(target_col, self._width):
            if self.get_number(1, right_col) != (right_col + self._width):
                print "tile (" + str(1) + ", " + str(right_col) + ") is not solved"
                return False
        
        # check last two rows
        if self._height == 3:
            first_row = 2
        elif self._height >= 4:
            first_row = self._height - 2
        elif self._height == 2:
            first_row = 999
        for below_row in range(first_row, self._height):
            for below_col in range(self._width):
                if self.get_number(below_row, below_col) != (below_col + self._width * below_row):
                    print "tile (" + str(below_row) + ", " + str(below_col) + ") is not solved"
                    return False
            
        return True

    def row1_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row one invariant
        at the given column (col > 1)
        Returns a boolean
        """
        # Tile zero is positioned at (1,j).
        if self.get_number(1, target_col) != 0:
            print "target tile is not zero"
            return False
            
        # All tiles in row 1 but to the right of (1,j) are positioned at their solved location.
        for right_col in range(target_col + 1, self._width):
            if self.get_number(1, right_col) != (right_col + self._width):
                print "tile (" + str(1) + ", " + str(right_col) + ") is not solved"
                return False
                
        # check last two rows
        if self._height == 3:
            first_row = 2
        elif self._height >= 4:
            first_row = self._height - 2
        elif self._height == 2:
            first_row = 999
        for below_row in range(first_row, self._height):
            for below_col in range(self._width):
                if self.get_number(below_row, below_col) != (below_col + self._width * below_row):
                    print "tile (" + str(below_row) + ", " + str(below_col) + ") is not solved"
                    return False
            
        return True

    def solve_row0_tile(self, target_col):
        """
        Solve the tile in row zero at the specified column
        Updates puzzle and returns a move string
        """
        assert self.row0_invariant(target_col), "checkpoint 6"
        
        # move the zero tile from (0,j) to (1,j-1)
        self.update_puzzle('ld')
        move = 'ld'
        if self.current_position(0, target_col) == (0, target_col):
            assert self.row1_invariant(target_col - 1), "checkpoint 7"
            return move
        
        # move the target tile to position (1,j−1) with tile zero in position (1,j−2)
        step = self.position_tile(1, target_col - 1, 0, target_col)
        move += step
        
        # apply the move string for a 2x3 puzzle
        step = 'urdlurrdluldrruld'
        self.update_puzzle(step)
        move += step
        
        assert self.row1_invariant(target_col - 1), "checkpoint 8"
        
        return move

    def solve_row1_tile(self, target_col):
        """
        Solve the tile in row one at the specified column
        Updates puzzle and returns a move string
        """
        assert self.row1_invariant(target_col), "checkpoint 9"
        
        move = self.position_tile(1, target_col)
        step = 'ur'
        self.update_puzzle(step)
        move += step
            
        assert self.row0_invariant(target_col), "checkpoint 10"

        return move

    ###########################################################
    # Phase 3 methods
    
    def check_2x2_solved(self):
        """
        Check if 2x2 puzzle is solved, return a boolean
        """
        for row in range(2):
            for col in range(2):
                if self.get_number(row, col) != (col + self._width * row):
                    return False
        return True
        
    def check_puzzle_solved(self):
        """
        Check if the whole puzzle is solved, return a boolean
        """
        for row in range(self._height):
            for col in range(self._width):
                if self.get_number(row, col) != (col + self._width * row):
                    return False
        return True

    def solve_2x2(self):
        """
        Solve the upper left 2x2 part of the puzzle
        Updates the puzzle and returns a move string
        """
        assert self.row1_invariant(1), "checkpoint 11"
        move = ""
        step = "r"
        
        # iteratively apply "u,l,d,r", since tile 0 is at (1,1)
        for dummy_run in range(100):
            # check if its solved, return if so
            if self.check_2x2_solved():
                break
            if step == "u":
                step = "l"
            elif step == "l":
                step = "d"
            elif step == "d":
                step = "r"
            elif step == "r":
                step = "u"
            
            self.update_puzzle(step)
            move += step

        return move

    def solve_puzzle(self):
        """
        Generate a solution string for a puzzle
        Updates the puzzle and returns a move string
        """
        height = self.get_height()
        width = self.get_width()
        move = ""
        
        # check if puzzle is already solved
        if self.check_puzzle_solved():
            return move
        
        # move tile 0 to the last tile
        zero_row, zero_col = self.current_position(0, 0)
        step = (width - 1 - zero_col) * 'r' + (height - 1 - zero_row) * 'd'
        self.update_puzzle(step)
        move += step

        # solve the bottom rows except the first 2 rows
        if self._height >= 3:
            for col in range(width - 1, 0, -1):
                step = self.solve_interior_tile(height - 1, col)
                move += step
            step = self.solve_col0_tile(height - 1)
            move += step
        
        if self._height >= 4:
            for row in range(height - 2, 1, -1):
                for col in range(width - 1, 0, -1):
                    step = self.solve_interior_tile(row, col)
                    move += step
                step = self.solve_col0_tile(row)
                move += step
        
        # solve the rightmost (width − 2) columns of the first two rows
        for col in range(width - 1, 1, -1):
            step = self.solve_row1_tile(col)
            move += step
            step = self.solve_row0_tile(col)
            move += step
            
        # solve the last 2x2 puzzle
        step = self.solve_2x2()
        move += step
        
        return move
        

# Start interactive simulation
# poc_fifteen_gui.FifteenGUI(Puzzle(4, 4))
