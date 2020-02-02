"""
Recurrence visualization tool

Circles correspond to instances of recurrence.  Area of circle is proportional to value of n
Click on circle to apply recurrence.  Note that rhs of recurrence is accumulated 
in "Current work".  Once all circles are gone, "Current work" contains the solutions
to the currence.

Specify structure of recurrence using the toggles "Reduction type", 
"Child type", and "Work type".  The base case is always r(1) = 1.

Set the desired initial value n for the recurrence in the input field 

Reset the simulation using the "Reset simulation" button
"""

import simplegui
import random
import math

# Global constants

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Lists that encode various components of basic recurrence
REDUCTION_FUNS = [(lambda n: n // 2), (lambda n: n - 1)]
CHILD_FUNS = [(lambda n: 1), (lambda n: 2), (lambda n: n)]
WORK_FUNS = [(lambda n: 0), (lambda n: 1), (lambda n: n)]

REDUCTION_TYPES = ["n / 2", "n - 1"]
CHILD_TYPES = ["1", "2", "n"]
WORK_TYPES = ["0", "1", "n"]

        
# helper function for distance

def dist(pt1, pt2):
    """
    Helper function that computes the Euclidean distance between points p1 and p2
    """
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

class Broom:
    """
    Representation for broom for use in recurrence simulation
    """
    
    def __init__(self, capacity, reduction_type, child_type, work_type, position, velocity):
        """
        Create broom with given capacity, reduction_type, children and work.  Also given a position and velocity
        """
        self._capacity = capacity
        self._reduction_type = reduction_type
        self._child_type = child_type
        self._work_type = work_type
        
        # visualize capacity as a circle with area = 100 * capacity
        self._radius = 10 * math.sqrt(self._capacity / math.pi)
        self._pos = position
        self._vel = velocity
        
    def __str__(self):
        """
        Return string rep for Broom
        """
        return "Broom with capacity = " + int(self._capacity) + ", children = " + \
               int(self._child_type) + ", work = " + self._work_type
                
    def update(self):
        """
        Update the position and velocity of a ball using wrapped canvas
        """
        
        # Update position
        self._pos[0] = (self._pos[0] + self._vel[0]) % CANVAS_WIDTH
        self._pos[1] = (self._pos[1] + self._vel[1]) % CANVAS_HEIGHT
        
    def get_pos(self):
        """
        Getter for position
        """
        return self._pos
    
    def get_radius(self):
        """
        Getter for radius
        """
        return self._radius
        
        
    def split(self, frame):
        """
        Apply recurrence to broom
        """
        if self._capacity == 1:
            frame._total_work += 1
            return
        
        frame._total_work += WORK_FUNS[self._work_type](self._capacity)        
        num_children = CHILD_FUNS[self._child_type](self._capacity)
        new_capacity = REDUCTION_FUNS[self._reduction_type](self._capacity)

        for dummy_index in range(num_children):
            new_pos = list(self._pos)
            new_vel = [random.randrange(-3, 4) / 3.0, random.randrange(-3, 4) / 3.0]
            frame.add_broom(Broom(new_capacity, self._reduction_type, self._child_type, 
                                    self._work_type, new_pos, new_vel))        
              

    def draw(self, canvas):
        """
        Draw a broom with a given radius at specified position
        """

        canvas.draw_circle(self._pos, self._radius, 1, "Black", "Yellow")


class RecurrenceSimulator:
    """
    GUI for recurrence simulator
    """    

    def __init__(self):
        """ 
        Initializer to create frame, sets handlers and initialize list of balls to be empty
        """
        self._frame = simplegui.create_frame("Recurrence simulator", 
                                            CANVAS_WIDTH, CANVAS_HEIGHT)
        self._frame.set_draw_handler(self.draw)
        self._frame.set_mouseclick_handler(self.click)
        self._frame.set_canvas_background("Blue")
        
        # add UI to choose recurrence
        self._reduction_label = self._frame.add_label("Recurrence", 200)
        self._frame.add_button("Select number of calls", self.set_child_type, 200)
        self._frame.add_button("Select type of reduction", self.set_reduction_type, 200)
        self._frame.add_button("Select amount of work", self.set_work_type, 200)
        
        # add label with current recurrence
        self._frame.add_input("Set initial value for n", self.set_capacity, 200)
        self._frame.add_button("Reset simulation", self.reset, 200)
        
        # initialize state of UI
        self._current_reduction_type = 0
        self._current_child_type = 1
        self._current_work_type = 1
        self.update_recur()
        
        # initialize UI quantities
        self._total_work = 0
        self._initial_capacity = 16
        self._broom_list = []
        self._frame.start()
        self.reset()        

        
    def update_recur(self):
        """
        Update the recurrence label after change the recurrence parameters
        """        
        reduction_text = "r(n) = " + CHILD_TYPES[self._current_child_type] + \
                     " * r(" + REDUCTION_TYPES[self._current_reduction_type] + ") + " + \
                     WORK_TYPES[self._current_work_type]
        self._reduction_label.set_text(reduction_text)
        
    def set_capacity(self, text):
        """
        Input handler that sets current capacity for new broom
        """
        self._initial_capacity = int(text)
        self._broom_list = []
        self._total_work = 0
        self.reset()
        
    def set_reduction_type(self):
        """
        Button handler that sets the current type of split for brooms
        """
        self._current_reduction_type = (self._current_reduction_type + 1) % len(REDUCTION_TYPES)
        self.update_recur()
        self._broom_list = []
        self._total_work = 0
        self.reset()

    def set_child_type(self):
        """
        Button handler that sets the current type of child for brooms
        """
        self._current_child_type = (self._current_child_type + 1) % len(CHILD_TYPES)
        self.update_recur()
        self._broom_list = []
        self._total_work = 0
        self.reset()

    def set_work_type(self):
        """
        Button handler that sets the current type of work for brooms
        """
        self._current_work_type = (self._current_work_type + 1) % len(WORK_TYPES)
        self.update_recur()
        self._broom_list = []
        self._total_work = 0
        self.reset()


    def reset(self):
        """
        Reset the simulation with a single new broom based on the current GUI parameters
        """
        new_pos = [CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2]
        new_vel = [random.randrange(-3, 4) / 3.0, random.randrange(-3, 4) / 3.0]
        self._total_work = 0
        self._broom_list = [Broom(self._initial_capacity, self._current_reduction_type, 
                                      self._current_child_type, self._current_work_type,   
                                      new_pos, new_vel)]        
                
    def add_broom(self, broom):
        """
        Add a broom to the list of brooms
        """
        self._broom_list.append(broom)        

    def click(self, pos):
        """ 
        Event handler for mouse clicks, takes mouse position pos, 
        finds selected broom, removes broom from broom_list and splits broom
        """  
        for broom in self._broom_list:
            if dist(pos, broom.get_pos()) <= broom.get_radius():
                self._broom_list.remove(broom)
                broom.split(self)
                return
                

    def draw(self, canvas):
        """
        Handler for draw events ............
        """
        for broom in self._broom_list:
            broom.update()
            broom.draw(canvas)
       
        canvas.draw_text("Current work = " + str(self._total_work), [CANVAS_WIDTH - 200, 30], 24, "White")
        canvas.draw_text("Initial value for n = " + str(self._initial_capacity), [30, 30], 24, "White")
            
# Start interactive simulation    
RecurrenceSimulator()
                

    
