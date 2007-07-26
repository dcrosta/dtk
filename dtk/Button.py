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
