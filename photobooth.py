#!/usr/bin/env python3

import RPi.GPIO as GPIO
import picamera
import time
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
from threading import Thread

# Physical pin 13
GPIO_PIN = 27
camera = picamera.PiCamera()
latest_image = ''

# HTTP Server request handler
class MyRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("GET request!", self.path)
        if self.path == '/latest.jpg':
            print("redirect to:", '/' + latest_image)
            self.path = '/' + latest_image
        return SimpleHTTPRequestHandler.do_GET(self)


#GPIO Callback
def onButton(channel):
        global latest_image
        print("Callback Triggered")
        if channel == GPIO_PIN:
                print("Taking photo")
                latest_image = 'image{:0}.jpg'.format(int(time.time()))
                camera.capture(latest_image)
                print(latest_image)
        # Reload webpage
        subprocess.run(["xdotool", "search", "--desktop", "0", "--class", "chromium", "windowactivate", "--sync", "key", "ctrl+F5"])

def main():
    global httpd
    global server_thread

    print("Starting...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=onButton, bouncetime=1000)

    httpd = HTTPServer(('', 8000), MyRequestHandler)

    chrome_proc = subprocess.Popen(["chromium-browser", "http://localhost:8000/latest.jpg"])
    httpd.serve_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)