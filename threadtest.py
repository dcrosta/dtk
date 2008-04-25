#!/usr/bin/env python
import threading
import logging
import time

import dtk.events
from dtk.engine import Engine


class TimerEvent(dtk.events.Event):

    def __init__(self, count):
        self.count = count

    def __repr__(self):
        return str(self.count)

class Timer(threading.Thread):
    """
    based on threading.Timer, but resets the timer
    unless cancel() is called.
    """

    def __init__(self, event_queue):
        threading.Thread.__init__(self)

        self.finished = threading.Event()
        self.event_queue = event_queue
        self.done = False

    def cancel(self):
        self.event_queue.add(TimerEvent(100))
        self.done = True
        self.finished.set()

    def run(self):
        for i in range(1, 6):
            self.finished.wait(1.0)
            if self.done:
                break
            else:
                self.event_queue.add(TimerEvent(i))
            self.finished.clear()

e = Engine()
t = Timer(e.get_event_queue())
t.start()

e.start_dtk()

