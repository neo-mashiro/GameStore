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
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem, CheckboxRightWidget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


# define globals for cards
card_width = 390
card_height = 606

suits = ['C', 'S', 'H', 'D']  # club, spade, heart, diamond
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
index = {'A': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, 'T': 9, 'J': 10, 'Q': 11, 'K': 12}
value = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}

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

    card_back = extract_texture(PilImage.open('../assets/card_back.png'), 'png')
    images['X'] = card_back

    # full_deck = extract_texture(PilImage.open('../assets/deck.png'), 'png')
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
    def __init__(self, suit, rank, pos, **kwargs):
        super().__init__(**kwargs)

        if (suit in suits) and (rank in ranks):
            self.suit = suit
            self.rank = rank
        else:
            raise ValueError(f"Invalid card: {suit}{rank}")

        self.pos = pos
        self.size = (card_width, card_height)
        self.texture = textures[self.suit][index[self.rank]]


Card(suit='A', rank='A', pos = suits.index(suit) * card_height, ranks.index(rank) * card_width)


class Hand:
    __counter = 0

    def __init__(self):
        self.cards = []
        self.point = 0

    def __str__(self):
        out_str = "Hand contains:"
        for card in self.cards:
            out_str += (' ' + card.suit + card.rank)
        return out_str

    def add_card(self, card):
        self.cards.append(card)
        self.point += value[card.rank]

    def get_value(self):
        # check if hand has aces
        has_ace = False
        for card in self.cards:
            if card.rank == 'A':
                has_ace = True
                break

        # if the hand has an ace, add 10 to self.point unless it would bust
        # any hand can only have one ace valued as 11, as 11 * 2 would bust
        if not has_ace:
            return self.point
        else:
            if self.point + 10 <= 21:
                return self.point + 10
            else:
                return self.point

    @staticmethod
    def count():
        return Hand.__counter


class Deck:
    def __init__(self):
        self.cards = [Card(suit=suit, rank=rank, pos=None) for suit in suits for rank in ranks]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card


class Root(BoxLayout):
    score = NumericProperty(0)
    outcome = StringProperty(None)
    d1 = d2 = d3 = d4 = d5 = d6 = d7 = ObjectProperty(None)
    p1 = p2 = p3 = p4 = p5 = p6 = p7 = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_win = False
        self.outcome = ''
        self.score = 0
        self.in_play = False
        self.deck = Deck()
        self.deck.shuffle()
        self.dealer_hand = Hand()
        self.player_hand = Hand()

    def deal(self):
        for i in range(2):
            self.player_hand.add_card(self.deck.deal())
            self.dealer_hand.add_card(self.deck.deal())
            self.score -= 1

        self.outcome = "Hit or stand?"
        self.in_play = True

    def hit(self):
        if self.in_play:
            self.player_hand.add_card(self.deck.deal())
            if self.player_hand.get_value() > 21:  # busted
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


class Game(MDApp):
    title = 'Blackjack'

    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "600"
        root = Root()
        root.deal()
        return root


if __name__ == '__main__':
    # load card sprite
    load_cards()

    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse, disable_multitouch')  # must be called before importing Window

    from kivy.core.window import Window
    Window.size = (980, 810)
    Window.clearcolor = get_color_from_hex('#BCADA1')

    Builder.load_file('memory.kv')
    LabelBase.register(name='perpeta', fn_regular='../assets/perpeta.ttf')
    LabelBase.register(name='Lato', fn_regular='../assets/Lato-Regular.ttf')
    LabelBase.register(name='OpenSans', fn_regular='../assets/OpenSans-Regular.ttf')

    Game().run()

