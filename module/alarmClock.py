#-*- coding : utf-8 -*-
import os
import time
import datetime
import threading
import subprocess
from tkinter import Toplevel,Label,StringVar
from PIL import Image as PILImage, ImageTk
from . import core

initArg = [ "entryXPos","entryYPos","entryHeight","entryWidth" ]
keywords = {"ac"}
describe = "闹钟"

window = ""
windowWidth = 550
windowHeight = 550
xPos = 0
yPos = 0

labelX = 10
labelWidth = 0
labelHeight = 60
timeY = 10
msgY = timeY + labelHeight + 10
imgY = msgY + labelHeight + 10
imgWidth = 0

textBg = ""
timeText = StringVar()
msgText = StringVar()

img = ""
imgLabel = ""
imgBg = ""

hide = False
clock = list()
autoStart = False
loop = False
exit = True
process = ""
index = -1
today = 0
weekday = "0"

def init(arg):
	global xPos,yPos,windowWidth,windowHeight,labelWidth,imgWidth
	xPos = arg[0]
	yPos = arg[1] + arg[2] + 10
	windowWidth = arg[3]
	windowHeight = windowWidth + 140
	labelWidth = windowWidth - 20
	imgWidth = windowWidth - 40
	loadClock(True)

def resolve(line):
	global exit
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		if exit:
			return core.setEntry("闹钟未启动")
		else:
			return core.setEntry(f"下一个闹钟: {today} {clock[index][1].strip()} {weekday}")		
	if arg[1] == "l":
		printAllClock()
	elif arg[1] == "r":
		if exit:
			loadClock(True)
		else:
			return core.setEntry("闹钟正在运行")
	elif arg[1] =="on": 
		return startCount()
	elif arg[1] =="off": 
		return stopCount()
	else:
		return core.setEntry(f"参数错误:{arg[1]}")
	
def printAllClock():
	global clock
	for c in clock:
		core.printValue(c[1].strip(),c[2:])

def printClock(isNext):
	global today,clock,index,weekday
	if isNext:
		print("下一个闹钟: ",end = "")
	else:
		print("当前闹钟: ",end = "")
	print(f"{today} {clock[index][1].strip()} {weekday}")

def loadClock(isToday):
	global today,clock,exit,weekday,autoStart,loop
	clock.clear()
	today = datetime.date.today() if isToday else today + datetime.timedelta(days = 1)
	weekday = str(today.isoweekday())
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
						autoStart = True
				elif t == "loop":
					if tmp[1].strip() == "true":
						loop = True
				elif t == "on":
					if len(tmp) < 7:
						print(f"参数错误:{line}")
						continue
					if tmp[2].find(weekday) == -1:
						continue
					try :
						tmp[0] = int(time.mktime( time.strptime(f"{today} {tmp[1].strip()}","%Y-%m-%d %H:%M:%S") ))
					except:
						print(f"时间错误:{tmp[1]}")
						continue
					clock.append(tmp)
			file.close()
			clock.sort(key = lambda x:x[0])
			if autoStart and exit:
				startCount()		
	except:
		print("读取列表错误")

def updateText(t,m):
	global timeText,msgText
	timeText.set(t.strip())
	if m.strip() == "None":
		msgText.set("")
	else:
		msgText.set(m.strip())

def killProcess():
	global process
	if process:
		process.kill()
		process.wait()
		process = ""

def closewindow(event = None):
	global exit,window,hide
	if exit:
		if window :
			window.destroy()
		window = ""
		hide = False
	else:
		window.withdraw()
		hide = True
	killProcess()

def getPath(arg,type):
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
			
def showWindow(arg):
	global window,textBg,imgBg,imgLabel,img
	if not window:
		window = Toplevel()
		window.attributes("-toolwindow",1)
		window.wm_attributes("-topmost",1)
		window.overrideredirect(True)
		window.geometry(f"{windowWidth}x{windowHeight}+{xPos}+{yPos}")

		textBg = ImageTk.PhotoImage(PILImage.open(f"module\\alarmClock\\textbg.png"))
		imgBg = ImageTk.PhotoImage(PILImage.open(f"module\\alarmClock\\imgbg.png"))

		timebg = Label(window,image = textBg)
		msgbg = Label(window,image = textBg)
		imgbg = Label(window,image = imgBg)

		timeLabel = Label(window,textvariable = timeText, bg = "white",font = ("Microsoft YaHei Light", 40))
		msgLabel = Label(window,textvariable = msgText, bg = "white", font = ("Microsoft YaHei Light", 30))
		imgLabel = Label(window)

		timebg.place(x = 0,y = timeY,width = windowWidth , height = labelHeight + 9)
		timeLabel.place(x = labelX,y = timeY,width = labelWidth , height = labelHeight)

		msgbg.place(x = 0,y = msgY,width = windowWidth , height = labelHeight + 9)
		msgLabel.place(x = labelX,y = msgY,width = labelWidth , height = labelHeight)
		
		imgbg.place(x = 0,y = imgY,width = windowWidth , height = windowWidth)
		imgLabel.place(x = labelX + 10,y = imgY + 10,width = imgWidth , height = imgWidth)

		window.bind("<Double-Button-1>",closewindow)
	else:
		if hide:
			window.update()
			window.deiconify()
	
	updateText(arg[1],arg[3])
	imgPath = getPath(arg[4],"img")
	try:
		i = PILImage.open(imgPath)
		if i.width != imgWidth or i.height != imgWidth:
			print("resize img")
			i = i.resize((imgWidth,imgWidth),PILImage.ANTIALIAS)
		img = ImageTk.PhotoImage(i)
		imgLabel.config(image = img)
	except:
		print("读取图片错误")

def playSound(arg):
	global process
	sound = getPath(arg,"sound")
	if sound == "None":
		return
	killProcess()
	process = subprocess.Popen(f"\"{os.path.dirname(__file__)}\\mpg123\\mpg123.exe\" --loop 5 \"{sound}\"",stdout = subprocess.PIPE,stderr = subprocess.STDOUT)

def openPath(arg):
	file = getPath(arg,"file")
	if file == "None":
		return
	core.runCommand(f"start \"\" \"{file}\"")

def func(now):
	global exit,clock,index,loop
	print("启动闹钟线程")
	exit = False
	printClock(True)
	while True:
		time.sleep(1)
		now += 1
		if now >= clock[index][0]:
			printClock(False)
			showWindow(clock[index])
			playSound(clock[index][5])
			openPath(clock[index][6])
			index += 1
			if index >= len(clock):
				if loop:
					index = 0
					while True:
						print("重新计时")
						loadClock(False)
						if clock:
							break
						else:
							time.sleep(1)
					now = int(time.time())
					printClock(True)
				else:
					exit = True
					print("全部闹钟已结束")
			else:
				printClock(True)
		if exit:
			print(f"退出闹钟线程")
			return

def startCount():
	global exit,clock,index
	if not exit:
		return core.setEntry("闹钟已启动")
	if not clock:
		return core.setEntry("无闹钟")
	now = int(time.time())
	index = -1
	for i in range(len(clock)):
		if now > clock[i][0]:
			continue
		else:
			index = i
			break
	if index == -1:
		return core.setEntry("无可用闹钟")
	threading.Thread(target = func,args = (now,)).start()

def stopCount():
	global exit
	if exit:
		return core.setEntry("闹钟已停止")
	else:
		exit = True
		closewindow()


