from Drawable import Drawable

class Stack(Drawable):
    """
    Basic stack of drawables.
    """

    def __init__(self, parent, name):
        Drawable.__init__(self, parent, name)

        self.stack = []


    def push(self, drawable):
        if len(self.stack) and self.stack[-1].hasFocus():
            self.getEngine().setFocus(drawable)

        self.stack.append(drawable)

        self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()


    def pop(self):
        drawable = self.stack.pop()

        if drawable.hasFocus() and len(self.stack):
            self.getEngine().setFocus(self.stack[-1])

        if len(self.stack):
            self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()


    def setSize(self, y, x, h, w):
        Drawable.setSize(self, y, x, h, w)

        if len(self.stack):
            self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.touch()


    def drawContents(self):
        if len(self.stack):
            self.stack[-1].render()
