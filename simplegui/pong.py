# Implementation of classic arcade game Pong

import simplegui
import random

# initialize globals
WIDTH = 600
HEIGHT = 400       
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80

ball_pos = [WIDTH / 2, HEIGHT / 2]
ball_vel = [0, 0]
paddle1_pos = PAD_HEIGHT / 2
paddle2_pos = PAD_HEIGHT / 2
paddle1_vel = 0
paddle2_vel = 0
score1 = 0
score2 = 0

# spawn a ball at the center of canvas
def spawn_ball(direction):
    global ball_pos, ball_vel
    ball_pos[0] = WIDTH / 2
    ball_pos[1] = HEIGHT / 2
    if direction == 'RIGHT':
        ball_vel[0] = random.randint(0, 1)  # flip a coin 0/1
        ball_vel[1] = -random.randrange(2, 3)
    if direction == 'LEFT':
        ball_vel[0] = -random.randrange(2, 3)
        ball_vel[1] = -random.randrange(2, 3)

# define button handler
def new_game():
    global score1, score2
    score1 = 0
    score2 = 0
    if random.randrange(0,2) == 0:
        spawn_ball('RIGHT')
    else:
        spawn_ball('LEFT')

# define draw handler
def draw(canvas):
    global score1, score2, paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, ball_pos, ball_vel

    # draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1, "White")
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, "White")
    canvas.draw_line([WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1, "White")
        
    # update ball
    if (ball_pos[1] <= BALL_RADIUS) or (ball_pos[1] >= HEIGHT - BALL_RADIUS):
        ball_vel[1] = -ball_vel[1]
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
            
    # draw ball
    canvas.draw_circle([ball_pos[0], ball_pos[1]], BALL_RADIUS, 1, "Red", "Red")
    
    # update paddle's vertical position, keep paddle on the screen
    if (paddle1_pos <= PAD_HEIGHT / 2) and (paddle1_vel < 0):
        paddle1_vel = 0
    elif (paddle1_pos >= HEIGHT - PAD_HEIGHT / 2) and (paddle1_vel > 0):
        paddle1_vel = 0
        
    if (paddle2_pos <= PAD_HEIGHT / 2) and (paddle2_vel < 0):
        paddle2_vel = 0
    elif (paddle2_pos >= HEIGHT - PAD_HEIGHT / 2) and (paddle2_vel > 0):
        paddle2_vel = 0
        
    paddle1_pos += paddle1_vel
    paddle2_pos += paddle2_vel
        
    # draw paddles
    canvas.draw_polygon([[0, paddle1_pos - PAD_HEIGHT / 2]
                        ,[PAD_WIDTH, paddle1_pos - PAD_HEIGHT / 2]
                        ,[PAD_WIDTH, paddle1_pos + PAD_HEIGHT / 2]
                        ,[0, paddle1_pos + PAD_HEIGHT / 2]
                        ], 2, "Blue", "Aqua")
    canvas.draw_polygon([[WIDTH - PAD_WIDTH, paddle2_pos - PAD_HEIGHT / 2]
                        ,[WIDTH, paddle2_pos - PAD_HEIGHT / 2]
                        ,[WIDTH, paddle2_pos + PAD_HEIGHT / 2]
                        ,[WIDTH - PAD_WIDTH, paddle2_pos + PAD_HEIGHT / 2]
                        ], 2, "Blue", "Aqua") 
    
    # determine whether paddle and ball collide
    if ball_pos[0] <= PAD_WIDTH + BALL_RADIUS:
        if (ball_pos[1] < paddle1_pos - PAD_HEIGHT / 2) or (ball_pos[1] > paddle1_pos + PAD_HEIGHT / 2):
            score2 += 1
            spawn_ball('RIGHT')
        else:
            ball_vel[0] = -1.1 * ball_vel[0]
            # ball_vel[1] = -1.1 * ball_vel[1]
    
    if ball_pos[0] >= WIDTH - (PAD_WIDTH + BALL_RADIUS):
        if (ball_pos[1] < paddle2_pos - PAD_HEIGHT / 2) or (ball_pos[1] > paddle2_pos + PAD_HEIGHT / 2):
            score1 += 1
            spawn_ball('LEFT')
        else:
            ball_vel[0] = -1.1 * ball_vel[0]
            # ball_vel[1] = -1.1 * ball_vel[1]
    
    # draw scores
    canvas.draw_text('Player A: ' + str(score1), (40, 50), 15, 'White')
    canvas.draw_text('Player B: ' + str(score2), (500, 50), 15, 'White')
        
def keydown(key):
    global paddle1_vel, paddle2_vel
    if key == simplegui.KEY_MAP["w"]:
        paddle1_vel = -4
    if key == simplegui.KEY_MAP["up"]:
        paddle2_vel = -4
    if key == simplegui.KEY_MAP["s"]:
        paddle1_vel = 4
    if key == simplegui.KEY_MAP["down"]:
        paddle2_vel = 4

def keyup(key):
    global paddle1_vel, paddle2_vel
    if key in [simplegui.KEY_MAP["w"], simplegui.KEY_MAP["s"]]:
        paddle1_vel = 0
    if key in [simplegui.KEY_MAP["up"], simplegui.KEY_MAP["down"]]:
        paddle2_vel = 0

# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button('Restart', new_game, 100)

# start frame
new_game()
frame.start()

