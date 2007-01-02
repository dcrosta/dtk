from core import Container, ContainerException
import curses
import util

class Slideshow(Container):
    """
    implements a simple layout scheme for Drawables which
    holds an arbitrary number of Drawables and only displays
    one at a time.
    """

    def __init__(self, *args, **kwargs):
        super(Slideshow, self).__init__(*args, **kwargs)
        self.bindKey('tab', self.nextSlide)
    
    def focus(self):
        """
        called when this Slideshow gains focus. note that this
        does not actually set focus.
        """
        return self.active.focus()

    def unfocus(self):
        """
        called when this Slideshow loses focus. note that this
        does not actually set focus.
        """
        self.active.unfocus()

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
            self.active = drawable

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
        
    def __refresh(self):
        self._setChildSizes()
        self.engine.setFocus(self.active)
        self.clear()

    def nextSlide(self):
        index = self.children.index(self.active) + 1
        if( index >= len(self.children) ):
            index = 0
        self.active = self.children[index]
        self.__refresh()

    def showSlide(self, slide):
        if slide not in self.children:
            return False
        self.active = slide
        self.__refresh()

    def drawContents(self):
        self.active.drawContents()

    
