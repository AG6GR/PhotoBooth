#!/usr/bin/python3

import RPi.GPIO as GPIO
import picamera
import time

camera = picamera.PiCamera()

#GPIO Callback
def onButton(channel):
		print("Callback Triggered")
		if channel == 27:
				print("Taking photo")
				camera.capture('image{:0}.jpg'.format(int(time.time())))

def main():
	print("Starting...")
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(27, GPIO.FALLING, callback=onButton, bouncetime=1000)
	print("Press any key to exit")

if __name__ == "__main__":
	main()
	input()
