import curses
import types

from InputHandler import InputHandler

class Drawable(InputHandler, object):
    """
    Drawable is the basic GUI unit of dtk. It contains methods
    to set onscreen position (which should only be called from
    Engine -- use Layout & children to position elements), get
    the contents that should be drawn, input handling (provided
    by extending InputHandler), and the like.
    """

    def __init__(self, parent, name):
        """
        the only thing a drawable absolutely has to have is a
        reference to the parent object. the base Drawable will
        have the Engine as its parent.
        """

        super(Drawable, self).__init__()

        # the parent pointer
        self.parent = parent

        # our name
        self.name = name

        # initialize sane default values
        self.y = self.x = self.h = self.w = 0
        self.border = 0
        self.focused = False

        # register with the parent
        self.parent.register(self)

        # whether to redraw?
        self.touched = True

    def __str__(self):
        """
        returns the type of class this is. use getName() to
        get the name of the instance
        """
        return self.name

        """
        # split off the package name
        name = str(self.__class__).split('.')
        # return only the class name
        return name[-1]
        """

    def getName(self):
        """
        returns the Drawable's name
        """
        return self.name

    def log(self, what, who = None):
        """
        sends the message up to the parent's log function. if who
        is None, then it is set to self.__str__() before calling the
        parent's log method
        """
        if who is None:
            who = self.name

        self.parent.log(what, who)

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


    def drawContents(self):
        """
        this function is called by Engine (and through the stack
        of Drawables) to get the curses Window objects that are
        going to be drawn. this is not implemented in Drawable.
        subclasses of Drawable should not return window objects
        that are outside of the bounds specified by self.y, self.x
        (the upper-left corner) and self.w, self.h (the width and
        height)
        """
        if self.touched:
            self.render()
            self.untouch()


    def render(self):
        """
        here's where all the redrawing gets done. this is split off
        from getContents() to simplify redrawing logic so that it
        only needs to happen here in Drawable
        """
        pass


    def setSize(self, y, x, h, w):
        """
        sets the size fields to those given. fields which
        are not assigned, or which are assigned None, are
        not changed.
        """

        if y < 0 or x < 0:
            raise ValueError, "y and x arguments to setSize must be non-negative"

        if y != self.y or x != self.x or h != self.h or w != self.w:
            self.touch()

            self.y = y
            self.x = x
            self.h = h
            self.w = w


    def focus(self):
        """
        called when this Drawable gets focus
        """
        self.focused = True
        self.touch()

    def unfocus(self):
        """
        called when this Drawable loses focus
        """
        self.focused = False
        self.touch()

    def getParent(self):
        """
        returns the Drawable's parent
        """
        return self.parent


    # these functions are provided as a convenience so 
    # that Drawables need not keep around a reference
    # to the Engine. recursion is a little slow, but the
    # GUI tree depth should never be prohibitively tall

    def hideCursor(self):
        """
        call parent's hideCursor method
        """
        self.parent.hideCursor()

    def showCursor(self):
        """
        call parent's showCursor method
        """
        self.parent.showCursor()

    def register(self, drawable):
        """
        registers the drawable with the Engine, by calling up the
        stack until we get to Engine.register(). this should not
        be called directly, it is called by the Drawable's
        initializer. this makes handling keyboard input through
        Engine possible.
        """
        self.parent.register(drawable)

    def getEngine(self):
        """
        recursively call parent.getEngine() until the Engine
        gets the call, and will return a reference to itself.
        """
        return self.parent.getEngine()
    
    def _draw(self, str, row, col, drawable, **kwargs):
        """
        because we can't have an argument's defuault value
        be self (itself an argument which therefore isn't bound
        when evaluating default arg values), we have a slightly
        hackish pair-of-functions for the drawing things. it
        seems to work well enough. don't want to force extra
        arguments on the user (ie, don't want them to have to
        type 'drawable = self' in each call to draw())

        _draw is necessary in Drawable, since Layouts and other
        container-type GUI components inherit Drawable, and can
        be parents for other Drawables
        """
        self.parent._draw(str, row, col, drawable, **kwargs)

    def draw(self, str, row, col, **kwargs):
        """
        call draw up the stack
        """
        self.parent._draw(str, row, col, drawable = self, **kwargs)

    def _box(self, x, y, w, h, drawable, **kwargs):
        """
        see _draw()
        """
        self.parent._box(x, y, w, h, drawable, **kwargs)

    def box(self, x, y, w, h, **kwargs):
        """
        call box up the stack.
        """
        self.parent._box(x, y, w, h, drawable = self, **kwargs)

    def _line(self, x, y, len, drawable, **kwargs):
        """
        see _draw()
        """
        self.parent._line(x, y, len, drawable, **kwargs)

    def line(self, x, y, len, **kwargs):
        """
        draws a line starting at (x, y) and going to the right for
        len cells. ending characters may be specified with the
        leftEnd and rightEnd attributes
        """
        self.parent._line(x, y, len, drawable = self, **kwargs)

    def _lineDown(self, x, y, len, drawable, **kwargs):
        """
        see _draw()
        """
        self.parent._lineDown(x, y, len, drawable, **kwargs)

    def lineDown(self, x, y, len, **kwargs):
        """
        draws a line starting at (x, y) and going down for
        len cells. ending characters may be specified with the
        topEnd and bottomEnd attributes. line is clipped to
        the available area.
        """
        self.parent._lineDown(x, y, len, drawable = self, **kwargs)

    def _clear(self, drawable):
        """
        see _draw()
        """
        self.parent._clear(drawable)

    def clear(self):
        """
        clears the whole drawable
        """
        self.parent._clear(self)

    # XXX: this is slightly confusing and should be changed:
    # this is not the same as the curses (or other) 'cursor,'
    # but a separate cursor-like indicator drawn to screen
    # by dtk. will need to change the name of one or the other
    # at some point
    def _showCursor(self, y, x, drawable):
        """
        see _draw()
        """
        self.parent._showCursor(y, x, drawable)

    def showCursor(self, y, x):
        """
        show a cursor at the position (y, x)
        """
        self.parent._showCursor(y, x, self)
