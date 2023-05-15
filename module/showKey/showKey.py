#-*- coding : utf-8 -*-
import mouse
import keyboard
import threading
from queue import Queue
from tkinter import Toplevel,Label,StringVar
from ..core import core

commands = {"hk","kh","mh"}
describe = "显示键盘按键或鼠标按键"
running = False
q = Queue()

keyHandler = ""
keyList = list()
keyText = ""
lastKey = ""
keyCount = 1
keyPause = False

mouseHandler = ""
mouseList = dict()
mouseText = ""
lastMouse = ""
mouseCount = 1
mousePause = False

main = ""
window = ""
xPos = 0
yPos = 0
width = 0
height = 100
hide = False
lableText = StringVar()

hookKeyList = ""
hookMouseList = ""

def clear():
	unhookKey(False)
	unhookMouse(False)
	closeWindow()

def init(arg):
	global main,xPos,yPos,width,hookKeyList,hookMouseList
	main = arg
	xPos = arg.entryXPos
	yPos = arg.yPos
	width = arg.entryWidth
	config = core.loadDict("module\\showKey\\config.txt")
	hookKeyList = config["keylist"]
	hookMouseList = config["mouselist"]

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if not core.checkArgLength(arg,2):
		return main.setEntry("缺少参数")
	if arg[1] == "on":
		createWindow()
		if arg[0] == "hk":
			hookKey()
			hookMouse()
		elif arg[0] == "kh":
			hookKey()
		elif arg[0] == "mh":
			hookMouse()
	elif arg[1] == "c":
		keyList.clear()
		mouseList.clear()
	elif arg[1] == "p":
		if arg[0] == "hk":
			pauseKey()
			pauseMouse()
		elif arg[0] == "kh":
			pauseKey()
		elif arg[0] == "mh":
			pauseMouse()
	elif arg[1] == "off":
		if arg[0] == "hk":
			unhookKey()
			unhookMouse()
		elif arg[0] == "kh":
			unhookKey()
		elif arg[0] == "mh":
			unhookMouse()
		if not keyHandler and not mouseHandler:
			q.put("exit")

def pauseKey():
	global keyPause
	if keyPause:
		keyPause = False
		keyList.clear()
	else:
		keyPause = True

def pauseMouse():
	global mousePause
	if mousePause:
		mousePause = False
		mouseList.clear()
	else:
		mousePause = True

def hookKey():
	global keyHandler,keyPause
	if not keyHandler:
		keyList.clear()
		keyPause = False
		keyHandler = keyboard.hook(keyEventHandler,suppress = False)
		return
	main.setEntry("已启动")

def hookMouse():
	global mouseHandler,mousePause
	if not mouseHandler:
		mouseList.clear()
		mousePause = False
		mouseHandler = mouse.hook(mouseEventHandler)
		return
	main.setEntry("已启动")

def unhookKey(msg = True):
	global keyHandler
	if keyHandler:
		keyboard.unhook(keyHandler)
		keyList.clear()
		keyHandler = ""
		return
	if msg:
		main.setEntry("已停止")

def unhookMouse(msg = True):
	global mouseHandler
	if mouseHandler:
		mouse.unhook(mouseHandler)
		mouseList.clear()
		mouseHandler = ""
		return
	if msg:
		main.setEntry("已停止")

def createWindow():
	global window
	if not window:
		window = Toplevel()
		window.overrideredirect(True)
		window.attributes("-alpha",0.8)
		window.attributes("-toolwindow",1)
		window.wm_attributes("-topmost",1)
		window.geometry(f"{width}x{height}+{xPos}+{yPos}")
		label = Label(window,textvariable = lableText, justify = 'center' , font = ("Microsoft YaHei Light",50))
		label.place(width = width , height = height )
		hideWindow()
	if not running:		
		threading.Thread(target = countThread).start()

def countThread():
	global hide,running
	running = True
	while True:
		try:
			text = q.get(timeout = 1.5)
			if text == "exit":
				print("退出线程")
				running = False
				hideWindow()
				return
			lableText.set(text)
			if hide and window:
				window.update()
				window.deiconify()
				hide = False
		except:
			hideWindow()

def hideWindow():
	global window,hide,lastKey,lastMouse
	if not hide:
		keyList.clear()
		mouseList.clear()
		lastKey = ""
		lastMouse = ""
		window.withdraw()
		hide = True

def closeWindow():
	global window
	hideWindow()
	if window:
		window.destroy()
		window = ""

def updateWindow():
	text = ""
	if keyList and keyText:
		text += keyText
	if mouseList and mouseText:
		text += " " + mouseText
	q.put(text)

def keyEventHandler(event):
	global keyText,lastKey,keyCount
	if keyPause:
		return
	if event.name.startswith("left "):
		name = event.name[5:]
	elif event.name.startswith("right "):
		name = event.name[6:]
	else:
		name = event.name
	if event.event_type == "down":
		if name not in keyList:
			keyList.append(name)
			keyText = "+".join(keyList)
			if hookKeyList and keyText not in hookKeyList:
				keyText = ""
				return
			if lastKey != keyText:
				lastKey = keyText
				keyCount = 1
			else:
				keyCount += 1
			if keyCount > 1:
				keyText += f" x{keyCount}"
			updateWindow()
		else:
			if lastKey == "+".join(keyList):
				updateWindow()
	else:
		try:
			keyList.remove(name)
		except:
			pass

def mouseEventHandler(event):
	global mouseText,lastMouse,mouseCount
	if mousePause:
		return
	if isinstance(event,mouse.ButtonEvent):
		if event.event_type == "up":
			try:
				del mouseList[event.button]
			except:
				pass
		else: 
			mouseList[event.button] = event.event_type
			mouseText = ""
			for key,value in mouseList.items():
				if value == "double":
					mouseText += "double " + key
				else:
					mouseText += key
			if hookMouseList and mouseText not in hookMouseList:
				mouseText = ""
				return
			if lastMouse != mouseText:
				lastMouse = mouseText
				mouseCount = 1
			else:
				mouseCount += 1
			if mouseCount > 1:
				mouseText += f" x{mouseCount}"
			updateWindow()

