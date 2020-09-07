"""
Specification:

- Make a 6x6 board with some cute icons (36/2 = 18 icons)
- Create a button above the board that selects the theme, each features a different set of 18 icons
- When the button is clicked, pop up a dropdown list or alike that lets the user choose a theme (new game)
- Add another button that restarts the game without changing the theme
- Choose a back side image for all themes, laid over by a border image

- Add animation effects when the card is flipped on the board
- If the second card flipped does not match, let them stay onboard for 2 seconds before flipping back
- During this process (before they are flipped back), disable mouse clicks and keyboard

- Keep track of time elapsed in seconds in a text label
- Keep track of total number of flips that have been made
- If all cards are matched, the user wins, pop up a dialog window saying congrats and display score (time)

Available themes:
- ACG (default)
- CSGO inventory skins 1 & 2
- International Saimoe League (ISML) 1 & 2
"""


import random
import numpy as np

from io import BytesIO
from PIL import Image as PilImage

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, BorderImage
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, OptionProperty, BoundedNumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


# game board configuration
card_width = 150
border_size = 10

aspect_ratio = {
    # aspect ratio for each theme
    'acg': 1.00,
    'isml1': 1.35,  # 480x648
    'isml2': 1.35,  # 480x648
    'csgo1': 0.75,  # 512x384
    'csgo2': 0.75,  # 512x384
}


class Card(Widget):
    index = BoundedNumericProperty(0, min=0, max=18)
    theme = StringProperty(None)
    texture = ObjectProperty(None)

    def __init__(self, index, theme='acg', **kwargs):
        super().__init__(**kwargs)
        self.index = index  # index of the image to be rendered, or 0 (card back)
        self.theme = theme
        self.update()

    def update(self):
        # load card image from disk
        if self.index == 0:
            image = PilImage.open("assets/card_back.jpg")
            image_format = 'jpg'
        else:
            try:
                image = PilImage.open(f"assets/{self.theme}/{self.index}.png")
                image_format = 'png'
            except FileNotFoundError:
                image = PilImage.open(f"assets/{self.theme}/{self.index}.jpg")
                image_format = 'jpg'

        # load image into bytes buffer, render as texture
        data = BytesIO()
        image.save(data, format=image_format)
        data.seek(0)
        im = CoreImage(BytesIO(data.read()), ext=image_format)
        self.texture = im.texture


class Board(Widget):
    rows = NumericProperty(0)
    cols = NumericProperty(0)
    theme = StringProperty(None)

    popup1 = ObjectProperty(None)
    popup2 = ObjectProperty(None)

    time_elapsed = NumericProperty(0)
    best_record = NumericProperty(0)

    state = OptionProperty(0,  # initial state
                           options=[
                               0,  # all cards flipped are matched, wait for a new card to be flipped
                               1   # there's one flipped card to be matched, try to flip a card
                           ])

    last_clicked = ObjectProperty(None)  # the flipped card that waits to be matched

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 6
        self.cols = 6
        self.theme = None
        self.cards = None  # 2D numpy array of card objects
        self.index = None  # 2D numpy array of card indices (index 0 is the card back)

        self.state = 0
        self.flips = 0  # total number of flips
        self.last_clicked = None
        self.time_elapsed = 0
        self.reset()

        Clock.schedule_interval(self.tick, 1)

    def tick(self):
        self.time_elapsed += 1

    def format_time(self):
        # copy from stopwatch example
        hour = self.time_elapsed // 3600
        minute, second = map(int, divmod(self.time_elapsed, 60))
        return f'[{hour}]:[{minute}]:[{second}]'

    def walk_cards(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield (row, col)

    def card_pos(self, x, y):
        """
        Compute the card widget position based on the row and col number.
        """
        return [border_size + card_width * y,
                border_size + card_width * (self.rows - 1 - x)]

    def card_row_col(self, pos):
        """
        Compute the card (row, col) number based on the position coordinates.
        This is the inverse function of self.card_pos().
        """
        return [self.rows - 1 - (pos[1] - border_size) // card_width,
                (pos[0] - border_size) // card_width]

    def reset(self, theme='acg'):
        self.theme = theme
        Window.size = (920, 920 * aspect_ratio[self.theme] + 200)

        # display the card back in each cell
        self.cards = np.zeros((self.rows, self.cols), dtype=object)
        for x, y in self.walk_tiles():
            position = self.card_pos(x, y)
            card_height = card_width * aspect_ratio[self.theme]
            self.cards[x, y] = Card(0, pos=position, size=(card_width, card_height))
            self.add_widget(self.cards[x, y])

        # shuffle the deck
        array = np.array(range(1, (self.rows * self.cols) // 2 + 1))
        array = np.concatenate((array, array))
        random.shuffle(array)
        self.index = array.reshape(self.rows, self.cols)

        # reset game state and statistics
        self.flips = 0
        self.state = 0
        self.last_clicked = None
        self.time_elapsed = 0

    def change_theme(self):
        if not self.popup1:
            self.popup1 = MDDialog(
                title="Current Moves",
                text=text,
                radius=[20, 20, 20, 20],
                size_hint=(0.7, None),
                buttons=[
                    MDFlatButton(
                        text="BACK",
                        font_name='Lato',
                        font_size="16sp",
                        text_color=(0, 153/255, 1, 1)
                    )
                ]
            )
        self.popup1.open()

    def congratulate(self):
        if self.time_elapsed < self.best_record:
            self.best_record = self.time_elapsed

        if not self.popup2:
            self.popup2 = MDDialog(
                title="You won!",
                text="time elapsed: " + self.format_time(),
                radius=[20, 20, 20, 20],
                size_hint=(0.7, None),
                buttons=[
                    MDFlatButton(
                        text="OK", text_color=(0, 153/255, 1, 1)
                    )
                ]
            )
        self.popup2.open()

    def flip(self, card):
        x, y = self.card_row_col(card.pos)
        new_index = self.index[x, y] if card.index == 0 else 0

        flipped = Card(index=new_index, theme=self.theme,
                       pos=card.pos, size=card.size)

        self.remove_widget(card)
        self.add_widget(flipped)
        self.cards[x, y] = flipped

        anim = Animation(pos=self.cell_pos(x, y),
                             duration=0.25, transition='linear')
        if not self.moving:
            anim.on_complete = flipped
            self.moving = True
        anim.start(card)

    def on_touch_up(self, touch):
        # disable when in state 2

        # determine which card is clicked on
        row = -1
        col = -1
        clicked_card = None

        for x, y in self.walk_cards():
            card = self.cards[x, y]
            if card.collide_points(touch.x, touch.y):
                row = x
                col = y
                clicked_card = card
                break

        # mouse click out of board, do nothing
        if clicked_card is None:
            return

        # clicked card is already exposed, do nothing
        if clicked_card.index > 0:
            return

        # otherwise, flip it and update board status
        else:
            self.flips += 1

            # the 1st card is clicked on
            if self.state == 0:
                self.flip(clicked_card)  # on flipped, the clicked card has been replaced so no longer useful
                self.last_clicked = self.cards[row, col]  # the newly flipped card, not the clicked card
                self.state = 1

            # the 2nd card is flipped
            else:
                self.flip(clicked_card)

                # if matched, reset the board to state 0 immediately
                if self.last_clicked.index == self.cards[row, col].index:
                    self.last_clicked = None
                    self.state = 0

                # if mismatched, flip both cards back after 2 seconds, then reset to state 0
                else:
                    # refrain from using time.sleep(2), otherwise the UI main event loop will be blocked
                    Clock.schedule_once(lambda dt: ..., 2)  # simply use a callback that does nothing
                    self.flip(self.last_clicked)
                    self.flip(self.cards[row, col])

                    self.last_clicked = None
                    self.state = 0


class Root(BoxLayout):
    ...


class Game(MDApp):
    title = 'Memory'

    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "600"
        root = Root()
        return root


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse, disable_multitouch')  # must be called before importing Window

    from kivy.core.window import Window
    Window.size = (920, 1100)
    Window.clearcolor = get_color_from_hex('#BCADA1')

    Builder.load_file('memory.kv')
    LabelBase.register(name='perpeta', fn_regular='assets/perpeta.ttf')
    LabelBase.register(name='Lato', fn_regular='assets/Lato-Regular.ttf')
    LabelBase.register(name='OpenSans', fn_regular='assets/OpenSans-Regular.ttf')

    Game().run()
