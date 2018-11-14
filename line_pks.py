#-*- coding: utf-8 -*-
import cv2,socket
from line import get_lane

ip = '192.168.43.134' # 라즈베리파이 주소
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip ,3000)
sock.connect(server_address)

cap = cv2.VideoCapture(0) # 노트북 유에스비

while cap.isOpened():
	try:
		ret, frame = cap.read()
    		try:
        		frame, point, num = get_lane(frame)
        		print "x좌표=",point,"선 개수=",num
	        	sock.send(point.encode())
			sock.send(num.encode())

    		except Exception, e:
			print e
			pass

    		cv2.imshow('get_lane', frame)

    		if cv2.waitKey(1) & 0xFF == ord('q'):
			sock.send("1111".encode())
			sock.send("9".encode())
	       		break

	except KeyboardInterrupt:
		sock.send("1111".encode())
		sock.send("9".encode())
        	break

	except Exception, e:
		print e
		sock.send("1111".encode())
		sock.send("9".encode())
		break

cv2.destroyAllWindows()
cap.release()
sock.close()
