from kivy.config import Config
# set configuration before importing other modules
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
    OptionProperty, BoundedNumericProperty, ListProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem, CheckboxRightWidget


class Login(Screen):
    ...


class Space(Screen):
    ...


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
