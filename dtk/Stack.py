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


from core import Drawable, Container, ContainerException

class Stack(Container):
    """
    Basic stack of drawables.
    """

    def __init__(self, **kwargs):
        super(Stack, self).__init__(**kwargs)


    def __len__(self):
        """
        return the number of items currently on the stack
        """
        return len(self.children)


    def push(self, drawable):
        """
        push a new element onto the stack. If the previous
        top Drawable was focused, then the new drawable will
        be set active automatically. if `drawable` already exists
        in the Stack, it will be removed first, then placed on
        top.
        """        
        # make sure there's only one copy of it
        # on the stack at any time
        if drawable in self.children:
            self.children.remove(drawable)

        self.children.append(drawable)

        drawable.setSize(self.y, self.x, self.h, self.w)
        self.setActiveDrawable(drawable)

        self.touch()


    def pop(self):
        """
        pop and return the top element off the stack. if the
        previous top stack Drawable was focused, the element
        underneath (if any) will be focused automatically. if
        the stack is empty after popping this element and that
        element had focus, then the stack itself is given
        focus
        """
        drawable = None

        if len(self.children):
            drawable = self.children.pop()

            if self.active is drawable:
                if len(self.children):
                    self.setActiveDrawable(self.children[-1])
                else:
                    self.log.debug('forcing focus on self')
                    self.engine.setFocus(self)

        if len(self.children):
            self.children[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()

        return drawable


    def setSize(self, y, x, h, w):
        super(Stack, self).setSize(y, x, h, w)

        if len(self.children):
            self.children[-1].setSize(self.y, self.x, self.h, self.w)

        self.touch()


    def drawContents(self):
        if len(self.children):
            self.children[-1].drawContents()
