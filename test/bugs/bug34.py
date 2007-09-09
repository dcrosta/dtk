import dtk
import curses
from dtktest import DtkTestCase


class BugThirtyFour(DtkTestCase):

    def testCallableClassBinding(self):

        call_trace = []
        def trace(fmt, *args):
            call_trace.append(fmt % args)

        class CallableClass(object):

            def __init__(self, log):
                """
                log should be a logging.Logger object; __call__ will
                log arguments given to the logging object with priority
                WARN
                """
                self.log = log

            def __call__(self, *args, **kwargs):
                trace('called with (%s, %s)', args, kwargs)


        class CallableWithInputKey(CallableClass):

            def __call__(self, _input_key, *args, **kwargs):
                trace('called with (_input_key = %s, %s, %s)', _input_key, args, kwargs)

        class CallableWithSourceObj(CallableClass):

            def __call__(self, _source_obj, *args, **kwargs):
                trace('called with (_source_obj = %s, %s, %s)', _source_obj, args, kwargs)

        class CallableWithBoth(CallableClass):

            def __call__(self, _input_key, _source_obj, *args, **kwargs):
                trace('called with (_input_key = %s, _source_obj = %s, %s, %s)', _input_key, _source_obj, args, kwargs)

        class CallableWithEventType(CallableClass):

            def __call__(self, _event_type, *args, **kwargs):
                trace('called with (_event_type = %s, %s, %s)', _event_type, args, kwargs)

        class CallableWithEventTypeSource(CallableClass):

            def __call__(self, _event_type, _source_obj, *args, **kwargs):
                trace('called with (_event_type = %s, _source_obj = %s, %s, %s)', _event_type, _source_obj, args, kwargs)


        self.scr.set_input('a','b','c','d','enter','q')
        

        e = dtk.Engine()
        e.bindKey('q', e.quit)

        b = dtk.Button('blah')

        e.setRoot(b)

        mycallable = CallableClass(e.log)
        mycallable_i = CallableWithInputKey(e.log)
        mycallable_s = CallableWithSourceObj(e.log)
        mycallable_is = CallableWithBoth(e.log)
        mycallable_e = CallableWithEventType(e.log)
        mycallable_es = CallableWithEventTypeSource(e.log)

        b.bindKey('a', mycallable)
        b.bindKey('b', mycallable_i)
        b.bindKey('c', mycallable_s)
        b.bindKey('d', mycallable_is)

        b.bindEvent('clicked', mycallable)
        b.bindEvent('clicked', mycallable_e)
        b.bindEvent('clicked', mycallable_s)
        b.bindEvent('clicked', mycallable_es)

        e.mainLoop()

        expected = [
            'called with ((), {})',
            'called with (_input_key = b, (), {})',
            'called with (_source_obj = Button, (), {})',
            'called with (_input_key = d, _source_obj = Button, (), {})',
            'called with ((), {})',
            'called with (_event_type = clicked, (), {})',
            'called with (_event_type = clicked, _source_obj = Button, (), {})',
            'called with (_source_obj = Button, (), {})',
        ]
        self.assertEquals(len(expected), len(call_trace), "same # of actual calls as expected")
        for e, a, i in zip(expected, call_trace, range(len(expected))):
            self.assertEquals(e, a, "expected call %d" % i)
