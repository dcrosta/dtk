from Drawable import Drawable

class Stack(Drawable):
    """
    Basic stack of drawables.
    """

    def __init__(self, **kwargs):
        super(Stack, self).__init__(**kwargs)

        self.stack = []

    
    def __len__(self):
        """
        return the number of items currently on the stack
        """
        return len(self.stack)


    def handleInput(self, input):
        """
        give input to top item on the stack
        """
        if len(self.stack):
            consumed = self.stack[-1].handleInput(input)
            if not consumed:
                consumed = super(Stack, self).handleInput(input)

            return consumed

        else:
            return super(Stack, self).handleInput(input)


    def push(self, drawable):
        """
        push a new element onto the stack. If the previous
        top Drawable was focused, then the new drawable will
        be focused automatically. if `drawable` already exists
        in the Stack, it will be removed first, then placed on
        top.
        """
        if len(self.stack) and self.stack[-1].focused:
            self.engine.setFocus(drawable)

        # make sure there's only one copy of it
        # on the stack at any time
        if drawable in self.stack:
            self.stack.remove(drawable)

        self.stack.append(drawable)

        self.stack[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()


    def pop(self):
        """
        pop the top element off the stack. if the previous
        top stack Drawable was focused, the element underneath
        (if any) will be focused automatically. if the stack
        is empty after popping this element and that element
        had focus, then the stack itself is given focus
        """
        if len(self.stack):
            drawable = self.stack.pop()

            if drawable.focused:
                if len(self.stack):
                    self.engine.setFocus(self.stack[-1])
                else:
                    self.log.debug('forcing focus on self')
                    self.engine.setFocus(self)

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
            self.stack[-1].drawContents()


    def focus(self):
        """
        hand focus to top stack element
        """
        if len(self.stack):
            return self.stack[-1].focus()

        else:
            return super(Stack, self).focus()
