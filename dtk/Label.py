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

__all__ = ['Label']

from core import Drawable

class Label(Drawable):
    """
    Label is a static text area that can be changed, but which provies no
    particular means for input. It's an un-editable bit of text, that's
    all.

    For now, Label only handles a single line of text -- this might need
    to change at some later point.
    """

    def __init__(self, text = '', **kwargs):
        super(Label, self).__init__(**kwargs)

        self.setText(text)


    def getText(self):
        """
        gets the Label's text
        """
        return self.text


    def setText(self, text):
        """
        sets the Label's text
        """
        self.text = text
        self.clear()
        self.touch()


    def render(self):
        """
        simply draw the text we have starting at the first position, and
        going on for as long as we can (Engine clips the text)
        """
        self.draw(self.text, 0, 0)
