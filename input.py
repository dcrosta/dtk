import threading
import time
import curses
import curses.ascii

class Monitor(threading.Thread):

    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self.stopped = False
        self.scr = None

    def stop(self):
        #print "setting stopped=True"
        self.stopped = True

    def update(self, message):
        print message

    def run(self):

        count = 0

        while not self.stopped:
            time.sleep(0.5)
            if self.scr is not None:
                self.scr.addstr(1, 0, "count is %d" % count)
                count += 1


def curses_input(scr, m):
    scr.move(0,0)
    scr.clrtobot()
    scr.immedok(1)
    scr.keypad(False)

    # find the thread, set it's scr attribute
    for thread in threading.enumerate():
        if isinstance(thread, Monitor):
            thread.scr = scr
            scr.addstr("set scr on %s" % thread)
            break

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

    m.join()



def start(m):
    curses.wrapper(curses_input, m)

if __name__ == '__main__':
    m = Monitor()
    m.start()

    start(m)

