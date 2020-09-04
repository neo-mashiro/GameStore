# template for "Stopwatch: The Game"
import simplegui

# define global variables
TIME_COUNT = 0
TOTAL_STOPS = 0
SUCCESS_STOPS = 0
IS_STOPWATCH_RUNNING = False

# define helper functions
def format(t):
    '''
    converts time in tenths of seconds into formatted string A:BC.D
    for example: 1625 = 162.5 s = 2:42.5
    '''
    minutes = t // 600
    seconds = int((t % 600) / 10)
    tenths = int(t % 600 % 10)
    return str(minutes) + ':' + str(seconds).rjust(2,'0') + '.' + str(tenths)
    
# define event handlers for buttons
def start():
    timer.start()
    global IS_STOPWATCH_RUNNING
    IS_STOPWATCH_RUNNING = True

def stop():
    global TOTAL_STOPS, SUCCESS_STOPS, IS_STOPWATCH_RUNNING
    if IS_STOPWATCH_RUNNING:
        TOTAL_STOPS += 1
        if TIME_COUNT % 10 == 0:
            SUCCESS_STOPS += 1
    timer.stop()
    IS_STOPWATCH_RUNNING = False

def reset():
    timer.stop()
    global TIME_COUNT, TOTAL_STOPS, SUCCESS_STOPS, IS_STOPWATCH_RUNNING
    IS_STOPWATCH_RUNNING = False
    TIME_COUNT = 0
    TOTAL_STOPS = 0
    SUCCESS_STOPS = 0

# define event handler for timer with 0.1 sec interval
def tick():
    global TIME_COUNT
    TIME_COUNT += 1

# define draw handler
def draw(canvas):
    canvas.draw_text(format(TIME_COUNT), (27, 90), 40, 'White')
    canvas.draw_text(str(SUCCESS_STOPS) + '/' + str(TOTAL_STOPS)
                    ,(100, 30), 20, 'Yellow')
    
# create frame
frame = simplegui.create_frame('Stopwatch', 150, 150)
frame.set_canvas_background('Blue')

# register event handlers
timer = simplegui.create_timer(100, tick)
frame.set_draw_handler(draw)
frame.add_button('start', start, 80)
frame.add_button('stop', stop, 80)
frame.add_button('reset', reset, 80)

# start frame
frame.start()

# Please remember to review the grading rubric
