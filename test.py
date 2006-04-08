#!/usr/bin/env python

import dtk
import time
import sys

items1 = None
indices1 = None

def add_item():
    items1.append('Your mom.')
    indices1.append(-1)
    
    lb1.append('Your mom.')

e = dtk.Engine(name='dtk Test App', log=file('log.txt','a'))

if len(sys.argv) > 1 and sys.argv[1] == 't':
    tf = dtk.TextField(e, 'textfield')

elif len(sys.argv) > 1 and sys.argv[1] == 'te':
    te = dtk.TextEditor(e, 'texteditor')

    e.setFocus(te)

elif len(sys.argv) > 1 and sys.argv[1] == 'r':
    c = dtk.Rows(e, 'rows')
    c.bindKey('a', add_item)

    items1 = ['First item', 'Second item', 'Third Item']
    indices1 = [1, 2, 3]
    lb1 = dtk.ListBox(c, 'listbox1')
    lb1.setItems(items1, indices1)

    lb2 = dtk.ListBox(c, 'listbox2')
    lb2.setItems(['Fourth item', 'Fifth item', 'Sixth Item'], [4,5,6])

    lb3 = dtk.ListBox(c, 'listbox3')
    lb3.setItems(['Dog', 'Cat', 'Squirrel'], [7,8,9])

    c.addRow(lb1, 5, weight = 1)
    c.addRow(lb2, 10, weight = 2)
    c.addRow(lb3, 5, weight = 2)

    e.setFocus(lb1)

elif len(sys.argv) > 1 and sys.argv[1] == 'c':
    c = dtk.Columns(e, 'columns')
    c.bindKey('a', add_item)

    items1 = ['First item', 'Second item', 'Third Item']
    indices1 = [1, 2, 3]
    lb1 = dtk.ListBox(c, 'listbox1')
    lb1.setItems(items1, indices1)

    lb2 = dtk.ListBox(c, 'listbox2')
    lb2.setItems(['Fourth item', 'Fifth item', 'Sixth Item'], [4,5,6])

    lb3 = dtk.ListBox(c, 'listbox3')
    lb3.setItems(['Dog', 'Cat', 'Squirrel'], [7,8,9])

    c.addColumn(lb1, 10, weight = 1)
    c.addColumn(lb2, 20, weight = 2)
    c.addColumn(lb3, 10, weight = 2)

    e.setFocus(lb1)

elif len(sys.argv) > 1 and sys.argv[1] == 'hclb':
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
        ['Schneider TM', 'Zoomer', 8, 'Cuba TM']
        ]

    clb = dtk.HierarchyColumnListBox(e, 'columnlistbox', vimlike = True)

    clb.addColumn(5, weight = 1, primary = True, name = 'Artist')
    clb.addColumn(5, weight = 1, primary = True, name = 'Album')
    clb.addColumn(2, 2, alignment = 'right', name = 'Track Number')
    clb.addColumn(5, weight = 2, name = 'Title')

    clb.setItems(items, [i for i in range(len(items))])

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

    table = dtk.TextTable(e, 'texttable', vimlike = True)

    table.addColumn(5, weight = 1, name = 'Artist')
    table.addColumn(5, weight = 1, name = 'Album')
    table.addColumn(2, 2, alignment = 'right')
    table.addColumn(5, weight = 2, name = 'Song')


    table.setItems(items, [i for i in range(len(items))])

elif len(sys.argv) > 1 and sys.argv[1] == 'l':
    l = dtk.Label(e, 'label', 'My Label Text')

elif len(sys.argv) > 1 and sys.argv[1] == 's':
    s = dtk.Stack(e, 'stack')

    lbl = dtk.Label(s, 'label-0', 'Label 0')
    s.push(lbl)
    e.setFocus(lbl)


    def stackPush(stack):
        lbl = dtk.Label(stack, 'label-%d' % len(stack), 'Label %d' % len(stack))
        stack.push(lbl)

    s.bindKey('page up', stackPush, s)
    s.bindKey('page down', s.pop)

elif len(sys.argv) > 1 and sys.argv[1] == 'button':
    r = dtk.Rows(e, 'rows', outerborder = False, innerborder = False)

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

    b1 = dtk.Button(r, 'Button 1')
    b2 = dtk.Button(r, 'Button 2')
    b3 = dtk.Button(r, 'Button 3')

    b1.bindKey('click', toggle, b1)
    b2.bindKey('click', toggle, b2)
    b3.bindKey('click', toggle, b3)

    r.addRow(b1, 1)
    r.addRow(b2, 1)
    r.addRow(b3, 1)

    e.setFocus(b1)

else:
    lb = dtk.ListBox(e, '+++', vimlike = True)
    lb.setItems(['First item', 'Second item', 'Third Item'], [1,2,3])


e.getRoot().bindKey('q', e.quit)
e.mainLoop()
