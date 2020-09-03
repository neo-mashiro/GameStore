from time import strftime
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex


class Root(BoxLayout):
    stopwatch_started = BooleanProperty(False)
    stopwatch_seconds = NumericProperty(0)
    total_stops = NumericProperty(0)
    success_stops = NumericProperty(0)
    tenths = NumericProperty(0)

    def update(self, interval):
        if self.stopwatch_started:
            self.stopwatch_seconds += interval

        self.ids.clock.text = strftime('[color=#d279ff]Clock[/color]: [b]%H[/b]:%M:%S')

        minute, second = divmod(self.stopwatch_seconds, 60)
        self.tenths = int(second * 10 % 10)
        self.ids.stopwatch.text = f'{int(minute):02d}:{int(second):02d}.' \
                                  f'[color=#ff0000]{self.tenths}[/color]'

    def press(self):
        self.stopwatch_started = not self.stopwatch_started
        if not self.stopwatch_started:
            self.total_stops += 1
            if self.tenths % 10 == 0:
                self.success_stops += 1

        self.ids.score.text = f'[color=#ff6600]score [/color]' \
                              f'[sup][size=40]{self.success_stops}[/size][/sup]' \
                              f'/[size=40]{self.total_stops}[/size]'


class Game(MDApp):
    # class-level string properties, not instance-level attributes!
    title = 'Stopwatch'

    def build(self):
        self.theme_cls.theme_style = "Dark"
        root = Root()
        Clock.schedule_interval(root.update, 0)
        return root


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,disable_multitouch')

    from kivy.lang import Builder
    Builder.load_file('stopwatch.kv')

    from kivy.core.window import Window
    Window.size = (600, 400)
    Window.clearcolor = get_color_from_hex('#101216')

    from kivy.core.text import LabelBase
    LabelBase.register(name='OpenSans', fn_regular='assets/OpenSans-Regular.ttf')

    Game().run()
