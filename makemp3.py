#-*- coding: utf-8 -*-
from gtts import gTTS


import os



def make(text):

	tts = gTTS(text, lang='ko')


	tts.save(text+".mp3")


	os.system("mpg321 "+text+".mp3")


#make(u"출발했습니다")
make(u"멈췄습니다")

