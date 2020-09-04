# GameStore

Draft implementations of some classic simple games in Python.

Most of the game logic is borrowed from the [Fundamentals of Computing Specialization](https://www.coursera.org/specializations/computer-fundamentals) offered by Rice University on Coursera, which were originally built on `codeskulptor` and `simplegui` when I was taking the courses several years ago. I have added some customized functionalities and migrated them to [kivy](https://kivy.org/#home) so that the user interfaces look prettier with material design and animation effects.

Kivy is a nice library for building cross-platform GUIs in Python especially when it comes to mobile applications, it's still being actively developed, but I personally do not like how it works, mostly due to its bizarre, counter-intuitive behaviors, horrible documentation and the lack of users & community support. The motivation of separating logic and interface design is nice, but for small desktop applications I personally think it's just making lives harder... It feels much better than the old-school Java Swing/AWT, but I would prefer PyQt5 or WxPython, etc. _Write once, run away._ LOL

---

## Stopwatch

Somewhat resembles a casino slot machine?

<p align="center">
  <img src="assets/stopwatch_play.png">
</p>



## Pong

The ball speeds up each time it collides with the paddle, paddle becomes shorter each time the player loses a round.

<p align="center">
  <img src="assets/pong_play.png">
</p>



## 2048

Win the game by making a 2048 tile.

![img](assets/2048.png)

in play                   | win
:------------------------:|:------------------------:
![](assets/2048_play.png) | ![](assets/2048_win.png)


















# Reference

- [Fundamentals of Computing Specialization](https://www.coursera.org/specializations/computer-fundamentals), Rice, Coursera
- Kivy framework API - https://kivy.org/doc/stable/api-kivy.html
- KivyMD documentation - https://kivymd.readthedocs.io/en/latest/index.html
- free image assets: https://www.goodfon.com/
- free transparent PNGs - https://www.stickpng.com/
