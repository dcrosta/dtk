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
    scr.keypad(False)
    delay = 1
    curses.halfdelay(delay)

    eq = EventQueue()

    e = Engine()
    e.set_event_queue(eq)
    e.set_screen(Screen(scr))
    m = threading.Thread(target=e.run)
    m.start()

    fp = file('log.txt','a')

    input_queue = []
    no_input_count = 0
    while len(threading.enumerate()) > 1:

        curses.halfdelay(delay)
        while True:
            input = scr.getch()
            input_queue.append(input)
            curses.cbreak()
            scr.nodelay(1)

            if input == -1:
                scr.nodelay(0)
                break

        if len(input_queue) == 1 and input_queue[0] == -1:
            input_queue = []
            if no_input_count >= 5:
                delay = 10
            no_input_count += 1
            continue

        delay = 1
        no_input_count = 0

        fp.write('input_queue: %s\n' % input_queue)
        parsed = parse_input(input_queue)
        fp.write('parsed: %s\n' % parsed)
        fp.flush()
        for key in parsed:
            eq.add(KeyEvent(key))
        
        input_queue = []

    m.join()
    curses.endwin()

def parse_input(queue):
    """
    parse a list of input integers (char codes) into
    the correct output list of DTK input strings. for
    printable characters, the output string is the
    name of the key (eg "a"); for special keys, it
    is one of the tail values in keymap.

    >>> parse_input([97])
    ['a']
    >>> parse_input([97, 98])
    ['a', 'b']
    >>> parse_input([97, -1])
    ['a']
    >>> parse_input([97, -1, 98, -1])
    ['a', 'b']
    >>> parse_input([])
    []
    >>> parse_input([27, -1])
    ['esc']
    >>> parse_input([27, 91, 49, 53, 126, -1])
    ['F5']

    It also works if there are no -1s separating
    the inputs for escape sequences.

    >>> parse_input([27, 27, 91, 49, 53, 126, -1])
    ['esc', 'F5']
    """

    out = []
    i = 0
    while i < len(queue):
        char = queue[i]
        if char == -1:
            i += 1
            continue
        elif curses.ascii.isprint(char):
            out.append(chr(char))
            i += 1
        else:
            keyname, consumed = parse_escape_sequence(queue[i:])
            out.append(keyname)
            i += consumed

    return out

def parse_escape_sequence(sequence):
    """
    parses as much of the input sequence (a list of
    ints as in parse_input) as it can, and returns
    a tuple (key_name, chars_parsed). if the
    sequence cannot be parsed at all, key_name is
    None, and chars_parsed is 0.

    parse_escape_sequence will consume a -1 in the
    input if it follows a valid escape sequence. it
    will also accept escape sequences which are not
    followed by a -1.

    >>> parse_escape_sequence([27, -1])
    ('esc', 2)
    >>> parse_escape_sequence([27])
    ('esc', 1)
    >>> parse_escape_sequence([27, 27, 91, 49, 53, 126, -1])
    ('esc', 1)
    """
    km = keymap
    keyname = None

    i = 0
    while i < len(sequence):
        char = sequence[i]
        i += 1
        if char in km:
            km = km[char]
        elif -1 in km:
            # there was no -1 in the input, but we 
            # found a leaf in the keymap
            keyname = km[-1]
            i -= 1
            break

        if type(km) in types.StringTypes:
            keyname = km
            break


    if keyname is None and -1 in km:
        keyname = km[-1]

    return (keyname, i)

def mainloop():
    curses.wrapper(curses_mainloop)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

