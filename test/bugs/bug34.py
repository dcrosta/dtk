import dtk
import curses
from dtktest import DtkTestCase


class BugThirtyFour(DtkTestCase):

    def testCallableClassBinding(self):

        call_trace = []
        def trace(fmt, *args):
            call_trace.append(fmt % args)

        class CallableClass(object):

            def __call__(self, *args, **kwargs):
                trace('(%s, %s)', args, kwargs)


        class CallableWithInputKey(CallableClass):

            def __call__(self, _input_key, *args, **kwargs):
                trace('(_input_key = %s, %s, %s)', _input_key, args, kwargs)

        class CallableWithSourceObj(CallableClass):

            def __call__(self, _source_obj, *args, **kwargs):
                trace('(_source_obj = %s, %s, %s)', _source_obj, args, kwargs)

        class CallableWithBoth(CallableClass):

            def __call__(self, _input_key, _source_obj, *args, **kwargs):
                trace('(_input_key = %s, _source_obj = %s, %s, %s)', _input_key, _source_obj, args, kwargs)

        class CallableWithEventType(CallableClass):

            def __call__(self, _event_type, *args, **kwargs):
                trace('(_event_type = %s, %s, %s)', _event_type, args, kwargs)

        class CallableWithEventTypeSource(CallableClass):

            def __call__(self, _event_type, _source_obj, *args, **kwargs):
                trace('(_event_type = %s, _source_obj = %s, %s, %s)', _event_type, _source_obj, args, kwargs)


        self.scr.set_input('a','b','c','d','enter','q')
        

        e = dtk.Engine()
        e.bindKey('q', e.quit)

        b = dtk.Button('blah')

        e.setRoot(b)

        mycallable = CallableClass()
        mycallable_i = CallableWithInputKey()
        mycallable_s = CallableWithSourceObj()
        mycallable_is = CallableWithBoth()
        mycallable_e = CallableWithEventType()
        mycallable_es = CallableWithEventTypeSource()

        b.bindKey('a', mycallable)
        b.bindKey('b', mycallable_i)
        b.bindKey('c', mycallable_s)
        b.bindKey('d', mycallable_is)

        b.bindEvent('clicked', mycallable)
        b.bindEvent('clicked', mycallable_e)
        b.bindEvent('clicked', mycallable_s)
        b.bindEvent('clicked', mycallable_es)

        e.mainLoop()


        def map_of_counts(l):
            m = {}
            for elm in l:
                m[elm] = m.get(elm, 0) + 1
            return m

        expected = [
            '((), {})',
            '(_input_key = b, (), {})',
            '(_source_obj = Button, (), {})',
            '(_input_key = d, _source_obj = Button, (), {})',
            '((), {})',
            '(_event_type = clicked, (), {})',
            '(_event_type = clicked, _source_obj = Button, (), {})',
            '(_source_obj = Button, (), {})',
        ]

        self.assertEquals(len(expected), len(call_trace), "same # of actual calls as expected")

        expected = map_of_counts(expected)
        actual = map_of_counts(call_trace)

        for elm in expected:
            self.assert_(elm in actual)
