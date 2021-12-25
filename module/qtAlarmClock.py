#-*- coding : utf-8 -*-
import os
import sys
import time
import datetime
import threading
import subprocess
from PyQt5.QtWidgets import QApplication,QGraphicsDropShadowEffect,QWidget,QLabel
from PyQt5.QtCore import QEvent,Qt,pyqtSignal
from PyQt5.QtGui import QFont,QPixmap
from . import core

initArg = [ "entryXPos","entryYPos","entryWidth","entryHeight" ]
keywords = {"qac"}
describe = "qt界面的闹钟"

app = ""
win = ""
xPos = 0
yPos = 0
windowWidth = 0
windowHeight = 0


def init(arg):
	global xPos,yPos,windowWidth,windowHeight
	xPos = arg[0]
	yPos = arg[1] + arg[3] + 10
	windowWidth = arg[2]
	windowHeight = windowWidth + 140
	threading.Thread(target = qtThread).start()
	
def resolve(line):
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		if win.exit:
			return core.setEntry("闹钟未启动")
		else:
			return core.setEntry(f"下一个闹钟: {win.today} {win.clock[win.index][1].strip()} {win.weekday}")		
	if arg[1] == "l":
		win.printAllClock()
	elif arg[1] == "r":
		if win.exit:
			win.loadClock(True)
		else:
			return core.setEntry("闹钟正在运行")
	elif arg[1] =="on":
		win.startCount()
	elif arg[1] =="off": 
		win.stopCount()
	else:
		return core.setEntry(f"参数错误:{arg[1]}")

def qtThread():
	global app,win
	app = QApplication(sys.argv)
	win = window()
	win.setWindowFlags(Qt.FramelessWindowHint)
	win.move(xPos,yPos)
	win.resize(windowWidth,windowHeight)
	win.labelWidth = windowWidth - 20
	win.setLableSize()
	win.loadClock(True)
	app.exec_()

class window(QWidget):
	showSignal = pyqtSignal(list)
	def __init__(self):
		super().__init__()
		self.labelX = 10
		self.labelWidth = 620
		self.labelHeight = 60
		self.timeY = 10
		self.msgY = self.timeY + self.labelHeight + 10
		self.imgY = self.msgY + self.labelHeight + 10

		self.clock = list()
		self.autoStart = False
		self.loop = False
		self.exit = True
		self.process = ""
		self.index = -1
		self.today = 0
		self.weekday = "0"

		self.timeShadow = QGraphicsDropShadowEffect()
		self.timeShadow.setOffset(0.5,4)
		self.timeShadow.setBlurRadius(8)
		self.timeShadow.setColor(Qt.gray)
		self.timeText = QLabel(self,alignment = Qt.AlignCenter)
		self.timeText.setFont(QFont("Microsoft YaHei Light", 30))
		self.timeText.setText("18:00:00")
		self.timeText.setStyleSheet("color:white;border:5px solid white") 
		self.timeText.setGraphicsEffect(self.timeShadow)
		self.timeText.installEventFilter(self)

		self.msgShadow = QGraphicsDropShadowEffect()
		self.msgShadow.setOffset(0.5,4)
		self.msgShadow.setBlurRadius(8)
		self.msgShadow.setColor(Qt.gray)
		self.msgText = QLabel(self,alignment = Qt.AlignCenter)
		self.msgText.setFont(QFont("Microsoft YaHei Light", 30))
		self.msgText.setStyleSheet("color:white;border:5px solid white")
		self.msgText.setGraphicsEffect(self.msgShadow)
		self.msgText.installEventFilter(self)

		self.picShadow = QGraphicsDropShadowEffect()
		self.picShadow.setOffset(0.5,4)
		self.picShadow.setBlurRadius(8)
		self.picShadow.setColor(Qt.gray)
		self.picture = QLabel(self,alignment = Qt.AlignCenter)
		self.picture.setStyleSheet("color:white;border:5px solid white")
		self.picture.setGraphicsEffect(self.picShadow)
		self.picture.installEventFilter(self)
		self.picture.setScaledContents(True)
		self.showSignal.connect(self.showWindow)

	def setLableSize(self):
		self.timeText.setGeometry(self.labelX,self.timeY,self.labelWidth,self.labelHeight)
		self.msgText.setGeometry(self.labelX,self.msgY,self.labelWidth,self.labelHeight)
		self.picture.setGeometry(self.labelX,self.imgY,self.labelWidth,self.labelWidth)

	def eventFilter(self,object,event):
		if event.type() == QEvent.Enter:
			object.setStyleSheet("color:white;border:5px solid black")
		elif event.type() == QEvent.Leave:
			object.setStyleSheet("color:white;border:5px solid white")
		return False

	def mouseDoubleClickEvent(self,e):
		self.killProcess()
		self.hide()

	def printAllClock(self):
		for c in self.clock:
			core.printValue(c[1].strip(),c[2:])

	def printClock(self,isNext):
		if isNext:
			print("下一个闹钟: ",end = "")
		else:
			print("当前闹钟: ",end = "")
		print(f"{self.today} {self.clock[self.index][1].strip()} {self.weekday}")

	def loadClock(self,isToday):
		self.clock.clear()
		self.today = datetime.date.today() if isToday else self.today + datetime.timedelta(days = 1)
		self.weekday = str(self.today.isoweekday())
		try:
			with open("module\\alarmClock\\list.txt", 'r', encoding = 'utf-8', errors = 'ignore') as file:
				for line in file:
					line = line.strip()
					if not line:
						continue
					if line.startswith("#"): 
						continue
					tmp = line.split("#")
					t = tmp[0].strip()
					if t == "start":
						if tmp[1].strip() == "true":
							self.autoStart = True
					elif t == "loop":
						if tmp[1].strip() == "true":
							self.loop = True
					elif t == "on":
						if len(tmp) < 7:
							print(f"参数错误:{line}")
							continue
						if tmp[2].find(self.weekday) == -1:
							continue
						try :
							tmp[0] = int(time.mktime( time.strptime(f"{self.today} {tmp[1].strip()}","%Y-%m-%d %H:%M:%S") ))
						except:
							print(f"时间错误:{tmp[1]}")
							continue
						self.clock.append(tmp)
				file.close()
				self.clock.sort(key = lambda x:x[0])
				if self.autoStart and self.exit:
					self.startCount()		
		except:
			print("读取列表错误")

	def updateText(self,t,m):
		self.timeText.setText(t.strip())
		if m.strip() == "None":
			self.msgText.setText("")
		else:
			self.msgText.setText(m.strip())

	def showWindow(self,arg):
		self.updateText(arg[1],arg[3])
		imgPath = self.getPath(arg[4],"img")
		try:
			self.picture.setPixmap(QPixmap(imgPath))
		except:
			print("读取图片错误")
		self.show()


	def killProcess(self):
		if self.process:
			self.process.kill()
			self.process.wait()
			self.process = ""

	def getPath(self,arg,type):
		arg = arg.strip()
		if not arg or arg == "None":
			return "None"
		if arg.find("\\") != -1 or arg.find("/") != -1:
			return arg
		else:
			if type == "sound":
				return f"{os.path.dirname(__file__)}\\alarmClock\\{arg}"
			else:
				return f"module\\alarmClock\\{arg}"
				
	def playSound(self,arg):
		sound = self.getPath(arg,"sound")
		if sound == "None":
			return
		self.killProcess()
		self.process = subprocess.Popen(f"\"{os.path.dirname(__file__)}\\mpg123\\mpg123.exe\" --loop 5 \"{sound}\"",stdout = subprocess.PIPE,stderr = subprocess.STDOUT)

	def openPath(self,arg):
		file = self.getPath(arg,"file")
		if file == "None":
			return
		core.runCommand(f"start \"\" \"{file}\"")

	def func(self,now):
		print("启动闹钟线程")
		self.exit = False
		self.printClock(True)
		while True:
			time.sleep(1)
			now += 1
			if now >= self.clock[self.index][0]:
				self.printClock(False)
				self.showSignal.emit(self.clock[self.index])
				self.playSound(self.clock[self.index][5])
				self.openPath(self.clock[self.index][6])
				self.index += 1
				if self.index >= len(self.clock):
					if self.loop:
						self.index = 0
						while True:
							print("重新计时")
							self.loadClock(False)
							if self.clock:
								break
							else:
								time.sleep(1)
						now = int(time.time())
						self.printClock(True)
					else:
						self.exit = True
						print("全部闹钟已结束")
				else:
					self.printClock(True)
			if self.exit:
				print(f"退出闹钟线程")
				return

	def startCount(self):
		if not self.exit:
			return core.setEntry("闹钟已启动")
		if not self.clock:
			return core.setEntry("无闹钟")
		now = int(time.time())
		self.index = -1
		for i in range(len(self.clock)):
			if now > self.clock[i][0]:
				continue
			else:
				self.index = i
				break
		if self.index == -1:
			return core.setEntry("无可用闹钟")
		threading.Thread(target = self.func,args = (now,)).start()

	def stopCount(self):
		if self.exit:
			return core.setEntry("闹钟已停止")
		else:
			self.killProcess()
			self.exit = True
			self.hide()


