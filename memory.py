"""
Specification:

- Make a 6x6 board with some cute icons (36/2 = 18 icons)
- Create a button above the board that selects the theme, each features a different set of 18 icons
- When the button is clicked, pop up a dropdown list or alike that lets the user choose a theme (new game)
- Add another button that restarts the game without changing the theme
- Choose a back side image for all themes, laid over by a border image

- Add animation effects when the card is flipped on the board
- If the second card flipped does not match, let them stay onboard for 2 seconds before flipping back
- When a click is being handled, disable mouse clicks until the handler returns

- Keep track of time elapsed in seconds in a text label
- Keep track of total number of flips that have been made
- Keep track of the best record (shortest time) the player has achieved
- If all cards are matched, the user wins, pop up a dialog window saying congrats and display score (time)

Things to note:

- A standard kivy application has only 1 main thread, the result of using more threads can be unexpected
- Window size and card size must be dynamically adjusted for themes with different aspect ratios
- In kivy, animation is asynchronous so execution does not wait for it to finish but will continue
- Refrain from using `time.sleep()`, this will block the main event loop and freeze the window

- To schedule an event, use `Clock.schedule_interval(callback, 1/60)` together with a callback function
- The scheduled event will be automatically unscheduled as soon as the callback returns False
- Typically, callbacks do not accept extra arguments since they are referenced only by names
- To work with additional arguments, wrap it with a partial function when you bind to it
- An alternative is to use a lambda function if the callback code fits on one line

- Everything including scheduled events are always asynchronous so that concurrency could be tricky
- Test carefully with logging messages to eliminate any possible race conditions (e.g. fast mouse clicks)
- There's no way to make a call equivalent to `time.sleep()` in kivy, other modules are required
- To implement custom concurrency behaviors, use the `asynckivy` module (recently released in July 2020)
- Keep in mind that the `asyncio`, threading` and `subprocess` may not work properly in kivy

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

##################################################################
# global configuration variables
##################################################################

n_rows = 6
n_cols = 6
border_size = 10
card_padding = 5
fixed_width = 180

base_dir = 'assets'
images = {}
themes = ['guns', 'knives']

aspect_ratio = {
    'guns': 0.75,    # 512x384
    'knives': 0.75   # 512x384
}


def extract_texture(image, image_format):
    """
    Load image into bytes buffer, convert to texture data
    """
    data = BytesIO()
    image.save(data, format=image_format)
    data.seek(0)
    return CoreImage(BytesIO(data.read()), ext=image_format).texture


def load_images():
    """
    On startup, load all image assets into memory to boost up game performance
    """
    global base_dir, images, themes
    card_back = extract_texture(PilImage.open("assets/weapon_case.png"), 'png')

    for theme in themes:
        folder = os.path.join(base_dir, theme)
        textures = [card_back]

        for index in range((n_rows * n_cols) // 2):
            try:
                image = PilImage.open(f"{folder}/{index + 1}.png")
                image_format = 'png'
            except FileNotFoundError:
                image = PilImage.open(f"{folder}/{index + 1}.jpg")
                image_format = 'jpeg'

            texture = extract_texture(image, image_format)
            textures.append(texture)

        images[theme] = textures


async def safe_sleep(n):
    """
    Sleep for n seconds without blocking the main event loop.
    This is the only working substitute for `time.sleep(n)`.
    """
    await ak.sleep(n)


class ThemeItem(OneLineAvatarIconListItem):
    """
    Each instance of this class represents a row item in the popup dialog window
    """
    divider = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._checkbox = CheckboxRightWidget(group="check")
        self.add_widget(self.checkbox)

    @property
    def checkbox(self):
        return self._checkbox

    def on_release(self):
        self.check(self.checkbox)

    def check(self, checkbox):
        print(self.text)
        # check the current checkbox and uncheck others
        checkbox.active = True
        check_list = checkbox.get_widgets(checkbox.group)
        for check in check_list:
            if check != checkbox:
                check.active = False


class Card(Widget):
    index = BoundedNumericProperty(0, min=0, max=18)
    theme = StringProperty(None)
    texture = ObjectProperty(None)
    endpoints = ListProperty([])  # list of points used to draw the card borders in .kv

    def __init__(self, index, theme='guns', **kwargs):
        super().__init__(**kwargs)
        self.index = index  # index of the image to be rendered, or 0 (card back)
        self.theme = theme
        self.texture = images[self.theme][self.index]  # load card image from memory, render as texture
        self.endpoints = [
            self.pos[0] - card_padding, self.pos[1] - card_padding,  # the start point
            self.pos[0] - card_padding, self.pos[1] + card_padding + self.size[1],
            self.pos[0] + card_padding + self.size[0], self.pos[1] + card_padding + self.size[1],
            self.pos[0] + card_padding + self.size[0], self.pos[1] - card_padding,
            self.pos[0] - card_padding, self.pos[1] - card_padding   # return to the start point
        ]


class Board(Widget):
    # define properties that can be accessed from the .kv file
    rows = NumericProperty(0)
    cols = NumericProperty(0)

    card_width = NumericProperty(0)
    card_height = NumericProperty(0)

    theme = StringProperty(None)
    flips = NumericProperty(0)
    time_label = StringProperty('00:00:00')

    popup1 = ObjectProperty(None)
    popup2 = ObjectProperty(None)

    time_elapsed = NumericProperty(0)
    best_record = NumericProperty(9999)

    state = OptionProperty(0,  # initial state
                           options=[
                               0,  # all cards flipped are matched, wait for a new card to be flipped
                               1   # there's one flipped card to be matched, try to flip a card
                           ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = n_rows
        self.cols = n_cols
        self.theme = None
        self.cards = None  # 2D numpy array of card objects
        self.index = None  # 2D numpy array of card indices (index 0 is the card back)

        self.state = 0
        self.flips = 0  # total number of flips
        self.time_elapsed = 0

        self.last_clicked = None  # the flipped card that waits to be matched
        self.mouse_disabled = False  # disable mouse clicks while events are being handled

        self.reset()

        Clock.schedule_interval(self.tick, 1)  # count time

    def tick(self, interval):
        self.time_elapsed += 1
        self.time_label = self.format_time()

    def format_time(self):
        hour = self.time_elapsed // 3600
        minute, second = map(int, divmod(self.time_elapsed, 60))
        return f'{hour:02d}:{minute:02d}:{second:02d}'

    def walk_cards(self):
        """
        The generator function to iterate over cards on the board.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                yield (row, col)

    def card_pos(self, x, y):
        """
        Compute the card widget position based on the row and col number.
        """
        return [border_size + self.card_width * y + card_padding,
                border_size + self.card_height * (self.rows - 1 - x) + card_padding]

    def card_row_col(self, pos):
        """
        Compute the card (row, col) number based on the position coordinates.
        This is the inverse function of self.card_pos().
        """
        return [self.rows - 1 - (pos[1] - border_size - card_padding) // self.card_height,
                (pos[0] - border_size - card_padding) // self.card_width]

    def reset(self, theme='guns'):
        # [bug fixed]: disable `new game` button while animation is still in progress
        if self.mouse_disabled:
            return

        self.theme = theme
        self.card_width = fixed_width
        self.card_height = int(fixed_width * aspect_ratio[self.theme])

        Window.size = (self.cols * self.card_width + 2 * border_size,
                       self.rows * self.card_height + 2 * border_size + 70)

        self.cards = np.zeros((self.rows, self.cols), dtype=object)
        self.canvas.clear()  # important!

        # clean up old card widgets if any
        for x, y in self.walk_cards():
            if self.cards[x, y] is not None:
                self.remove_widget(self.cards[x, y])

        # display the card back in each cell
        for x, y in self.walk_cards():
            position = self.card_pos(x, y)
            self.cards[x, y] = Card(
                index=0, theme=self.theme, pos=position,
                size=(self.card_width - 2 * card_padding,
                      self.card_height - 2 * card_padding)
            )
            self.add_widget(self.cards[x, y])

        # shuffle the deck
        array = np.array(range(1, (self.rows * self.cols) // 2 + 1))
        array = np.concatenate((array, array))
        random.shuffle(array)
        self.index = array.reshape(self.rows, self.cols)

        # reset game state and statistics
        self.flips = 0
        self.state = 0
        self.time_elapsed = 0
        self.last_clicked = None
        self.mouse_disabled = False

    async def flip_one(self, card, event):
        """
        Given an idle event, flip the card and wait for the animation to finish.
        Once done, activate the event so that the caller can safely continue execution.
        ------------------------------------------------------------------------------
        To flip a list of cards in sequence, call flip_one() one by one.
        To flip a list of cards all at once, use the concurrent version flip_all().
        """
        x, y = self.card_row_col(card.pos)
        new_index = self.index[x, y] if card.index == 0 else 0

        # create the new card widget which is initially transparent
        flipped = Card(index=new_index, theme=self.theme,
                       pos=card.pos, size=card.size, opacity=0.5)

        self.cards[x, y] = flipped

        # animate the old card opacity from 1 to 0.5, wait until finish, then remove the old card widget
        await ak.animate(card, opacity=0.5, duration=0.25, transition='in_out_sine')
        self.remove_widget(card)

        # add the new card widget (which is transparent)
        self.add_widget(flipped)

        # animate the new card opacity from 0.5 to 1, wait until finish, then set it to opaque
        await ak.animate(flipped, opacity=1, duration=0.25, transition='in_out_sine')
        self.cards[x, y].opacity = 1

        event.set()  # animation complete, notify the caller who is waiting for the event

    async def flip_all(self, cards, event):
        """
        Given an idle event, flip a list of cards all at once and wait until all finish.
        Once done, activate the event so that the caller can safely continue execution.
        ------------------------------------------------------------------------------
        This is the concurrent version of flip_one(), animations play simultaneously.
        Each card is tracked by a unique child event to eliminate possible race conditions.
        """
        child_events = []
        # start asynchronous calls
        for card in cards:
            child_event = ak.Event()
            child_events.append(child_event)
            ak.start(self.flip_one(card, child_event))

        # wait until all events join
        for child_event in child_events:
            await child_event.wait()

        event.set()  # all animations complete, notify the caller who is waiting for the event

    async def click(self, touch):
        # disable mouse clicks until the function returns
        self.mouse_disabled = True

        # determine which card is clicked on
        row = -1
        col = -1
        clicked_card = None

        for x, y in self.walk_cards():
            card = self.cards[x, y]
            if card.collide_point(touch.x, touch.y):
                row = x
                col = y
                clicked_card = card
                break

        # mouse click outside the board, do nothing
        if clicked_card is None:
            self.mouse_disabled = False
            return

        # clicked card is already exposed, do nothing
        if clicked_card.index > 0:
            self.mouse_disabled = False
            return

        # otherwise, flip it and update board status
        else:
            self.flips += 1

            # the 1st card is clicked on
            if self.state == 0:
                event = ak.Event()
                coroutine = self.flip_one(clicked_card, event)
                ak.start(coroutine)
                await event.wait()
                print('1st card flipped')

                self.last_clicked = self.cards[row, col]  # after flip, the card back no longer exists
                self.state = 1

            # the 2nd card is clicked on
            else:
                event = ak.Event()
                coroutine = self.flip_one(clicked_card, event)
                ak.start(coroutine)
                await event.wait()
                print('2nd card flipped')

                # if matched, reset the board to state 0, check win conditions
                if self.last_clicked.index == self.cards[row, col].index:
                    self.last_clicked = None
                    self.state = 0

                    is_win = True
                    for x, y in self.walk_cards():
                        if self.cards[x, y].index == 0:
                            is_win = False
                            break

                    if is_win:
                        self.congratulate()
                        self.reset(self.theme)

                # if mismatched, flip both cards back after 2 seconds, then reset to state 0
                else:
                    await safe_sleep(0.5)

                    event = ak.Event()
                    cards = [self.last_clicked, self.cards[row, col]]
                    coroutine = self.flip_all(cards, event)
                    ak.start(coroutine)
                    await event.wait()
                    print('both cards are hidden')

                    self.last_clicked = None
                    self.state = 0

        self.mouse_disabled = False

    def on_touch_up(self, touch):
        if self.mouse_disabled:
            return
        coroutine = self.click(touch)
        ak.start(coroutine)

    def close_dialog(self, *args):
        if self.popup1:
            self.popup1.dismiss()
        if self.popup2:
            self.popup2.dismiss()
        self.mouse_disabled = False

    def change_theme(self, *args):
        for item in self.popup1.items:
            if item.checkbox.active:
                self.theme = item.text
                break
        self.close_dialog(*args)
        self.reset(self.theme)

    def choose_theme(self):
        # [bug fixed]: disable `set theme` button while animation is still in progress
        if self.mouse_disabled:
            return

        # [bug fixed]: disable all main UI events until the dialog is closed
        self.mouse_disabled = True

        if not self.popup1:
            button_style = dict(font_name='Lato',
                                font_size="16sp",
                                text_color=(0, 153 / 255, 1, 1))

            button1 = MDFlatButton(text="RESTART", **button_style)
            button2 = MDFlatButton(text="CANCEL", **button_style)

            button1.bind(on_release=self.change_theme)
            button2.bind(on_release=self.close_dialog)

            self.popup1 = MDDialog(
                title="Themes",
                type="confirmation",
                items=[
                    ThemeItem(text="guns"),
                    ThemeItem(text="knives")
                ],
                size_hint=(0.3, None),
                auto_dismiss=False,
                buttons=[button1, button2]
            )
        self.popup1.open()

    def congratulate(self):
        if self.time_elapsed < self.best_record:
            self.best_record = self.time_elapsed

        text = f'Total time used: {self.format_time()}, ' \
               f'total clicks: {self.flips}, ' \
               f'best record: {self.best_record}.'

        button_style = dict(font_name='Lato',
                            font_size="16sp",
                            text_color=(0, 153 / 255, 1, 1))

        button = MDFlatButton(text="OK", **button_style)
        button.bind(on_release=self.close_dialog)

        # create a new dialog with new statistics each time
        self.popup2 = MDDialog(
            title="Congratulations, You Won!",
            text=text,
            radius=[20, 20, 20, 20],
            size_hint=(0.7, None),
            auto_dismiss=False,
            buttons=[button]
        )
        self.popup2.open()


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
    load_images()

    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse, disable_multitouch')  # must be called before importing Window

    from kivy.core.window import Window
    Window.size = (980, 810)
    Window.clearcolor = get_color_from_hex('#BCADA1')

    Builder.load_file('memory.kv')
    LabelBase.register(name='perpeta', fn_regular='assets/perpeta.ttf')
    LabelBase.register(name='Lato', fn_regular='assets/Lato-Regular.ttf')
    LabelBase.register(name='OpenSans', fn_regular='assets/OpenSans-Regular.ttf')

    Game().run()
