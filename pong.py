import random
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp


class Ball(Widget):
    # for cross-platform compatibility, use class-level properties (they are not static attributes)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos  # unpack operator *


class Paddle(Widget):
    length = NumericProperty(180)


class Root(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    score1 = NumericProperty(0)
    score2 = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def serve_ball(self):
        self.ball.center = self.center
        self.ball.velocity = Vector(4, 4).rotate(random.randint(0, 360))

    def update_ball(self, interval):
        # bounce off top and bottom
        if self.ball.y <= 0 or (self.ball.y >= self.height - self.ball.height):
            self.ball.velocity_y *= -1

        # collide with player paddles
        if self.ball.collide_widget(self.player1) or self.ball.collide_widget(self.player2):
            self.ball.velocity_x *= -1.1
            self.ball.velocity_y *= 1.02

        # out of bound, increment score
        if self.ball.x < -self.ball.width:
            self.score2 += 1
            self.serve_ball()
            self.player1.length = max(self.player1.length - 10, 50)  # decrement loser's paddle length
        elif self.ball.x > self.width:
            self.score1 += 1
            self.serve_ball()
            self.player2.length = max(self.player2.length - 10, 50)

        self.ball.move()

    def on_touch_move(self, touch):
        if touch.x < self.width * 1 / 3:
            self.player1.center_y = touch.y
            self.player1.y = min(max(self.player1.y, 0), self.height - self.player1.size[1])
        if touch.x > self.width * 2 / 3:
            self.player2.center_y = touch.y
            self.player2.y = min(max(self.player2.y, 0), self.height - self.player2.size[1])


class Game(MDApp):
    title = 'Pong'

    def build(self):
        root = Root()
        root.serve_ball()
        Clock.schedule_interval(root.update_ball, 0)
        return root


if __name__ == "__main__":
    Builder.load_file('pong.kv')
    Window.size = (720 * 1.2, 450 * 1.2)
    Game().run()
