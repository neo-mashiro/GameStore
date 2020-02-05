# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False

FRICTION_FACTOR = 0.98

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info_off = ImageInfo([45, 45], [90, 90], 35)
ship_info_on = ImageInfo([135, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def process_sprite_group(canvas, object_set):
    for obj in set(object_set):
        obj.update()
        if obj.update():
            object_set.remove(obj)
        else:
            obj.draw(canvas)

def group_collide(group, other_object):
    for obj in set(group):
        if obj.collide(other_object):
            group.remove(obj)
            return True
    return False
    
def group_group_collide(rocks, missiles):
    count = 0
    for rock in set(rocks):
        #group_collide(missiles, rock)
        if group_collide(missiles, rock):
            count += 1
            rocks.remove(rock)
    return count

def new_game():
    global score, lives, time, my_ship, rock_group, missile_group
    score = 0
    lives = 3
    time = 0
    started = False
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info_off)
    rock_group = set()
    missile_group = set()
    soundtrack.rewind()
    soundtrack.play()
    timer.start()

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def rotate(self, direction):
        if direction == "left":
            self.angle_vel -= 0.05
        elif direction == "right":
            self.angle_vel += 0.05
            
    def navigate(self, on = True):
        if on:
            self.thrust = True
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            self.thrust = False
            ship_thrust_sound.rewind()
            
    def shoot(self):
        forward = angle_to_vector(self.angle)
        cannon_pos = [self.pos[0] + forward[0] * self.radius
                     ,self.pos[1] + forward[1] * self.radius]
        missile_vel = [self.vel[0] + 5 * forward[0]
                      ,self.vel[1] + 5 * forward[1]]
        
        a_missile = Sprite(cannon_pos,                                # pos
                           missile_vel,                               # vel
                           0,                                         # ang
                           0,                                         # ang_vel
                           missile_image, missile_info, missile_sound
                          )
        missile_group.add(a_missile)
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
        
    def draw(self,canvas):
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White", self.angle)
        if self.thrust:
            canvas.draw_image(self.image, ship_info_on.get_center(), ship_info_on.get_size(),
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, ship_info_off.get_center(), ship_info_off.get_size(),
                              self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * 0.2
            self.vel[1] += acc[1] * 0.2
        
        self.vel[0] *= FRICTION_FACTOR
        self.vel[1] *= FRICTION_FACTOR
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
            
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def collide(self, other_object):
        if dist(self.pos, other_object.get_position()) <= self.radius + other_object.get_radius():
            return True
        return False
   
    def draw(self, canvas):
        # canvas.draw_circle(self.pos, self.radius, 1, "Red", "Red")
        canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)
    
    def update(self):
        self.age += 1
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.angle += self.angle_vel
        
        if self.age >= self.lifespan:
            return True
        else:
            return False

           
def draw(canvas):
    global time, score, lives, started, rock_group, missile_group, my_ship
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()

    # draw score and lives
    canvas.draw_text('lives: ' + str(lives), [50, 50], 25, "Aqua", "monospace")
    canvas.draw_text('score: ' + str(score), [650, 50], 25, "Aqua", "monospace")
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
    
    # draw groups of rocks and missiles
    process_sprite_group(canvas, rock_group)
    process_sprite_group(canvas, missile_group)
    
    # draw lives
    if group_collide(rock_group, my_ship):
        lives -= 1
    
    # draw scores
    score += group_group_collide(rock_group, missile_group)
    
    # game over
    if lives <= 0:
        started = False
        rock_group = set()
        missile_group = set()
        timer.stop()
            
# timer handler that spawns a rock    
def rock_spawner():
    hard_level = 1
    hard_level += (time // 1200) * 0.5
    if len(rock_group) <= 5 and time > 60 and started:
        a_rock = Sprite([random.randrange(0, WIDTH), random.randrange(0, HEIGHT)],   # pos
                        [hard_level * (random.random() - 0.5), hard_level * (random.random() - 0.5)],  # vel
                        random.random() * math.pi * 2,                         # ang
                        (random.random() - 0.5) * 0.2 ,                               # ang_vel
                        asteroid_image, asteroid_info
                       )
        if dist(a_rock.get_position(), my_ship.get_position()) > 2 * (a_rock.get_radius() + my_ship.get_radius()):
            rock_group.add(a_rock)

# key handlers
def keydown(key):
    if simplegui.KEY_MAP["left"] == key:
        my_ship.rotate("left")
    elif simplegui.KEY_MAP["right"] == key:
        my_ship.rotate("right")
    elif simplegui.KEY_MAP["up"] == key:
        my_ship.navigate(on = True)
    elif simplegui.KEY_MAP["space"] == key:
        my_ship.shoot()

def keyup(key):
    if simplegui.KEY_MAP["left"] == key:
        my_ship.angle_vel = 0
    elif simplegui.KEY_MAP["right"] == key:
        my_ship.angle_vel = 0
    elif simplegui.KEY_MAP["up"] == key:
        my_ship.navigate(on = False)
    elif simplegui.KEY_MAP["space"] == key:
        pass
        
# mouse handlers
def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        new_game()

# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# register handlers
frame.set_draw_handler(draw)
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
new_game()
frame.start()