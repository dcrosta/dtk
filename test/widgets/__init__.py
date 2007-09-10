import os, os.path

# get a list of all the modules in this directory -- that is,
# every file that ends in .py except __init__.py
mod_path = os.path.dirname(__file__)
modules = []
for name in os.listdir(mod_path):
    (base, ext) = os.path.splitext(name)
    if ext == '.py' and (not base == '__init__'):
        modules.append(base)


# import into 'dtk' namespace only those things
# with the same name as the file they appear in,
# and then only if it begins with a capital letter
for module in modules:
    try:
        exec 'from %s import *' % module
    except SyntaxError:
        pass
