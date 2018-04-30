import picamera

camera = picamera.PiCamera()
camera.resolution = (820, 1232)
camera.awb_mode='fluorescent'

camera.start_preview()
print("Press enter to quit")
input()
camera.stop_preview()