import datetime
import locale
import logging
import os

import text
import threading
import queue
import time
import gbl
import lightHandler
import home_loop

q_read = queue.Queue()
q_speak = gbl.q_speak
l_audio = threading.Lock()
l_thread = threading.Lock()

from aiy.leds import Color
from aiy.cloudspeech import CloudSpeechClient
from aiy.board import Board
import aiy.voice.tts


def locale_language():
    language, _ = locale.getdefaultlocale()
    return language


hints = ["ho comprato",
         "dimmi le mie notifiche",
         "togli dalla lista",
         "fai i conti",
         "si",
         "sì",
         "esatto",
         "certo",
         "no",
         "annulla"]


def main():

    if os.getuid() is not 0:
        print("Must Be Run As root")
        return

    for i in range (1,40):
        hints.append("%d" % i)
    logging.basicConfig(level=logging.DEBUG)
    thread2 = Parser("Parser Thread")
    thread3 = Teller("Speak Thread")
    thread4 = lightHandler.Colors("Color Thread")
    thread5 = Checker("Color Thread")
    thread2.daemon = True
    thread3.daemon = True
    thread4.daemon = True
    thread5.daemon = True
    thread2.start()
    thread3.start()
    thread4.start()
    #thread5.start()

    print("Ready...")

    lightHandler.led_off()

    with Board() as board:
        while True:
            board.button.wait_for_press()
            board.button.wait_for_release()
            toggle()


running = None


def toggle():
        l_thread.acquire()
        if running is None:
            start()
        else:
            stop()
        l_thread.release()


def start():
    global running
    global reset
    global q_read
    if running is None:
        running = Listener("Listener Thread")
        running.daemon = True
        running.start()
        timer = Timer("Timer Thread")
        timer.daemon = True
        timer.start()
        time.sleep(1)
        lightHandler.led_on()
        reset = datetime.datetime.now() + datetime.timedelta(seconds=30)


def stop():
    global running
    global reset
    global q_read
    if running is not None:
        gbl.username = ""
        running.kill()
        running = None
        lightHandler.led_off()
        reset = datetime.datetime.min
        q_read.put(None)


class Listener(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.name = nome
        self.stopped = False

    def run(self):
        global l_audio
        global q_read
        client = CloudSpeechClient()
        while True:
            l_audio.acquire()
            lightHandler.pre_listen()
            read = client.recognize(language_code="it_IT", hint_phrases=hints)
            l_audio.release()
            if self.stopped:
                return
            if read is None:
                logging.info('You said nothing.')
                continue

            logging.info('You said: "%s"' % read)
            read = read.lower()
            q_read.put(read)
            while not gbl.listen:
                time.sleep(0.1)

    def kill(self):
        self.stopped = True


class Teller(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.nome = nome

    def run(self):
        while True:
            global args
            global l_audio
            global q_speak
            global reset

            l_audio.acquire()
            while not q_speak.empty():
                say = q_speak.get(True)
                print("Devo Dire: %s" % say)
                lightHandler.talking(False)
                aiy.voice.tts.say(text=say,lang="it-IT",volume=45)
                lightHandler.talking(True)
            l_audio.release()
            reset = datetime.datetime.now() + datetime.timedelta(seconds=30)


class Parser(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.nome = nome

    def run(self):
        global q_speak
        global q_read
        text.process_text(q_read)


class Checker(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.nome = nome

    def run(self):
        home_loop.people_home(start, stop)


reset = datetime.datetime.min


class Timer(threading.Thread):
    def __init__(self, nome):
        threading.Thread.__init__(self)
        self.nome = nome

    def run(self):
        global reset
        while reset > datetime.datetime.now():
            time.sleep(0.1)
        stop()


if __name__ == '__main__':
    main()
