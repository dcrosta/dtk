"""
test case for new 'active' events for task #41

"""

import dtk
import logging


e = dtk.Engine()
e.beginLogging(file='log.txt', level=logging.ERROR)


def logEventAsError(_source_obj, _event_type):
    _source_obj.log.error('%s got "%s" event', _source_obj.name, _event_type)

rw = dtk.Rows()

lb = dtk.ListBox()
lb.name = 'English'
lb.setItems([
        'First item',
        'Second item',
        'Third item',
        'And another'])

lb.bindEvent('became active', logEventAsError)
lb.bindEvent('became inactive', logEventAsError)


rw.addRow(lb)


lb = dtk.ListBox()
lb.name = 'Spanish'
lb.setItems([
        'primer item',
        'segundo item',
        'tercer item'])

lb.bindEvent('became active', logEventAsError)
lb.bindEvent('became inactive', logEventAsError)


rw.addRow(lb)

cl = dtk.Columns(outerborder=False)
cl.name = 'buttons'
cl.bindEvent('became active', logEventAsError)
cl.bindEvent('became inactive', logEventAsError)

cl.unbindKey('tab')
cl.bindKey('`', cl.nextColumn)


b = dtk.Button('Foo')
b.name = 'foo'
b.bindEvent('became active', logEventAsError)
b.bindEvent('became inactive', logEventAsError)

cl.addColumn(b)

b = dtk.Button('Bar')
b.name = 'bar'
b.bindEvent('became active', logEventAsError)
b.bindEvent('became inactive', logEventAsError)

cl.addColumn(b)

b = dtk.Button('Baz')
b.name = 'baz'
b.bindEvent('became active', logEventAsError)
b.bindEvent('became inactive', logEventAsError)

cl.addColumn(b)

rw.addRow(cl)


e.setRoot(rw)
e.bindKey('q', e.quit)

e.mainLoop()
