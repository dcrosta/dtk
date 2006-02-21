from Drawable import Drawable
import utils

import types
import re



class TextEditor(Drawable):
    """
    A simple multi-line text edtor/viewer that does smart things.
    """

    def __init__(self, parent, name):
        Drawable.__init__(self, parent, name)

        # the buffer of lines
        self.buffer = []
        self.cursor = (0, 0)


    def setText(self, text):
        """
        accepts a list of strings (each string is a paragraph in the
        editor) or a single string, which is split by newline
        characters ('\n').
        """
        if type(text) in types.StringTypes:
            self.buffer = text.split('\n')
        

    def render(self):

        wrapped = []
        for line in self.buffer:
            wrapped.extend(utils.wrap(line, self.w))

        y = 0
        for line in wrapped:
            self.draw(line, y, 0)
            y += 1


