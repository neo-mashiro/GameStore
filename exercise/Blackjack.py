# Mini-project #6 - Blackjack

import simplegui
import random

# load card sprite - 936x384 - source: jfitz.com
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    

# initialize some useful global variables
in_play = False
outcome = ""
score = 0
player_hand = []
dealer_hand = []

# define globals for cards
SUITS = ('C', 'S', 'H', 'D')  # club, spade, heart, diamond
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}


# define card class
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: ", suit, rank

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos):
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank), 
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(card_images, card_loc, CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)
        
# define hand class
class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0

    def __str__(self):
        hand_str = "Hand contains "
        for card in self.cards:
            hand_str += (card.suit + card.rank + ' ')
        return hand_str

    def add_card(self, card):
        self.cards.append(card)
        self.value += VALUES[card.get_rank()]

    def get_value(self):
        # check if hand has aces
        has_ace = False
        for card in self.cards:
            if card.get_rank() == RANKS[0]:
                has_ace = True
                
        # always count aces as 1 in self.value, if the hand has an ace, add 10 to it if it doesn't bust
        # don't worry about if a hand has more than one ace, because if you add 10 * 2, it always busts
        if not has_ace:
            return self.value
        else:
            if self.value + 10 <= 21:
                return self.value + 10
            else:
                return self.value
            
    def draw(self, canvas, pos):
        card_pos = pos
        for card in self.cards:
            card.draw(canvas, card_pos)
            card_pos[0] += CARD_SIZE[0] + 10
 
        
# define deck class 
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card
    
    def __str__(self):
        deck_str = "Deck contains "
        for card in self.cards:
            deck_str += (card.suit + card.rank + ' ')
        return deck_str


#define event handlers for buttons
def deal():
    global outcome, in_play, deck, player_hand, dealer_hand, score
    
    if in_play:
        outcome =  "You have surrendered, new deal?"
        in_play = False
        score -= 1
    
    outcome = ""
    deck = Deck()
    deck.shuffle()
    player_hand = Hand()
    dealer_hand = Hand()
    
    for i in range(2):
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())
    
    outcome = "Hit or stand?"
    in_play = True

def hit():
    global score, in_play, outcome
    # if the hand is in play, hit the player
    if in_play:
        player_hand.add_card(deck.deal_card())
   
        # if busted, assign a message to outcome, update in_play and score
        if player_hand.get_value() > 21:
            outcome =  "You have busted, new deal?"
            in_play = False
            score -= 1

def stand():
    global in_play, outcome, score
    # if hand is in play, repeatedly hit dealer until his hand has value 17 or more
    if in_play:
        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal_card())
            
        if dealer_hand.get_value() > 21:
            outcome = "Dealer has busted, you win! New deal?"
            in_play = False
            score += 1
        else:
            in_play = False
            if player_hand.get_value() <= dealer_hand.get_value():
                outcome = "You lose, new deal?"
                score -= 1
            else:
                outcome = "You win! New deal?"
                score += 1

    # assign a message to outcome, update in_play and score

# draw handler    
def draw(canvas):
    global in_play, outcome
    canvas.draw_text("WELCOME TO BLACKJACK!", [20, 50], 30, "Black")
    canvas.draw_text("Dealer", [32, 230], 20, "Black")
    canvas.draw_text("Player", [32, 460], 20, "Black")
    canvas.draw_text("score: " + str(score), [370, 120], 30, "Aqua")
    canvas.draw_text(outcome, [120, 360], 30, "Yellow")
    
    dealer_hand.draw(canvas, [120, 180])
    player_hand.draw(canvas, [120, 410])
    
    if in_play:
        canvas.draw_image(card_back, (CARD_CENTER[0], CARD_CENTER[1]), CARD_SIZE, 
                          [120 + CARD_SIZE[0]/2, 180 + CARD_SIZE[1]/2], CARD_SIZE
                         )

# initialization frame
frame = simplegui.create_frame("Blackjack", 600, 600)
frame.set_canvas_background("Green")

#create buttons and canvas callback
frame.add_button("Deal", deal, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
frame.set_draw_handler(draw)


# get things rolling
deal()
frame.start()


# remember to review the gradic rubric