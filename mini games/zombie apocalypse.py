"""
Student portion of Zombie Apocalypse mini-project
"""

import random
import poc_grid
import poc_queue
import poc_zombie_gui

# global constants
EMPTY = 0 
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7

class Apocalypse(poc_grid.Grid):
    """
    Class for simulating zombie pursuit of human on grid with
    obstacles
    """

    def __init__(self, grid_height, grid_width, obstacle_list = None, 
                 zombie_list = None, human_list = None):
        """
        Create a simulation of given size with given obstacles,
        humans, and zombies
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        if obstacle_list != None:
            for cell in obstacle_list:
                self.set_full(cell[0], cell[1])
        if zombie_list != None:
            self._zombie_list = list(zombie_list)
        else:
            self._zombie_list = []
        if human_list != None:
            self._human_list = list(human_list)  
        else:
            self._human_list = []
        
    def clear(self):
        """
        Set cells in obstacle grid to be empty
        Reset zombie and human lists to be empty
        """
        poc_grid.Grid.clear(self)
        self._zombie_list = []
        self._human_list = []
        
    def add_zombie(self, row, col):
        """
        Add zombie to the zombie list
        """
        self._zombie_list.append((row, col))
                
    def num_zombies(self):
        """
        Return number of zombies
        """
        return len(self._zombie_list)
          
    def zombies(self):
        """
        Generator that yields the zombies in the order they were
        added.
        """
        for index in range(self.num_zombies()):
            yield self._zombie_list[index]

    def add_human(self, row, col):
        """
        Add human to the human list
        """
        self._human_list.append((row, col))
        
    def num_humans(self):
        """
        Return number of humans
        """
        return len(self._human_list)
    
    def humans(self):
        """
        Generator that yields the humans in the order they were added.
        """
        for index in range(self.num_humans()):
            yield self._human_list[index]
        
    def compute_distance_field(self, entity_type):
        """
        Function computes and returns a 2D distance field
        Distance at member of entity_list is zero
        Shortest paths avoid obstacles and use four-way distances
        """
        # visited keeps track of if a cell has been calculated, if so, skip it in the loop
        visited = poc_grid.Grid(self.get_grid_height(), self.get_grid_width())
        # distance_field records the Manhattan distance for each cell
        distance_field = [[self.get_grid_height() * self.get_grid_width() \
                           for dummy_col in range(self.get_grid_width())] \
                             for dummy_row in range(self.get_grid_height())]
                             
        boundary = poc_queue.Queue()
        if len(self._zombie_list) > 0:
            for zombie in self.zombies():
                boundary.enqueue(zombie)
                visited.set_full(zombie[0], zombie[1])
                distance_field[zombie[0]][zombie[1]] = EMPTY
        else:
            for human in self.humans():
                boundary.enqueue(human)
                visited.set_full(human[0], human[1])
                distance_field[human[0]][human[1]] = EMPTY
                
        while len(boundary) != 0:
            cell = boundary.dequeue()
            four_neighbors = self.four_neighbors(cell[0], cell[1])
            for nbr in four_neighbors:
                if visited.is_empty(nbr[0], nbr[1]) and self.is_empty(nbr[0], nbr[1]):
                    visited.set_full(nbr[0], nbr[1])
                    # enqueue() makes the calculation able to spread over the grid, like a wildfire
                    boundary.enqueue(nbr)
                    distance_field[nbr[0]][nbr[1]] = distance_field[cell[0]][cell[1]] + 1
                    
        return distance_field
    
    def move_humans(self, zombie_distance_field):
        """
        Function that moves humans away from zombies, diagonal moves
        are allowed
        """
        for cell in list(self.humans()):
            eight_neighbors = self.eight_neighbors(cell[0], cell[1])
            
            max_dist = zombie_distance_field[cell[0]][cell[1]]
            target_tile = cell
            for tile in eight_neighbors:
                if zombie_distance_field[tile[0]][tile[1]] > max_dist \
                and self.is_empty(tile[0], tile[1]):
                    max_dist = zombie_distance_field[tile[0]][tile[1]]
                    target_tile = tile
            move = target_tile
            # set old position to empty
            self.set_empty(cell[0], cell[1])
            # make the best move
            self._human_list[self._human_list.index(cell)] = move
    
    def move_zombies(self, human_distance_field):
        """
        Function that moves zombies towards humans, no diagonal moves
        are allowed
        """
        for cell in list(self.zombies()):
            four_neighbors = self.four_neighbors(cell[0], cell[1])
            
            min_dist = human_distance_field[cell[0]][cell[1]]
            target_tile = cell
            for tile in four_neighbors:
                if human_distance_field[tile[0]][tile[1]] < min_dist:
                    min_dist = human_distance_field[tile[0]][tile[1]]
                    target_tile = tile
            move = target_tile
            # set old position to empty
            self.set_empty(cell[0], cell[1])
            # make the best move
            self._zombie_list[self._zombie_list.index(cell)] = move

# poc_zombie_gui.run_gui(Apocalypse(30, 40))
