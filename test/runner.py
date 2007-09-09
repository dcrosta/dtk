import unittest
import sys
import os
import os.path

# add the path of this file to the python path, so that
# "import curses" picks up the test curses module
sys.path.insert( 0, os.path.abspath( os.path.dirname( __file__ ) ) )

# add the path to the locally checked out dtk module (one
# directory up) so that import dtk works and uses the local
# source, not any insalled site-package of the same name
sys.path.insert( 1, os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )


import curses
import dtk

# this defines the test base class and a simple test case
# for sanity checking
from dtktest import *

# get any test cases defined in bugs/
from bugs import *

if __name__ == '__main__':
    unittest.main()
