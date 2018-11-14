#-*- coding: utf-8 -*-
import Ultrasonic_Avoidance
import time, socket

ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)  # GPIO 20

timeout = 10

ip = '192.168.43.134'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, 4000)
sock.connect(server_address)


try:
	while True:
		distance = ua.get_distance()
		if distance < 0:
			distance = 0
		elif distance > 100:
			distacne = 100

		print distance, "cm"

		if distance < 10:
			sock.send("stop".encode())
			time.sleep(0.0001)
		else:
			sock.send("gogo".encode())
			time.sleep(0.0001)

except KeyboardInterrupt:
	sock.send("exit".encode())
	sock.close()

except Exception, e:
	print e
	sock.send("exit".encode())
	sock.close()

finally:
	ua.clean_up()
