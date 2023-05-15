#-*- coding : utf-8 -*-
import time
import datetime
import threading
import subprocess
from tkinter import Toplevel,Label,StringVar
from PIL import Image as PILImage, ImageTk
from ..core import core

commands = {"ac"}
describe = "闹钟"

main = ""
window = ""
windowWidth = 550
windowHeight = 550

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
stop = True
process = ""
index = -1
today = 0
weekday = "0"
skipNext = False

def clear():
	global stop
	if not stop:
		stop = True
	closewindow()

def init(arg):
	global main,windowWidth,windowHeight,labelWidth,imgWidth
	main = arg
	windowWidth = arg.entryWidth
	windowHeight = windowWidth + 140
	labelWidth = windowWidth - 20
	imgWidth = windowWidth - 40
	loadClock()

def resolve(line,isReturn):
	global skipNext
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		if stop:
			main.setEntry("闹钟未启动")
		else:
			main.setEntry(f"下一个闹钟: {today} {clock[index]['time']} {weekday}")	
	elif arg[1] == "l":
		printAllClock()
	elif arg[1] == "r":
		if stop:
			loadClock()
		else:
			main.setEntry("闹钟正在运行")
	elif arg[1] == "d":
		core.runCommand("start \"\" \"module\\alarmClock\"")
	elif arg[1] == "ls":
		core.runCommand("start \"\" \"module\\alarmClock\\list.txt\"")
	elif arg[1] == "sn":
		skipNext = True
	elif arg[1] == "on": 
		startCount()
	elif arg[1] == "off": 
		stopCount()
	else:
		main.setEntry(f"参数错误:{arg[1]}")

def printAllClock():
	print("\n")
	for c in clock:
		for key,value in c.items():
			if key == "ex":
				for e in value:
					print(e)
			else:
				print(f"{key}:{value}")
		print("\n")

def printClock(isNext):
	if isNext:
		print("下一个闹钟: ",end = "")
	else:
		print("当前闹钟: ",end = "")
	print(f"{today} {clock[index]['time']} {weekday}")

def appendClock(key,value):
	tmp = dict()
	ex = list()
	tmp["time"] = key
	try :
		tmp["timeStamp"] = int(time.mktime( time.strptime(f"{today} {key.strip()}","%Y-%m-%d %H:%M:%S") ))
	except:
		print(f"时间错误:{tmp['time']}")
		return
	for v in value:
		if v[0] == "status":
			if v[1] != "on":
				return
		elif v[0] == "alarm":
			tmp["alarm"] = v[1]
		elif v[0] == "day":
			tmp["day"] = v[1]
		elif v[0] == "msg":
			tmp["msg"] = v[1]
		elif v[0] == "pic":
			tmp["pic"] = v[1]
		elif v[0] == "ring":
			tmp["ring"] = v[1]
		else:
			ex.append(v)
	tmp["ex"] = ex
	return tmp

def loadClock():
	global today,clock,weekday,autoStart,loop
	clock.clear()
	today = datetime.date.today()
	weekday = str(today.isoweekday())
	data = core.splitDict(core.loadDict("module\\alarmClock\\list.txt"))
	for key,value in data.items():
		if key == "config":
			for v in value:
				if v[0] == "start":
					autoStart = True if v[1] == "True" else False
				elif v[0] == "loop":
					loop = True if v[1] == "True" else False
			continue
		tmp = appendClock(key,value)
		if tmp:
			clock.append(tmp)
	clock.sort(key = lambda x:x["timeStamp"])
	if autoStart:
		startCount()

def playSound(arg):
	global process
	sound = getPath(arg,"sound")
	if sound == "None":
		return
	killProcess()
	process = subprocess.Popen(f"\"{core.selfPath}\\module\\alarmClock\\mpg123\\mpg123.exe\" --loop 5 \"{sound}\"",stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
	
def selectClock(now = None):
	global index,today,weekday
	count = 0
	while True:
		index += 1
		if index >= len(clock):
			if not loop:
				return False
			for v in clock:
				v["timeStamp"] += 86400
			today = today + datetime.timedelta(days = 1)
			weekday = str(today.isoweekday())
			index = -1
			count += 1
			if count >= 8:
				return False
			continue
		if now:
			if now > clock[index]["timeStamp"]:
				continue
		if weekday in clock[index]["day"]:
			printClock(True)
			return True

def ticktick():
	global stop,index,skipNext
	print("启动闹钟线程")
	index = -1
	stop = False
	now = int(time.time())
	if not selectClock(now):
		stop = True
		return main.setEntry("无可用闹钟")
	while True:
		time.sleep(1)
		now += 1
		if now >= clock[index]["timeStamp"]:
			printClock(False)
			if skipNext:
				skipNext = False
			else:
				if clock[index]["alarm"] == "True":
					showWindow(clock[index])
					playSound(clock[index]["ring"])
				main.runShortcutCmd(clock[index]["ex"])
				now = int(time.time())
			if not selectClock():
				stop = True
		if stop:
			print(f"退出闹钟线程")
			return

def startCount():
	if not stop:
		return main.setEntry("闹钟已启动")
	if not clock:
		return main.setEntry("无闹钟")
	threading.Thread(target = ticktick).start()

def stopCount():
	global stop
	if stop:
		main.setEntry("闹钟已停止")
	else:
		stop = True
		closewindow()

def updateText(t,m):
	global timeText,msgText
	timeText.set(t)
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
	global stop,window,hide
	if stop:
		if window :
			window.destroy()
		window = ""
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
			return f"{core.selfPath}\\module\\alarmClock\\{arg}"
		else:
			return f"module\\alarmClock\\{arg}"
			
def showWindow(arg):
	global window,hide,textBg,imgBg,imgLabel,img
	if not window:
		window = Toplevel()
		window.attributes("-toolwindow",1)
		window.wm_attributes("-topmost",1)
		window.overrideredirect(True)
		window.geometry(f"{windowWidth}x{windowHeight}+{main.entryXPos}+{main.yPos}")

		textBg = ImageTk.PhotoImage(PILImage.open(f"module\\alarmClock\\textbg.png"))
		imgBg = ImageTk.PhotoImage(PILImage.open(f"module\\alarmClock\\imgbg.png"))

		timebg = Label(window,image = textBg)
		msgbg = Label(window,image = textBg)
		imgbg = Label(window,image = imgBg)

		timeLabel = Label(window,textvariable = timeText, bg = "#fafafa", fg = "#707070", font = ("Microsoft YaHei Light", 30))
		msgLabel = Label(window,textvariable = msgText, bg = "#fafafa", fg = "#606060", font = ("Microsoft YaHei Light", 25))
		imgLabel = Label(window)

		timebg.place(x = 0,y = timeY,width = windowWidth , height = labelHeight + 9)
		timeLabel.place(x = labelX,y = timeY,width = labelWidth , height = labelHeight)

		msgbg.place(x = 0,y = msgY,width = windowWidth , height = labelHeight + 9)
		msgLabel.place(x = labelX,y = msgY,width = labelWidth , height = labelHeight)
		
		imgbg.place(x = 0,y = imgY,width = windowWidth , height = windowWidth)
		imgLabel.place(x = labelX + 10,y = imgY + 10,width = imgWidth , height = imgWidth)

		window.bind("<Double-Button-1>",closewindow)
		hide = False
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
	
	updateText(arg["time"],arg["msg"])
	imgPath = getPath(arg["pic"],"img")
	try:
		i = PILImage.open(imgPath)
		if i.width != imgWidth or i.height != imgWidth:
			i = i.resize((imgWidth,imgWidth),PILImage.ANTIALIAS)
		img = ImageTk.PhotoImage(i)
		imgLabel.config(image = img)
	except:
		print("读取图片错误")



