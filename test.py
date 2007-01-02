#!/usr/bin/env python

import dtk, dtk.util
import time
import sys, os
import logging

items1 = None
indices1 = None

def add_item():
    items1.append('Your mom.')
    indices1.append(-1)
    
    lb1.append('Your mom.')

if len(sys.argv) > 1 and sys.argv[1] == 'wrap':
    text = """This helps staff gauge the importance of this issue to you, the user. "High" severity means you can't get important work done, or can't log in; "medium" means you've found a problem with an SCCS service or want to request a new piece of software be installed; "low" covers annoyances or minor hangups that you would like to see resolved but can work around easily enough. You may also leave this field blank.

Hey y'all, welcome to the SCCS Staff Wiki. Here we're going to gather together little bits and pieces of documentation over time so we don't have to bother each other with "how do i..." or "wtf is..." questions on staffmail. If you're unfamiliar with Wikis, read on below, otherwise let's get to work. If you add something new and cool, put a link to it (or to some category organization page or something like that) here on the front page. Also remember to attribute anything useful you say with your name (see below). And make a user page so we don't have lots of dead links flying about. If you can't find anything here, check the StaffDiary."""
    
    wrapped = dtk.util.wrap(text, 78)
    import pprint
    pprint.PrettyPrinter().pprint(wrapped)

    sys.exit()

levels = {'debug':logging.DEBUG,
          'info' :logging.INFO,
          'warn' :logging.WARN,
          'error':logging.ERROR,
          'critical':logging.CRITICAL
          }
if 'DTKDEBUG' in os.environ:
    level = levels[os.environ['DTKDEBUG']]
else:
    level = levels['debug']

e = dtk.Engine()
e.beginLogging(file = 'log.txt', level = level)

if len(sys.argv) > 1 and sys.argv[1] == 't':
    tf = dtk.TextField()
    e.setRoot(tf)

elif len(sys.argv) > 1 and sys.argv[1] == 'te':
    te = dtk.TextEditor()
    e.setRoot(te)

elif len(sys.argv) > 1 and sys.argv[1] == 'r':
    c = dtk.Rows()
    c.bindKey('a', add_item)
    e.setRoot(c)

    items1 = ['First item', 'Second item', 'Third Item']
    indices1 = [1, 2, 3]
    lb1 = dtk.ListBox()
    lb1.setItems(items1, indices1)

    lb2 = dtk.ListBox()
    lb2.setItems(['Fourth item', 'Fifth item', 'Sixth Item'], [4,5,6])

    lb3 = dtk.ListBox()
    lb3.setItems(['Dog', 'Cat', 'Squirrel'], [7,8,9])

    c.addRow(lb1, fixedsize=5)
    c.addSeparator(type='line')
    c.addRow(lb2, fixedsize=10)
    c.addSeparator(type='blank')
    c.addRow(lb3, weight = 2)

    e.setFocus(lb1)

elif len(sys.argv) > 1 and sys.argv[1] == 'c':
    c = dtk.Columns()
    c.bindKey('a', add_item)
    e.setRoot(c)

    lb1 = dtk.ListBox()
    lb1.setItems(['First item', 'Second item', 'Third Item', id(lb1)])

    lb2 = dtk.ListBox()
    lb2.setItems(['Fourth item', 'Fifth item', 'Sixth Item', id(lb2)])

    lb3 = dtk.ListBox()
    lb3.setItems(['Dog', 'Cat', 'Squirrel', id(lb3)])

    c.addColumn(lb1, fixedsize = 15)
    c.addSeparator(type='line')
    c.addColumn(lb2, weight = 1)
    c.addSeparator(type='blank')
    c.addColumn(lb3, weight = 2)


elif len(sys.argv) > 1 and sys.argv[1] == 'table':
    items = [
        ['Radiohead', 'Kid A',  1, 'Everything In Its Right Place'],
        ['Radiohead', 'Kid A',  2, 'Kid A'],
        ['Radiohead', 'Kid A',  3, 'The National Anthem'],
        ['Radiohead', 'Kid A',  4, 'How To Disappear Completely'],
        ['Radiohead', 'Kid A',  5, 'Treefingers'],
        ['Radiohead', 'Kid A',  6, 'Optimistic'],
        ['Radiohead', 'Kid A',  7, 'In Limbo'],
        ['Radiohead', 'Kid A',  8, 'Idioteque'],
        ['Radiohead', 'Kid A',  9, 'Morning Bell'],
        ['Radiohead', 'Kid A', 10, 'Motion Picture Sountrack'],
        ['Radiohead', 'OK Computer',  1, 'Airbag'],
        ['Radiohead', 'OK Computer',  2, 'Paranoid Android'],
        ['Radiohead', 'OK Computer',  3, 'Subterranean Homesick Alien'],
        ['Radiohead', 'OK Computer',  4, 'Exit Music (For a Film)'],
        ['Radiohead', 'OK Computer',  5, 'Let Down'],
        ['Radiohead', 'OK Computer',  6, 'Karma Police'],
        ['Radiohead', 'OK Computer',  7, 'Fitter Happier'],
        ['Radiohead', 'OK Computer',  8, 'Electioneering'],
        ['Radiohead', 'OK Computer',  9, 'Climbing Up the Walls'],
        ['Radiohead', 'OK Computer', 10, 'No Surprises'],
        ['Radiohead', 'OK Computer', 11, 'Lucky'],
        ['Radiohead', 'OK Computer', 12, 'The Tourist'],
        ['Schneider TM', 'Zoomer', 1, 'Reality Check'],
        ['Schneider TM', 'Zoomer', 2, 'Frogtoise'],
        ['Schneider TM', 'Zoomer', 3, 'Abyss'],
        ['Schneider TM', 'Zoomer', 4, 'DJ Guy?'],
        ['Schneider TM', 'Zoomer', 5, 'Turn On'],
        ['Schneider TM', 'Zoomer', 6, 'Hunger'],
        ['Schneider TM', 'Zoomer', 7, '999'],
        ['Schneider TM', 'Zoomer', 8, 'Cuba TM'],
        ['The Dandy Warhols', 'Thirteen Tales of Urban Bohemia', 1, 'Godless'],
        ['The Dandy Warhols', 'Thirteen Tales of Urban Bohemia', 2, 'Mohammed'],
        ['The Dandy Warhols', 'Thirteen Tales of Urban Bohemia', 3, 'Nietzsche'],
        ]

    table = dtk.TextTable(vimlike = True)
    e.setRoot(table)

    table.addColumn(weight = 1, name = 'Artist')
    table.addColumn(weight = 1, name = 'Album')
    table.addColumn(fixedsize = 2, alignment = 'right')
    table.addColumn(weight = 2, name = 'Song')


    table.setItems(items, [i for i in range(len(items))])

elif len(sys.argv) > 1 and sys.argv[1] == 'l':
    l = dtk.Label('My Label Text')
    e.setRoot(l)

elif len(sys.argv) > 1 and sys.argv[1] == 's':
    s = dtk.Stack()
    e.setRoot(s)

    lbl = dtk.Label('Label 0')
    s.push(lbl)


    def stackPush(stack):
        e.log.debug('creating "Label %d"', len(stack))
        lbl = dtk.Label('Label %d' % len(stack))
        stack.push(lbl)
        e.setFocus(stack)

    s.bindKey('page up', stackPush, s)
    s.bindKey('page down', s.pop)

elif len(sys.argv) > 1 and sys.argv[1] == 'button':
    r = dtk.Rows(outerborder = False, innerborder = False)

    def toggle(item):
        text = item.getText()
        split = text.split()

        dict = {'1': 'One',
                'One': '1',
                '2': 'Two',
                'Two': '2',
                '3': 'Three',
                'Three': '3'}

        item.setText('%s %s' % (split[0], dict[split[1]]))

    b1 = dtk.Button('Button 1')
    b2 = dtk.Button('Button 2')
    b3 = dtk.Button('Button 3')

    b1.bindKey('click', toggle, b1)
    b2.bindKey('click', toggle, b2)
    b3.bindKey('click', toggle, b3)

    r.addRow(b1)
    r.addRow(b2)
    r.addRow(b3)

    e.setRoot(r)
    e.setFocus(b1)

elif len(sys.argv) > 1 and sys.argv[1] == 'dialog':
    fp = file('dtk/ListBox.py', 'r')
    text = ''.join(fp.readlines())
    fp.close()

    p = dtk.Pager()
    p.setText(text)
    e.setRoot(p)

    d = dtk.Dialog()
    d.setType('yesno')
    d.setTitle('Dialog Box')
    d.setText('If a module is syntactically correct but its initialization fails then Andrew gets very unhappy and wants to walk to Pearson. Mustafa is busy color-calibrating the monitor in the corner; Dan wishes he had coffee. If a module is syntactically correct but its initialization fails then Andrew gets very unhappy and wants to walk to Pearson. Mustafa is busy color-calibrating the monitor in the corner; Dan wishes he had coffee?')

    def showDialog():
        d.show()

    p.bindKey('enter', showDialog)

else:
    lb = dtk.ListBox(vimlike = True)
    e.setRoot(lb)
    lb.setItems(
        ['Radiohead Kid A  1 Everything In Its Right Place',
        'Radiohead Kid A  2 Kid A',
        'Radiohead Kid A  3 The National Anthem',
        'Radiohead Kid A  4 How To Disappear Completely',
        'Radiohead Kid A  5 Treefingers',
        'Radiohead Kid A  6 Optimistic',
        'Radiohead Kid A  7 In Limbo',
        'Radiohead Kid A  8 Idioteque',
        'Radiohead Kid A  9 Morning Bell',
        'Radiohead Kid A 10 Motion Picture Sountrack',
        'Radiohead OK Computer  1 Airbag',
        'Radiohead OK Computer  2 Paranoid Android',
        'Radiohead OK Computer  3 Subterranean Homesick Alien',
        'Radiohead OK Computer  4 Exit Music (For a Film)',
        'Radiohead OK Computer  5 Let Down',
        'Radiohead OK Computer  6 Karma Police',
        'Radiohead OK Computer  7 Fitter Happier',
        'Radiohead OK Computer  8 Electioneering',
        'Radiohead OK Computer  9 Climbing Up the Walls',
        'Radiohead OK Computer 10 No Surprises',
        'Radiohead OK Computer 11 Lucky',
        'Radiohead OK Computer 12 The Tourist',
        'Schneider TM Zoomer 1 Reality Check',
        'Schneider TM Zoomer 2 Frogtoise',
        'Schneider TM Zoomer 3 Abyss',
        'Schneider TM Zoomer 4 DJ Guy?',
        'Schneider TM Zoomer 5 Turn On',
        'Schneider TM Zoomer 6 Hunger',
        'Schneider TM Zoomer 7 999',
        'Schneider TM Zoomer 8 Cuba TM'])
    lb.setDrawStyle(
            hstyle = {'highlight':True},
            sstyle = {'bold':True},
            ustyle = {},
            scheck = '> ',
            ucheck = '')


e.bindKey('q', e.quit)
e.bindKey('esc', e.quit)
e.mainLoop()
