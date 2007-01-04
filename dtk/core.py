import string
import types
import time
import logging

import _curses
import curses
import curses.ascii


class InputHandler(object):
    """
    The base class for objects which deal with keyboard and
    pseudo-key input.
    """

    # remap certain printable inputs for output
    printableVersion = {
        'space':' '
        }


    def __init__(self, *args, **kwargs):
        # keybindings dict
        self.keybindings = {}


    def handleInput(self, input):
        """
        first sees if the InputHandler is set up to handle printable
        input by looking for the 'printable' key in self.keybindings.
        if so, then the printable characters method is called with
        optional userdata. if not, processing proceeds as below:

        if we can find key in self.keybindings, then we execute the
        associated function with the associated userdata and return
        the result of the method (True or False) to indicate that
        handling is finished, or else we return False to indicate that
        this InputHandler's parent should be asked to handle the
        input
        """

        self.log.debug("handleInput('%s')", input)

        method = None
        args   = []
        kwargs = {}
                
        if 'printable' in self.keybindings and self.isprintable(input):
            (method, args, kwargs) = self.keybindings['printable']

            if len(input) > 1:
                input = self.printableVersion[input] # map things like 'space' => ' '            

        elif input in self.keybindings:
            (method, args, kwargs) = self.keybindings[input]

        else:
            return False
       
        # copy the kwargs dictionary so that we don't save any of the
        # extra information we're about to conditionally pass along
        # (or overwrite anything passed in from the user)
        kwargs = dict(kwargs)

        # if the method is asking for a _input_key argument,
        # supply it to the method before calling it
        # unless another input key is already being supplied to the method
        # TODO this is actually broken (see below)
        if '_input_key' in method.func_code.co_varnames:
            kwargs['_input_key'] = kwargs.get('_input_key', None) or input

        # if the method is asking for a _source_obj argument,
        # bind the present object to the method before calling it
        # unless another object is already bound to the method
        # TODO this is actually broken. it will still fill the slot
        # if the user passes in a POSITIONAL argument for _source_obj,
        # resulting in an exception.
        if '_source_obj' in method.func_code.co_varnames:
            kwargs['_source_obj'] = kwargs.get('_source_obj', None) or self
            
        ret = method(*args, **kwargs)
        return True


    def bindKey(self, key, method, *args, **kwargs):
        """
        tell the input subsystem that the given key should
        have the effect of calling the given method with
        the given arguments and keyword arguments
        """
        self.keybindings[key] = (method, args, kwargs)


    def unbindKey(self, key):
        """
        removes the binding for key from the InputHandler's
        keybindings, if it exists. removing the pseudo-key 'all'
        removes all keybindings from the InputHandler.
        """

        if key == 'all':
            for key in self.keybindings.keys():
                del(self.keybindings[key])

        elif key in self.keybindings:
            del(self.keybindings[key])


    def bindPrintable(self, method, *args, **kwargs):
        """
        tell the input subsystem that printable characters
        should be passed to the given method as they arrive.
        printable characters are anything for which
        curses.ascii.isprint() returns True. 
        """
        self.keybindings['printable'] = (method, args, kwargs)


    def unbindPrintable(self):
        """
        tells the input subsystem that we don't want to handle
        printable character input
        """
        self.unbindKey('printable')


    def isprintable(self, input):
        if input in self.printableVersion:
            return True
        elif len(input) > 1:
            return False
        else:
            return curses.ascii.isprint(input)



class Drawable(InputHandler):
    """
    Drawable is the basic GUI unit of dtk. It contains methods
    to set onscreen position (which should only be called from
    Engine -- use Containers & children to position elements), get
    the contents that should be drawn, input handling (provided
    by extending InputHandler), and the like.
    """

    def __init__(self, *args, **kwargs):
        """
        the only thing a drawable absolutely has to have is a
        reference to the parent object. the base Drawable will
        have the Engine as its parent.
        """

        super(Drawable, self).__init__(*args, **kwargs)

        # initialize sane default values
        self.y = self.x = self.h = self.w = 0
        self.border = 0

        # child of the 'dtk' logger, so Engine's handler if
        # any, will handle logging calls against self.log
        self.log = logging.getLogger('dtk.' + str(self.__class__.__name__))

        self.name = self.__class__.__name__
        if 'name' in kwargs:
            self.name = kwargs['name']

        self.engine = Engine()
        self.context = self.engine

        self.touched = True
        self._meta = dict()


    # `self.focused` is a property that checks whether
    # this is the Engine's current focused drawable; this
    # ensures that only one drawable can ever be focused
    def _setFocused(self, value):
        raise EngineException("Do not set focus on a Drawable directly.  Call Engine::setFocus instead.")
    def _getFocused(self):
        return self.context.getFocusedDrawable() is self
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
            self.log.debug('calling render()')
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
        self.engine.drawDown(str, row, col, drawable = self, **kwargs)


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



class Container(Drawable):
    """
    base class for all on-screen elements which contain other
    on-screen elements. This class and subclasses need to
    implement a few methods:

    * setActiveDrawable(Drawable):
       * considers each of its children
       * if the child is the drawable, it updates its internal
         active reference and returns True
       * if the child is a container, it says
         child.setActiveDrawable(someDrawable), and looks at
         the return value
       * if the return is True, it updates its internal active
         reference to point at the container and returns True
       * otherwise it continues through it's list/dict/whatever
         of children. if it gets through all of them without
         getting True or finding the drawable, then it returns
         False, leaving the active reference as it was 
    * getActiveDrawable():
       * if active reference is a Drawable, return it
       * otherwise call getActiveDrawable() on the active child 
    * getActivePath():
       * Returns a list of the Drawables and Containters on the
         active path beginning at this node. The first element
         in the list will be self, the next element will be the
         active reference, etc. 
    * touchAll():
       * for each child, call touchAll() (if child is a Container)
         or touch() (if child is a Drawable)
    * setContext(context):
       * for each child, call setContext() (if child is a Container)
         or simply set the context member to the given value (if
         child is a Drawable)

    Containers which want to provide methods to update the active
    status among their children (ie nextRow() in Rows) can update
    the active reference; if the Rows is on the active path, then
    the new child is automatically focused. When doing this,
    Containers should call getActivePath() on Engine; if self is
    in the active path, then the previous active path below self
    should be notified that it is no longer active, and the new
    active path should be notified that it is now active.

    The default state of active for a Container is up to the
    container to decide; pick something sensible for each.

    Additionally, containers need to define a drawContents()
    method which calls the container's children's drawContents()
    methods as appropriate to the container.

    Containers should also override setSize(...) from Drawable
    in a way appropriate to the container.

    The methods in this class use a list, self.children, and a
    reference, self.active, to implement the above-described
    behavior. Subclasses should directly manage those instance
    variables.
    """

    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self.children = []
        self.active = None

    def drawContents(self):
        """
        Draws the contents of the container.  The proper drawing
        behavior is defined differently by each Container subclass
        and is not defined for the Container interface itself.
        """
        if not issubclass(self.__class__, Container):
            raise ContainerException("drawContents method not implemented")
        else:
            super(Container, self).drawContents()

    def setActiveDrawable(self, drawable):
        """
        * considers each of its children
        * if the child is the drawable, it updates its internal
          active reference and returns True
        * if the child is a container, it says
          child.setActiveDrawable(someDrawable), and looks at
          the return value
        * if the return is True, it updates its internal active
          reference to point at the container and returns True
        * otherwise it continues through it's list/dict/whatever
          of children. if it gets through all of them without
          getting True or finding the drawable, then it returns
          False, leaving the active reference as it was 
        """
        success = False

        for child in self.children:
            if child is drawable:
                self.log.debug('setting active to drawable == %s', drawable)
                self.active = child
                success = True
                break

            elif isinstance(child, Container):
                self.log.debug('calling setActiveDrawable on %s', child)
                if child.setActiveDrawable(drawable):
                    self.active = child
                    success = True
                    break

        return success


    def getActiveDrawable(self):
        """
        * if active reference is a Drawable, return it
        * otherwise call getActiveDrawable() on the active child 
        """

        if isinstance(self.active, Container):
            return self.active.getActiveDrawable()

        else:
            return self.active


    def getActivePath(self):
        """
        * Returns a list of the Drawables and Containters on the
          active path beginning at this node. The first element
          in the list will be self, the next element will be the
          active reference, etc. 
        """

        path = [self]

        if isinstance(self.active, Container):
            path.extend(self.active.getActivePath())

        else:
            path.append(self.active)

        return path


    def touchAll(self):
        """
        call touchAll() or touch() on each child if it is
        a Container or a Drawable, respectively. also
        touch self.
        """
        for child in self.children:
            if isinstance(child, Container):
                child.touchAll()
            elif isinstance(child, Drawable): 
                child.touch()

        self.touch()


    def setContext(self, context):
        """
        sets the context member of each Drawable and Container
        at or below this Container; should be used only from
        within Engine
        """
        for child in self.children:
            if isinstance(child, Container):
                child.setContext(context)
            else:
                child.context = context

        self.context = context


    def handleInput(self, input):
        """
        try the input on the active child/path first, and if it
        is not consumed, then try it on self before returning.
        return True if the active path at or below this node consumed
        the input, False otherwise
        """

        self.log.debug('InputHandler: calling handleInput on %s', self.active)
        consumed = self.active.handleInput(input)
        if not consumed:
            self.log.debug('InputHandler: calling handleInput on %s', self)
            consumed = super(Container, self).handleInput(input)

        return consumed



class EngineException(Exception):
    pass

class NoInputCharException(Exception):
    pass

class ContainerException(Exception):
    pass


class InputContext(InputHandler):

    def __init__(self, modal = True, *args, **kwargs):
        super(InputContext, self).__init__(*args, **kwargs)

        self.root = None
        self.modal = modal
        self.done = False


    def quit(self):
        """
        stop processing this context
        """
        self.done = True


    def unquit(self):
        """
        allow input processing to happen again
        """
        self.done = False


    def getFocusedDrawable(self):
        """
        returns the drawable that has focus
        """
        if isinstance(self.root, Container):
            return self.root.getActiveDrawable()
        else:
            return self.root


    def setFocus(self, drawable):
        """
        Set the focused drawable to the given one
        """

        if isinstance(self.root, Container):
            self.log.debug('self.root.setActiveDrawable(%s)', drawable)
            self.root.setActiveDrawable(drawable)
        else:
            if self.root is drawable:
                return
            else:
                raise EngineException, "To change the root Drawable, use setRoot()"
 

    def setRoot(self, drawable):
        """
        set the given drawable as the root drawable.
        """
        self.root = drawable


    def getRoot(self):
        """
        returns the root drawable, as set by setRoot()
        """
        return self.root





class Engine(InputContext):
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

    # for managing the singleton instance
    _instance = None
    _initialized = False


    # attributes for drawing
    attrs = {
        'bold':curses.A_BOLD,
        'highlight':curses.A_REVERSE,
        'normal':curses.A_NORMAL,
        'blink':curses.A_BLINK,
        'dim':curses.A_DIM,
        'bright':curses.A_STANDOUT,
        'underline':curses.A_UNDERLINE
        }

    colors = None


    # this map is used to handle non-printable input characters
    # from the curses module with the keypad(True) method called.
    # in theory input values are meant to be in [0-255], but
    # python's curses module seems to give back some values
    # that are more than one byte, but that might be OK as long
    # as it is consistent.
   
    keymap = { 
               curses.ascii.ESC : "esc",
               curses.ascii.TAB : "tab",
               curses.ascii.NL  : "enter", # regular "return" key
               curses.KEY_ENTER : "enter", # the numpad enter key

               curses.KEY_UP    : "up",
               curses.KEY_DOWN  : "down",
               curses.KEY_LEFT  : "left",
               curses.KEY_RIGHT : "right",

               curses.KEY_HOME  : "home",
               curses.KEY_NPAGE : "page down",
               curses.KEY_PPAGE : "page up",
               curses.KEY_END   : "end",

               curses.KEY_BACKSPACE : "backspace",
               curses.ascii.DEL : "backspace",

               curses.KEY_IC    : "insert",
               curses.KEY_DC    : "delete",

               curses.KEY_F1  : "F1",
               curses.KEY_F2  : "F2",
               curses.KEY_F3  : "F3",
               curses.KEY_F4  : "F4",
               curses.KEY_F5  : "F5",
               curses.KEY_F6  : "F6",
               curses.KEY_F7  : "F7",
               curses.KEY_F8  : "F8",
               curses.KEY_F9  : "F9",
               curses.KEY_F10 : "F10",
               curses.KEY_F11 : "F11",
               curses.KEY_F12 : "F12",
               } 




    def __new__(clazz, *args, **kwargs):
        """
        Allocate or return the singleton instance of Engine. Currently
        creates an instance of the concrete sublcass CursesEngine (no
        other known concrete implementations exist).
        """
        if clazz._instance is None:
            Engine._instance = object.__new__(Engine)

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

            super(Engine, self).__init__(modal = False)

            # some things can only be done once curses.init_scr has been called
            self.cursesInitialized = False
            self.doWhenCursesInitialized = []

            self.name = kwargs.get('name', 'dtk Application')
            self.title = self.name

            self.log = logging.getLogger('dtk')
            self.log.setLevel(logging.NOTSET + 1) # log all messages

            # initially, we are tiny!
            self.w = 0
            self.h = 0
            self.resized = False



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
        return a tuple (height, width) of the current screen size,
        or (None, None) if curses hasn't been initialized
        """
        if self.cursesInitialized:
            return self.scr.getmaxyx()
        else:
            return (None, None)
        

    def setTitle(self, title):
        """
        Set the title of the window running DTK, if possible
        """
        self.title = title
        print "\033]0;%s\007" % self.title


    def getTitle(self):
        """
        Return the title as previously set by setTitle()
        """
        return self.title


    def mainLoop(self):
        """
        runs the main event loop
        """

        # check things we need
        if self.root is None:
            raise EngineError, "Must set a root Drawable with setRoot()"

        curses.wrapper(self.cursesMainLoop)


    def cursesMainLoop(self, scr):
        """
        the actual main loop. waits for input and
        does its thing.
        """

        self.scr = scr
        (self.h, self.w) = self.scr.getmaxyx()
        
        self.setTitle(self.title)

        # our terminating condition
        self.done = False

        # ask curses to parse the input for us into
        # single integers at a time
        self.scr.keypad(True)
        
        # this doesn't always work in all terms, but will never
        # fail in such a way as to break anything. by default
        # we want to hide it to keep the GUI pretty
        self.hideCursor()

        # here we do anything we decided could only be done
        # after curses is initialized
        self.cursesInitialized = True
        for foo in self.doWhenCursesInitialized:
            if type(foo) == types.TupleType:
                (method, kwargs) = foo

                method(**kwargs)
            else:
                foo()

        # these are all 0 so that we get a "resize" on the first time
        self.lasth = self.lastw = 0
        self.resized = True

        # handle input every 2/10th of a second
        #
        # this is necessary to handle input of (possibly
        # among others) 'esc'
        curses.halfdelay(3)

        self.contextLoop(self)

        self.shellMode()


    def contextLoop(self, context):
        (h, w) = self.scr.getmaxyx()
        context.root.setSize(0, 0, h, w)

        if isinstance(context.root, Container):
            context.root.setContext(context)
        else:
            context.root.context = context

        # call into the main loop of the current context
        while not context.done:
            (h, w) = self.scr.getmaxyx()

            # update self.resized to be True if the height
            # or width has changed since the last iteration
            resized = self.resized or h != self.lasth or w != self.lastw
            if resized:
                # a resize has happened
                self.log.debug('screen resized (%d, %d) => (%d, %d)', self.lasth, self.lastw, h, w)

                # try to erase everything (necessary in some terms)
                self.scr.move(0,0)
                self.scr.clrtobot()
                self.scr.refresh()

                context.root.setSize(0, 0, h, w)

                self.resized = False
                self.lasth = h
                self.lastw = w


            # wait to update the screen state
            self.scr.noutrefresh()


            context.root.drawContents()


            # draw the cursor only if it's valid and should be shown
            if self.cursorpos == (-1, -1):
                if curses.tigetstr('civis') is not None:
                    curses.curs_set(0)
            else:
                if curses.tigetstr('cnorm') is not None:
                    curses.curs_set(1)
                self.scr.move(self.cursorpos[0], self.cursorpos[1])


            # now update
            self.scr.refresh()
            curses.doupdate()

            # get and parse the input
            #
            # for multi-byte input, this whole section will
            # be called multiple times, which means that
            # parseInput only gets access to one byte of the
            # input at a time, and must maintain its state
            # (ie location in keymap) somehow
            input = self.scr.getch()
            try:
                input = self.parseInput(input)
            except NoInputCharException:
                input = None
                
            # after this, input will be a convenient string
            # such as 'a' or 'space', or None, which means
            # we're waiting on further multi-byte input

            if input is not None:
                self.log.debug('Engine: calling handleInput on %s', context.root)
                if not context.root.handleInput(input) and not context.modal:
                    self.log.debug('Engine: calling handleInput on %s', context)
                    context.handleInput(input)
        



    def parseInput(self, char):
        """
        if the char is a printable character, we just return it.
        if it's one of the special curses characters (for things
        like arrow keys, combinations, etc) then we will try
        our best to figure out what it was and return that instead.

        Ths method has been ruined by Peter Norton

        Now with logging
        """

        # In half-delay mode with 8-bit (and more! BONUS BITS!)  input
        # python curses' screen.getch() will return -1 to indicate
        # that no key was pressed. It's documented as raising an
        # exception, but I'm happy to get something consistant in this
        # all-too-underdocumented module.
        #
        # XXX report the documentation inconsistancy to get it fixed?
        #
        # -PN
        if char == -1:
            # awwww... heck, raise an exception
            raise NoInputCharException

        # If it's the decimal representation of
        # a printable character... HEY! THAT'S EASY!
        elif curses.ascii.isprint(char):
            self.log.debug("Returning char %s" % chr(char))
            return chr(char)

        # If it's in keymap via a direct lookup, we're golden
        elif char in self.keymap:
            self.log.debug("Returning char %d as %s (curses name %s)", char, self.keymap[char], curses.keyname(char))
            return(self.keymap[char])

        # If we got here, bad user, bad user
        else:
            self.log.info("couldn't parse char: %d" % char)
            # return None
            raise NoInputCharException


    def resize(self):
        """
        tells the engine that a resize has happened or that it
        should believe that one has happened and resize all the
        visible Drawables
        """
        self.resized = True


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
        return {'attributes': self.attrs.keys(),
                'keynames': self.keymap.values() }


    def shellMode(self):
        """
        pauses the main loop and returns the terminal to the shell
        mode it was in before starting the Engine. opposite of
        dtkMode()
        """

        # save the program mode
        curses.def_prog_mode()

        self.scr.move(0, 0)
        self.scr.clrtobot()

        # this drops us to shell mode...
        # the next call to curses.refresh() will
        # return to curses mode
        curses.endwin()


    def dtkMode(self):
        """
        returns to dtk mode (from shell mode) and restarts the main
        loop. opposite of shellMode()
        """
        self.touchAll()

    
    def touchAll(self):
        """
        causes all drawables to be re-drawn on the next refresh
        TODO: implement in Container?
        """
        if isinstance(self.root, Container):
            self.root.touchAll()
        else:
            self.root.touch()


    def hideCursor(self):
        """
        hides the cursor, if possible
        """
        self.cursorpos = (-1, -1)


    def showCursor(self, y, x, drawable):
        """
        draws a "cursor" to the given screen position, or none at all
        if (x, y) is outside the area allowed for the drawable
        """
        if x < 0 or x > drawable.w or y < 0 or y > drawable.h:
            self.cursorpos = (-1, -1)
        else:
            self.cursorpos = (drawable.y + y, drawable.x + x)


    def draw(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the given row and column,
        relative to the drawing area for the drawable, with
        the drawing style defined in **kwargs. if drawing
        should continue out of the area the drawable is allowed
        to draw in, it will be clipped
        """

        # if it's completely off-screen, don't draw
        if row < 0 or row > self.h or col > self.w:
            return

        # truncate the string to fit
        if col + len(str) > drawable.w:
            str = str[:self.w - col]

        if col < 0:
            str = str[-col:]
            col = 0

        # offset the drawable by its origin
        row += drawable.y
        col += drawable.x

        # now draw it
        try:
            #self.log.debug('addstr(%d, %d, "%s", %d)', row, col, str, self.cursesAttr(kwargs))
            self.scr.addstr(row, col, str, self.cursesAttr(kwargs))
        except _curses.error, e:
            pass


    def drawDown(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the position given by row and col, with
        the drawing style defined by arguments given in **kwargs.
        these will often include things like face attributes (bold,
        underline, etc), colors, and other things specific to the
        Engine. capabilities() should list all the possibilities.
        """

        if row > drawable.h or col < 0 or col > drawable.w:
            return

        attr = self.cursesAttr(kwargs)

        row += drawable.y

        for char, r in zip(str, range(row, min(drawable.y + drawable.h, self.h))):
            self.scr.addstr(r, col, char, attr)


        
    def box(self, row, col, w, h, drawable, **kwargs):
        """
        draws a line using border characters, starting at the location
        (row, col) with the given width and height. fails silently if
        any part of the box is outside the Drawable's bounds
        """

        # check bounds
        if col < 0 or row < 0 or col + w > drawable.w or row + h > drawable.h:
            return

        col += drawable.x
        row += drawable.y

        attr = self.cursesAttr(kwargs)

        # draw corners
        self.scr.addch(row, col, curses.ACS_ULCORNER, attr)
        self.scr.addch(row, col + w - 1, curses.ACS_URCORNER, attr)
        self.scr.addch(row + h - 1, col, curses.ACS_LLCORNER, attr)
        try:
            self.scr.addch(row + h - 1, col + w - 1, curses.ACS_LRCORNER, attr)
        except _curses.error, e:
            pass

        # draw edges
        if attr:
            # if we have an attribute, we have to draw char-brow-char
            for r in range(col + 1, col + w - 1):
                self.scr.addch(row, r, curses.ACS_HLINE, attr)
                self.scr.addch(row + h - 1, r, curses.ACS_HLINE, attr)
    
            for c in range(row + 1, row + h - 1):
                self.scr.addch(c, col, curses.ACS_VLINE, attr)
                self.scr.addch(c, col + w - 1, curses.ACS_VLINE, attr)

        else:
            # else we can use these functions which are probablrow quicker
            self.scr.hline(row, col + 1, curses.ACS_HLINE, w - 2)
            self.scr.hline(row + h - 1, col + 1, curses.ACS_HLINE, w - 2)

            self.scr.vline(row + 1, col, curses.ACS_VLINE, h - 2)
            self.scr.vline(row + 1, col + w - 1, curses.ACS_VLINE, h - 2)


    def line(self, row, col, len, drawable, **kwargs):
        """
        Draw the string starting at (row, col) relative to the
        upper left of this Drawable and going down. Drawing 
        will be bounded to stay within the Drawable's size.
        """
        self.log.debug('line(row=%d, col=%d, len=%d, drawable="%s", rightEnd = %s, leftEnd = %s)', row, col, len, drawable, kwargs.get('rightEnd', None), kwargs.get('leftEnd', None))

        # invisible line
        if row < 0 or row > drawable.h:
            return

        if col < 0:
            len += col
            col = 0
        if col + len > drawable.w:
            len -= (drawable.w - len)

        col += drawable.x
        row += drawable.y

        attr = self.cursesAttr(kwargs)

        if 'leftEnd' in kwargs:
            self.scr.addch(row, col, kwargs['leftEnd'], attr)
            len -= 1
            col += 1

        if 'rightEnd' in kwargs:
            self.scr.addch(row, col + len - 1, kwargs['rightEnd'], attr)
            len -= 1

        if attr:
            for c in range(col, col + len):
                self.scr.addch(row, c, curses.ACS_HLINE, attr)
        else:
            self.scr.hline(row, col, curses.ACS_HLINE, len)



    def lineDown(self, row, col, len, drawable, **kwargs):
        """
        Draw a line starting at (row, col) relative to the upper
        left of this Drawable and going down for len characters.
        Ending characters may be specified with the topEnd and
        bottomEnd attributes.
        """
        self.log.debug('lineDown(row=%d, col=%d, len=%d, drawable="%s", topEnd = %s, bottomEnd = %s)', row, col, len, drawable, kwargs.get('topEnd', None), kwargs.get('bottomEnd', None))

        # invisible line
        if col < 0 or col > drawable.w:
            return

        if row < 0:
            len += row
            row = 0
        if row + len > drawable.h:
            len -= (drawable.h - len)

        col += drawable.x
        row += drawable.y

        attr = self.cursesAttr(kwargs)

        if 'topEnd' in kwargs:
            self.scr.addch(row, col, kwargs['topEnd'], attr)
            len -= 1
            row += 1

        if 'bottomEnd' in kwargs:
            self.scr.addch(row + len - 1, col, kwargs['bottomEnd'], attr)
            len -= 1

        if attr:
            for r in range(row, row + len):
                self.scr.addch(r, col, curses.ACS_VLINE, attr)
        else:
            self.scr.vline(row, col, curses.ACS_VLINE, len)


    def clear(self, drawable):
        """
        clears the whole drawable
        """

        self.log.debug('clear(%d, %d => %d, %d)', drawable.y, drawable.x, drawable.y + drawable.h, drawable.x + drawable.w)

        for r in range(drawable.y, drawable.y + drawable.h):
            try:
                self.scr.addstr(r, drawable.x, ' ' * (drawable.w))
            except:
                pass


    # curses support functions

    def cursesAttr(self, attrdict):
        """
        calculate the attribute bitstring for curses drawing
        """

        attr = 0

        fg = 'white'
        bg = 'black'

        for name in attrdict.keys():
            if name == 'foreground' or name == 'fg':
                fg = attrdict[name]
            elif name == 'background' or name == 'bg':
                bg = attrdict[name]
            elif name in self.attrs and attrdict[name] == True:
                attr |= self.attrs[name]

        attr |= self.lookupColorPair(fg, bg)

        return attr


    def lookupColorPair(self, fg, bg):
        """
        initialize curses colors, adds appropriate
        constants to self.attrs
        """

        fg = fg.lower()
        bg = bg.lower()

        if self.colors is None:
            curses.start_color()
            self.colors = {}
            self.numColors = 1 # 0 is reserved

        try:
            curses.use_default_colors()
            clearColor = -1
        except:
            clearColor = curses.COLOR_BLACK

        # white on black is the default color, which is pre-defined
        # and can't be overwritten
        if fg == 'white' and (bg == 'black' or bg == 'clear'):
            return 0

        colormap = {
            'white':curses.COLOR_WHITE,
            'black':curses.COLOR_BLACK,
            'blue':curses.COLOR_BLUE,
            'cyan':curses.COLOR_CYAN,
            'green':curses.COLOR_GREEN,
            'magenta':curses.COLOR_MAGENTA,
            'red':curses.COLOR_RED,
            'yellow':curses.COLOR_YELLOW,
            'clear':clearColor
            }

        # otherwise, we first check if the requested
        # color pair exists in our cache of colors, and
        # either return it, or create it and then return it
        if fg not in self.colors.keys():
            self.colors[fg] = {}

        if bg not in self.colors[fg].keys():
            curses.init_pair(self.numColors, colormap[fg], colormap[bg])
            self.colors[fg][bg] = curses.color_pair(self.numColors)
            self.numColors += 1

        return self.colors[fg][bg]

