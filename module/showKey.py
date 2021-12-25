#-*- coding : utf-8 -*-
import mouse
import keyboard
from tkinter import Toplevel,Label,StringVar
from . import core

initArg = [ "entryXPos","entryYPos","entryHeight","entryWidth" ]
keywords = {"hk","kh","mh"}
describe = "显示键盘按键或鼠标按键"

keyHook = ""
keyList = list()
keyText = ""
lastKey = ""
keyCount = 1
keyPause = False

mouseHook = ""
mouseList = dict()
mouseText = ""
lastMouse = ""
mouseCount = 1
mousePause = False

window = ""
xPos = 0
yPos = 0
width = 0
height = 100
hide = False
lableText = StringVar()
maxCount = 0

hookKeyList = core.config["keylist"]
hookMouseList = core.config["mouselist"]

def init(arg):
	global xPos,yPos,width
	xPos = arg[0]
	yPos = arg[1] + arg[2] + 10
	width = arg[3]

def resolve(line):
	global window,keyHook,mouseHook
	arg,argLen = core.getArgList(line)
	if argLen < 2:
		return core.setEntry("缺少参数")
	if arg[1] == "on":
		if not window:
			showWindow()
		if arg[0] == "hk":
			hookKey()
			hookMouse()
		elif arg[0] == "kh":
			return hookKey()
		elif arg[0] == "mh":
			return hookMouse()
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
			return unhookKey()
		elif arg[0] == "mh":
			return unhookMouse()
		if not keyHook and not mouseHook:
			closeWindow()

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
	global keyHook,keyPause
	if not keyHook:
		keyList.clear()
		keyPause = False
		keyHook = keyboard.hook(keyEventHandler,suppress = False)
		return
	return core.setEntry("已启动")

def hookMouse():
	global mouseHook,mousePause
	if not mouseHook:
		mouseList.clear()
		mousePause = False
		mouseHook = mouse.hook(mouseEventHandler)
		return
	return core.setEntry("已启动")

def unhookKey():
	global keyHook
	if keyHook:
		keyboard.unhook(keyHook)
		keyList.clear()
		keyHook = ""
		return
	return core.setEntry("已停止")

def unhookMouse():
	global mouseHook
	if mouseHook:
		mouse.unhook(mouseHook)
		mouseList.clear()
		mouseHook = ""
		return
	return core.setEntry("已停止")

def showWindow():
	global window
	window = Toplevel()
	window.overrideredirect(True)
	window.attributes("-alpha",0.8)
	window.attributes("-toolwindow",1)
	window.wm_attributes("-topmost",1)
	window.geometry(f"{width}x{height}+{xPos}+{yPos}")
	label = Label(window,textvariable = lableText, justify = 'center' , font = ("Microsoft YaHei Light",50))
	label.place(width = width , height = height )
	hideWindow()

def countTime():
	global lastKey,lastMouse,maxCount
	if mouseList:
		maxCount = 0
	else:
		maxCount += 1
		if maxCount > 7:
			maxCount = 0
			keyList.clear()
			mouseList.clear()
			lastKey = ""
			lastMouse = ""
			hideWindow()
			return
	window.after(200,countTime)
	
def hideWindow():
	global window,hide
	window.withdraw()
	hide = True

def closeWindow():
	global window
	if window:
		window.destroy()
		window = ""

def updateWindow():
	global window,hide,maxCount
	text = ""
	if keyList and keyText and not keyPause:
		text += keyText
	if mouseList and mouseText and not mousePause:
		text += " " + mouseText
	lableText.set(text)
	maxCount = 0
	if hide and window:
		window.update()
		window.deiconify()
		hide = False
		window.after(100,countTime)

def keyEventHandler(event):
	global keyText,lastKey,keyCount,maxCount
	if keyPause:
		return
	if event.event_type == "down":
		if event.name not in keyList:
			keyList.append(event.name)
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
				maxCount = 0
	else:
		try:
			keyList.remove(event.name)
		except:
			pass

def mouseEventHandler(event):
	global mouseText,lastMouse,mouseCount,maxCount
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
					mouseText += "double "+key
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

