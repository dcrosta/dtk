import string
import types
import time
import logging

from InputHandler import InputHandler


class EngineError(Exception):
    pass


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

            self.focusedDrawable = None
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
        return self.focusedDrawable


    def setFocus(self, drawable):
        """
        sets the focus to be on the given drawable, given
        by name or reference
        """
        if self.focusedDrawable is not None:
            self.log.debug('unfocusing %s (%d)', self.focusedDrawable, id(self.focusedDrawable))
            self.focusedDrawable.unfocus()

        self.log.debug('focusing %s (%d)', drawable, id(drawable))
        self.focusedDrawable = drawable.focus()
 

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


    def capabilities(self):
        """
        Returns a dict of lists of the capabilities of this
        Engine instance. Returned dict will have at least
        'attributes' and 'keynames':

          attributes: list of drawing attributes supported
            by drawing functions
          keynames: list of symbolic key names understood
            by the input system in addition to standard
            printable characters
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


    def draw(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the given row and column,
        relative to the drawing area for the drawable, with
        the drawing style defined in **kwargs. if drawing
        should continue out of the area the drawable is allowed
        to draw in, it will be clipped
        """
        pass


    def drawDown(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the position given by row and col, with
        the drawing style defined by arguments given in **kwargs.
        these will often include things like face attributes (bold,
        underline, etc), colors, and other things specific to the
        Engine. capabilities() should list all the possibilities.
        """
        pass

        
    def box(self, row, col, w, h, drawable, **kwargs):
        """
        draws a line using border characters, starting at the location
        (row, col) with the given width and height. fails silently if
        any part of the box is outside the Drawable's bounds
        """
        pass


    def line(self, row, col, len, drawable, **kwargs):
        """
        Draw the string starting at (row, col) relative to the
        upper left of this Drawable and going down. Drawing 
        will be bounded to stay within the Drawable's size.
        """
        pass


    def lineDown(self, row, col, len, drawable, **kwargs):
        """
        Draw a line starting at (row, col) relative to the upper
        left of this Drawable and going down for len characters.
        Ending characters may be specified with the topEnd and
        bottomEnd attributes.
        """
        pass


    def clear(self, drawable):
        """
        clears the whole drawable
        """
        pass


    def showCursor(self, y, x, drawable):
        """
        draws a "cursor" to the given screen position, or none at all
        if (x, y) is outside the area allowed for the drawable
        """
        pass
