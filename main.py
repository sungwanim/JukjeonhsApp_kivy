from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
import requests
import time
import olefile
from pdf2image import convert_from_bytes
import numpy as np
from PIL import Image as img

import kivy

kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.screenmanager import TransitionBase
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

# 스크린 매니저 생성
sm = ScreenManager()

API_KEY = "73977e5306894980844a1b64e662b879"
mealdate = ""
fontName = "NanumGothic.ttf"
answer = ''

# 처음 화면
class FirstScreen(Screen):
	def __init__(self, **kwargs):
		super(FirstScreen, self).__init__(**kwargs)
		layout = BoxLayout(orientation='vertical')
		button1 = Button(text='급식', font_name=fontName)
		button2 = Button(text='시간표', font_name=fontName)
		button3 = Button(text='지필 정답', font_name=fontName)

		layout.add_widget(button1)
		layout.add_widget(button2)
		layout.add_widget(button3)

		self.add_widget(layout)

		button1.bind(on_release=self.btn_meal)
		button2.bind(on_release=self.btn_schedule)
		button3.bind(on_release=self.btn_answer)

	def btn_meal(self, *args):
		self.manager.current = 'date'
	def btn_schedule(self, *args):
		print('btn_schedule')
	def btn_answer(self, *args):
		self.manager.current = 'answer'

# 날짜 선택	
class DateScreen(Screen):

	def __init__(self, **kwargs):
		super(DateScreen, self).__init__(**kwargs)
		layout = BoxLayout(orientation='horizontal')
		# 레이아웃 가로배치
		layout2 = BoxLayout(orientation='vertical')
		# 레이아웃 속 레이아웃(세로)
		put1 = TextInput(hint_text='년 (ex: 2020)', font_name=fontName)
		put2 = TextInput(hint_text='월', font_name=fontName)
		put3 = TextInput(hint_text='일', font_name=fontName)
		layout2.add_widget(put1)
		layout2.add_widget(put2)
		layout2.add_widget(put3)

		button1 = Button(text='오늘', font_name=fontName)
		button2 = Button(text='내일', font_name=fontName)
		button3 = Button(text='위 날짜로 입력', font_name=fontName)
		backbtn = Button(text='뒤로가기', font_name=fontName)
		button1.bind(on_release=self.btn_today)
		button2.bind(on_release=self.btn_tomorrow)
		button3.bind(on_release=lambda *args: self.btn_submit(put1.text, put2.text, put3.text, *args))
		backbtn.bind(on_release=self.btn_back)
		# 버튼을 눌렀을때 동작하는 함수 설정

		layout2.add_widget(button3)
		layout2.add_widget(backbtn)
		layout.add_widget(button1)
		layout.add_widget(button2)

		layout.add_widget(layout2)
		# 속의 레이아웃을 겉의 레이아웃에 추가
		self.add_widget(layout)
		# 창에 레이아웃 추가
	def btn_today(self, *args):
		global mealdate
		mealdate = time.strftime('%Y%m%d', time.localtime(time.time()))
		sm.add_widget(MealScreen(name='meal'))
		self.manager.current = 'meal'
	def btn_tomorrow(self, *args):
		global mealdate
		numberdate = int(time.strftime('%Y%m%d', time.localtime(time.time()))) + 1
		sm.add_widget(MealScreen(name='meal'))
		mealdate = str(numberdate)
		self.manager.current = 'meal'
	def btn_submit(self, put1, put2, put3, *args):
		global mealdate
		sm.add_widget(MealScreen(name='meal'))
		mealdate = put1 + put2 + put3
		self.manager.current = 'meal'
	def btn_back(self, *args):
		self.manager.current = 'first'

class MealScreen(Screen):
	def __init__(self, **kwargs):
		super(MealScreen, self).__init__(**kwargs)	
		def meal_enter(self):
			URL = "https://open.neis.go.kr/hub/mealServiceDietInfo?KEY="+API_KEY+"&Type=xml&ATPT_OFCDC_SC_CODE=J10&SD_SCHUL_CODE=7530525&MLSV_YMD="+mealdate
			res = requests.get(URL)
			root = ET.ElementTree(ET.fromstring(res.text)).getroot()
			self.label = Label()

			# 해당 날짜에 급식이 없을때 받는 응답:
			# <RESULT>
			# 	<CODE>INFO-200</CODE>
			# 	<MESSAGE>해당하는 데이터가 없습니다.</MESSAGE>
			# </RESULT> 
			
			if root.find("MESSAGE") != None:
				self.label = Label(text="해당 날짜에 데이터가 없습니다", font_name=fontName)

			# 해당 날짜에 급식 있을때 받는 응답
			# <mealServiceDietInfo>
  	# 			<row>
  	#   			<DDISH_NM><![CDATA[j통새우튀김오므라이스1.2.5.6.9.10.12.13.15.16.<br/>j미소된장국5.6.8.9.13.<br/>j오이깍둑무침5.6.13.<br/>j파닭꼬치5.6.13.15.<br/>j깍두기9.13.<br/>j미니사과]]></DDISH_NM>
  	# 			</row>
			# </mealServiceDietInfo>

			else:
 				meallist = root.find("row").find("DDISH_NM").text.split("<br/>")
 				# <br/>를 기준으로 문자열을 나눠서 각각 급식을 리스트에 넣음
 				labeltext = ""
 				for i in meallist:
 					labeltext += i+"\n"
 				self.label = Label(text=labeltext,font_name=fontName)

			self.backbutton = Button(text='Back', size_hint=(.25,.1))
			self.backbutton.bind(on_release=self.btn_back)
			self.add_widget(self.label)
			self.add_widget(self.backbutton)
		self.bind(on_enter=meal_enter)
	def btn_back(self, *args):
		sm.switch_to(DateScreen(name='date'))
		# 현재 스크린을 삭제하면서 이동

class AnswerScreen(Screen):
	def __init__(self, **kwargs):
		super(AnswerScreen, self).__init__(**kwargs)
		layout = BoxLayout(orientation='vertical')
		grade = TextInput(hint_text='ex) 1', size_hint=(1, 0.5))
		semester = TextInput(hint_text='ex) 1', size_hint=(1, 0.5))
		num = TextInput(hint_text='ex) 1', size_hint=(1, 0.5))
		sub = TextInput(hint_text='ex)통합과학(띄어쓰기하고 결과없을시 띄어쓰기없이)', font_name=fontName)
		btn = Button(text='제출', font_name=fontName)
		backbtn = Button(text='뒤로가기', font_name=fontName)
		
		layout.add_widget(Label(text='최근 지필 평가 정답을 보여줍니다. ', font_name=fontName, font_size=24))
		layout.add_widget(Label(text='학년과 학기, 과목, 몇차 지필평가인지를 정확히 입력해주세요. ', font_name=fontName, font_size=24))
		layout.add_widget(Label(text='학년:', font_name=fontName))
		layout.add_widget(grade)
		layout.add_widget(Label(text='학기:', font_name=fontName))
		layout.add_widget(semester)
		layout.add_widget(Label(text='몇차 지필평가:', font_name=fontName))
		layout.add_widget(num)
		layout.add_widget(Label(text='과목:', font_name=fontName))
		layout.add_widget(sub)
		layout.add_widget(btn)
		layout.add_widget(backbtn)
		
		btn.bind(on_release=lambda *args: self.btn_release(grade.text, semester.text, num.text, sub.text, *args))
		backbtn.bind(on_release=self.btn_back)
		self.add_widget(layout)
	def btn_back(self, *args):
		self.manager.current = 'first'

	def btn_release(self, grade, sem, num, sub, *args):
		def answer_page(href):
			global answer
			URL = "http://jukjeon.hs.kr"+href
			bs = BeautifulSoup(requests.get(URL).text, 'html.parser')
			hwp = ''
			for i in bs.findAll("a"):
				if sem+"학기" in i.attrs['href'] and num+"차" in i.attrs['href'] and sub in i.attrs['href']:
					hwp = i.attrs['href']
			URL = "http://jukjeon.hs.kr"+hwp
			res = requests.get(URL, allow_redirects=True)
			if ".pdf" in hwp:
				answer = convert_from_bytes(res.content)
				sm.add_widget(PrintanswerScreen(name='panswer'))
				self.manager.current = 'panswer'
			if ".hwp" in hwp:
				ole = olefile.OleFileIO(res.content)
				txt = ole.openstream('PrvText').read()
				answer = txt.decode('UTF-16').replace("\r", "")
				sm.add_widget(PrintanswerScreen(name='panswer'))
				self.manager.current = 'panswer'

		if grade == '1':
			URL = "http://jukjeon.hs.kr/board.list?mcode=151410&cate=151410"
			# 1학년 지필평가 정답 URL
			bs = BeautifulSoup(requests.get(URL).text, 'html.parser')
			href = ''
			for i in bs.findAll("a"):
				if 'title' in i.attrs:
					if sem != '' or num != '' or sub != '':
						if sem+"학기" in i.attrs['title'] and num+"차" in i.attrs['title'] and sub in i.attrs['title']:
							href = i.attrs['href']
			answer_page(href)

		if grade == '2':
			URL = "http://jukjeon.hs.kr/board.list?mcode=151411&cate=151411"
			# 2학년 지필평가 정답 URL
			bs = BeautifulSoup(requests.get(URL).text, 'html.parser')
			href = ''
			for i in bs.findAll("a"):
				if 'title' in i.attrs:
					if sem != '' or num != '' or sub != '':
						if sem+"학기" in i.attrs['title'] and num+"차" in i.attrs['title'] and sub in i.attrs['title']:
							href = i.attrs['href']
			answer_page(href)

		if grade == '3':
			URL = "http://jukjeon.hs.kr/board.list?mcode=151411&cate=151412"
			URL2 = "http://jukjeon.hs.kr/board.list?mcode=151412&cate=151412&page=2"
			# 3학년 지필평가 정답 URL
			bs = BeautifulSoup(requests.get(URL).text, 'html.parser')
			mybs = BeautifulSoup(requests.get(URL2).text, 'html.parser')
			href = ''
			for i in bs.findAll("a")+mybs.findAll("a"):
				if 'title' in i.attrs:
					if sem != '' or num != '' or sub != '':
						if sem+"학기" in i.attrs['title'] and num+"차" in i.attrs['title'] and sub in i.attrs['title']:
							href = i.attrs['href']
			answer_page(href)

class PrintanswerScreen(Screen):
	def __init__(self, **kwargs):
		super(PrintanswerScreen, self).__init__(**kwargs)
		def print_enter(self):
			global answer
			if type(answer) == type(""):
				self.add_widget(Label(text=answer, font_name=fontName))

			else:

				answernp = np.array(answer[0].transpose(img.FLIP_TOP_BOTTOM))
				print(answernp)

				# cv2.imshow('Answer', answer[0])
				texture = Texture.create(size=(answernp.shape[1], answernp.shape[0]), colorfmt='bgr')
				texture.blit_buffer(answernp.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
				self.add_widget(Image(texture=texture))
		self.bind(on_enter=print_enter)
# 스크린매니저에 스크린들 등록

sm.add_widget(FirstScreen(name='first'))
sm.add_widget(DateScreen(name='date'))
sm.add_widget(AnswerScreen(name='answer'))

class JHApp(App):	
	def build(self):
		return sm

if __name__ == '__main__':
	JHApp().run()