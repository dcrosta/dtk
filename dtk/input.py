import threading
import time
import types
import curses
import curses.ascii
import traceback

from events import EventQueue, KeyEvent
from core import Engine

waiter = threading.Event()

class Monitor(threading.Thread):

    def __init__(self, scr, event_queue, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self.stopped = False
        self.scr = scr
        self.event_queue = event_queue

        self.count = 0

    def stop(self):
        self.scr.addstr(9, 0, "Monitor set stopped=True")
        self.stopped = True

    def update(self):
        self.count += 1

    def run(self):
        self.scr.addstr(10, 0, "Monitor                 %d" % id(waiter))

        while not self.stopped:
            input = self.event_queue.get()
            self.scr.addstr(10, 0, "Monitor got a notice   ")

            self.scr.addstr(1, 0, "count is %3d   %s" % (self.count, bool(self.stopped)))


def curses_mainloop(scr):
    scr.move(0,0)
    scr.clrtobot()
    scr.immedok(1)
    scr.keypad(False)

    eq = EventQueue()

    e = Engine()
    e.set_event_queue(eq)
    e.set_scr(scr)
    m = threading.Thread(target=e.run)
    m.start()

    e.log.debug('Threads are:')
    for thread in threading.enumerate():
        e.log.debug('  %s', thread)


    input_queue = []
    while True:

        while True:
            input = scr.getch()
            # have to do this after we get the char
            scr.nodelay(1)
            input_queue.append(input)
            if input == -1:
                scr.nodelay(0)
                break

        km = keymap
        i = 0
        for char in input_queue:
            try:
                km = km[char]
            except Exception, e:
                # usually this exception is OK, because
                # it often comes from printable keys, which
                # are not mapped in the keymap
                break

        # if input_queue is 2 long (something then a -1),
        # then the first element is the key code for a
        # printable character; else km should be the string
        # name of the key found from the keymap
        if len(input_queue) == 2 and input_queue[0] not in keymap:
            input = input_queue[0]
            if curses.ascii.isprint(input):
                input = chr(input)

        elif type(km) != types.StringType:
            # throw an exception?
            #km = str(input_queue) # for now
            pass

        else:
            input = km

        if input == 'q':
            eq.clear()
            break

        eq.add(KeyEvent(input))
        
        input_queue = []


    waiter.set()
    m.join()
    curses.endwin()

# map special keys to nicer names
keymap = {
    27: { -1: "esc",
          91: { 49: { 53: { 126: { -1: "F5" } },
                      55: { 126: { -1: "F6" } },
                      56: { 126: { -1: "F7" } },
                      57: { 126: { -1: "F8" } }
                    },
                50: { 48: { 126: { -1: "F9" } },
                      49: { 126: { -1: "F10" } },
                      51: { 126: { -1: "F11" } },
                      52: { 126: { -1: "F12" } },
                    },
                53: { 126: { -1: "page up" } },
                54: { 126: { -1: "page down" } },
                65: { -1: "up" },
                66: { -1: "down" },
                67: { -1: "right" },
                68: { -1: "left" },
                70: { -1: "end" },
                72: { -1: "home" },
              },
          79: { 80: { -1: "F1" },
                81: { -1: "F2" },
                82: { -1: "F3" },
                83: { -1: "F4" },
              },
        },
    127: { -1: "backspace" }
    }


def mainloop():
    curses.wrapper(curses_mainloop)

if __name__ == '__main__':
    mainloop()

