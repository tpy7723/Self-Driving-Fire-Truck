#-*- coding: utf-8 -*-
from __future__ import division # Free Division
import PCA9685 #PWM Driver
import Servo #PWM Driver - Servo
import TB6612 #Motor Driver - DC
import socket, threading, time, sys, os
from RPi import GPIO
import requests



def _set_right_pwm(value): # 우측 모터 pwm 셋팅 
        pulse_wide = pwm.map(value, 0, 100, 0, 4095)
        pwm.write(PWM_right_motor, 0, pulse_wide)

def _set_left_pwm(value): # 좌측 모터 pwm 셋팅
        pulse_wide = pwm.map(value, 0, 100, 0, 4095)
        pwm.write(PWM_left_motor, 0, pulse_wide)

def forward(speed): # 전진 # 기본 속도 설정
        left_wheel.forward()
        left_wheel.speed = speed
        right_wheel.forward()
        right_wheel.speed = speed

def turn_left(angle): # 좌회전
        front_wheel.write(90-angle)

def turn_straight(): # 앞방향
        front_wheel.write(90)

def turn_right(angle): # 우회전
        front_wheel.write(90+angle)


ip = '192.168.43.134'
pwm=PCA9685.PWM(bus_number=1, address=0x40)	#PCA_9685 address
pwm.setup()
pwm.frequency = 60 # picar.setup() # pwm = 60으로 설정

right_motor = 17 # right back gpio
left_motor = 27 # left back gpio

PWM_right_motor = 4 # right back
PWM_left_motor = 5 # left back

left_wheel = TB6612.Motor(left_motor, offset=0)
right_wheel = TB6612.Motor(right_motor, offset=0)

left_wheel.pwm  = _set_right_pwm
right_wheel.pwm= _set_left_pwm

front_wheel = Servo.Servo(channel=0, bus_number=1, offset=-69)

CAR_CENTER = 320 # width / 2

Speed = 50
Def_speed = 50

Voice = True # 음성인식 초기 값
Obstacle = False  # ultra 장애물 초기 값
IsRed = False # 빨간 신호등 초기 값

GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT) # 펌프 모터

def function_line(): # 라인 따라가는 함수
	global CAR_CENTER, Obstacle, Speed, IsRed, x_point, Car_back, Voice
	while True:
    		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    		server_address = (ip, 3000)
    		print("line socket listening...")
	    	sock.bind(server_address)
   		sock.listen(1)
	        client, address = sock.accept()
        	print("Line Connected")

		while True:
	            	x_point = client.recv(4) # 차량 방향 제어
			num = client.recv(1)# 라인 개수

			if Voice == False or IsRed == True or Obstacle == True: # 멈춰 or 빨간불 or 장애물발견 시
				if Voice==False:
					print "Voice stop"
				forward(0)
			else:
     				x_point = int(x_point)
				num = int(num)

	       	                if x_point == 1111: # 연결 종료 신호
        	                	turn_straight()
					forward(0)
        	                        break

				elif num == 2: # 선이 2개 보일 때 ( 직진 )
       		                 	if CAR_CENTER - 20 <= x_point and x_point <= CAR_CENTER + 20: # 300~340 사이
	           	                        print "straight "
	                                        turn_straight()
	                                        forward(Speed)
					elif x_point < CAR_CENTER - 20: # 좌회전 # 300 미만
                                                print "left ", (10.5 - x_point / 30)
                                                turn_left(10.5 - x_point / 30)
                                                forward(Speed)
	                                elif CAR_CENTER + 20 < x_point: # 우회전 # 340 초과 
                                                print "right ", (x_point / 30) - 9.5
                                                turn_right((x_point / 30) - 9.5)
                                                forward(Speed)

				elif num == 1: # 선이 1개 보일 때 ( 커브 )	
		            		if CAR_CENTER - 20 <= x_point and x_point <= CAR_CENTER + 20: # 직
	        	        		print "straight "
	                			turn_straight()
	                			forward(Speed)
					elif CAR_CENTER - 150 <= x_point and x_point < CAR_CENTER - 20 : # 좌회전
	 					print "small left"
						turn_left(3)
						forward(Speed)
					elif CAR_CENTER + 20 < x_point and x_point <= CAR_CENTER + 150: # 우회전
						print "small right"
						turn_right(3)
						forward(Speed)
			  		elif x_point < CAR_CENTER - 150: # 좌회전
						turn_left(20 - x_point / 20)
						print "left ", (20-x_point/20)
	                       	       	 	forward(Speed)
	                       		elif CAR_CENTER + 150 < x_point: # 우회전
	                               		turn_right((x_point / 21) - 17.5)
						print "right ", (x_point / 21) - 17.5
	                                	forward(Speed)



				else: # 선이 안보일 때 ( 방향은 그대로 앞으로 간다 )
					forward(Speed)
		sock.close()


def function_Ultra(): # 초음파 센서 함수
	global Obstacle
	while True:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    		server_address = (ip, 4000)
    		print("Ultra socket listening...")
    		sock.bind(server_address)
    		sock.listen(1)
        	client, address = sock.accept()
        	print "Ultra connected"
		Ultra_temp = 1111 # 기본 값

        	while True:
			data = client.recv(4) # 측정 거리

             		if data == "exit": # 연결 종료 신호
                       		break
	     		elif data == "stop": # 물체가 특정 거리 안에 있을 경우 stop
                		print("stop")
                		speed = 0
				Obstacle = True
				if Ultra_temp != data: # 사운드를 한번만 나오게 설정
					os.system("mpg321 -o alsa stop.mp3")	# stop 사운드 출력

             		elif data == "gogo": # 물체가 특정 거리 보다 멀리 있을 경우 go
				print "go"
				Obstacle = False
				if Ultra_temp != data: # 사운드를 한번만 나오게 설정
					os.system("mpg321 -o alsa go.mp3")	# go 사운드 출력

	     		Ultra_temp = data # 측정 거리를 임시 저장
		sock.close()


def function_YOLO(): # 딥러닝 처리 함수 
	global Obstacle, Speed, Def_speed, IsRed, x_point, Car_back, Voice, Obstacle

	while True:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	    	server_address = (ip, 5000)
	    	print("YOLO socket listening...")
    	    	sock.bind(server_address)
	    	sock.listen(1)
	        client, address = sock.accept()
	        print("YOLO connected")
		isFire = False
	        while True:
		    	data = client.recv(4) # 딥 러닝 신호 ( 인식된 사물 결과 )
			if Voice == False or Obstacle == True:
				if Voice == False:
					print "Voice stop"
				forward(0)
	            	elif data == 'gogo': # 아무것도 없을 때
				print("GO")
				if isFire == True: # 불이 났다는 상태를 꺼졌다는 상태로 초기화
					requests.get('http://45.77.10.162:5000/fire/insert?fire=0') # 화재 상태 0
					requests.post("http://45.77.10.162:5000/fire") # 화재 상태 리셋
					isFire == False

				if Speed != Def_speed: # Def_speed 로 주행
					for i in range(Speed,Def_speed+1): # 부드럽게 속도 가속
						Speed = Def_speed
						time.sleep(0.02)

		    	elif data == 'stop': # 정지 신호
			    	print("STOP")
				if Speed != 0:
					for i in range(Speed,-1,-1): # 부드럽게 속도 감속
						Speed = i
						time.sleep(0.02)

		    	elif data == 'limi': # 감속 신호
			    	print("LIM")
				if Speed >= 50:
					for i in range(Speed,34,-1):
						Speed = i
						time.sleep(0.02)
				Def_speed = 40 # Def_speed 를 40으로 줄여준다.

                    	elif data == 'redd': # 빨간 불
                            	print("red")
				if Speed != 0:
					for i in range(Speed,-1,-1):
						Speed = i
						time.sleep(0.02)
				IsRed = True# 빨간 불 상태

                    	elif data == 'gree': # 초록 불
                            	print("green")
				if IsRed == True: # 빨간 불 다음에 초록 불이어야 출발
					IsRed = False # 빨간 불 상태 수정
					for i in range(Def_speed+1):
						Speed = i
						time.sleep(0.02)
				Def_speed = 80 # 50

                    	elif data == 'fire': # 화재
				isFire = True # 화재 상태

				requests.get('http://45.77.10.162:5000/fire/insert?fire=1') # 화재 상태 1
				requests.post("http://45.77.10.162:5000/fire") # 화재 상태 리셋

				client.send("next".encode())
				Bot_fire = client.recv(3) # 화재 아래의 좌표
				Bot_fire = int(Bot_fire)
				print " Bot_fire           ", Bot_fire
				if ((0 <= Bot_fire) and (Bot_fire <= 640)):
	                            	print("Fire!! : Car stop")
					Speed = 0
					GPIO.output(16,GPIO.HIGH) # 물 분사
					time.sleep(1)
					GPIO.output(16,GPIO.LOW) # 물 분사 중지
				elif Bot_fire < 0: # 감속
					Car_back =False
					print("Fire!! : Car slow")
					if Speed != 20:
						for i in range(Speed, 19, -1):
							Speed = i
							time.sleep(0.02)

                    	elif data == 'carr': # 자동차
				client.send("next".encode())
				Center_car = client.recv(3) # 자동차 하단의 좌표
				Center_car = int(Center_car)
                            	print("car")
				Speed = 30 # 차량 앞뒤 간격 유지를 위한 감속
				if (Center_car > 420): # 차량이 가까이 있을 시 정지
					Speed = 0

                            	
                    	elif data == 'huma': # 사람
				client.send("next".encode())
				Center_human = client.recv(3) # 사람 중심의 좌표
				Center_human = int(Center_human)
				x_point = int(x_point)
				print "center_human           "  ,Center_human
				print "x_point              ", x_point
				if ((int(x_point) - 200 < Center_human) and (Center_human < int(x_point) + 200)): # 라인 안의 사람 -> 정지
	                            	print("human in line")
					Speed = 0
				else: # 라인 바깥의 사람 -> 감속
					print("human outside of line")
					Speed = 20

		    	elif data == 'exit': # 연결 종료 신호
        	                turn_straight()
        	                Speed = 0
			    	break

		    	client.send("next".encode()) # 다음 내용을 보내라

		sock.close()

def function_VOICE():
	global Voice

	while True:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            	server_address = (ip, 6000)
            	print("VOICE socket listening...")
            	sock.bind(server_address)
            	sock.listen(1)
               	client, address = sock.accept()
               	print("VOICE connected")
		Voice = False # 연결 됐을 때 차량이 멈춤

		while True:
              		data = client.recv(20) # 음성인식 정보
	    		print "입력 받은 음성: " ,data

       			if data == '출발':
				print 'go'
				Voice = True # voice 상태 수정
				os.system("mpg321 -o alsa 출발했습니다.mp3") # 음성 출력
    			elif data == '멈춰':
				print 'stop'
				Voice = False # voice 상태 수정
				os.system("mpg321 -o alsa 멈췄습니다.mp3") # 음성 출력
    			elif data == 'exit': # 연결 종료 신호
				Voice = True # voice 상태 수정
				break
    		sock.close()

# 스레딩 방식
LINE = threading.Thread(target=function_line)
ULTRA = threading.Thread(target=function_Ultra)
YOLO = threading.Thread(target=function_YOLO)
VOICE = threading.Thread(target=function_VOICE)

LINE.start()
ULTRA.start()
YOLO.start()
VOICE.start()

LINE.join()
ULTRA.join()
YOLO.join()
VOICE.join()

GPIO.cleanup()
