#-*- coding: utf-8 -*-

from flask import Flask, request
from tinydb import TinyDB, Query
import os

app = Flask(__name__)
global fire_data,gps_data,fire_DB,gps_DB

try:
        fire_DB = TinyDB('/root/fire_DB.json') # JSON 파일 생성
        gps_DB = TinyDB('/root/gps_DB.json')

        fire_DB.purge() # 초기화
        gps_DB.purge()
        fire_DB.insert({"fire":"0"}) # 추가
        gps_DB.insert({"lati":"0","longi":"0"})

except Exception,e:
        os.system("rm fire_DB.json") # 삭제
        fire_DB = TinyDB('/root/fire_DB.json')
        fire_DB.insert({"fire":"0"}) # 초기값

        os.system("rm gps_DB.json")
        gps_DB = TinyDB('/root/gps_DB.json')
        gps_DB.insert({"lati":"0","longi":"0"})

@app.route('/gps/insert', methods = ["POST","GET"])
def gps(): # 위도 경도 관련
        global gps_DB
        try:
            gps_DB.purge()
            lati = request.args.get("lati") # 값을 받아옴
            longi = request.args.get("longi")
            gps_DB.insert({"lati":lati,"longi":longi}) # 저장
        except Exception,e:
            os.system("rm gps_DB.json")
            gps_DB = TinyDB('/root/gps_DB.json')
            gps_DB.insert({"lati":"0","longi":"0"})
        return "gps success"

@app.route('/gps', methods = ["POST","GET"])
def background_gps():
        global gps_DB
        try:
            gps_data = str(gps_DB.all())
        except Exception,e:
            os.system("rm gps_DB.json")
            gps_DB = TinyDB('/root/gps_DB.json')
            gps_DB.insert({"lati":"0","longi":"0"})
            gps_data = str(gps_DB.all())
        return gps_data
@app.route('/fire/insert', methods = ["POST","GET"])
def fire(): # 화재유무 관련
        global fire_DB
        try:
            fire_DB.purge()
            fire = request.args.get("fire")
            fire_DB.insert({"fire":fire})
        except Exception, e:
            os.system("rm fire_DB.json")
            fire_DB = TinyDB('/root/fire_DB.json')
            fire_DB.insert({"fire":"0"})
        return "fire success"@app.route('/fire', methods = ["POST","GET"])
def background_fire():
        global fire_DB
        try:
            fire_data = str(fire_DB.all())
        except Exception, e:
            os.system("rm fire_DB.json")
            fire_DB = TinyDB('/root/fire_DB.json')
            fire_DB.insert({"fire":"0"})
            fire_data = str(fire_DB.all())
        return fire_data

if __name__ == '__main__':
        debug = True
        app.run(host='0.0.0.0',port=5000) # 모든 사용자 접근 가능, 포트 5000




