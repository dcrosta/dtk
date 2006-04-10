from Drawable import Drawable

class Stack(Drawable):
    """
    Basic stack of drawables.
    """

    def __init__(self, parent, name):
        super(Stack, self).__init__(parent, name)

        self.stack = []


    def push(self, drawable):
        if len(self.stack) and self.stack[-1].focused:
            self.getEngine().pushFocus(drawable)

        self.stack.append(drawable)

        self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()


    def pop(self):
        drawable = self.stack.pop()

        if drawable.focused and len(self.stack):
            self.getEngine().popFocus(self.stack[-1])

        if len(self.stack):
            self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()


    def setSize(self, y, x, h, w):
        super(Stack, self).setSize(y, x, h, w)

        if len(self.stack):
            self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.touch()


    def drawContents(self):
        if len(self.stack):
            self.stack[-1].render()
