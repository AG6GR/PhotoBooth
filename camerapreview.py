import picamera

camera = picamera.PiCamera()
camera.resolution = (820, 1232)
camera.awb_mode='off'
camera.awb_gains=(Fraction(363, 256), Fraction(531, 256))

camera.start_preview()
print("Press enter to quit")
input()
camera.stop_preview()