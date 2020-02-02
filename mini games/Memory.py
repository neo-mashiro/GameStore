# implementation of card game - Memory

import simplegui
import random

last1idx = None
last2idx = None

# helper function to initialize globals
def new_game():
    global state, cards, turns, exposed
    
    # initialize
    state = 0
    cards = []
    turns = 0
    exposed = [False] * 16
    
    # create random cards list
    x = list(range(8))
    y = list(range(8))
    cards = x + y
    random.shuffle(cards)
     
# define event handlers
def mouseclick(pos):
    global state, last1idx, last2idx, turns, exposed
      
    # determine which card is clicked on
    index = pos[0] // 50
    print "You clicked card", str(index + 1)

    # if the card being clicked on is already exposed, do nothing
    if not exposed[index]:
        # expose the current card if it's not
        exposed[index] = True
          
        # update "turns" label
        turns += 0.5
        
        # state = 0, no unmatched cards are exposed
        if state == 0:
            state = 1
        # state = 1, one exposed card is yet to be matched
        elif state == 1:
            state = 2
            # find an exposed card other than this card, that has the same number
            for idx, card in enumerate(cards):
                if card == cards[index] and idx != index and exposed[idx]:
                    state = 0
        else:
            # state = 2 means the last 2 cards exposed don't match, so hide them
            exposed[last1idx] = False
            exposed[last2idx] = False
            # now the current card is exposed and not matched yet
            state = 1
            
        # update the last 2 cards clicked
        last2idx = last1idx
        last1idx = index

# cards are logically 50x100 pixels in size    
def draw(canvas):
    global text_position, exposed
    text_position = []
    for index, card in enumerate(cards):
        text_position.append((17 + 50 * index, 62))
        canvas.draw_text(str(cards[index]), text_position[index], 30, "White")
        if not exposed[index]:
            canvas.draw_polygon([[0 + 50 * index, 0]
                                ,[50 + 50 * index, 0]
                                ,[50 + 50 * index, 100]
                                ,[0 + 50 * index, 100]
                                ], 1, "Green", "Green"
                               )
        canvas.draw_line([50 + 50 * index, 0], [50 + 50 * index, 100], 2, "Black")
    if turns % 1 == 0:
        label.set_text("Turns = " + str(turns))

# create frame and add a button and labels
frame = simplegui.create_frame("Memory", 800, 100)
frame.set_canvas_background('Blue')
frame.add_button("Reset", new_game)
label = frame.add_label("Turns = 0")

# register event handlers
frame.set_mouseclick_handler(mouseclick)
frame.set_draw_handler(draw)

# get things rolling
new_game()
frame.start()


# Always remember to review the grading rubric