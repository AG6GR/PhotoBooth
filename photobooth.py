#!/usr/bin/env python3

import RPi.GPIO as GPIO
import picamera
import time
import subprocess
import shutil
import threading
import random

# Physical pin 13
GPIO_PIN = 27

# Camera setup
camera = picamera.PiCamera()
camera.resolution = (820, 1232)
camera.awb_mode='off'
camera.awb_gains=(Fraction(363, 256), Fraction(531, 256))

# Background files
backgrounds_path = 'Blender/backgrounds/'
backgrounds = ['moon_crop.jpg', 'the_scream_crop.jpg']

# Button debouncing class from https://raspberrypi.stackexchange.com/questions/76667/debouncing-buttons-with-rpi-gpio-too-many-events-detected
class ButtonHandler(threading.Thread):
    def __init__(self, pin, func, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)

        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in ['falling', 'both'])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in ['rising', 'both']))
        ):
            self.func(*args)

        self.lastpinval = pinval
        self.lock.release()

# Launch Blender/process render
def doRender():
    shutil.copyfile(backgrounds_path + random.choice(backgrounds), 'background.jpg')
    arglist = ['blender', '-b', 'Blender/GeneratePreview.blend', '-x', '0', '-o', './render#.png', '-f', '1']
    subprocess.run(arglist)

#GPIO Callback
def onButton(channel):
    print("Callback Triggered")
    if channel == GPIO_PIN:
        print("Taking photo")
        latest_image = 'image{:0}.jpg'.format(int(time.time()))
        camera.capture(latest_image)
        print(latest_image)
        shutil.copyfile(latest_image, "latest.jpg")
    
    # Move webpage to Processing
    subprocess.run(["xdotool", "search", "--desktop", "0", "--class", "chromium", "windowactivate", "--sync", "key", "P"])
    doRender()
    # Move webpage to Result
    subprocess.run(["xdotool", "search", "--desktop", "0", "--class", "chromium", "windowactivate", "--sync", "key", "R"])
    time.sleep(15)
    # Move webpage to Welcome
    subprocess.run(["xdotool", "search", "--desktop", "0", "--class", "chromium", "windowactivate", "--sync", "key", "W"])


def main():
    global httpd
    global server_thread

    print("Starting...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    cb = ButtonHandler(GPIO_PIN, onButton, edge='rising', bouncetime=20)
    cb.start()
    GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=cb)

    print("Init chrome")
    chrome_proc = subprocess.Popen(["chromium-browser", "--noerrdialogs", "--incognito", "--kiosk", "http://localhost:80/welcome.html"])

if __name__ == "__main__":
    main()
    input()
