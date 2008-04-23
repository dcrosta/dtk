#!/usr/bin/env python

from setuptools import setup

version = '0.3'

readme = open('README.txt').read() + '\n\n' + open('ChangeLog').read()

setup(name='dtk',
      version=version,
      description="A curses 'GUI' toolkit for Python programs",
      long_description=readme,
      author="Dan Crosta, Ethan Jucovy",
      author_email="dtk-dev@sccs.swarthmore.edu",
      url="http://trac.sccs.swarthmore.edu/dtk",
      license="LGPLv3",
      copyright="(C) 2006-2007 Dan Crosta, Ethan Jucovy",
      docformat="epytext en",
      packages=['dtk'])
