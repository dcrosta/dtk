from Drawable import Drawable
import curses
import util

#todo figure out why it doesn't clear the display

class Slideshow(Drawable):
    """
    implements a simple layout scheme for Drawables which
    holds an arbitrary number of Drawables and only displays
    one at a time.
    """

    def __init__(self, **kwargs):
        super(Slideshow, self).__init__(**kwargs)
        
        # the slides
        self.slides = []
        
        # the slide we're currently targeted on
        self.currentSlide = 0

        # todo this key is not good.
        self.bindKey('s', self.nextSlide)


    def handleInput(self, input):
        """
        give input to the current slide
        """
        consumed = self.slides[self.currentSlide].handleInput(input)
        if not consumed:
            consumed = super(Slideshow, self).handleInput(input)

        return consumed
    

    def focus(self):
        self.slides[self.currentSlide].focus()


    def unfocus(self):
        self.slides[self.currentSlide].unfocus()


    def __str__(self):
        return 'Slideshow'


    def addSlide(self, drawable):
        """
        add a Drawable to the end of the list of slides. the
        newly-added Drawable will be hidden by default.
        """                
        self.slides.append(drawable)
        drawable.setSize(0, 0, 0, 0)


    def _setChildSizes(self):
        """
        hide all child Drawables except the currently-viewed one.
        """
        y = self.y
        x = self.x
        h = self.h
        w = self.w

        for i in range(len(self.slides)):
            if i == self.currentSlide:
                self.slides[i].setSize(y, x, h, w)
            else:
                self.slides[i].setSize(0, 0, 0, 0)


    def setSize(self, y, x, h, w):
        super(Slideshow, self).setSize(y, x, h, w)

        if y == 0 and x == 0 and h == 0 and w == 0:
            return

        self.log.debug('setSize(%d, %d, %d, %d)' % (y, x, h, w))
        self._setChildSizes()
        # use the values from parent's setSize()
        
    def _refresh(self):
        self._setChildSizes()
        self.getEngine().setFocus(self.slides[self.currentSlide])
        self.clear()

    def nextSlide(self):
        self.currentSlide += 1
        if( self.currentSlide >= len(self.slides) ):
            self.currentSlide = 0
        self._refresh()

    def showSlide(self, slide):
        try:
            self.currentSlide = self.slides.index(slide)
            self._refresh()
        except IndexError:
            return

    def drawContents(self):
        self.slides[self.currentSlide].drawContents()

    
