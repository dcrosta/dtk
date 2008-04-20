#!/usr/bin/env python
import threading
import logging
import time

import dtk.events


class TimerEvent(dtk.events.Event):

    def __init__(self, count):
        self.count = count

    def __repr__(self):
        return self.count

class Timer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.event_queue = dtk.events.EventQueue()

    def run(self):
        for i in range(1, 6):
            time.sleep(1)
            self.event_queue.add(TimerEvent(i))

t = Timer()
t.start()
dtk.mainloop()
