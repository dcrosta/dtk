from Drawable import Drawable

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
    """

    def __init__(self, parent, name):
        super(TextField, self).__init__(parent, name)

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
        self.touch()


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

    def delete(self):
        self.buffer = self.buffer[:self.cursor] + self.buffer[self.cursor+1:]

        self.touch()

    def typing(self, _input_key):
        self.buffer = self.buffer[:self.cursor] + _input_key + self.buffer[self.cursor:]
        self.moveRight()

        self.touch()

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
