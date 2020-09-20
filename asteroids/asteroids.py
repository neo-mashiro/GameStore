from kivy.config import Config

# set configuration before importing other modules
Config.set('input', 'mouse', 'mouse, disable_multitouch')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', 600)
Config.set('graphics', 'height', 800)

import random
from functools import partial
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Keyboard, Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    NumericProperty, ObjectProperty, StringProperty,
    ListProperty, ReferenceListProperty, BooleanProperty
)
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager, WipeTransition
from kivy.vector import Vector
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.picker import MDTimePicker


def collide_1_1(spr1, spr2):
    """
    Check if two sprite widgets have collided with each other.
    """
    return spr1.collide_widget(spr2)


def collide_1_9(spr, spr_list):
    """
    Check if spr has collided with any other sprite widget in the spr_list.
    """
    for spr2 in spr_list:
        if collide_1_1(spr, spr2):
            return True, spr, spr2
    return False, None, None


def collide_9_9(spr_list1, spr_list2):
    """
    Check if any pair of sprite widgets have collided (one from each list).
    """
    for spr in spr_list1:
        collided, spr1, spr2 = collide_1_9(spr, spr_list2)
        if collided:
            return collided, spr1, spr2
    return False, None, None


class Sprite(Widget):
    """
    A general class for rock, missile, meteorite, ufo, bonus and cannon objects
    """
    hp = NumericProperty(0)  # health point
    source = StringProperty(None)
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    velocity = ReferenceListProperty(vel_x, vel_y)
    angle = NumericProperty(0)  # for rotation

    __source = {
        'cannon': '../assets/cannon.png',
        'bonus': '../assets/bonus.png',
        'missile': '../assets/missile.png',
        'meteorite1': '../assets/meteorite1.png',
        'meteorite2': '../assets/meteorite2.png',
        'saturn': '../assets/saturn.png',
        'ufo': '../assets/ufo2.png'
    }

    def __init__(self, model, pos, size, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.pos = pos
        self.size = size
        self.exploded = False
        self.spawn()
        Clock.schedule_interval(self.move, 1 / 60)

    def spawn(self):
        self.source = Sprite.__source[self.model]

        # the raider fires a cannon that flies directly upward very fast
        if self.model == 'cannon':
            self.vel_x = 0
            self.vel_y = 15

        # the bonus moves downward at a random angle, but is quite slow
        elif self.model == 'bonus':
            self.velocity = Vector(1, 1).rotate(random.randint(135, 315))  # 135~315: downward

        # heavy sprite object falls down at a steeper angle, slow but hard to destroy (high hp)
        elif self.model in ('saturn', 'meteorite1', 'meteorite2'):
            self.hp = 3
            self.velocity = Vector(2, 2).rotate(random.randint(205, 245))  # 205~245: steep

        # enemy aircrafts make fast and aggressive moves, very dangerous, but vulnerable (low hp)
        elif self.model in ('ufo', 'missile'):
            self.hp = 2
            self.vel_x = 0
            self.vel_y = -5

    def revive(self):
        """
        Sometimes when an enemy sprite dies, it becomes a bonus object flying around the screen.
        The player can move the raider to catch it and gain more points.
        The sprite revives at exactly the same position where it died, so self.pos does not update.
        """
        self.model = 'bonus'
        self.source = '../assets/bonus.png'
        self.angle = 0
        self.size = 80, 80
        self.velocity = Vector(2, 2).rotate(random.randint(0, 360))  # downward only

    def explode(self):
        if self.model != 'bonus':
            self.source = '../assets/explosion.png'
            self.size = 100, 100
        else:
            self.source = '../assets/galaxy2.png'

        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.exploded = True

    def move(self, interval):
        # a bonus sprite bounces off left and right
        if self.model == 'bonus':
            if self.exploded:
                self.opacity -= 0.02  # gradually fade away
            elif self.x <= 0 or (self.x >= 600 - self.size[0]):
                self.vel_x *= -1

        # meteorites rotate while moving
        if self.model in ('meteorite1', 'meteorite2'):
            if self.exploded:
                self.opacity -= 0.02  # gradually fade away
            else:
                self.angle += 2

        if self.model in ('ufo', 'missile', 'saturn') and self.exploded:
            self.opacity -= 0.02  # gradually fade away

        if self.model == 'static':
            return False  # for static sprite, cancel the clock schedule

        # universal update function
        self.pos = Vector(*self.velocity) + self.pos


class Raider(Widget):
    thrust = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.offset_x = None  # distance from the mouse touch point
        self.offset_y = None

    def shoot(self):
        size = (20, 40)
        pos = self.pos[0] + 154 / 3 - size[0] / 2, self.pos[1] + 224 / 2 + 30 - size[1] / 2
        missile = Sprite(model='cannon', pos=pos, size=size)
        return missile


class Login(Screen):
    ...


class Space(Screen):
    in_play = BooleanProperty(False)
    timer = NumericProperty(0)
    shield_time = NumericProperty(0)

    time_label = StringProperty('00:00:00')
    rgba_label = ListProperty([1, 1, 1, 0])  # shield color

    score = NumericProperty(0)
    raider = ObjectProperty(None)

    pause_label = ObjectProperty(None)
    resume_label = ObjectProperty(None)
    pause_button = ObjectProperty(None)
    time_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)
        Clock.schedule_interval(self.tick, 0.2)
        Clock.schedule_interval(self.spawn_enemies, 0.2)
        Clock.schedule_interval(self.garbage_collect, 1 / 60)

        # list of sprite objects
        self.bonus = []
        self.cannons = []
        self.enemies = []  # meteorites, saturn, ufos and missiles...

        self.time_dialog = MDTimePicker()  # test

    def tick(self, interval):
        if self.in_play:
            self.timer += 1
            self.shield_time += 1
            self.time_label = self.format_time()
            self.rgba_label = self.format_rgba()
            if __debug__:  # this will be called by running `python -O asteroids.py` on the command line
                # make sure that objects are garbage collected
                print(len(self.bonus))
                print(len(self.cannons))
                print(len(self.enemies))

    def format_time(self):
        hour = self.timer // 3600
        minute, second = map(int, divmod(self.timer, 60))
        return f'{hour:02d}:{minute:02d}:{second:02d}'

    def format_rgba(self):
        if self.shield_time < 40 and self.shield_time % 2 == 0:
            return 1, 1, 1, 1
        elif 20000 <= self.shield_time <= 20020 and self.shield_time % 2 == 0:
            return 1, 1, 0, 1
        return 1, 1, 1, 0

    def spawn_enemies(self, interval):
        if self.in_play:
            if self.timer % 5 == 0:  # every second
                menu = ['meteorite1', 'meteorite2', 'saturn', 'ufo', 'missile']
                model = random.choice(menu)

                if model == 'missile':
                    size = (90, 120)
                elif model == 'saturn':
                    size = (140, 70)
                elif model == 'ufo':
                    size = (110, 110 / 1.77)
                else:
                    size = (75, 100)

                pos = random.randint(int(size[0] / 2), int(self.size[0] - size[0] * 1.5)), self.size[1]
                enemy = Sprite(model=model, pos=pos, size=size)
                self.enemies.append(enemy)
                self.add_widget(enemy)

    def clear_sprite(self, *args, spr=None):
        self.remove_widget(spr)

    def garbage_collect(self, interval):
        """
        Check boundaries and collisions, so as to remove dead widgets on a regular basis.
        Free resources periodically to prevent memory overload and make the game smooth.
        """
        if not self.in_play:
            return

        for wid in self.cannons.copy():
            if self.out_of_bound(wid):
                self.cannons.remove(wid)
                self.remove_widget(wid)

        for wid in self.enemies.copy():
            if self.out_of_bound(wid):
                self.enemies.remove(wid)
                self.remove_widget(wid)

            elif wid.hp <= 0:
                self.enemies.remove(wid)
                if random.random() > 0.9:
                    wid.revive()
                    self.bonus.append(wid)
                else:
                    wid.explode()  # explosion effect (takes around 0.5 ~ 1 seconds)
                    callback = partial(self.clear_sprite, spr=wid)  # partial function
                    Clock.schedule_once(callback, timeout=2)  # remove widget after 2 seconds
            else:
                collided, enemy, cannon = collide_1_9(wid, self.cannons)
                if collided:
                    self.remove_widget(cannon)
                    self.cannons.remove(cannon)
                    enemy.hp -= 1
                    self.score += 1

        for wid in self.bonus.copy():
            if wid.y < -150 or wid.y > self.size[1]:  # bonus escapes the top or bottom
                self.bonus.remove(wid)
                self.remove_widget(wid)

            elif collide_1_1(wid, self.raider):
                self.bonus.remove(wid)

                wid.explode()  # explosion effect (takes around 0.5 ~ 1 seconds)
                callback = partial(self.clear_sprite, spr=wid)  # partial function
                Clock.schedule_once(callback, timeout=2)  # remove widget after 2 seconds

                self.score += 1000  # bonus score
                self.shield_time = 20000  # add protection shield

    def out_of_bound(self, spr):
        """
        Check if a sprite widget has *completely* moved out of bound.
        """
        if spr.x < -spr.size[0] or spr.x > self.size[0]:
            return True
        if spr.y < -spr.size[1] or spr.y > self.size[1]:
            return True
        return False

    def on_touch_down(self, touch):
        """
        Important Notice:
        -----------------
        Unlike listeners such as on_press, on_release and on_key_down, which are triggered only
        on a specific widget, on_touch_down fires everything within a widget tree, be it a button
        click or a mouse drag event, literally any event happened on the screen. The same is true
        for on_touch_up and on_touch_move.

        The consequence of this is, when you override an on_touch method, for instance, to control
        a moving widget with your mouse and finger touches, if there are other buttons and text
        inputs on the same screen, they are not going to work properly since their bindings rely
        on the original on_touch implementations. In some other scenarios, the on_touch method can
        overshadow your defined callback, or unexpectedly fired on other objects from a different
        widget tree, or a widget can be fired twice by different callbacks, which leads to conflict.

        To get around this issue, there's only one solution: code up the overriding method partially
        with caution, override only where you are interested using if-else, do not override the
        whole function. Place a call to the superclass method wherever applicable, so as to inherit,
        keep, mutate or disable the original behavior depending on the type of conflict you have.
        """
        if not self.in_play:
            return super().on_touch_down(touch)

        if self.raider.collide_point(touch.x, touch.y):
            self.raider.offset_x = self.raider.center_x - touch.x
            self.raider.offset_y = self.raider.center_y - touch.y

    def on_touch_up(self, touch):
        if not self.in_play:
            return super().on_touch_down(touch)

        self.raider.thrust = False
        self.raider.offset_x = None
        self.raider.offset_y = None

    def on_touch_move(self, touch):
        if not self.in_play:
            return super().on_touch_down(touch)

        if self.raider.offset_x and self.raider.offset_y:
            self.raider.thrust = True
            self.raider.center_x = min(max(touch.x + self.raider.offset_x, self.raider.size[0] / 2),
                                       self.width - self.raider.size[0] / 2)
            self.raider.center_y = min(max(touch.y + self.raider.offset_y, self.raider.size[1] / 2),
                                       self.width - self.raider.size[1] / 2)

    def switch_screen(self, *args):
        # clear the pause widgets before switch
        self.remove_widget(self.pause_label)
        self.remove_widget(self.resume_label)
        self.remove_widget(self.pause_button)
        self.remove_widget(self.time_button)

        self.manager.transition = WipeTransition()
        self.manager.current = 'login'

    def pause(self):
        # pause the game and all scheduled events
        self.in_play = False

        # create pause widgets (only the first time)
        if not self.pause_label:
            self.pause_label = Label(font_name='perpeta', font_size=40, text='GAME PAUSED',
                                     pos_hint={"center_x": 0.5, "center_y": 0.6})

        if not self.resume_label:
            self.resume_label = Label(font_name='perpeta', font_size=18, color=(0.8, 0.8, 0.8, 0.5),
                                      text='PRESS ENTER AGAIN TO RESUME',
                                      pos_hint={"center_x": 0.5, "center_y": 0.55})

        if not self.pause_button:
            self.pause_button = MDRectangleFlatButton(font_name='OpenSans', font_size=20,
                                                      pos_hint={"center_x": 0.5, "center_y": 0.48},
                                                      text_color=(1, 1, 1, 1),
                                                      text='BACK TO MENU')
            self.pause_button.md_bg_color = (0, 1, 0, 0.2)
            self.pause_button.bind(on_release=self.switch_screen)

        if not self.time_button:
            self.time_button = MDRectangleFlatButton(font_name='OpenSans', font_size=20,
                                                     pos_hint={"center_x": 0.5, "center_y": 0.4},
                                                     text_color=(1, 1, 1, 1),
                                                     text='TIME LEAP')
            self.time_button.md_bg_color = (0, 0, 1, 0.2)
            self.time_button.bind(on_release=self.time_dialog.open)

        # display pause widgets on the screen
        self.add_widget(self.pause_label)
        self.add_widget(self.resume_label)
        self.add_widget(self.pause_button)
        self.add_widget(self.time_button)

    def resume(self):
        # clear the pause widgets before resume
        self.remove_widget(self.pause_label)
        self.remove_widget(self.resume_label)
        self.remove_widget(self.pause_button)
        self.remove_widget(self.time_button)

        self.in_play = True  # resume the game

    def on_key_down(self, window, key, *args):
        if key == Keyboard.keycodes['spacebar']:
            if self.in_play:
                missile = self.raider.shoot()
                self.cannons.append(missile)
                self.add_widget(missile)
        elif key == Keyboard.keycodes['enter']:
            if self.in_play:
                self.pause()
            else:
                self.resume()


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
