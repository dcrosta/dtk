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

e = dtk.Engine(name='dtk Test App')
e.beginLogging(file = 'log.txt', level = level)

col = dtk.Slideshow()
lb = dtk.ListBox()

lll = []
for i in "eins zwei drei vier fuenf".split():
    lll.append(i)

text = dtk.TextEditor()
text.setText("This is the text")

lb.setItems(lll)

col.addSlide(lb)
col.addSlide(text)

e.setRoot(col)
#e.setFocus(col)

e.bindKey('q', e.quit)

e.mainLoop()
 
