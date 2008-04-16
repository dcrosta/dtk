# DTK, a curses "GUI" toolkit for Python programs.
# 
# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# 
# DTK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# DTK is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with Foobar. If not, see <http://www.gnu.org/licenses/>.

import threading

class Event(object):
    pass

class EventQueue(object):
    """
    A thread-safe queue used to hold events that the Engine
    must handle. Events will be one of the types that are defined
    in this module, and will subclass dtk.events.Event.
    """

    def __init__(self):
        self.queue = []

        # locks so that only one thread
        # can diddle the Queue at a time
        self.queue_lock = threading.RLock()

        # an Event which add() uses to release
        # someone waiting on get()
        self.available = threading.Event()

    def add(self, event):
        """
        add an event to the queue. raises TypeError if
        the event is not a subclass of Event
        """
        if not isinstance(event, Event):
            raise TypeError("Can only add dtk.events.Event (or sublcass) instances to EventQueue")

        self.queue_lock.acquire()
        self.queue.append(event)
        from core import Engine
        Engine().log.debug("input queue is now: %s", str(self.queue))
        self.queue_lock.release()

        # release threads blocking on get()
        self.available.set()

    def get(self):
        """
        return the oldest (first) event from the queue. blocks
        until an event is available in the queue. will return
        None if another thread calls clear() while a thread
        is waiting on get().
        """
        from core import Engine
        Engine().log.debug("wait()ing")
        self.available.wait()
        Engine().log.debug("wait() returned")
        self.queue_lock.acquire()
        try:
            event = self.queue.pop(0)
        except IndexError:
            # queue is empty
            event = None
        self.queue_lock.release()
        self.available.clear()
        return event
    
    def clear(self):
        """
        clear the queue and release any threads waiting
        """
        self.queue_lock.acquire()
        self.queue = []
        self.queue_lock.release()

        self.available.set()

class KeyEvent(Event):
    """
    An event to represent a parsed keyboard input. str()- and
    repr()-able to a friendly name for the key, as defined
    in dtk.input.keymap. The key name is also available as
    the keyname attribute of the Event.
    """

    def __init__(self, keyname):
        self.keyname = keyname

    def __repr__(self):
        return self.keyname

