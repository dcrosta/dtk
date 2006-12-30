import logging

from Engine import Engine
from InputHandler import InputHandler

class Drawable(InputHandler):
    """
    Drawable is the basic GUI unit of dtk. It contains methods
    to set onscreen position (which should only be called from
    Engine -- use Layout & children to position elements), get
    the contents that should be drawn, input handling (provided
    by extending InputHandler), and the like.
    """

    def __init__(self, **kwargs):
        """
        the only thing a drawable absolutely has to have is a
        reference to the parent object. the base Drawable will
        have the Engine as its parent.
        """

        super(Drawable, self).__init__(**kwargs)

        # initialize sane default values
        self.y = self.x = self.h = self.w = 0
        self.border = 0

        # child of the 'dtk' logger, so Engine's handler if
        # any, will handle logging calls against self.log
        self.log = logging.getLogger('dtk.' + str(self.__class__.__name__))

        self.name = self.__class__.__name__
        if 'name' in kwargs:
            self.name = name

        self.engine = Engine()


    # `self.focused` is a property that checks whether
    # this is the Engine's current focused drawable; this
    # ensures that only one drawable can ever be focused
    def _setFocused(self, value):
        pass
    def _getFocused(self):
        return self.engine.getFocusedDrawable() == self
    focused = property(_getFocused, _setFocused)


    def __str__(self):
        """
        returns the type of class this is. use getName() to
        get the name of the instance
        """
        return self.name


    def handleInput(self, input):
        """
        Container-type drawables should override this to call
        handleInput on the correct child or children. For other,
        "regular" drawables, we just invoke InputHandler's
        handleInput here, and everything works.
        """
        return super(Drawable, self).handleInput(input)


    def touch(self):
        """
        marks the drawable as needing a redraw. this is usually called
        by the functions of the Drawable, and should not need to be
        called from outside
        """
        self.touched = True


    def untouch(self):
        """
        marks the drawable as not needing a redraw. this is usually
        called by the functions of the Drawable, and should not need
        to be called from outside
        """
        self.touched = False


    def focus(self):
        """
        this drawable has just gotten focus. return a reference
        to self to indicate to engine which drawable currently
        has focus (allows container-type drawables to hand focus
        to others)
        """
        self.log.debug('got focus (%d)', id(self))
        self.touch()

        return self


    def unfocus(self):
        """
        this drawable has just lost focus
        """
        self.log.debug('lost focus (%d)', id(self))
        self.touch()


    def drawContents(self):
        """
        if this drawable needs redrawing (because someone called
        touch() on it) then redraw using the render() method.
        otherwise, do nothing.
        """
        if self.touched:
            self.render()
            self.untouch()


    def render(self):
        """
        Drawable-specific render function. Should use self's
        draw*(), line*(), clear(), etc methods for drawing.
        """
        pass


    def setSize(self, y = None, x = None, h = None, w = None):
        """
        sets the size fields to those given. fields which
        are not assigned, or which are assigned None, are
        not changed.
        """

        if y < 0 or x < 0:
            raise ValueError, "y and x arguments to setSize must be non-negative"

        if y is not None and y != self.y:
            self.touch()
            self.y = y

        if x is not None and x != self.x:
            self.touch()
            self.x = x

        if w is not None and w != self.w:
            self.touch()
            self.w = w

        if h is not None and h != self.h:
            self.touch()
            self.h = h


    # drawables should use these methods for drawing rather than
    # directly calling Engine's equivalents, since these will
    # pass a reference to this Drawable to the Engine for bounding

    def showCursor(self, row, col):
        """
        Move the cursor to (row, col) relative to this Drawable's
        upper left, and show it if it is currently hidden.
        """
        self.engine.showCursor(row, col, drawable = self)
        

    def hideCursor(self):
        """
        call Engine's hideCursor method
        """
        self.engine.hideCursor()


    def draw(self, str, row, col, **kwargs):
        """
        Draw the string starting at (row, col) relative to the
        upper left of this Drawable. Drawing will be bounded
        to stay within this Drawable's size.
        """
        self.engine.draw(str, row, col, drawable = self, **kwargs)

    
    def drawDown(self, str, row, col, **kwargs):
        """
        Draw the string starting at (row, col) relative to the
        upper left of this Drawable and going down. Drawing 
        will be bounded to stay within the Drawable's size.
        """
        self.engine.draw(str, row, col, drawable = self, **kwargs)


    def box(self, row, col, w, h, **kwargs):
        """
        Draw a box of border characters, beginning at (row, col)
        relative to the upper left of this Drawable, extending
        for w characters wide (inclusive of both borders) and
        h characters high (inclusive of both borders).
        """
        self.engine.box(row, col, w, h, drawable = self, **kwargs)


    def line(self, row, col, len, **kwargs):
        """
        Draw a line starting at (row, col) relative to this
        Drawable's upper-left and going right for len characters.
        Ending characters may be specified with the leftEnd and
        rightEnd attributes.
        """
        self.engine.line(row, col, len, drawable = self, **kwargs)


    def lineDown(self, row, col, len, **kwargs):
        """
        Draw a line starting at (row, col) relative to the upper
        left of this Drawable and going down for len characters.
        Ending characters may be specified with the topEnd and
        bottomEnd attributes.
        """
        self.engine.lineDown(row, col, len, drawable = self, **kwargs)


    def clear(self):
        """
        clears the whole drawable
        """
        self.engine.clear(self)
