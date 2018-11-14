#-*- coding: utf-8 -*-
import socket

def get_box(path):
	f = open(path, "r")
	x = f.read()

	if x == '':
		x = '0 0 0 0'

	x = [int(x) for x in x.split(' ')]
	f.close()

	return [x[0],x[1],x[2],x[3]]


ip = '192.168.43.226'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, 5000)
sock.connect(server_address)
print("connected")

	# {label : [ 발견 횟수, 미발견 횟수]}
Check = {'stop':[0,0], 'limit':[0,0], 'fire':[0,0], 'car':[0,0], 'human':[0,0], 'red':[0,0], 'green':[0,0]}


while True:
	sock.send("7777".encode()) # 서버가 받길 기다리니까 먼저 보내줌
	try:

                stop_array = get_box("/home/pjm001/last/stop.txt") # stop
                limit_array  = get_box("/home/pjm001/last/limit.txt") # limit
		fire_array  = get_box("/home/pjm001/last/fire.txt")
		car_array  = get_box("/home/pjm001/last/car.txt")
		human_array  = get_box("/home/pjm001/last/human.txt")
		red_array  = get_box("/home/pjm001/last/red.txt")
		green_array  = get_box("/home/pjm001/last/green.txt")

#####################################################################
#''' 미발견 하였을 때 '''

		if stop_array[3] <= 240:
			Check["stop"][1] += 1
			Check["stop"][0] = 0 # 발견횟수 0
		if limit_array[3] <= 240:
			Check["limit"][1] += 1 
			Check["limit"][0] = 0 # 발견횟수 0
		if fire_array[3] <= 240:
			Check["fire"][1] += 1 
			Check["fire"][0] = 0 # 발견횟수 0
		if car_array[3] <= 240:
			Check["car"][1] += 1 
			Check["car"][0] = 0 # 발견횟수 0
		if human_array[3] <= 240:
			Check["human"][1] += 1 
			Check["human"][0] = 0 # 발견횟수 0
		if red_array == [0, 0, 0, 0]:
			Check["red"][1] += 1 
			Check["red"][0] = 0 # 발견횟수 0
		if green_array == [0, 0, 0, 0]:
			Check["green"][1] += 1 
			Check["green"][0] = 0 # 발견횟수 0

#####################################################################
#''' 발견 하였을 때'''

		if stop_array[3] > 240:
			Check["stop"][0] += 1
			Check["stop"][1] = 0 # 미발견횟수 0
        	if limit_array[3] > 240:
	                Check["limit"][0] += 1 
			Check["limit"][1] = 0 # 미발견횟수 0
        	if fire_array[3] > 240:
	                Check["fire"][0] += 1 
			Check["fire"][1] = 0 # 미발견횟수 0
        	if car_array[3] > 240:
	                Check["car"][0] += 1 
			Check["car"][1] = 0 # 미발견횟수 0
        	if human_array[3] > 240:
	                Check["human"][0] += 1 
			Check["human"][1] = 0 # 미발견횟수 0
		if red_array != [0, 0, 0, 0]:
			Check["red"][0] += 1 
			Check["red"][1] = 0 # 미발견횟수 0
		if green_array != [0, 0, 0, 0]:
			Check["green"][0] += 1 
			Check["green"][1] = 0 # 미발견횟수 0

######################################################################
#''' 발견 조건 (5회) 에 충족하였을 때 '''

		if Check["stop"][0] >= 5:
			print "stop"
			sock.recv(4)
			sock.send("stop".encode())
			Check["stop"][0] = 0 # 발견횟수 0
	        if Check["limit"][0] >= 5:
	                print "limit"
			sock.recv(4)
	                sock.send("limi".encode())
	                Check["limit"][0] = 0 # 발견횟수 0
	        if Check["fire"][0] >= 5:
	                print "fire"
			sock.recv(4)
	                sock.send("fire".encode())
	                Check["fire"][0] = 0 # 발견횟수 0
	        if Check["car"][0] >= 5:
	                print "car"
			sock.recv(4)
	                sock.send("carr".encode())
	                Check["car"][0] = 0 # 발견횟수 0
	        if Check["human"][0] >= 5:
	                print "human"
			sock.recv(4)
	                sock.send("huma".encode())
	                Check["human"][0] = 0 # 발견횟수 0
		if Check["red"][0] >= 5:
			print "red"
       	        	sock.recv(4)
	                sock.send("redd".encode())
			Check["red"][0] = 0 # 발견횟수 0
		if Check["green"][0] >= 5:
			print "green"
			sock.recv(4)
			sock.send("gree".encode())
			Check["green"][0] = 0 # 발견횟수 0

######################################################################
#''' 미발견 조건 (5회) 에 충족하였을 때 '''

		if (Check["stop"][1] >= 5 and Check["limit"][1] >= 5 and Check["fire"][1] >= 5 and \
		    Check["car"][1] >= 5 and Check["human"][1] >= 5 and Check["red"][1] >= 5 and Check["green"][1] >= 5):

			print "go"
			sock.recv(4)
			sock.send("gogo".encode())
			Check["stop"][1] = 0 # stop sign 미발견 횟수 초기화
			Check["limit"][1] = 0 # limit sign 미발견 횟수 초기화
			Check["fire"][1] = 0
			Check["car"][1] = 0
			Check["human"][1] = 0
			Check["red"][1] = 0 # red sign
			Check["green"][1] = 0
#######################################################################

		sock.recv(4)

	except KeyboardInterrupt:
		sock.send("exit".encode())
		exit(1)
	        break

sock.close()
