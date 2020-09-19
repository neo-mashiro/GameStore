from kivy.config import Config
# set configuration before importing other modules
from kivy.vector import Vector

Config.set('input', 'mouse', 'mouse, disable_multitouch')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', 600)
Config.set('graphics', 'height', 800)

import simplegui
import math
import random

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
    OptionProperty, BoundedNumericProperty, ListProperty,
    ReferenceListProperty, BooleanProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem, CheckboxRightWidget
from kivy.core.window import Keyboard, Window


class Raider(Widget):
    thrust = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)

        # distance from the mouse touch point
        self.offset_x = None
        self.offset_y = None

    def shoot(self):
        ...

    def on_key_down(self, window, key, *args):
        if key == Keyboard.keycodes['spacebar']:
            self.shoot()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.offset_x = self.center_x - touch.x
            self.offset_y = self.center_y - touch.y

    def on_touch_up(self, touch):
        self.thrust = False
        self.offset_x = None
        self.offset_y = None

    def on_touch_move(self, touch):
        if self.offset_x and self.offset_y:
            self.thrust = True
            self.center_x = min(max(touch.x + self.offset_x, self.size[0]/2), 600 - self.size[0]/2)
            self.center_y = min(max(touch.y + self.offset_y, self.size[1]/2), 600 - self.size[1]/2)


class Login(Screen):
    ...


class Space(Screen):
    in_play = BooleanProperty(False)
    timer = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.tick, 0.2)

    def tick(self, interval):
        if self.in_play:
            self.timer += 1


class Root(ScreenManager):
    ...


class Game(MDApp):
    title = 'asteroids'

    def build(self):
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "600"
        return Root()


if __name__ == '__main__':
    Builder.load_file('asteroids.kv')

    LabelBase.register(name='perpeta', fn_regular='../assets/perpeta.ttf')
    LabelBase.register(name='Lato', fn_regular='../assets/Lato-Regular.ttf')
    LabelBase.register(name='OpenSans', fn_regular='../assets/OpenSans-Regular.ttf')

    Game().run()
