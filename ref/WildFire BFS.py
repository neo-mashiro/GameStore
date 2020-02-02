"""
Simulation of wild fire using breadth first search (BFS)
Click in the canvas to add cells to the boundary of the fire
"""

import poc_grid
import poc_queue
import poc_wildfire_gui

# constants
EMPTY = 0 
FULL = 1


class WildFire(poc_grid.Grid):
    """
    Class that models a burning wild fire using a grid and a queue
    The grid stores whether a cell is burned (FULL) or unburned (EMPTY)
    The queue stores the cells on the boundary of the fire
    """

    def __init__(self, grid_height, grid_width, queue = poc_queue.Queue()):
        """
        Override initializer for Grid, add queue to store boundary of fire
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        self._fire_boundary = queue

    def clear(self):
        """
        Set cells to be unburned and the fire boundary to be empty
        """
        poc_grid.Grid.clear(self)
        self._fire_boundary.clear()  


    def enqueue_boundary(self, row, col):
        """
        Add cell with index (row, col) the boundary of the fire
        """
        self._fire_boundary.enqueue((row, col))
    
    def dequeue_boundary(self):
        """
        Remove an element from the boundary of the fire
        """
        return self._fire_boundary.dequeue()
    
    def boundary_size(self):
        """
        Return the size of the boundary of the fire
        """
        return len(self._fire_boundary)

    def fire_boundary(self):
        """
        Generator for the boundary of the fire
        """
        for cell in self._fire_boundary:
            yield cell
        # alternative syntax
        #return (cell for cell in self._fire_boundary)
    
    def update_boundary(self):
        """
        Function that spreads the wild fire using one step of BFS
        Updates both the cells and the fire_boundary
        """
        cell = self._fire_boundary.dequeue()
        neighbors = self.four_neighbors(cell[0], cell[1])
        #neighbors = self.eight_neighbors(cell[0], cell[1])
        for neighbor in neighbors:
            if self.is_empty(neighbor[0], neighbor[1]):
                self.set_full(neighbor[0], neighbor[1])
                self._fire_boundary.enqueue(neighbor)

                
# run gui to visualize wildfire                
poc_wildfire_gui.run_gui(WildFire(30, 40))
