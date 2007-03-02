import dtk
import logging


e = dtk.Engine()
e.beginLogging(level=logging.ERROR, file='log.txt')

# a method which creates a new event whenever
# it receives one; it will be bound to
# both a key event and to the event
# it creates
def dumb_event_target(_event_type, _source_obj):
    e.log.error("got '%s' event from '%s'", _event_type, _source_obj)
    e.enqueueEvent(None, 'dummy event')


b = dtk.Button()
b.setText('Set the ball rolling')

e.setRoot(b)

b.bindEvent('clicked', dumb_event_target)
e.bindEvent(None, 'dummy event', dumb_event_target)


e.bindKey('q', e.quit)


e.mainLoop()
