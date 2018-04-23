#!/usr/bin/env python3

import RPi.GPIO as GPIO
import picamera
import time
import subprocess
import shutil
import threading

# Physical pin 13
GPIO_PIN = 27

# Camera setup
camera = picamera.PiCamera()
camera.resolution = (1200, 720)

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
    time.sleep(5)
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
