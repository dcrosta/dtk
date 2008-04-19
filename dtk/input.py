import threading
import types
import curses
import curses.ascii
import traceback

from events import EventQueue, KeyEvent
from engine import Engine
from screen import Screen

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

running = True

def stop():
    global running
    running = False

def curses_mainloop(scr):
    scr.move(0,0)
    scr.clrtobot()
    scr.keypad(False)
    #curses.halfdelay(3)

    eq = EventQueue()

    e = Engine()
    e.set_event_queue(eq)
    e.set_screen(Screen(scr))
    m = threading.Thread(target=e.run)
    m.start()

    fp = file('log.txt', 'a')
    input_queue = []
    while running:

        while True:
            input = scr.getch()
            scr.nodelay(1)
            input_queue.append(input)

            if input == -1:
                scr.nodelay(0)
                break

        fp.write('input_queue: %s\n' % str(input_queue))
        fp.flush()

        if len(input_queue) == 1 and input_queue[0] == -1:
            input_queue = []
            curses.cbreak()
            continue

        curses.halfdelay(1)

        km = keymap
        i = 0
        # FIXME: need to handle cases where there isn't
        # enough time between input that getch() returns
        # a -1... so this requires smarter traversal of
        # the keymap as well as some intuition about what
        # keys are regular keycodes (ascii keys, i guess?)
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

        eq.add(KeyEvent(input))
        
        input_queue = []

    m.join()
    curses.endwin()

def mainloop():
    curses.wrapper(curses_mainloop)

if __name__ == '__main__':
    mainloop()

