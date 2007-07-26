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
