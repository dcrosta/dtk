import dtk
import logging

class CallableClass(object):

    def __init__(self, log):
        """
        log should be a logging.Logger object; __call__ will
        log arguments given to the logging object with priority
        WARN
        """
        self.log = log

    def __call__(self, *args, **kwargs):
        self.log.warn('called with (%s, %s)', args, kwargs)


class CallableWithInputKey(CallableClass):

    def __call__(self, _input_key, *args, **kwargs):
        self.log.warn('called with (_input_key = %s, %s, %s)', _input_key, args, kwargs)

class CallableWithSourceObj(CallableClass):

    def __call__(self, _source_obj, *args, **kwargs):
        self.log.warn('called with (_source_obj = %s, %s, %s)', _source_obj, args, kwargs)

class CallableWithBoth(CallableClass):

    def __call__(self, _input_key, _source_obj, *args, **kwargs):
        self.log.warn('called with (_input_key = %s, _source_obj = %s, %s, %s)', _input_key, _source_obj, args, kwargs)

class CallableWithEventType(CallableClass):

    def __call__(self, _event_type, *args, **kwargs):
        self.log.warn('called with (_event_type = %s, %s, %s)', _event_type, args, kwargs)

class CallableWithEventTypeSource(CallableClass):

    def __call__(self, _event_type, _source_obj, *args, **kwargs):
        self.log.warn('called with (_event_type = %s, _source_obj = %s, %s, %s)', _event_type, _source_obj, args, kwargs)


e = dtk.Engine()
e.beginLogging(file='log.txt', level=logging.WARN)
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
