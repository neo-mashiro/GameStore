# Reference

- A. [IIPP + PoC, Fundamentals of Computing Specialization, Rice, Coursera](https://www.coursera.org/specializations/computer-fundamentals)
- B. SimpleGUICS2Pygame, PyOPENGL documentation
- C. first read source code of many other fantastic games to get a sense


## Note
- limit the number of global variables, as the script size increases, global variables could make a bunch of nasty bugs that are hard to fix.
- Build a class to keep track of the game status from multiple perspectives, wrap global variables up into fields within the class, and add methods as appropriate.

```python
'''
It's a good habit not to use public fields, the class fields should all be private. Private means the fields are only visible within the class and should not be handled or manipulated from outside.
'''

class GameState():
    def __init__(self):
        self._time = 0
        self._status = True
        self._frame_height = 600   
        self._frame_width = 800
```

