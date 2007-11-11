#!/usr/bin/env python

from setuptools import setup
import dtk

version = '0.3'

setup(name='dtk',
      version=version,
      description="A curses 'GUI' toolkit for Python programs",
      author="Dan Crosta, Ethan Jucovy",
      author_email="dtk-dev@lists.openplans.org",
      url="https://trac.sccs.swarthmore.edu/dtk",
      license="LGPLv3",
      packages=['dtk'])
