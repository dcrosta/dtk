#!/usr/bin/env python

import dtk, dtk.util
import time
import sys, os
import logging

levels = {'debug':logging.DEBUG,
          'info' :logging.INFO,
          'warn' :logging.WARN,
          'error':logging.ERROR,
          'critical':logging.CRITICAL
          }
if 'DTKDEBUG' in os.environ:
    level = levels[os.environ['DTKDEBUG']]
else:
    level = levels['error']

e = dtk.Engine(name='dtk Test App', log = True, logfile = 'log.txt', loglevel = level)

def switchto(o):
    e.setFocus(o)

row = dtk.Rows(e, 'row')

col = dtk.Slideshow(row, 'col')
lb = dtk.ListBox(row, 'lb')

class Foo:
    def __init__(self, a):
        self.a = a
        self.__dtk_str__ = str(a)

class Bar:
    def __init__(self, a):
        self.a = a    
    def __dtk_str__(self):
        return "Foo like %s" % self.a


lb.setItems([Foo(1), Foo(2), Foo(3)])

row.addRow(col)
row.addRow(lb)

options = "t te r c hclb table l s button dialog lb".split()
optionlist = dtk.ListBox(col, 'options')
optionlist.setItems(options)

o2ptions = [Bar(a) for a in "one two three four".split()]
o2ptionlist = dtk.ListBox(col, 'o2ptions')
o2ptionlist.setItems(o2ptions)

col.addSlide(optionlist)
col.addSlide(o2ptionlist)

def printdim(_source_obj):
    print _source_obj.w, _source_obj.h

o2ptionlist.bindKey('x', printdim)
optionlist.bindKey('x', printdim)

e.setFocus(optionlist)

#col.bindKey('tab', col.nextSlide)

e.bindKey('q', e.quit)
e.bindKey('esc', e.quit)

e.mainLoop()
