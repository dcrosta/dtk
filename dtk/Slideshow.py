# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# All rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share to copy, distribute, display, and perform the work
#   * to Remix to make derivative works
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


from core import Container, ContainerException
import curses
import util

class Slideshow(Container):
    """
    implements a simple layout scheme for Drawables which
    holds an arbitrary number of Drawables and only displays
    one at a time.

    Events:
     * 'active child changed' when a new slide is shown
    """

    def __init__(self, *args, **kwargs):
        super(Slideshow, self).__init__(*args, **kwargs)
        self.bindKey('tab', self.nextSlide)
    
    def addSlide(self, drawable):
        """
        add a Drawable to the end of the list of slides. the
        newly-added Drawable will be hidden by default unless
        it is the only slide in the slideshow.
        """                
        self.children.append(drawable)
        if self.active:
            drawable.setSize(0, 0, 0, 0)
        else:
            self.setActiveDrawable(drawable)

    def _setChildSizes(self):
        """
        hide all child Drawables except the currently-viewed one.
        """
        y, x, h, w = self.y, self.x, self.h, self.w

        for child in self.children:
            if child == self.active:
                child.setSize(y, x, h, w)
            else:
                child.setSize(0, 0, 0, 0)

    def setSize(self, y, x, h, w):
        super(Slideshow, self).setSize(y, x, h, w)

        self.log.debug('setSize(%d, %d, %d, %d)' % (y, x, h, w))
        self._setChildSizes()
        
    def nextSlide(self):
        index = self.children.index(self.active) + 1
        if( index >= len(self.children) ):
            index = 0
        self.setActiveDrawable(self.children[index])
        self._setChildSizes()

    def previousSlide(self):
        index = self.children.index(self.active) - 1
        if( index < 0 ):
            index = len(self.children) - 1
        self.setActiveDrawable(self.children[index])
        self._setChildSizes()

    def showSlide(self, slide):
        if slide not in self.children:
            return False
        self.setActiveDrawable(slide)
        self._setChildSizes()

    def drawContents(self):
        self.active.drawContents()
