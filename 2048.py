import random
import numpy as np

from io import BytesIO
from PIL import Image as PilImage

from kivy.lang import Builder
from kivy.core.window import Keyboard
from kivy.core.text import LabelBase
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


# configuration
image_size = (1400, 100)
image = PilImage.open("assets/2048.png")

keymaps = {
    Keyboard.keycodes['up']: 'u',
    Keyboard.keycodes['down']: 'd',
    Keyboard.keycodes['left']: 'l',
    Keyboard.keycodes['right']: 'r'
}


class Tile(Widget):
    value = NumericProperty(0)
    texture = ObjectProperty(None)

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.tile_size = 100
        self.value = value
        self.update()

    def update(self):
        index = int(np.log2(self.value)) if self.value else 0
        spacing = (index * self.tile_size, 0, (index + 1) * self.tile_size, self.tile_size)
        cropped = image.crop(spacing)  # crop the image

        # load image directly from the memory, render as texture
        data = BytesIO()
        cropped.save(data, format='png')
        data.seek(0)  # prevent memory leak
        im = CoreImage(BytesIO(data.read()), ext='png')
        self.texture = im.texture


class Board(Widget):
    rows = NumericProperty(0)
    cols = NumericProperty(0)
    popup = ObjectProperty(None)

    best_score = NumericProperty(0)
    tile_size = NumericProperty(100)
    border_size = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)
        self.rows = 4  # user-customized
        self.cols = 4  # user-customized
        self.tiles = None
        self.reset()
        self.offset = {'u': (1, 0), 'd': (-1, 0), 'l': (0, 1), 'r': (0, -1)}
        self.border = {
            'u': [(0, col) for col in range(self.cols)],
            'l': [(row, 0) for row in range(self.rows)],
            'd': [(self.rows - 1, col) for col in range(self.cols)],
            'r': [(row, self.cols - 1) for row in range(self.rows)]
        }

    def walk_tiles(self):
        for row in range(self.rows):
            for col in range(self.cols):
                yield (row, col)

    def tile_pos(self, x, y):
        """Compute the tile position based on the row index and col index"""
        return [self.border_size + self.tile_size * y,
                self.border_size + self.tile_size * (self.rows - 1 - x)]

    def reset(self):
        self.tiles = np.zeros((self.rows, self.cols), dtype=object)
        for x, y in self.walk_tiles():
            position = self.tile_pos(x, y)
            self.tiles[x, y] = Tile(0, pos=position, size=(self.tile_size, self.tile_size))
            self.add_widget(self.tiles[x, y])
        self.new_tile()
        self.new_tile()

    def new_tile(self):
        """Create a new tile in a randomly selected empty cell.
           The tile should be 2 90% of the time and 4 10% of the time.
        """
        zeros = [(row, col) for row in range(self.cols)
                            for col in range(self.rows)
                            if self.tiles[row, col].value == 0]

        if len(zeros) != 0:
            random_tile = random.choice(zeros)
            random_list = [2] * 90 + [4] * 10

            new_value = random.choice(random_list)
            new_tile = Tile(new_value,
                            pos=self.tiles[random_tile].pos,
                            size=(self.tile_size, self.tile_size))

            self.remove_widget(self.tiles[random_tile])
            self.tiles[random_tile] = new_tile
            self.add_widget(new_tile)

    def move(self, direction):
        """Move all tiles in the given direction and add a new tile if any tiles moved."""
        legal = False
        border = self.border[direction]
        step = self.offset[direction]

        # merge list one by one
        for tile in border:
            if step[0] == 0:
                index_tuples = [(tile[0], tile[1] + step[1] * col)
                                for col in range(self.cols)]
            else:
                index_tuples = [(tile[0] + step[0] * row, tile[1])
                                for row in range(self.rows)]

            old_tile_values = [self.tiles[tup].value for tup in index_tuples]
            new_tile_values = Board.merge(old_tile_values)

            # tiles list metabolism
            for idx, tup in enumerate(index_tuples):
                if old_tile_values[idx] != new_tile_values[idx]:
                    legal = True
                    old_tile = self.tiles[tup]
                    new_tile = Tile(new_tile_values[idx], pos=old_tile.pos, size=old_tile.size)

                    self.tiles[tup] = new_tile
                    self.remove_widget(old_tile)
                    self.add_widget(new_tile)

        # update game status
        if legal:
            new_high = max([self.tiles[tup].value for tup in self.walk_tiles()])
            if new_high > self.best_score:
                self.best_score = new_high

            target = [2048 for tup in self.walk_tiles() if self.tiles[tup].value == 4096]
            if len(target) > 0:
                self.congratulate()
                self.reset()
            else:
                self.new_tile()

    @staticmethod
    def merge(line):
        """Merge a single row or column in 2048."""
        # slide zeros to the end of the list
        slide_zero = [num for num in line if num != 0]
        slide_zero.extend([num for num in line if num == 0])

        # merge adjacent numbers
        merged = [False] * len(slide_zero)
        for curr_tile in range(len(slide_zero) - 1):
            if slide_zero[curr_tile] == slide_zero[curr_tile + 1] \
                    and slide_zero[curr_tile] != 0 \
                    and not merged[curr_tile]:
                slide_zero[curr_tile] *= 2

                # slide the rest of the tiles forward
                for next_tile in range(curr_tile + 1, len(slide_zero)):
                    try:
                        slide_zero[next_tile] = slide_zero[next_tile + 1]
                    except IndexError:
                        slide_zero[next_tile] = 0
                merged[curr_tile] = True
            else:
                continue

        return slide_zero

    def congratulate(self):
        if not self.popup:
            self.popup = MDDialog(
                title="Congratulations!",
                text="You have won the 2048, nice work!",
                radius=[20, 20, 20, 20],
                size_hint=(0.7, None),
                buttons=[
                    MDFlatButton(
                        text="OK", text_color=(0, 153/255, 1, 1)
                    )
                ]
            )
        self.popup.open()

    def on_key_down(self, window, key, *args):
        if key in keymaps:
            self.move(keymaps[key])


class Root(BoxLayout):
    ...


class Game(MDApp):
    title = '2048'

    def build(self):
        root = Root()
        return root


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse, disable_multitouch')  # must be called before importing Window

    from kivy.core.window import Window
    Window.size = (420, 480)
    Window.clearcolor = get_color_from_hex('#BCADA1')

    Builder.load_file('2048.kv')
    LabelBase.register(name='perpeta', fn_regular='assets/perpeta.ttf')
    LabelBase.register(name='Lato', fn_regular='assets/Lato-Regular.ttf')
    LabelBase.register(name='OpenSans', fn_regular='assets/OpenSans-Regular.ttf')

    Game().run()
