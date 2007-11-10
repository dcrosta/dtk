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

from Label import Label

class Button(Label):
    """
    Button is a clickable widget which is displayed with
    customizable decoration. 'enter' is bound to the click
    action which fires the 'clicked' event.

    Events (in addition to standard Drawable events):
     * 'clicked' when the user "clicks" the button (hitting enter)
    """

    def __init__(self, text = None, decoration = '[%s]', **kwargs):
        super(Button, self).__init__(text, **kwargs)

        self.setDecoration(decoration)
        self.bindKey('enter', self.clicked)


    def setDecoration(self, decoration):
        """
        sets the 'button decoration'. this should
        be a format string with a single string
        format conversion.
        """
        self.decoration = decoration


    def clicked(self):
        """
        called when the button is clicked by a keybinding,
        or when you want to simulate such a click
        """
        self.fireEvent('clicked')


    def render(self):
        """
        Draw the text formatted with the decoration. If
        focused, we draw with the highlight attribute
        (usually reverse-colors)
        """
        self.draw(self.decoration % self.text, 0, 0, highlight = self.focused)
