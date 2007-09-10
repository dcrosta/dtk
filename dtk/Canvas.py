# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# Some rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share -- to copy, distribute, display, and perform the work
#   * to Remix -- to make derivative works
# 
# Under the following conditions:
# 
#   * Attribution. You must attribute the work in the manner specified by the
#     author or licensor (but not in any way that suggests that they endorse you
#     or your use of the work).
#   * Share Alike. If you alter, transform, or build upon this work, you may
#     distribute the resulting work only under the same, similar or a compatible
#     license.
# 
#   * For any reuse or distribution, you must make clear to others the license
#     terms of this work.
#   * Any of the above conditions can be waived if you get permission from the
#     copyright holder.
#   * Apart from the remix rights granted under this license, nothing in this
#     license impairs or restricts the author's moral rights.
# 
# 
# Full text of the license can be found online:
# 
#   <http://creativecommons.org/licenses/by-sa/3.0/us/>

from core import Drawable

class Canvas(Drawable):
    """
    Canvas is a free-form drawing area. It exposes the drawing methods DTK
    uses internally. Drawing commands are queued for exactly one iteration
    of render(), which means that if this Widget is resized all content on
    it will be lost. Therefore it is the responsibility of the  client to
    listen for the 'resized' event, and redraw the contents as appropriate.
    """

    def __init__(self, **kwargs):
        super(Canvas, self).__init__(**kwargs)

        self.draw_queue = []


    # make local private references to the
    # actual drawing methods on Drawable
    __draw = Drawable.draw
    __drawDown = Drawable.drawDown
    __box = Drawable.box
    __line = Drawable.line
    __lineDown = Drawable.lineDown
    __clear = Drawable.clear

    def draw(self, str, row, col, **kwargs):
        """
        Draw the string starting at (row, col) relative to the
        upper left of this Drawable. Drawing will be bounded
        to stay within this Drawable's size.
        """
        self.log.debug("queing draw('%s', %d, %d, %s)" % (str, row, col, kwargs))
        self.draw_queue.append( lambda: self.__draw( str, row, col, **kwargs ) )
        self.touch()

    
    def drawDown(self, str, row, col, **kwargs):
        """
        Draw the string starting at (row, col) relative to the
        upper left of this Drawable and going down. Drawing 
        will be bounded to stay within the Drawable's size.
        """
        self.log.debug("queing drawDown('%s', %d, %d, %s)" % (str, row, col, kwargs))
        self.draw_queue.append( lambda: self.__drawDown( str, row, col, **kwargs ) )
        self.touch()


    def box(self, row, col, w, h, **kwargs):
        """
        Draw a box of border characters, beginning at (row, col)
        relative to the upper left of this Drawable, extending
        for w characters wide (inclusive of both borders) and
        h characters high (inclusive of both borders).
        """
        self.log.debug("queing box(%d, %d, %d, %d, %s)" % (row, col, w, h, kwargs))
        self.draw_queue.append( lambda: self.__box( row, col, w, h, **kwargs ) )
        self.touch()


    def line(self, row, col, len, **kwargs):
        """
        Draw a line starting at (row, col) relative to this
        Drawable's upper-left and going right for len characters.
        Ending characters may be specified with the leftEnd and
        rightEnd attributes.
        """
        self.log.debug("queing line(%d, %d, %d, %s)" % (row, col, len, kwargs))
        self.draw_queue.append( lambda: self.__line( row, col, len, **kwargs ) )
        self.touch()


    def lineDown(self, row, col, len, **kwargs):
        """
        Draw a line starting at (row, col) relative to the upper
        left of this Drawable and going down for len characters.
        Ending characters may be specified with the topEnd and
        bottomEnd attributes.
        """
        self.log.debug("queing lineDown(%d, %d, %d, %s)" % (row, col, len, kwargs))
        self.draw_queue.append( lambda: self.__lineDown( row, col, len, **kwargs ) )
        self.touch()


    def clear(self):
        """
        clears the whole drawable
        """
        self.log.debug("queing clear()")
        self.draw_queue.append( lambda: self.__clear() )
        self.touch()


    def render(self):
        """
        process the draw queue. all elements in the queue are just
        curried callables, so just call them with no arguments
        """

        for command in self.draw_queue:
            command()
