import string
import types
import time
import logging

from Drawable import Drawable
from InputHandler import InputHandler

class Engine(InputHandler):
    """
    Engine handles the main event loop of dtk, manages
    a list of Drawables, and handles input parsing and
    dispatch to Drawables.

    conventions:
    
    the 'root' Drawable is the currently displayed
    drawable that takes up the entire available screen.
    it may itself contain other Drawables, which may be
    smaller.

    the 'focused' Drawable is the first to recieve input
    after it is parsed. it is always in the tree of
    Drawables defined with the 'root' drawable as it's
    root (hence the name).

    for the most part, Engine is an abstract class, that
    should have functionality implemented in a platform-
    specific way by a child class (eg CursesEngine)

    Engine is an abstract class. CursesEngine is the concrete
    implementation for the curses library.

    Engine is a singleton. This means you don't need to ever
    keep a reference to it, you can simply call

      e = Engine()

    at any time, and you will get the first-created instance
    of Engine assigned to e.
    """

    _instance = None
    _initialized = False

    def __new__(clazz, *args, **kwargs):
        """
        Allocate or return the singleton instance of Engine. Currently
        creates an instance of the concrete sublcass CursesEngine (no
        other known concrete implementations exist).
        """
        if clazz._instance is None:
            import CursesEngine
            Engine._instance = object.__new__(CursesEngine.CursesEngine)

        return clazz._instance

    def __init__(self, **kwargs):
        """
        Initialize a new Engine. Engine will create a console environment
        and everything, so you don't need to do that outside or pass
        any arguments in. Calling the mainLoop() function will start
        the main event loop.
        """

        if not Engine._initialized:
            # _initialized is False the first time Engine() is
            # allocated and initialized; subsequently it is True
            Engine._initialized = True

            super(Engine, self).__init__()

            self.name = 'dtk Application'
            self.title = self.name

            self.log = logging.getLogger('dtk')
            self.log.setLevel(logging.NOTSET + 1) # log all messages

            self.drawables = {}
            self.focusStack = []
            self.root = None


    def __str__(self):
        return 'Engine'


    def beginLogging(self, file = None, level = logging.ERROR, formatter = None, handler = None):
        """
        configure the logging subsystem and begin logging
        calls from within dtk.

        if `file` is not None, a FileHandler will be created
        with the given filename. the level for this handler
        will be that specified in `level`. if `formatter` is
        not None, this formatter will be used in place of the
        defailt formatter: 

          logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

        if `handler` is a log handler, it will used in addition
        to any handler possibly created by other arguments
        """ 

        if file is not None:
            fileHandler = logging.FileHandler(file)
            fileHandler.setLevel(level)

            if isinstance(formatter, logging.Formatter):
                fileHandler.setFormatter(formatter)
            else:
                fileHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))

            self.log.addHandler(fileHandler)
            
        if isinstance(handler, logging.Handler): 
            self.log.addHandler(handler)

        self.log.debug('Logging initialized')


    def getScreenSize(self):
        """
        return a tuple (height, width) of the current screen size
        """
        pass
        

    def setTitle(self, title):
        """
        Set the title of the window running DTK, if possible
        """
        self.title = title


    def getTitle(self):
        """
        Return the title as previously set by setTitle()
        """
        return self.title


    def mainLoop(self):
        """
        runs the main event loop
        """
        pass


    def getFocusedDrawable(self):
        """
        returns the drawable that has focus. raises an Exception
        if the number of focused drawables is not exactly 1
        """
        f = []
        for name in self.drawables:
            drawable = self.drawables[name]
            if drawable.focused:
                f.append(drawable)

        if len(f) is not 1:
            self.log.debug("focused drawables: %s" % f)
            raise Exception, "Number of focused drawables is not exactly 1."

        return f[0]


    def setFocus(self, drawable):
        """
        sets the focus to be on the given drawable, given
        by name or reference
        """

        self.focusStack = []
        self._setFocus(drawable)


    def _setFocus(self, drawable):

        if type(drawable) in types.StringTypes:
            drawable = self.drawables[drawable]

        if isinstance(drawable, Drawable):
            toFocus = None
            for d in self.drawables.values():
                if d == drawable:
                    toFocus = d
                elif d.focused:
                    d.unfocus()

            # do this last, so that the unfocusing 
            # happens first
            if toFocus is not None: toFocus.focus()

        else:
            raise TypeError, "setFocus expects a dtk.Drawable or the name of a registered Drawable"


    def pushFocus(self, drawable):
        """
        like setFocus, but retains the previous focused elements
        in an internal stack. calls to popFocus undo this action
        incrementally; calls to setFocus erase the stack.
        """

        # if we're pushing for the first time, prepend the name of the 
        # currently focused drawable
        if len(self.focusStack) == 0:
            self.focusStack.append(self.getFocusedDrawable().name)

        if isinstance(drawable, Drawable):
            drawable = drawable.name

        elif not type(drawable) in types.StringTypes:
            raise TypeError, "pushFocus expects a dtk.Drawable or the name of a registered Drawable"

        # make sure it only ends up in the stack once
        if drawable in self.focusStack:
            self.focusStack.remove(drawable)
        self.focusStack.append(drawable)

        self._setFocus(drawable)


    def popFocus(self, drawable = None):
        """
        If there is more than one Drawable on the focused
        elements stack, then the most recently pushed Drawable
        is removed, and the next most recently focused one
        is set to be the focused Drawable. Otherwise, no
        action is taken

        if the optional 'drawable' argument is set, the stack
        is popped to the element just underneath the given
        drawable, if it is in the stack
        """
        
        if len(self.focusStack) > 1:
            if isinstance(drawable, Drawable):
                drawable = drawable.name
    
                if drawable in self.focusStack:
                    spot = self.focusStack.index(drawable)
        

                    # remove the elements after spot
                    del self.focusStack[spot:]


            else:
                self.focusStack.pop()
    

            self._setFocus(self.focusStack[-1])
            self.root.clear()


    def peekFocus(self, drawable = None):
        """
        returns the top element from the focus stack 
        """
        
        if len(self.focusStack):
            return self.focusStack[-1]

        return None


    def register(self, drawable):
        """
        registers the drawable with the Engine. this should not
        be called directly, it is called by the Drawable's
        initializer. this makes handling keyboard input through
        Engine possible.
        """
        self.drawables[drawable.name] = drawable

        # if this is the first drawable we get registered,
        # it is by default the focused root drawable
        if len(self.drawables) == 1:
            self.setRoot(drawable)
            self.setFocus(drawable)

    def setRoot(self, drawable):
        """
        set the given drawable as the root drawable. this is
        usually not necessary, as the first drawable to register
        with Engine as its parent will be set as the root drawable
        automatically. this is provided in cases where you want
        to change the root drawable.
        """
        self.root = drawable

    def getRoot(self):
        """
        returns the root drawable, as set by setRoot()
        """
        return self.root

    
    def getDrawable(self, name):
        """
        returns the Drawable with the given name, or None if
        Engine doesn't know about the given Drawable
        """
        try:
            return self.drawables[name]
        except:
            return None


    def resize(self):
        """
        tells the engine that a resize has happened or that it
        should believe that one has happened and resize all the
        visible Drawables
        """
        pass
            

    def quit(self):
        """
        quit the main loop, exit the program, etc
        """
        pass

    def getEngine(self):
        """
        recursively call parent.getEngine() until the Engine
        gets the call, and will return a reference to itself.
        """
        return self

    def capabilities(self):
        """
        returns a list of the drawing capabilities of this Engine
        """
        pass

    def shellMode(self):
        """
        pauses the main loop and returns the terminal to the shell
        mode it was in before starting the Engine. opposite of
        dtkMode()
        """
        pass

    def dtkMode(self):
        """
        returns to dtk mode (from shell mode) and restarts the main
        loop. opposite of shellMode()
        """
        pass

    def touchAll(self):
        """
        causes all drawables to be re-drawn on the next refresh
        """
        pass

    def _draw(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the position given by row and col, with
        the drawing style defined by arguments given in **kwargs.
        these will often include things like face attributes (bold,
        underline, etc), colors, and other things specific to the
        Engine. capabilities() should list all the possibilities.
        """
        pass

    def _drawDown(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the position given by row and col, with
        the drawing style defined by arguments given in **kwargs.
        these will often include things like face attributes (bold,
        underline, etc), colors, and other things specific to the
        Engine. capabilities() should list all the possibilities.
        """
        pass

    def _box(self, x, y, w, h, drawable, **kwargs):
        """
        draws a line using border characters appropriate to the 
        underlying technology, starting at the location given by
        (x, y) with the given width and height.
        """
        pass

    def _line(self, x, y, len, drawable, **kwargs):
        """
        draws a line starting at (x, y) and going to the right for
        len cells. ending characters may be specified with the
        leftEnd and rightEnd attributes
        """
        pass

    def _lineDown(self, x, y, len, drawable, **kwargs):
        """
        draws a line starting at (x, y) and going down for
        len cells. ending characters may be specified with the
        topEnd and bottomEnd attributes. line is clipped to
        the available area.
        """
        pass

    def _clear(self, drawable):
        """
        clears the whole drawable
        """
        pass

    def _showCursor(self, y, x, drawable):
        """
        draws a cursor to the given screen position, or none at all
        if (x, y) is outside the area allowed for the drawable
        """
        pass
