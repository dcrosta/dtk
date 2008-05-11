"""
DECOMMISSIONING THIS TEST. We have currently removed focus events pending review


import dtk
import dtktest

class BugThirtySix(dtktest.DtkTestCase):

    def testFocusEvents(self):
        self.scr.set_input('tab','tab','q')

        event_trace = []
        def trace_events(_source_obj, _event_type):
            event_trace.append((_source_obj, _event_type))


        e = dtk.Engine()

        cols = dtk.ColumnLayout()
        rows = dtk.RowLayout()
        lb = dtk.ListBox()

        lll = []
        for i in "eins zwei drei vier fuenf".split():
            lll.append(i)

        text = dtk.TextEditor()
        text.setText("This is the text")

        lb.setItems(lll)

        rows.addRow(lb)
        rows.addRow(text)

        def dothings():
            rows.log.error("switching child")
            rows.nextRow()

        rows.bindKey('tab', dothings)

        text.bindEvent("became active", trace_events)
        text.bindEvent("became inactive", trace_events)

        cols.addColumn(rows)
        cols.addColumn(dtk.Label(text='Hi'))
        cols.bindKey('F1', cols.nextColumn)

        e.setRoot(cols)

        e.bindKey('q', e.quit)

        e.mainLoop()


        expected = [
            (text, 'became active'),
            (text, 'became inactive')
            ]

        self.assertEqual(len(expected), len(event_trace))
        for e, a, i in zip( expected, event_trace, range(len(expected))):
            self.assertEqual(e[0], a[0], "source objs: event %d" % i)
            self.assertEqual(e[1], a[1], "event types: event %d" % i)
"""
