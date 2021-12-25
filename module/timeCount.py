#-*- coding : utf-8 -*-
import time
import datetime
import threading
from math import floor
from tkinter import Toplevel,Label,StringVar
from . import core
from .common import funcs

initArg = [ "entryXPos","entryYPos","entryHeight","entryWidth" ]
keywords = {"cd","tc","ck"}
describe = "计时、倒计时、时钟"

xPos = 0
yPos = 0
width = 550

def init(arg):
	global xPos,yPos,width
	xPos = arg[0]
	yPos = arg[1] + arg[2] + 10
	width = arg[3]

def resolve(line):
	arg,argLen = core.getArgList(line)
	TimeCount(xPos,yPos,width).showWindow(arg,argLen)

class TimeCount:
	def __init__(self,x,y,w):
		self.window = ""
		self.xPos = x - 7
		self.yPos = y
		self.width = w - 2
		self.height = 100
		self.type = ""
		self.bh = 0
		self.bm = 0
		self.bs = 0
		self.bt = ""
		self.hour = 0
		self.minuter = 0
		self.second = 0
		self.millisecond = 0
		self.exit = True
		self.id = round(time.time()*1000000)
		self.label = ""
		self.text = StringVar()
		self.startTime = 0
		self.ms = False
		self.stop = False
		self.top = False
		self.fs = False
		self.dst = ""
		self.dstType = ""
		self.times = ""
		print(f"ID:{self.id}")

	def getText(self):
		h = str(self.hour).zfill(2)
		m = str(self.minuter).zfill(2)
		s = str(self.second).zfill(2)
		if self.ms:
			ms = str(self.millisecond).zfill(3)
			return(f"{h}:{m}:{s}.{ms}")
		else:
			return(f"{h}:{m}:{s}")

	def updateCount(self):
		self.text.set(self.getText())

	def updateClock(self):
		if self.ms:
			self.text.set(datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3])
			time.sleep(0.05)
		else:
			self.text.set(datetime.datetime.now().strftime("%H:%M:%S"))
			time.sleep(1)

	def resetCount(self,event):
		if self.type == "ck":
			self.times = ""
			return
		if not self.exit:
			return
		self.millisecond = 0
		self.second = self.bs
		self.minuter = self.bm
		self.hour = self.bh
		self.type = self.bt
		self.label.config(fg = "black")
		self.updateCount()
		self.times = ""

	def closewindow(self):
		print(f"关闭窗口:{self.id}")
		self.exit = True
		self.window.destroy()

	def minCount(self,type):
		if type == "ms":
			if self.second <= 0 and not self.minCount("s"):
				return False
			self.second -= 1
			self.millisecond += 1000
		elif type == "s":
			if self.minuter <= 0 and not self.minCount("m"):
				return False
			self.minuter -= 1
			self.second += 60
		elif type == "m":
			if self.hour <= 0:
				return False
			self.hour -= 1
			self.minuter += 60
		return True

	def reverseCount(self):
		self.label.config(fg = "red")
		if self.stop:
			self.exit = True
		else:
			self.type = "tc"
	
	def addCount(self,type,count):
		if type == "ms":	
			self.millisecond += count
			if self.millisecond >= 1000:
				self.millisecond -= 1000
				self.addCount("s",1)
		elif type == "s":
			self.second += count
			if self.second >= 60:
				self.second = 0
				self.addCount("m",1)
		elif type == "m":
			self.minuter += 1
			if self.minuter >= 60:
				self.minuter = 0
				self.hour += 1

	def secondCount(self):
		time.sleep(1)
		if self.exit:
			return False
		if self.type == "tc":
			self.addCount("s",1)
		else:
			self.second -= 1
			if self.second <= 0 and not self.minCount("s"):
				self.second = 0
				self.reverseCount()
				return True
		return False

	def msecondCount(self):
		if self.startTime == 0:
			self.startTime = round(time.time()*1000)
		time.sleep(0.05)
		if self.exit:
			return False
		endTime = round(time.time()*1000)
		c = endTime - self.startTime
		self.startTime = endTime
		if self.type == "tc":
			self.addCount("ms",c)
		else:
			self.millisecond -= c
			if self.millisecond < 0 and not self.minCount("ms"):
				self.millisecond = 0
				self.reverseCount()
				return True
		return False

	def func(self):
		while True:
			if self.type == "ck":
				self.updateClock()
			else:
				if self.ms:	
					s = self.msecondCount()	
				else:
					s = self.secondCount()
				self.updateCount()
				if s and self.dst:
					[ core.runCommand(f"start \"\" \"{d}\"",True) for d in self.dst ]
			if self.exit:
				print(f"结束计时线程 :{self.id}")
				return

	def startCount(self,event = None):
		if self.exit:
			self.exit = False
			self.startTime = 0
			threading.Thread(target = self.func).start()
		else:
			self.exit = True

	def getArg(self,arg):
		for a in arg:
			if a == "fs":
				self.fs = True
			elif a == "m":
				self.ms = True
			elif a == "st":
				self.stop = True
			elif a == "tp":
				self.top=True
			else:
				self.dst = core.getInputPath(a)

	def resizeWindow(self,event):
		if self.width != self.window.winfo_width() or self.height != self.window.winfo_height():
			if self.width != self.window.winfo_width():
				self.width = self.window.winfo_width()
			if self.height != self.window.winfo_height():
				self.height = self.window.winfo_height()
			self.label.place(width = self.width , height = self.height )
			self.label.config(font = ("宋体", floor(self.width/10)))

	def fullscreen(self,event = None):
		if self.window.attributes("-fullscreen"):
			self.window.attributes("-fullscreen",0)
		else:
			self.window.attributes("-fullscreen",1)
			self.window.focus()

	def copyTime(self,event):
		if self.type == "ck":
			if self.ms:
				self.times += datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]+"\n"
			else:
				self.times += datetime.datetime.now().strftime("%H:%M:%S")+"\n"
		else:
			self.times += f"{self.getText()}\n"
		core.appedClipboardText(self.times)

	def showWindow(self,arg,argLen):
		if arg[0] == "cd":
			if argLen == 1:
				print("缺少参数")
				return
			self.getArg(arg[2:])
			seconds = funcs.getSeconds(arg[1])
			if seconds == -1:
				return
			self.hour,self.minuter,self.second = funcs.getHMS(seconds)
			self.bh = self.hour
			self.bm = self.minuter
			self.bs = self.second
		else:
			self.getArg(arg[1:])
		
		self.type = arg[0]
		self.bt = arg[0]
		self.window = Toplevel()
		if self.top:
			self.window.attributes("-toolwindow",1)
			self.window.wm_attributes("-topmost",1)
		if self.type == "cd":
			self.window.title("倒计时: " + " ".join(arg[1:]))
		elif self.type == "tc":
			if argLen == 1:
				self.window.title("计时器")
			else:
				self.window.title("计时器: " + " ".join(arg[1:]))
		else:
			self.window.title("时钟")
		self.window.geometry(f"{self.width}x{self.height}+{self.xPos}+{self.yPos}")
		self.window.protocol("WM_DELETE_WINDOW",self.closewindow)
		self.window.bind("<Configure>",self.resizeWindow)
		self.window.bind("<space>",self.startCount)
		self.window.bind("<Return>",self.fullscreen)
		self.window.bind("<ButtonRelease-3>",self.startCount)
		self.window.bind("<+>",self.copyTime)
		self.window.bind("<Escape>",self.resetCount)
		self.window.bind("<Double-Button-1>",self.resetCount)
		self.label = Label(self.window,textvariable = self.text, justify = 'center' , font = ("宋体",floor(self.width/10)))
		self.label.place(width = self.width , height = self.height,anchor="nw")
		if self.fs:
			self.fullscreen()
		if arg[0] == "ck":
			self.startCount()
		else:
			self.updateCount()
		
