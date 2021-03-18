
import queue
import time
import threading
from aiy.leds import Leds, Color
from aiy.board import Board, Led


color_q = queue.Queue()

state = False

color = Color.RED

lock = threading.Lock()


def _setColor(color):
    global state
    if(state):
        Leds().update(Leds.rgb_on(color))


def talking(end):
    global color
    global lock
    if(end):
        _setColor(color)
        lock.release()
    else:
        lock.acquire()
        _setColor(Color.PURPLE)


def pre_listen():
    global color
    global lock
    lock.acquire()
    if color == Color.BLUE or color == Color.RED:
        _setColor(Color.YELLOW)
        t = Delay("Delay thread")
        t.start()


def setcolor(color):
    global color_q
    color_q.put(color)


def led_on():
    global state
    lock.acquire()
    state = True
    Board().led.state = Led.ON
    lock.release()


def led_off():
    global state
    lock.acquire()
    state = False
    Board().led.state = Led.OFF
    lock.release()


class Colors(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.name = nome
        self.stopped = False

    def run(self):
        global color
        while not self.stopped:
            color = color_q.get(True)
            lock.acquire()
            _setColor(color)
            lock.release()

    def kill(self):
        self.stopped = True


class Delay(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.name = nome

    def run(self):
        global color
        time.sleep(1)
        _setColor(color)
        lock.release()