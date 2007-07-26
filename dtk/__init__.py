"""
dtk
Copyright (C) 2006-2007 Dan Crosta
Copyright (C) 2006-2007 Ethan Jucovy

@author: Dan Crosta <dcrosta@sccs.swarthmore.edu>
@author: Ethan Jucovy <ejucovy@openplans.org>
"""
__docformat__ = 'epytext en'

__version__ = '0.2'
__url__ = 'https://firefly.student.swarthmore.edu/trac/wiki/Dtk'
__copyright__ = '(C) 2006-2007 Dan Crosta, Ethan Jucovy'
__license__ = 'CC By-Sa 3.0 US'
__license_long__ = """
Copyright (C) 2006-2007 Dan Crosta
Copyright (C) 2006-2007 Ethan Jucovy
Some rights reserved.

DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
license. Under this license you are free:

  * to Share -- to copy, distribute, display, and perform the work
  * to Remix -- to make derivative works

Under the following conditions:

  * Attribution. You must attribute the work in the manner specified by the
    author or licensor (but not in any way that suggests that they endorse you
    or your use of the work).
  * Share Alike. If you alter, transform, or build upon this work, you may
    distribute the resulting work only under the same, similar or a compatible
    license.

  * For any reuse or distribution, you must make clear to others the license
    terms of this work.
  * Any of the above conditions can be waived if you get permission from the
    copyright holder.
  * Apart from the remix rights granted under this license, nothing in this
    license impairs or restricts the author's moral rights.


Full text of the license can be found online:

  <http://creativecommons.org/licenses/by-sa/3.0/us/>
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
