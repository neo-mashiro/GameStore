"""
Student facing code for Tantrix Solitaire
http://www.jaapsch.net/puzzles/tantrix.htm

Game is played on a grid of hexagonal tiles.
All ten tiles for Tantrix Solitaire and place in a corner of the grid.
Click on a tile to rotate it.  Cick and drag to move a tile.

Goal is to position the 10 provided tiles to form
a yellow, red or  blue loop of length 10
"""


# Core modeling idea - a triangular grid of hexagonal tiles are 
# model by integer tuples of the form (i, j, k) 
# where i + j + k == size and i, j, k >= 0.

# Each hexagon has a neighbor in one of six directions
# These directions are modeled by the differences between the 
# tuples of these adjacent tiles

# Numbered directions for hexagonal grid, ordered clockwise at 60 degree intervals
DIRECTIONS = {0 : (-1, 0, 1), 1 : (-1, 1, 0), 2 : (0, 1, -1), 
              3 : (1, 0, -1), 4 : (1, -1, 0), 5 : (0,  -1, 1)}

def reverse_direction(direction):
    """
    Helper function that returns opposite direction on hexagonal grid
    """
    num_directions = len(DIRECTIONS)
    return (direction + num_directions / 2) % num_directions


# Color codes for ten tiles in Tantrix Solitaire
# "B" denotes "Blue", "R" denotes "Red", "Y" denotes "Yellow"
SOLITAIRE_CODES = ["BBRRYY", "BBRYYR", "BBYRRY", "BRYBYR", "RBYRYB",
                "YBRYRB", "BBRYRY", "BBYRYR", "YYBRBR", "YYRBRB"]

# Minimal size of grid to allow placement of 10 tiles
MINIMAL_GRID_SIZE = 4



class Tantrix:
    """
    Basic Tantrix game class
    """
    
    def __init__(self, size):
        """
        Create a triangular grid of hexagons with size + 1 tiles on each side.
        """
        assert size >= MINIMAL_GRID_SIZE
        self._tiling_size = size

        # Initialize dictionary tile_value to contain codes for ten
        # tiles in Solitaire Tantrix in one 4x4 corner of grid
        self._tile_value = {}
        counter = 0        
        for index_i in range(MINIMAL_GRID_SIZE):
            for index_j in range(MINIMAL_GRID_SIZE - index_i):
                index_k = self._tiling_size - (index_i + index_j)
                grid_index = (index_i, index_j, index_k)
                self.place_tile(grid_index, SOLITAIRE_CODES[counter])
                counter += 1

    def __str__(self):
        """
        Return string of dictionary of tile positions and values
        """
        return str(self._tile_value)
        
    def get_tiling_size(self):
        """
        Return size of board for GUI
        """
        return self._tiling_size
    
    def tile_exists(self, index):
        """
        Return whether a tile with given index exists
        """
        return self._tile_value.has_key(index)
    
    def place_tile(self, index, code):
        """
        Play a tile with code at cell with given index
        """
        self._tile_value[index] = code       

    def remove_tile(self, index):
        """
        Remove a tile at cell with given index
        and return the code value for that tile
        """
        return self._tile_value.pop(index)
               
    def rotate_tile(self, index):
        """
        Rotate a tile clockwise at cell with given index
        """
        value = self._tile_value[index]
        new_value = value[-1] + value[:-1] 
        self._tile_value[index] = new_value

    def get_code(self, index):
        """
        Return the code of the tile at cell with given index
        """
        return self._tile_value[index]

    def get_neighbor(self, index, direction):
        """
        Return the index of the tile neighboring the tile with given index in given direction
        """
        neighbor_offset = DIRECTIONS[direction]
        neighbor_index = tuple([index[dim] + neighbor_offset[dim] for dim in range(3)])
        return neighbor_index

    def is_legal(self):
        """
        Check whether a tile configuration obeys color matching rules for adjacent tiles
        """
        
        for tile_index in self._tile_value.keys():
            tile_code = self._tile_value[tile_index]
            for direction in DIRECTIONS.keys():
                neighbor_index = self.get_neighbor(tile_index, direction)
                if self.tile_exists(neighbor_index):
                    neighbor_code = self.get_code(neighbor_index)
                    if tile_code[direction] != neighbor_code[reverse_direction(direction)]:
                        return False
        return True
            
    def has_loop(self, color):
        """
        Check whether a tile configuration has a loop of size 10 of given color
        """
        if not self.is_legal():
            return False        
        
        # choose arbitrary starting point
        tile_indices = self._tile_value.keys()
        start_index = tile_indices[0]
        start_code = self._tile_value[start_index]
        next_direction = start_code.find(color)
        next_index = self.get_neighbor(start_index, next_direction)
        current_length = 1
   
        # loop through neighboring tiles that match given color
        while start_index != next_index:
            current_index = next_index
            if not self.tile_exists(current_index):
                return False
            current_code = self._tile_value[current_index]
            if current_code.find(color) == reverse_direction(next_direction):
                next_direction = current_code.rfind(color)
            else:
                next_direction = current_code.find(color)
            next_index = self.get_neighbor(current_index, next_direction)
            current_length += 1
      
        return current_length == len(SOLITAIRE_CODES)

    
# run GUI for Tantrix
import poc_tantrix_gui
poc_tantrix_gui.TantrixGUI(Tantrix(6))