"""
number card has value equal to the number
face card (K, Q, J) has value 10
Ace has value 1 or 11 (player's choice)



"""
import asynckivy as ak
import numpy as np
import os
import random
import time

from functools import partial
from io import BytesIO
from PIL import Image as PilImage

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import (
    NumericProperty, ObjectProperty, StringProperty,
    OptionProperty, BoundedNumericProperty, ListProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem, CheckboxRightWidget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


# define globals for cards
card_width = 195
card_height = 303

images = {
    'D': [],   # list of image texture objects
    'C': [],
    'H': [],
    'S': [],
    'X': None  # card back texture object
}


def extract_texture(image):
    """
    Load image into bytes buffer, convert to texture data
    """
    data = BytesIO()
    image.save(data, format='png')
    data.seek(0)
    return CoreImage(BytesIO(data.read()), ext='png').texture


def load_cards():
    global images

    card_back = extract_texture(PilImage.open('../assets/card_back.png'))
    images['X'] = card_back

    full_deck = PilImage.open('../assets/deck.png')

    for row in range(4):
        textures = []
        suit = list(images.keys())[row]

        for col in range(13):
            spacing = (col * card_width, row * card_height, (col + 1) * card_width, (row + 1) * card_height)
            cropped = full_deck.crop(spacing)  # crop the image
            texture = extract_texture(cropped)
            textures.append(texture)

        images[suit] = textures


class Card(Widget):
    suits = ['C', 'S', 'H', 'D']  # club, spade, heart, diamond
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    index = {'A': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, 'T': 9, 'J': 10, 'Q': 11, 'K': 12}

    texture = ObjectProperty(None)

    def __init__(self, suit, rank, visible, **kwargs):
        super().__init__(**kwargs)

        if (suit in Card.suits) and (rank in Card.ranks):
            self.suit = suit
            self.rank = rank
        else:
            raise ValueError(f"Invalid card: {suit}{rank}")

        self.pos = (0, 0)
        self.size = (card_width, card_height)

        self.visible = visible
        self.set_visible(visible)

    def set_visible(self, visible=False):
        self.visible = visible
        if visible:
            self.texture = images[self.suit][Card.index[self.rank]]
        else:
            self.texture = images['X']


class Hand:
    values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}

    def __init__(self):
        self.cards = []

    def __str__(self):
        # used to cheat the dealer...
        out_str = "Hand contains:"
        for card in self.cards:
            out_str += (' ' + card.suit + card.rank)
        return out_str

    def __getitem__(self, idx):
        return self.cards[idx]

    def add_card(self, card):
        self.cards.append(card)

    def count(self):
        visible_count = [1 if card.visible else 0 for card in self.cards]
        return sum(visible_count)

    def has_ace(self):
        has_ace = False
        for card in self.cards:
            if card.visible and card.rank == 'A':
                has_ace = True
                break
        return has_ace

    def get_value(self):
        value = 0
        for card in self.cards:
            if card.visible:
                value += Hand.values[card.rank]

        # if the hand has an ace, add 10 to self.point unless it would bust
        # any hand can only have one ace valued as 11, as 11 * 2 would bust
        if not self.has_ace():
            return value
        else:
            if value + 10 <= 21:
                return value + 10
            else:
                return value


class Deck:
    suits = ['C', 'S', 'H', 'D']  # club, spade, heart, diamond
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

    def __init__(self):
        self.cards = [Card(suit=suit, rank=rank, visible=False, opacity=0)
                      for suit in Deck.suits for rank in Deck.ranks]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card


class Table(GridLayout):
    score = NumericProperty(0)
    outcome = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 2
        self.cols = 8

        self.is_win = False
        self.outcome = ''
        self.score = 0
        self.in_play = False

        self.deck = None
        self.dealer_hand = None
        self.player_hand = None

        self.deal()

    def deal(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.dealer_hand = Hand()
        self.player_hand = Hand()

        self.canvas.clear()
        self.clear_widgets()

        # deal cards to the player and dealer in turn
        for col in range(self.cols):
            self.player_hand.add_card(self.deck.deal())  # invisible + transparent card
            self.dealer_hand.add_card(self.deck.deal())  # invisible + transparent card

        # fill out the table row by row (dealer on top)
        for col in range(self.cols):
            self.add_widget(self.dealer_hand[col])
        for col in range(self.cols):
            self.add_widget(self.player_hand[col])

        # dealer's cards, the second one is not visible
        self.dealer_hand[0].set_visible(True)

        # player's cards, both are visible
        self.player_hand[0].set_visible(True)
        self.player_hand[1].set_visible(True)

        # display 2 cards on the table
        for i in range(2):
            self.dealer_hand[i].opacity = 1
            self.player_hand[i].opacity = 1

        self.outcome = "Hit or stand?"
        self.in_play = True
        self.is_win = False

    def hit(self):
        if self.in_play:
            for idx, card in enumerate(self.player_hand):
                if not card.visible:
                    self.player_hand[idx].set_visible(True)
                    self.player_hand[idx].opacity = 1
                    break

            if self.player_hand.get_value() > 21:
                self.outcome = "You have busted, new deal?"
                self.in_play = False
                self.score -= 1

    def stand(self):
        if self.in_play:
            # hit dealer until his hand has value 17 or more
            while self.dealer_hand.get_value() < 17:
                self.dealer_hand.add_card(self.deck.deal())

            if self.dealer_hand.get_value() > 21:
                self.outcome = "Dealer has busted, you win! New deal?"
                self.score += 1
            else:
                if self.player_hand.get_value() <= self.dealer_hand.get_value():
                    self.outcome = "You lose, new deal?"
                    self.score -= 1
                else:
                    self.outcome = "You win! New deal?"
                    self.score += 1

            self.in_play = False


class Root(BoxLayout):
    ...


class Game(MDApp):
    title = 'Blackjack'

    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "600"
        root = Root()
        return root


if __name__ == '__main__':
    # load card sprite
    load_cards()

    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse, disable_multitouch')  # must be called before importing Window

    from kivy.core.window import Window
    Window.size = (800, 750)
    Window.clearcolor = get_color_from_hex('#BCADA1')

    Builder.load_file('blackjack.kv')
    LabelBase.register(name='perpeta', fn_regular='../assets/perpeta.ttf')
    LabelBase.register(name='Lato', fn_regular='../assets/Lato-Regular.ttf')
    LabelBase.register(name='OpenSans', fn_regular='../assets/OpenSans-Regular.ttf')

    Game().run()

