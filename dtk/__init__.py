"""
DTK, a curses "GUI" toolkit for Python programs.

Copyright (C) 2006-2007 Dan Crosta
Copyright (C) 2006-2007 Ethan Jucovy

@author: Dan Crosta <dcrosta@sccs.swarthmore.edu>
@author: Ethan Jucovy <ejucovy@openplans.org>

DTK is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

DTK is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public
License along with DTK. If not, see <http://www.gnu.org/licenses/>.
"""

import os, os.path

# get a list of all the modules in this directory -- that is,
# every file that ends in .py except __init__.py
mod_path = os.path.dirname(os.path.join(os.getcwd(), __file__))
modules = []
for name in os.listdir(mod_path):
    (base, ext) = os.path.splitext(name)
    if ext == '.py' and (not base == '__init__'):
        modules.append(base)


# first get the core classes
from core import *

# import into 'dtk' namespace only those things
# with the same name as the file they appear in,
# and then only if it begins with a capital letter
for module in modules:
    if module[0] == module[0].upper():
        try:
            exec 'from %s import %s' % (module, module)
        except SyntaxError:
            pass

from input import mainloop
