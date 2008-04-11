import threading
import time
import curses
import curses.ascii

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

    while True:
        input = scr.getch()
        if curses.ascii.isprint(input):
            input = chr(input)

        scr.move(3, 0)
        scr.clrtoeol()
        scr.addstr(3, 0, "input was '%s'" % input)
        if input == 'q':
            m.stop()
            break

        m.update()
        
        scr.addstr(11, 0, "Main acquired waiter    %d" % id(waiter))
        waiter.set()
        scr.addstr(11, 0, "Main notifying         ")


    waiter.set()
    m.join()
    curses.endwin()


def start():
    curses.wrapper(curses_input)

if __name__ == '__main__':
    start()

