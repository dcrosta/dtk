#!/usr/bin/env python

from setuptools import setup

version = '0.3'

f = open('README.txt')
readme = "".join(f.readlines())
f.close()

setup(name='dtk',
      version=version,
      description="A curses 'GUI' toolkit for Python programs",
      long_description=readme,
      author="Dan Crosta, Ethan Jucovy",
      author_email="dtk-dev@lists.openplans.org",
      url="https://trac.sccs.swarthmore.edu/dtk",
      license="LGPLv3",
      copyright="(C) 2006-2007 Dan Crosta, Ethan Jucovy",
      docformat="epytext en",
      test_suite="test.runner",
      packages=['dtk'])
