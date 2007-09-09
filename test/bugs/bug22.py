"""
Demonstrates TextEditor bug when text is taller than screen.
Make sure to run this in a terminal window shorter than the
length of the text, or, alternatively, press enter repeatedly
to keep adding lines to the text until the error occurs.
"""

import dtk
import logging
import sys

# set up an import path to ../ so we can get the
# DtkTestCase class
#sys.path.insert( 1, os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

from dtktest import DtkTestCase

class BugTwentyTwo(DtkTestCase):

    def testLongTextEditor(self):
        """
        TextEdtior raises an exception if you scroll down too far.
        This test is considered to pass if it raises no exception
        """

        args = ['down'] * 25
        args.append('esc')
        self.scr.set_input(*args)
        
        e = dtk.Engine()
        l = dtk.TextEditor()
        l.setText([
                'Lorem ipsum dolor sit amet,',
                'consectetuer adipiscing elit.',
                'Nullam ac elit. Nullam consectetuer ultrices elit. Morbi a sem.',
                'Sed urna.',
                'Nam magna erat', 'pellentesque quis', 'ultricies id',
                'hendrerit molestie, nibh.',
                'Cras placerat pellentesque erat.',
                'Vestibulum fringilla,',
                'ligula eget tristique convallis',
                'enim',
                'Lorem ipsum dolor sit amet,',
                'consectetuer adipiscing elit.',
                'Nullam ac elit. Nullam consectetuer ultrices elit. Morbi a sem.',
                'Sed urna.',
                'Nam magna erat', 'pellentesque quis', 'ultricies id',
                'hendrerit molestie, nibh.',
                'Cras placerat pellentesque erat.',
                'Vestibulum fringilla,',
                'ligula eget tristique convallis',
                'enim',
                'risus dignissim lacus, at pharetra velit purus vitae lectus.',
                'Vivamus aliquet',
                'vehicula nunc. Nulla commodo ligula eu felis.',
                'Duis eu sapien quis',
                'leo posuere rutrum. Suspendisse porttitor',
                'pulvinar elit.',
                'In scelerisque elit a elit. Praesent accumsan.',
                'Fusce sed lacus',
                'in lectus varius aliquam. Proin lobortis.',
                'Vestibulum ante ipsum primis in faucibus orci luctus et',
                'ultrices posuere cubilia Curae; Suspendisse aliquam ultrices pede.',
                'Suspendisse bibendum dolor vel diam. Morbi vel arcu vitae',
                'magna fermentum interdum. Donec ornare sollicitudin enim.'
                ])

        e.bindKey('esc', e.quit)
        e.setRoot(l)
        e.mainLoop()

