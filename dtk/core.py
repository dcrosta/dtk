# DTK, a curses "GUI" toolkit for Python programs.
# 
# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# 
# DTK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# DTK is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with Foobar. If not, see <http://www.gnu.org/licenses/>.


import string
import types
import time
import logging
import logging.handlers

import _curses
import curses
import curses.ascii



class InputHandler(object):
    """
    The base class for objects which deal with keyboard input.
    """

    # remap the dtk nice name for some keys back
    # to the actual character it represents (for
    # printable input only)
    printableVersion = {
        'space':' '
        }


    def __init__(self, *args, **kwargs):
        # keybindings dict
        self.keybindings = {}


    def handleInput(self, input):
        """
        handleInput checks the list of keybindings, and for keys
        which are bound, dispatches to the bound method. if a
        binding for 'printable' exists (printable characters are
        letters, numbers, symbols, the space key, tab and enter;
        see isPrintable) the bound method for the 'printable'
        binding will be called. if there is no 'printable' binding
        or if the input fails the isPrintable test, the input's
        dtk friendly name will be looked for in the key binding
        map; if successful, the bound method for that input
        will be called. note that this means that an object which
        binds 'printable' and any printable character, the letter
        'a' for example, will only ever call the method bound
        to 'printable' when an 'a' arrives as input.

        before calling any bound method, handleInput checks the
        argument list.  if '_input_key' or '_source_obj' exist in the
        argument list and weren't explicitly set to another value at
        binding time, then the translated (see below) input character
        and bound object (ie 'self'), respectively, will be passed to
        the method using those names. if the method does not
        explicitly name '_input_key' or '_source_obj', the extra
        arguments will not be passed, even if the method accepts
        *args or **kwargs.

        (certain keys are represented in dtk with easy-to-use
        names, for example the space character is bound with
        the name 'space', not ' '. when passing a value for
        _input_key, the translated version ' ' will be used. the
        list of translated characters is in the dict
        InputHandler.printableVersion.)

        handleInput always returns True if a binding is found and
        a method is called; the return value of the called method
        is ignored.
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
        try:
            varnames = method.func_code.co_varnames
        except AttributeError:
            varnames = method.__call__.func_code.co_varnames
        if '_input_key' in varnames:
            kwargs['_input_key'] = kwargs.get('_input_key', None) or input

        # if the method is asking for a _source_obj argument,
        # bind the present object to the method before calling it
        # unless another object is already bound to the method
        # TODO this is actually broken. it will still fill the slot
        # if the user passes in a POSITIONAL argument for _source_obj,
        # resulting in an exception.
        if '_source_obj' in varnames:
            kwargs['_source_obj'] = kwargs.get('_source_obj', None) or self
            
        method(*args, **kwargs)
        return True


    def bindKey(self, key, method, *args, **kwargs):
        """
        Bind the method (or function) with the given positional
        and named arguments to the given input key. When this
        object recieves the given key as input, the most recent
        method bound to the key will be called with the given
        arguments. See the docstring for handleInput() for
        more details on bound method calling.
        """
        self.keybindings[key] = (method, args, kwargs)


    def unbindKey(self, key):
        """
        Removes the binding for the given key for this InputHandler.
        If key is 'all', then all existing keybindings (including
        bindings created by bindPrintable) will be removed.
        """

        if key == 'all':
            self.keybindings = {}

        elif key in self.keybindings:
            del self.keybindings[key]


    def bindPrintable(self, method, *args, **kwargs):
        """
        tell the input subsystem that printable characters
        should be passed to the given method as they arrive.
        see isprintable().
        """
        self.keybindings['printable'] = (method, args, kwargs)


    def unbindPrintable(self):
        """
        Unbind the previously set 'printable' keybinding.
        """
        self.unbindKey('printable')


    def isprintable(self, input):
        """
        a character is printable if curses.ascii.isprint()
        returns true or if the dtk character name (eg 'space')
        exists in InputHandler.printableVersion
        """
        if input in self.printableVersion:
            return True
        elif len(input) > 1:
            return False
        else:
            return curses.ascii.isprint(input)



class Drawable(InputHandler):
    """
    Drawable is the base class for on-screen DTK elements. It
    provides implementations and stubs for methods crucial to 
    drawing onscreen "widgets." In general, methods defined
    here should only be called by subclasses or other parts
    of the DTK core.

    This class is a fully concrete class that can be instantiated,
    though it won't do much by itself, unless you need a widget
    which will never draw anything to the screen.
    
    To extend Drawable, subclasses must at least implement the
    render() function. render() is called whenever it is time
    to redraw the widget, and should use the drawing methods
    (draw, drawDown, line, lineDown, clear and box) defined here
    rather than directly calling the versions of same in Engine.
    These methods all take positional arguments relative to the
    origin, the upper-left, of the Drawable.

    touch(), untouch() and drawContents() are used by DTK core to
    control when render() is called. Render will be called by
    drawContents only if the object has been touched by a call to
    touch(). untouch() is the inverse of touch(). Sub-classes will
    generally not need to override any of these methods.

    setSize is used by DTK core to set the size of the widget.
    after it is called, the instance attributes y, x, h, and w are
    set to the on screen origin (y, x) and the size (h, w) of the
    Drawable. These should not be changed from within sub-classes.
    Some drawables which do not wish to take up the entire space
    allotted for them by DTK core may override setSize. 

    Finally, each Drawable has a reference to the Engine and the
    context in which it exists. For more information on input
    contexts, see the documentation in InputContext and Engine.
    Drawables may check the focused attribute to determine if
    they are currently the focused Drawable in their context. Some
    Drawables use this value to change their drawing style: ListBox
    shows the active highlighted row in reverse-colors when it has
    focus, and normally when it does not, creating a cursor only
    when the ListBox has focus.

    Events:
     * 'got focus' when this Drawable gains focus
     * 'lost focus' when this Drawable loses focus
     * 'became active' when this Drawable is on an active path (see
       becameActive())
     * 'became inactive' when this Drawable is no longer on an
       active path (see becameInactive())
     * 'resized' when this Drawable is resized
    """

    def __init__(self, *args, **kwargs):

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
    focused = property(_getFocused, _setFocused,
            doc="True when this Drawable is the focused Drawable. "
                "Focus means this drawable will get input keys "
                "before any others.")

    
    def __str__(self):
        """
        A printable representation of this Drawable, either the name
        attribute, if set, or the class name.
        """
        return self.name


    def touch(self):
        """
        marks the drawable as needing a redraw. this is usually called
        by the functions of the Drawable
        """
        self.touched = True


    def untouch(self):
        """
        marks the drawable as not needing a redraw. this is usually
        called by the functions of the Drawable
        """
        self.touched = False


    def becameActive(self):
        """
        this drawable is now part of an active path of some subtree.
        note that this does not mean that it is on *the* active path
        (ie the one beginning at the context root).
        """
        self.touch()
        self.fireEvent('became active')


    def becameInactive(self):
        """
        this drawable is now part of an active path of some subtree.
        note that this does not mean that it is on *the* active path
        (ie the one beginning at the context root).
        """
        self.touch()
        self.fireEvent('became inactive')


    def setContext(self, context):
        """
        update the context reference and rebind events
        to the new context
        """
        self.log.debug('moving bindings from context %s to %s', self.context, context)

        bindings = self.context.dropBindings(self)
        self.context = context
        self.context.loadBindings(self, bindings)


    def drawContents(self):
        """
        If the Drawable needs redrawing, will delegate to the
        render() method and mark it as no longer needing redraw;
        otherwise, does nothing
        """
        if self.touched:
            self.log.debug('drawContents() calling render()')
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
        not changed. if the size changed, call touch() and
        fire the 'resized' event
        """
        sizeChanged = False

        if y < 0 or x < 0:
            raise ValueError, "y and x arguments to setSize must be non-negative"

        if y is not None and y != self.y:
            sizeChanged = True
            self.y = y

        if x is not None and x != self.x:
            sizeChanged = True
            self.x = x

        if w is not None and w != self.w:
            sizeChanged = True
            self.w = w

        if h is not None and h != self.h:
            sizeChanged = True
            self.h = h

        if sizeChanged:
            self.touch()
            self.fireEvent('resized')



    # convenience method for binding and unbinding events on
    # this instance
    def bindEvent(self, event, method, *args, **kwargs):
        """
        bind method with the given args and keyword args
        on this instance. see InputContext.bindEvent for
        more details on event binding.
        """
        self.context.bindEvent(self, event, method, *args, **kwargs)
    

    def unbindEvent(self, event, method):
        """
        unbind the given method on this instance. see
        InputContext.bindEvent for more details on event
        binding.
        """
        self.context.unbindEvent(self, event, method)


    def fireEvent(self, event):
        """
        enqueue the given event with the context with self
        as the source
        """
        self.context.enqueueEvent(self, event)


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
        Hide the cursor in terminals which support it.
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
        if not issubclass(self.__class__, Container):
            raise ContainerException("do not create an instance of Container. instantiate a subclass of Container instead.")

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

        self.log.debug('got setActiveDrawable(%s)', drawable)
        for child in self.children:
            if child is drawable:
                if child is not self.active:
                    self.log.debug('setting active to drawable == %s', drawable)
                    if self.active is not None:
                        self.active.becameInactive()
                    self.active = child
                    self.active.becameActive()
                success = True
                break

            elif isinstance(child, Container):
                self.log.debug('calling setActiveDrawable on %s', child)
                if child.setActiveDrawable(drawable):
                    if child is not drawable:
                        child.becameInactive()
                        self.active = child
                        self.active.becameActive()
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
            child.setContext(context)

        super(Container, self).setContext(context)


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


    def touch(self):
        """
        touch the active child as well as self
        """
        super(Container, self).touch()
        self.active.touch()



class EngineException(Exception):
    pass

class NoInputCharException(Exception):
    pass

class ContainerException(Exception):
    pass


class InputContext(InputHandler):
    """
    An InputContext creates an isolated set of Drawables on which
    Engine's input loop operates. Essentially, InputContext is
    a pointer to a root drawable and some methods for manipulating
    the tree of drawables rooted there. This is useful, though,
    as it provides a way for Drawables to create nested input loops
    if they have some special purpose. For example, Dialog creates
    an InputContext and processes it so that interactions with the
    dialog are not available to the "regular" DTK drawable tree (ie
    the Dialog is modal).
    """

    def __init__(self, modal = True, *args, **kwargs):
        super(InputContext, self).__init__(*args, **kwargs)

        if getattr(self, 'log', None) is None:
            self.log = logging.getLogger('dtk')

        self.root = None
        self.modal = modal
        self.done = False
        self.started = False

        # a list of tuples (source, event)
        self.eventQueue = []

        # nested dict of bindings:
        #
        # eventBindings keyed by source (incl None)
        #  + sub-dicts keyed by event
        #     + sub-dicts keyed by method
        #        + value is tuple (*args, **kwargs)
        self.eventBindings = {}


    def quit(self):
        """
        stop processing this context
        """
        self.done = True


    def getFocusedDrawable(self):
        """
        returns the drawable in this context that has focus
        """
        if isinstance(self.root, Container):
            return self.root.getActiveDrawable()
        else:
            return self.root


    def setFocus(self, drawable):
        """
        Set the focused drawable in this context to the given one
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
        set the given drawable as the root drawable of the context
        """
        self.root = drawable


    def getRoot(self):
        """
        returns the root drawable of the context, as set by setRoot()
        """
        return self.root


    def bindEvent(self, source, event, method, *args, **kwargs):
        """

        add a binding for events of the given type from the given source.
        some events without a source object may have 'None' as the
        source; for others, source will be a reference to the Drawable
        which caused the event. method may be a function or method. when
        a matching event is found in the event queue, method will be
        called with the given arguments and keyword arguments. many
        bindings may be made for a given (source, event, method). bound
        methods with an argument named '_source_obj' will receive a
        reference to the source in that argument. bound methods with an
        argument named '_event_type' will receive a copy of the event
        type (usually a string) in thar argument.
        
        the return value of bound methods (if any) is ignored when
        processing events
        """

        if source not in self.eventBindings:
            self.eventBindings[source] = {}

        if event not in self.eventBindings[source]:
            self.eventBindings[source][event] = {}

        self.eventBindings[source][event][method] = (args, kwargs)
        self.log.debug('bound event handler for (%s, %s) => %s', source, event, method)


    def unbindEvent(self, source, event, method):
        """
        remove the given method from the list of event bindings on the
        given source and event.
        """
        try:
            del self.eventBindings[source][event][method]
            self.log.debug("unbound %s on (%s, %s)", method, source, event)
        
        except KeyError:
            self.log.debug("no bindings for %s on (%s, %s)", method, source, event)


    def enqueueEvent(self, source, event):
        """
        add an event to the event queue. the event queue is processed
        periodically by the contextLoop (see Engine), at which time
        any events with matching bindings will trigger a call to
        each bound method. for user events without a source object,
        set source to 'None', which will match bindings to events
        with 'None' as source.
        """
        if self.started and not self.done:
            self.eventQueue.append((source, event))
            self.log.debug('enqueued event for (%s, %s)', source, event)


    def processEvents(self):
        """
        process all the events in the event queue, and clear the queue
        """

        if len(self.eventQueue) > 0:
            self.log.debug('processing event queue with %d items', len(self.eventQueue))

        # make a local copy
        localEventQueue = list(self.eventQueue)
        self.eventQueue = []

        if self.done: return

        for (source, event) in localEventQueue:
            # do this in a try/catch since we expect
            # it to fail in most cases
            try:
                # the dict of methods bound to this (source, event)
                bindings = self.eventBindings[source][event]

                # each method bound to the (source, event)
                for method in bindings.keys():
                    (args, kwargs) = bindings[method]

                    try:
                        varnames = method.func_code.co_varnames
                    except AttributeError:
                        varnames = method.__call__.func_code.co_varnames

                    # copy the kwargs dictionary so that we don't save any of the
                    # extra information we're about to conditionally pass along
                    # (or overwrite anything passed in from the user)
                    kwargs = dict(kwargs)

                    # if the method is asking for a _source_obj argument,
                    # bind the event source to the method before calling it
                    # unless another object is already bound to the method
                    # TODO this is actually broken. it will still fill the slot
                    # if the user passes in a POSITIONAL argument for _source_obj,
                    # resulting in an exception.
                    if '_source_obj' in varnames:
                        kwargs['_source_obj'] = kwargs.get('_source_obj', None) or source

                    # do the same for _event_type
                    if '_event_type' in varnames:
                        kwargs['_event_type'] = kwargs.get('_event_type', None) or event


                    method(*args, **kwargs)
                    self.log.debug('calling %s(*args = %s, **kwargs = %s)', method, args, kwargs)

            except KeyError:
                pass


    def dropBindings(self, source):
        """
        return the dict of bindings for the given source, and
        remove them from the eventBindings dictionary. this
        should only be called from Drawable.setContext()
        """
        bindings = self.eventBindings.get(source, {})

        try:
            del self.eventBindings[source]
        except KeyError:
            pass

        return bindings
    

    def loadBindings(self, source, bindings):
        """
        add the bindings to the bindings dictionary for the given
        source. this should only be called from Drawable.setContext().
        if any bindings exist for the (source, event, method), then
        we will overwrite them here and issue a warning to the log
        """

        if source not in self.eventBindings:
            # the simple case, where no previous bindings
            # exist for the source -- just set the reference
            self.eventBindings[source] = bindings

        else:
            # if previous bindings exist, we have to merge
            # the incoming ones with what exists. i doubt
            # this will happen, but be careful just in case
            sbindings = self.eventBindings[source]

            for event in bindings.keys():
                if event not in sbindings:
                    sbindings[event] = bindings[event]

                else:
                    ebindings = self.eventBindings[source][event]

                    new_ebindings = bindings[event]

                    for method in new_ebindings.keys():
                        if method in ebindings:
                            self.log.warn('overwriting existing binding on (%s, %s) => %s', source, event, method)

                        ebindings[method] = new_ebindings[method]
                        
                    



class Engine(InputContext):
    """
    Engine handles input processing, screen drawing and the event
    loop for the DTK core. Engine is an InputContext which means
    that it also contains a root drawable and methods for
    manipulating a tree of Drawables.

    Engine is a singleton. This means you don't need to ever
    keep a reference to it, you can simply call

      e = Engine()

    at any time, and you will get the first-created instance
    of Engine assigned to e.


    conventions:
    
    * the 'root' Drawable is the currently displayed
      drawable that takes up the entire available screen.
      it may itself contain other Drawables, which may be
      smaller.

    * the 'focused' Drawable is the first to recieve input
      after it is parsed. it is always in the tree of
      Drawables defined with the 'root' drawable as it's
      root (hence the name).
    """

    # for managing the singleton instance
    _instance = None
    _initialized = False



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
        Initialize a new Engine. Calling the mainLoop() function will start
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

            # set up a null logger to avoid the "no logger" message
            self.beginLogging(handler=logging.handlers.BufferingHandler(0))
            #self.beginLogging(file='log.txt', level=logging.DEBUG)


    def set_event_queue(self, event_queue):
        self.event_queue = event_queue

    def set_scr(self, scr):
        self.scr = scr
        self.cursesInitialized = True

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


    def setTitle(self, title):
        """
        Set the title of the window running DTK
        """
        self.title = title
        print "\033]0;%s\007" % self.title


    def getTitle(self):
        """
        Return the title as previously set by setTitle()
        """
        return self.title


    def run(self):
        """
        runs the main input loop
        """
        self.log.debug("run() called")
        if not self.cursesInitialized:
            self.log.debug("curses not initialized")
            raise Exception("run() called before scr set")
        self.log.debug("self.scr is %s", self.scr)

        (self.h, self.w) = self.scr.getmaxyx()
        self.log.debug("run() called")
        
        self.setTitle(self.title)
        self.log.debug("run() called")

        # this doesn't always work in all terms, but will never
        # fail in such a way as to break anything. by default
        # we want to hide it to keep the GUI pretty
        self.hideCursor()
        self.log.debug("run() called")

        # here we do anything we decided could only be done
        # after curses is initialized
        for foo in self.doWhenCursesInitialized:
            if type(foo) == types.TupleType:
                (method, kwargs) = foo

                method(**kwargs)
                self.log.debug("calling %s", method)
            else:
                foo()
                self.log.debug("calling %s", foo)

        # these are all 0 so that we get a "resize" on the first time
        self.lasth = self.lastw = 0
        self.resized = True

        self.log.debug("calling contextLoop(self)")
        self.contextLoop(self)

        self.shellMode()


    def contextLoop(self, context):
        """
        contextLoop runs an input loop on a given InputContext. It
        redraws the context's Drawable tree, beginning at the root,
        then waits for keyboard input from the user, parses it into
        a DTK friendly string (eg "page up" and "enter") and passes
        it off to the context's root Drawable for input processing.
        """


        # context.processEvents()
        self.log.debug("Began contextloop")
        context.started = True


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

                # try to erase everything (necessary in some terms)
                self.scr.move(0,0)
                self.scr.clrtobot()
                self.scr.refresh()

                context.root.setSize(0, 0, h, w)

                self.resized = False
                self.lasth = h
                self.lastw = w
                self.log.debug("resized to %dx%d", h, w)


            # wait to update the screen state
            self.scr.noutrefresh()


            context.root.drawContents()
            self.log.debug("finished drawContents()")
            #context.processEvents()


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
            self.log.debug("flushed curses")

            # wait for an event from the queue
            self.log.debug('Waiting on event_queue...')
            event = self.event_queue.get()
            self.log.debug('Got event: %s', event)

            try:
                input = event.keyname
                
                # after this, input will be a convenient string
                # such as 'a' or 'space', or None, which means
                # we're waiting on further multi-byte input

                if input is not None:
                    self.log.debug('Engine: calling handleInput on %s', context.root)
                    if not context.root.handleInput(input):
                        self.log.debug('Engine: calling handleInput on %s', context)
                        if not context.handleInput(input) and not context.modal:
                            self.log.debug('Engine: calling handleInput on self')
                            self.handleInput(input)
                        
            except:
                # event_queue was clear()ed, so lets stop
                self.quit()
                break

            # input handling may have caused events, so we process them here
            #context.processEvents()

        # clean up when we're done
        self.clear(self)


    
    def touchAll(self):
        """
        causes all drawables to be re-drawn on the next refresh
        TODO: move to InputContext?
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


