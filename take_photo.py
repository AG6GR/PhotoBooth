#!/usr/bin/python3

import RPi.GPIO as GPIO
import picamera
import time

# Physical pin 13
GPIO_PIN = 27
camera = picamera.PiCamera()

#GPIO Callback
def onButton(channel):
		print("Callback Triggered")
		if channel == GPIO_PIN:
				print("Taking photo")
				camera.capture('image{:0}.jpg'.format(int(time.time())))

def main():
	print("Starting...")
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=onButton, bouncetime=1000)
	print("Press any key to exit")

if __name__ == "__main__":
	main()
	input()
