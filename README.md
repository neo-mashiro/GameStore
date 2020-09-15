# GameStore

Draft implementations of some classic simple games in Python.

Most games in this repo are borrowed from the [Fundamentals of Computing Specialization](https://www.coursera.org/specializations/computer-fundamentals) offered by Rice University on Coursera, which were originally built on `codeskulptor` and `simplegui` when I was taking the courses several years ago, located in the `simplegui` folder. I have added some customized functionalities and migrated them to [kivy](https://kivy.org/#home) so that the user interfaces look prettier with material design and animation effects.

Kivy is a nice library for building cross-platform GUIs in Python especially when it comes to mobile applications, it's still being actively developed, but I personally do not like how it works, mostly due to its bizarre, counter-intuitive behaviors, horrible documentation and the lack of users & community support. The motivation of separating logic and interface design is nice, but for small desktop applications it's just making lives harder, perhaps the worst ever library I've used... Certainly it looks much better than the old-school Java Swing stuff or alike, but still far from perfect, hope it would improve in the future, or "_Write once, run away_".

It might be a nice attempt to deploy kivy apps online and render them in a web browser, but currently this is not feasible. While it's not impossible to do so, the amount of technical work required is anything but a non-trivial task, using web applications framework instead would be a way better option.


## Game list

As a benchmark measure of **implementation complexity**, I have rated each game with stars, this is after all my personal sense so by no means objective. Code complexity is not the same as game difficulty, but an indicator of development workload and how hard it is to build the user interface. For instance, the strategy to build a **15 puzzle** solver is hard, but the UI development is trivial, the UI of **Asteroids** looks fancy, but all objects are moving asynchronously so it's easy to implement as well. In contrast, the **Memory** game has nothing fancy in it, both the logic and UI design looks simple at first glance. However, it turns out to be quite hard as soon as you start coding, there are many corner cases that could lead to bugs, some events need to block and wait, and it's not as easy to handle concurrency as appropriate (which comes from the animation coroutines, popup window time delays, unexpected mouse/keyboard events, etc), especially because kivy does not work well with `sleep`, `thread`, `async` and `await`.

Game                      | Stars 
:------------------------:|:-----:
[Stopwatch](#stopwatch)   | ★☆☆☆☆
[Pong](#pong)             | ★★☆☆☆
[2048](#2048)             | ★★★★☆
[15 puzzle](#15-puzzle)   | ★★★★☆
[Memory](#memory)         | ★★★★★
 TBD | ☆☆☆☆☆ 
 TBD | ☆☆☆☆☆ 

<br/>

## Stopwatch

A clicker game, somewhat resembles a casino slot machine?

__Game Logic:__ The window as a vertical box layout contains three rows: a clock showing the current time (in CPU clock), two buttons which are self-explanatory, and a stopwatch along with the score (wins / total rounds). When the user clicks "start", the button text changes to "stop", and the stopwatch starts to run, if the stopwatch stops when the last red digit (tenth of a second) is exactly 0, the user wins the round.

<p align="center">
  <img src="assets/stopwatch_play.png">
</p>

<br/>

## Pong

A classic arcade game that simulates table tennis.

__Game Logic:__ A ball spawns from the center of the window, moves at an initial speed in a random direction. The ball bounces off the top and bottom of the screen as well as the left and right player paddles. The player can move a paddle by dragging the mouse in the border area to hit the ball, or lose a point if the ball flies out of bound. The ball speeds up each time it collides with the paddle, paddle becomes shorter each time the player loses a round.

<p align="center">
  <img src="assets/pong_play.png">
</p>

<br/>

## 2048

Win the game by making a 2048 tile.

__Game Logic:__ Use the up, down, left and right arrow keys to slide the tiles on the board. When the tiles slide, adjacent tiles with the same number will be merged into a number that is doubled, and a new tile will appear in a randomly selected empty cell. The new tile is 2 90% of the time and 4 10% of the time. If there are no more empty cells and no legal merges can be made, the board is deadlocked so the user loses. The best score is the largest tile ever made on the board.

![img](assets/2048.png)

in play                   | win
:------------------------:|:------------------------:
![](assets/2048_play.png) | ![](assets/2048_win.png)

<br/>

## 15 puzzle

A sliding puzzle that consists of a frame of numbered square tiles in random order with one tile missing. [[wiki]](https://en.wikipedia.org/wiki/15_puzzle)

__Game Logic:__ The 4x4 board contains 15 numbers from 1 to 15 and an empty tile. For convenience, the empty tile here is represented by the number 0. Given a random configuration of the board, make a sequence of moves by sliding the 0 tile to exchange position with numbers nearby, so as to move the board back to the solved configuration. (where numbers 0 to 15 are placed in order on the grid)

On the top of the window is an _on-focus_ text field where the user can input a move string, it includes valid characters `u:up d:down l:left r:right` and must not exceed 30 characters. When the user presses enter, numbers on the board will move according to the string. The user can also just use the keyboard arrow keys to move the 0 tile, or click the button to see the current moves that have been made.

For any chaotic configuration, clicking the "solve puzzle" button enters the solving mode, the board will start to show the moves step by step to return to the solved state. Before this stage finishes, keyboard is disabled so that no key events will be triggered, any content typed into the text input field will simply be discarded.

To make a slack UI design, the window is drawn in dark mode, and the board canvas uses a CSS light gradient background. On top of that, each tile superimposes a rectangle graphic instruction to increase the hue, draws the label number and applies a CSS style border image using a transparent crystal ball image. Below are the screenshots.

__*__ Github may have a limit on frame rate so the GIF may not be rendered at a speed > 60 fps.

|      enter a move string      |      move string too long      |
| :---------------------------: | :----------------------------: |
| ![](assets/15_puzzle_ui1.png) | ![](assets/15_puzzle_ui2.png)  |

|    print moves (dark mode)    |         a simple demo          |
| :---------------------------: | :----------------------------: |
| ![](assets/15_puzzle_ui3.png) | ![](assets/15_puzzle_demo.gif) |

<br/>

## Memory

A nice matching game that tests your short-term memory.

__Game Logic:__ The objective of this game is to match all cards on the board. The board has 36 cells, comprised of 18 pairs of cards, face down in random order. The player turns over two cards at a time, with the goal of turning over a matching pair, by using his memory. A matched pair will stay visible on board, a mismatched pair will be turned back 0.5 seconds after they are turned over. Here I'm using images of weapons from the [CSGO](https://store.steampowered.com/app/730/CounterStrike_Global_Offensive/) inventory to simulate case opening, for fun. Of course, there's no way I could afford these rare items with real $dollars.

![image](assets/memory1.png)



The complexity of this game mainly comes from concurrency issues, most of which stem from the animation effects (also the popup dialog window). The key functions are coded as described below, but there are many corner cases in the caller elsewhere. In brief, card animation is achieved by animating the image texture opacity, first from 1 to 0, then change texture (flip the card), then from 0 to 1, so as to visually create a fade effect. Without animation effects, it would be a lot easier to implement.

```python
# To flip a list of cards in sequence, call flip_one() one by one.
# To flip a list of cards all at once, use the concurrent version flip_all().

async def flip_one(self, card, event):
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
    child_events = []
    # start asynchronous calls
    for card in cards:
        child_event = ak.Event()  # each card has a child event to avoid race conditions
        child_events.append(child_event)
        ak.start(self.flip_one(card, child_event))

    # wait until all events join
    for child_event in child_events:
        await child_event.wait()

    event.set()  # all animations complete, notify the caller who is waiting for the event
```

Given that every call in kivy is asynchronous, execution does not wait for animations to finish but will continue immediately, leaving a vulnerable time window when many things could go awry due to race conditions. Besides, a mismatched pair of cards need to stay visible on board (sleep) for a while before they are turned back, so that players can have enough time to remember them. To handle these issues properly, my implementation uses `asynckivy` which is a new module recently released in July 2020.

<details>
<summary>Detailed specifications</summary>

- Make a 6x6 board with some cute icons (36/2 = 18 icons)
- Create a button above the board that selects the theme, each features a different set of 18 icons
- When the button is clicked, pop up a dropdown list or alike that lets the user choose a theme
- Add another button that restarts the game without changing the theme
- Choose a back side image for all themes, laid over by a border image

- Add animation effects when the card is flipped on the board
- If the second card flipped does not match, let them stay onboard for 2 seconds before flipping back
- When a click is being handled, disable mouse clicks until the handler returns

- Keep track of time elapsed in seconds in a text label
- Keep track of total number of flips that have been made
- Keep track of the best record (shortest time) the player has achieved
- If all cards are matched, the user wins, pop up a dialog window saying congrats and display score (time)
</details>

<details>
<summary>Implementation caveats</summary>

- Window size and card size must be dynamically adjusted for themes with different aspect ratios
- Refrain from using `time.sleep()`, this will block the main event loop and freeze the window
- To schedule an event, use `Clock.schedule_interval()` together with a callback function
- The scheduled event will be automatically unscheduled as soon as the callback returns False
- Typically, callbacks do not accept extra arguments since they are referenced only by names
- To work with additional arguments, wrap it with a partial function when you bind to it
- Everything including scheduled events are asynchronous so that concurrency could be tricky

- Test carefully with logging messages to eliminate any possible race conditions (e.g. fast mouse clicks)
- There's no way to make a call equivalent to `time.sleep()` in kivy, other modules are required
- To implement custom concurrency behaviors, use the newly released `asynckivy` module
- Keep in mind that the `asyncio`, `threading` and `subprocess` may not work properly in kivy
</details>

**A small demo:**

![image](assets/memory_demo.gif)

<br/>

### Blackjack

```bash
$ convert 1.png 2.png 3.png ... +append out.png  # merge horizontally
$ convert 1.png 2.png 3.png ... -append out.png  # merge vertically
```



assets courtesy of



<br/>


Pyinstaller / Nuitka: package to .exe



# Reference

- [Fundamentals of Computing Specialization](https://www.coursera.org/specializations/computer-fundamentals), Rice, Coursera
- Kivy framework API - https://kivy.org/doc/stable/api-kivy.html
- KivyMD documentation - https://kivymd.readthedocs.io/en/latest/index.html
- free image assets: https://www.goodfon.com/
- free transparent PNGs - https://www.stickpng.com/
