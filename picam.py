import cv2
import socket
from test12 import get_lane
#from utils import Rotate
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

#width, height = 240, 320
ip = '192.168.43.227'
print "hi"
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 64
rawCapture = PiRGBArray(camera, size=(320, 240))
print 'hi'
time.sleep(0.1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, 1693)
sock.connect(server_address)
print 'hi'

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        image = frame.array
	try:
		image,point = get_lane(image)
		print point
		sock.send(point.encode())
	except:
                print("error")
                pass

        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        rawCapture.truncate(0)

        if key == ord("q"):
		sock.send("1111".encode())
                break

   # except KeyboardInterrupt:
    #    sock.send("1111".encode())
     #   break

sock.close()
