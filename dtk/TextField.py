# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# Some rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share -- to copy, distribute, display, and perform the work
#   * to Remix -- to make derivative works
# 
# Under the following conditions:
# 
#   * Attribution. You must attribute the work in the manner specified by the
#     author or licensor (but not in any way that suggests that they endorse you
#     or your use of the work).
#   * Share Alike. If you alter, transform, or build upon this work, you may
#     distribute the resulting work only under the same, similar or a compatible
#     license.
# 
#   * For any reuse or distribution, you must make clear to others the license
#     terms of this work.
#   * Any of the above conditions can be waived if you get permission from the
#     copyright holder.
#   * Apart from the remix rights granted under this license, nothing in this
#     license impairs or restricts the author's moral rights.
# 
# 
# Full text of the license can be found online:
# 
#   <http://creativecommons.org/licenses/by-sa/3.0/us/>


from core import Drawable

class TextField(Drawable):
    """
    A simple one-line textfield that obeys the following keybindings:

    left arrow, right arrow: move cursor one character left or right,
      respectively
    home, end: move cursor to start or end, respectively
    backspace: delete the character just behind the cursor
    delete: delete the character just ahead of the cursor
    
    to have a certain key be the "end" of the input (eg, 'enter' or
    'escape' you must bind it yourself from outside the TextField


    Events (in addition to standard Drawable events):
     * 'text changed' whenever the text changes
    """

    def __init__(self, **kwargs):
        super(TextField, self).__init__(**kwargs)

        self.buffer = ''
        self.cursor = 0
        self.start = 0

        # keybindings
        self.bindPrintable(self.typing)
        self.bindKey('left', self.moveLeft)
        self.bindKey('right', self.moveRight)
        self.bindKey('home', self.moveToStart)
        self.bindKey('end', self.moveToEnd)
        self.bindKey('backspace', self.backspace)
        self.bindKey('delete', self.delete)


    def setText(self, text):
        self.buffer = text
        self.moveToStart()
        self.touch()

        self.fireEvent('text changed') 


    def getText(self):
        return self.buffer

    def moveLeft(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = 0

        if self.cursor < self.start:
            self.start = self.cursor

        self.touch()


    def moveRight(self):
        self.cursor += 1
        if self.cursor > len(self.buffer):
            self.cursor = len(self.buffer)

        if self.cursor >= self.start + self.w:
            self.start += 1

        self.touch()

    def moveToStart(self):
        self.cursor = 0

        if self.start > 0:
            self.start = 0

        self.touch()

    def moveToEnd(self):
        self.cursor = len(self.buffer)

        if self.cursor >= self.start + self.w:
            self.start = len(self.buffer) - self.w + 1

        self.touch()

    def backspace(self):
        # the max(0, self.cursor - 1) is necessary to avoid having [:-1] as our slice
        self.buffer = self.buffer[:max(0, self.cursor-1)] + self.buffer[self.cursor:]
        self.moveLeft()

        self.fireEvent('text changed') 

    def delete(self):
        self.buffer = self.buffer[:self.cursor] + self.buffer[self.cursor+1:]

        self.touch()

        self.fireEvent('text changed') 

    def typing(self, _input_key):
        self.buffer = self.buffer[:self.cursor] + _input_key + self.buffer[self.cursor:]
        self.moveRight()

        self.touch()

        self.fireEvent('text changed') 

    def render(self):
        """
        re-displays the buffer into the curses environment
        """

        self.clear()

        self.draw(self.buffer[self.start:], 0, 0)
        if self.focused:
            self.showCursor(0, self.cursor - self.start)
        else:
            self.hideCursor()
