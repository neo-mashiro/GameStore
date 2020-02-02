"""
Ball/ball collision simulator, currrently spawns balls via mouse clicks,
Implemented wih quadratic collision check
"""

import simplegui
import random
import time
import math
import codeskulptor
import simpleplot
codeskulptor.set_timeout(10)

# global constants
BALL_RADIUS = 25
BALL_DIAMETER_SQUARED = 4 * BALL_RADIUS ** 2
VEL_RANGE = 6

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

def dot(vec1, vec2):
    """
    Return the dot product of two 2D vectors
    """
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]


class Ball:
    """
    Representation for balls used in collision simulations
    """
    
    def __init__(self, position, velocity):
        """
        Create balls, takes the postion of the ball's center (in pixels)
        and it's velocity in pixels per update
        """
        
        self._pos = position
        self._vel = velocity
        
    def get_pos(self):
        """
        Getter for position
        """
        return self._pos
    
    def get_vel(self):
        """
        Getter for velocity
        """
        return self._vel
    
    def set_vel(self, velocity):
        """
        Setter for velocity
        """
        self._vel = velocity
        
    def update(self, ball_list, ball_num):
        """
        Update the position and velocity of a ball
        """
        
        # Update position
        self._pos[0] += self._vel[0]
        self._pos[1] += self._vel[1]
        
        # Update velocity due to hitting the walls
        if (self._pos[0] <= BALL_RADIUS) or (self._pos[0] >= CANVAS_WIDTH - 1 - BALL_RADIUS):
            self._vel[0] = -self._vel[0]
        if (self._pos[1] <= BALL_RADIUS) or (self._pos[1] >= CANVAS_HEIGHT - 1 - BALL_RADIUS):
            self._vel[1] = -self._vel[1]
            
        # test for collision with balls with index less than ball_num
        for idx in range(ball_num):
            other_ball = ball_list[idx]
            if self.collide(other_ball):
                self.bounce(other_ball)
                
    def collide(self, other_ball):
        """
        Method to check whether two balls collide
        """
        other_ball_pos = other_ball.get_pos()
        distance_squared = (other_ball_pos[0] - self._pos[0]) ** 2 + \
                               (other_ball_pos[1] - self._pos[1]) ** 2
        return distance_squared <= BALL_DIAMETER_SQUARED
        
                
    def bounce(self, other_ball):
        """
        Update the velocities for two colliding balls
        """
        # Compute normal for collision
        other_ball_pos = other_ball.get_pos()        
        center_chord = [other_ball_pos[0] - self._pos[0], other_ball_pos[1] - self._pos[1]]   
        chord_length = math.sqrt(center_chord[0] ** 2 + center_chord[1] ** 2)
        normal = [center_chord[0] / chord_length, center_chord[1]/ chord_length]
                
        # Compute tangential component of velocities for both balls
        other_ball_vel = other_ball.get_vel()        
        self_dot = dot(normal, self._vel)
        self_tangent = [self._vel[0] - self_dot * normal[0], 
                        self._vel[1] - self_dot * normal[1]]
        other_dot = dot(normal, other_ball_vel)
        other_tangent = [other_ball_vel[0] - other_dot * normal[0],
                         other_ball_vel[1] - other_dot * normal[1]]

        # Update velocities for both balls                
        self._vel[0] = self_tangent[0] + other_dot * normal[0]
        self._vel[1] = self_tangent[1] + other_dot * normal[1]
        other_ball_vel = [other_tangent[0] + self_dot * normal[0], 
                          other_tangent[1] + self_dot * normal[1]]
        other_ball.set_vel(other_ball_vel)
    
    def draw(self, canvas):
        """
        Draw a ball with given canvas with BALL_RADIUS at specified position
        """
        canvas.draw_circle(self._pos, BALL_RADIUS, 1, "White", "White")


        
class Simulation:
    """
    Class representation for ball physics simulation
    """
    
    def __init__(self):
        """
        Create a simulation
        """
        self._ball_list = []
    
    def add_ball(self, pos):
        """ 
        Add a ball with a random velocity to the simulation
        """
        x_vel = random.randrange(-VEL_RANGE, VEL_RANGE + 1) / float(VEL_RANGE)
        y_vel = random.randrange(-VEL_RANGE, VEL_RANGE + 1) / float(VEL_RANGE)
        new_ball = Ball(list(pos), [x_vel, y_vel])
        
        for ball in self._ball_list:
            if new_ball.collide(ball):
                return
        self._ball_list.append(new_ball)

    def num_balls(self):
        """
        Return the number of balls in the simulation
        """
        return len(self._ball_list)
    
    def update(self):
        """
        Do one physics update for simulation
        """
        for idx in range(len(self._ball_list)):
            ball = self._ball_list[idx]
            ball.update(self._ball_list, idx)

    def draw(self, canvas):
        """
        Draw the balls in the simulation
        """
        for ball in self._ball_list:
            ball.draw(canvas)
    
        


class SimulationGUI:
    """
    Container for interactive content
    """    

    def __init__(self):
        """ 
        Initializer to create frame, sets handlers and initialize list of balls to be empty
        """
        self.simulation = Simulation()
        self._frame = simplegui.create_frame("ball/ball collision simulator", 
                                            CANVAS_WIDTH, CANVAS_HEIGHT)
        self._frame.set_draw_handler(self.draw)
        self._frame.set_mouseclick_handler(self.click)
        self._prev_time = time.time()
        self._frame_rate = 60.0
        
    def start(self):
        """
        Start frame
        """
        self._frame.start()

    def click(self, pos):
        """ 
        Event handler for mouse clicks, takes mouse position pos, 
        adds new ball to ball_list at pos if space is empty
        """
  
        # Create random velocity with max of one pixel per update
        self.simulation.add_ball(pos)

    def draw(self, canvas):
        """
        Handler for draw events, draws balls and some stats
        """
        
        # Compute frame_rate
        current_time = time.time()
        if current_time != self._prev_time:
            self._frame_rate = 0.99 * self._frame_rate + (0.01 / (current_time - self._prev_time))
        self._prev_time = current_time
        
        # Display number of balls and frame rate
        canvas.draw_text("Frame rate " + str(int(self._frame_rate // 1)), [550, 24], 24, "White")  
        canvas.draw_text("Number of balls " + str(self.simulation.num_balls()), [50, 24], 24, "White")
        
        # Draw and update balls
        self.simulation.update()
        self.simulation.draw(canvas)
            
# Start interactive simulation    
def run_gui():
    """
    Encapsulate frame
    """
    gui = SimulationGUI()
    gui.start()
    
run_gui()


# extra plotting code
NUM_UPDATES = 5
TIME_PLOT = True
RATIO_PLOT = False

def plot_performance(plot_length, plot_type):
    """
    Build list that estimates running of physics update for ball_list
    """

    simulation = Simulation()
    plot = []
    
    for index in range(10, plot_length):
        
        # add a ball to ball_list
        while simulation.num_balls() != index:
            simulation.add_ball([random.randrange(CANVAS_WIDTH), random.randrange(CANVAS_HEIGHT)])
        
        # run update for all balls, num_updates times
        start_time = time.time()
        simulation.update()
        estimated_time = (time.time() - start_time) / float(NUM_UPDATES)
        
        if plot_type == TIME_PLOT:
            plot.append([index, estimated_time])
        else:
            plot.append([index, estimated_time / (index ** 2)])
    
    if plot_type == TIME_PLOT:
        simpleplot.plot_lines("Running time for quadratic update", 400, 400, "# balls", "time to update", [plot])    
    else:
        simpleplot.plot_lines("Comparison of running time to quadratic function", 400, 400, "# balls", "ratio", [plot])    

plot_performance(100, TIME_PLOT)
                

    
