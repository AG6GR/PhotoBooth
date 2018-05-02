#!/usr/bin/env python3

import RPi.GPIO as GPIO
import picamera
import time
import subprocess
import shutil
import threading
import random
from os import mkdir
from datetime import datetime
import json
import qrcode
from zipfile import ZipFile

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

class PhotoBooth:

    # Physical pin 13
    GPIO_PIN = 27

    # Background files
    backgrounds_path = 'Blender/backgrounds/'
    backgrounds = ['moon_crop.jpg', 'the_scream_crop.jpg']

    hostname = 'photobooth.lan/'

    def __init__(self):
        # Camera setup
        self.camera = picamera.PiCamera()
        self.camera.resolution = (820, 1232)
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = (363/256, 531/256)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PhotoBooth.GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.cb = ButtonHandler(PhotoBooth.GPIO_PIN, self.onButton, edge='rising', bouncetime=20)
        self.cb.start()
        GPIO.add_event_detect(PhotoBooth.GPIO_PIN, GPIO.RISING, callback=self.cb)

        self.latest_image = ''
        self.latest_info = {
            'result_link': PhotoBooth.hostname + 'results/'
        }

    # Launch Blender/process render
    def do_render(self):
        shutil.copyfile(PhotoBooth.backgrounds_path + random.choice(PhotoBooth.backgrounds), 'background.jpg')
        arglist = ['blender', '-b', 'Blender/GeneratePreview.blend', '-x', '0', '-o', './render#.png', '-f', '1']
        subprocess.run(arglist)

    def make_static(self):
        output_dir = 'results/result{:%H%M%S}'.format(datetime.now())
        mkdir(output_dir)
        shutil.copyfile('render1.png', output_dir+'/result.png')
        shutil.copyfile('background.jpg', output_dir+'/background.jpg')
        shutil.copyfile('ref.jpg', output_dir+'/ref.jpg')
        shutil.copyfile(self.latest_image, output_dir+'/original.jpg')
        shutil.copyfile('Blender/composite.blend', output_dir+'/composite.blend')
        shutil.copyfile('result_static.html', output_dir+'/index.html')

        qr = qrcode.make(PhotoBooth.hostname + output_dir+'/index.html')
        qr.save('qr_latest.png')

        zf = ZipFile(output_dir+'/all_files.zip', mode='w')
        zf.write(output_dir+'/result.png', arcname='result.png')
        zf.write(output_dir+'/background.jpg', arcname='background.jpg')
        zf.write(output_dir+'/ref.jpg', arcname='ref.jpg')
        zf.write(output_dir+'/original.jpg', arcname='original.jpg')
        zf.write(output_dir+'/composite.blend', arcname='composite.blend')
        zf.close()

        self.latest_info['result_link'] = PhotoBooth.hostname + output_dir
        with open('latest.json', 'w') as outfile:
            json.dump(self.latest_info, outfile)

    #GPIO Callback
    def onButton(self, channel):
        print("Callback Triggered")
        if channel == PhotoBooth.GPIO_PIN:
            print("Taking photo")
            self.latest_image = 'image{:0}.jpg'.format(int(time.time()))
            self.camera.capture(self.latest_image)
            print(self.latest_image)
            shutil.copyfile(self.latest_image, "latest.jpg")
        
        # Move webpage to Processing
        subprocess.run(["xdotool", "search", "--desktop", "0", "--class", "chromium", "windowactivate", "--sync", "key", "P"])
        self.do_render()
        self.make_static()
        # Move webpage to Result
        subprocess.run(["xdotool", "search", "--desktop", "0", "--class", "chromium", "windowactivate", "--sync", "key", "R"])

def main():

    print("Starting...")
    pb = PhotoBooth()

    print("Init chrome")
    chrome_proc = subprocess.Popen(["chromium-browser", "--noerrdialogs", "--incognito", "--kiosk", "http://localhost:80/welcome.html"])

if __name__ == "__main__":
    main()
    input()
