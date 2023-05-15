#-*- coding : utf-8 -*-
import time
import datetime
from math import floor
from tkinter import Toplevel,Label,StringVar
from ..core import core

commands = {"cd","tc","ck"}
describe = "计时、倒计时、时钟"

main = ""
xPos = 0
yPos = 0
width = 550
config = ""

def init(arg):
	global main,xPos,yPos,width,config
	main = arg
	xPos = arg.entryXPos
	yPos = arg.yPos
	width = arg.entryWidth
	config = core.splitDict(core.loadDict("module\\timeCount\\config.txt"))

def resolve(line,isReturn):
	global config
	arg,argLen = core.getArgList(line)
	if argLen == 2 and arg[1] == "r":
		config = core.splitDict(core.loadDict("module\\timeCount\\config.txt"))
		return
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
		self.id = round(time.time()*1000000)
		self.label = ""
		self.text = StringVar()
		self.startTime = 0
		self.ms = False
		self.stop = False
		self.top = False
		self.loop = False
		self.fs = False
		self.command = []
		self.times = ""
		self.running = False
		self.timer = ""
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
		else:
			self.text.set(datetime.datetime.now().strftime("%H:%M:%S"))

	def resetCount(self,event,auto = False):
		if self.type == "ck":
			self.times = ""
			return
		if not auto and self.running:
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
		if self.running:
			self.window.after_cancel(self.timer)
		print(f"关闭窗口:{self.id}")
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
			self.running = False
		elif self.loop:
			self.resetCount(None,True)
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

	def ticktick(self):
		if self.type == "ck":
			self.updateClock()
		else:
			if self.ms:	
				s = self.msecondCount()	
			else:
				s = self.secondCount()
			self.updateCount()
			if s and self.command:
				main.runShortcutCmd(self.command)
				
		if self.running:
			if self.ms:
				self.timer = self.window.after(50,self.ticktick)
			else:
				self.timer = self.window.after(1000,self.ticktick)
		else:
			self.window.after_cancel(self.timer)
			
	def startCount(self,event = None):
		if self.running:
			print("停止计时")
			self.running = False
			self.window.after_cancel(self.timer)	
		else:
			print("开始计时")
			self.running = True
			if self.ms:
				self.timer = self.window.after(50,self.ticktick)
			else:
				self.timer = self.window.after(1000,self.ticktick)

	def getArg(self,arg):
		for a in arg:
			if a == "f":
				self.fs = True
			elif a == "m":
				self.ms = True
			elif a == "s":
				self.stop = True
			elif a == "l":
				self.loop = True
			elif a == "t":
				self.top = True
			else:
				if a in config:
					self.command.extend(config[a])

	def resizeWindow(self,event):
		if self.width != self.window.winfo_width() or self.height != self.window.winfo_height():
			if self.width != self.window.winfo_width():
				self.width = self.window.winfo_width()
			if self.height != self.window.winfo_height():
				self.height = self.window.winfo_height()
			self.label.place(width = self.width , height = self.height )
			self.label.config(font = ("French Script MT", floor(self.width/8)))

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
			seconds = core.getSeconds(arg[1])
			if seconds == -1:
				return
			m,s = divmod(seconds,60)
			h,m = divmod(m,60)
			self.hour = h
			self.minuter = m
			self.second = s
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
		self.label = Label(self.window,textvariable = self.text, bg = "#F4F4F4", fg = "#363636", justify = 'center' , font = ("French Script MT",floor(self.width/7)))
		self.label.place(width = self.width , height = self.height,anchor="nw")
		if self.fs:
			self.fullscreen()
		self.running = False
		if arg[0] == "ck":
			self.updateClock()
			self.startCount()
		else:
			self.updateCount()
		
