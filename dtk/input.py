import threading
import time
import types
import curses
import curses.ascii
import traceback

waiter = threading.Event()

class Monitor(threading.Thread):

    def __init__(self, scr, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self.stopped = False
        self.scr = scr

        self.count = 0

    def stop(self):
        self.scr.addstr(9, 0, "Monitor set stopped=True")
        self.stopped = True

    def update(self):
        self.count += 1

    def run(self):
        self.scr.addstr(10, 0, "Monitor                 %d" % id(waiter))

        while not self.stopped:
            self.scr.addstr(10, 0, "Monitor waiting %s      " % self.count)
            waiter.wait()
            waiter.clear()
            self.scr.addstr(10, 0, "Monitor got a notice   ")

            self.scr.addstr(1, 0, "count is %3d   %s" % (self.count, bool(self.stopped)))


def curses_input(scr):
    scr.move(0,0)
    scr.clrtobot()
    scr.immedok(1)
    scr.keypad(False)

    m = Monitor(scr)
    m.start()

    scr.move(1,0)
    scr.addstr("blah")

    lasttime = time.time()
    line = 3


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
            scr.move(15 + i, 0)
            scr.clrtoeol()
            key = '.'.join([str(x) for x in input_queue[0:min(i+1,len(input_queue))]])
            try:
                scr.addstr(15 + i, 0, "type at key %s is " % key)
                km = km[char]
                scr.addstr(str(type(km)))
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

        now = time.time()
        if now - lasttime < 0.1:
            line += 1
        else:
            for y in range(3, 8):
                scr.move(y, 0)
                scr.clrtoeol()
            line = 3
        lasttime = time.time()

        scr.move(line, 0)
        scr.clrtoeol()
        scr.addstr(line, 0, "input was '%s'" % str(input))
        scr.addstr(8, 0, "iq was '%s'" % str(input_queue))
        if input == 'q':
            m.stop()
            break

        m.update()
        
        scr.addstr(11, 0, "Main acquired waiter    %d" % id(waiter))
        waiter.set()
        scr.addstr(11, 0, "Main notifying         ")

        input_queue = []


    waiter.set()
    m.join()
    scr.move(0, 0)
    scr.clrtobot()
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


def start():
    curses.wrapper(curses_input)

if __name__ == '__main__':
    start()

