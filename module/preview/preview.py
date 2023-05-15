#-*- coding : utf-8 -*-
import os
from math import floor,ceil
from tkinter import Toplevel,Label
from PIL import Image as PILImage, ImageTk
from ..core import core


commands = {"view","ve","vap"}
describe = "预览图片"


files = list()
current = 0
isDir = False
dirCurrent = 0

screenWidth = 0
screenHeight = 0
hide = ""
window = ""
imgLable = ""
image = ""

interval = ""
timer = ""
shortcuts = dict()

def clear():
	closewindow(isClose = "close")

def init(arg):
	global screenWidth,screenHeight
	screenWidth = arg.workArea[2]
	screenHeight = arg.workArea[3]
	tmp = core.splitDict(core.loadDict("module\\preview\\config.txt"))
	for val in tmp["shortcut"]:
		shortcuts[val[0]] = val[1]

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "view":
		return preview(arg,argLen)
	path = files[current][dirCurrent] if isDir else files[current]
	if not core.checkArgLength(arg,2):
		return
	if arg[0] == "ve":
		if arg[1] in core.programDict:
			core.runCommand(f"\"{core.programDict[arg[1]][0]}\" \"{path}\"")
		else:
			print("参数错误:",arg[1])
	elif arg[0] == "vap":
		core.appendDict(arg[1],core.pathDict,"ap",value = [ path ],checkRepeat = True,printVal = False)
		print(files[current])

def preview(arg,argLen):
	global files,current,interval
	p = ["*","0","0"]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[i+1]
	if p[0] in {"r","d","l"}:
		path = files[current][dirCurrent] if isDir else files[current]
		if p[0] == "r":
			return [ path ]
		elif p[0] == "d":
			delFile()
		elif p[0] == "l":
			print(path)
		return

	files = core.getInputPath(p[0])
	if not files:
		return
	length = len(files)
	index = 0
	while index < length:
		if os.path.isdir(files[index]):
			dirfiles = os.listdir(files[index])
			if dirfiles:
				images = list()
				for file in dirfiles:
					if core.getFileType(file) == "image":
						images.append(f"{files[index]}\\{file}")
				if images:
					files[index] = images
					index += 1
					continue
			del files[index]
			length -= 1
		else:
			index += 1
	if files:	
		try:
			current = int(p[1])
			if current > 0:
				current -= 1
		except:
			print(p[1],"不是数字")
			return
		if abs(current) >= len(files):
			print("参数错误:",p[1])
			return
		if current < 0:
			current += len(files)
		interval = int(p[2])
		if interval < 0:
			print("参数错误:",p[2])
			return
		setCurrent(True)
		showWindow()

def setCurrent(forward):
	global isDir,dirCurrent
	if isinstance(files[current],str):
		isDir = False
		return
	isDir = True
	if forward:
		dirCurrent = 0
	else:
		dirCurrent = len(files[current]) - 1

def selectFile(forward):
	global current
	if forward:
		if current + 1 < len(files):
			current += 1
			setCurrent(forward)
			return True
		else:
			return False
	elif current > 0:
		current -= 1
		setCurrent(forward)
		return True

def showNext():
	global current,dirCurrent
	if isDir and dirCurrent + 1 < len(files[current]):
		dirCurrent += 1
	elif not selectFile(True):
		current = 0
		setCurrent(True)
	showPicture()

def delFile():
	global current,dirCurrent
	if isDir:
		os.remove(files[current][dirCurrent])
		print("删除:",files[current][dirCurrent])
		del files[current][dirCurrent]
		
		fileLen = len(files[current])
		if fileLen == 0:
			del files[current]
			if len(files) == 0:
				closewindow(isClose = "hide")
				return
			if current >= len(files):
				selectFile(False)
			else:
				setCurrent(True)
		else:
			if dirCurrent >= len(files[current]):
				if not selectFile(True):
					dirCurrent -= 1
	else:
		os.remove(files[current])
		print("删除:",files[current])
		del files[current]
		fileLen = len(files)
		if fileLen == 0:
			closewindow(isClose = "hide")
			return
		if current >= fileLen:
			selectFile(False)
		else:
			setCurrent(True)
	showPicture()

def eventHandler(event):
	global current,dirCurrent
	if event.num == 1:
		if isDir and dirCurrent > 0:
			dirCurrent -= 1
		elif not selectFile(False):
			return
	elif event.num == 3:
		if isDir and dirCurrent + 1 < len(files[current]):
			dirCurrent += 1
		elif not selectFile(True):
			return
	showPicture()
	
def closewindow(event = None,isClose = "hide"):
	global window,hide,timer
	if window in core.windows:
		core.windows.remove(window)
	if timer:
		window.after_cancel(timer)
		timer = ""
	if isClose == "close" and window:
		window.destroy()
		window = ""
	elif isClose == "hide" and not hide and window:
		window.withdraw()
		hide = True

def keyEventHandler(event):
	key = core.getShortcut(event)
	if key in shortcuts:
		resolve(shortcuts[key],False)
	else:
		print("未知的快捷键:",key)

def showWindow():
	global window,hide,imgLable
	if not window:
		hide = False
		window = Toplevel()
		window.overrideredirect(True)
		imgLable = Label(window, bd = 0, bg = "#FFFFFF")
		window.bind("<ButtonPress-1>", eventHandler)
		window.bind("<ButtonPress-3>", eventHandler)
		window.bind("<h>",closewindow)
		window.bind("<Escape>",lambda event:closewindow(event,"close"))
		for key in shortcuts.keys():
			window.bind(f"<{key}>", keyEventHandler)
		core.windows.append(window)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)
	showPicture()

def showPicture():
	global image,timer
	try:
		path = files[current][dirCurrent] if isDir else files[current]
		img = PILImage.open(path)
	except:
		print("打开文件错误")
		return
	(w, h) = img.size
	x = 0
	y = 0
	windowWidth = 0
	windowHeight = 0
	if w + 20 > screenWidth or h + 20 > screenHeight:
		if w/h > screenWidth/screenHeight:
			windowWidth = screenWidth
			windowHeight = ceil(screenWidth*h/w)
			y = floor((screenHeight - windowHeight)/2)
		elif w/h < screenWidth/screenHeight:
			windowWidth = ceil(w*screenHeight/h)
			windowHeight = screenHeight
			x = floor((screenWidth - windowWidth)/2)
		else:
			windowWidth = screenWidth
			windowHeight = screenHeight
		img = img.resize((windowWidth - 20,windowHeight - 20), PILImage.ANTIALIAS)
	else:
		windowWidth = w + 20
		windowHeight = h + 20
		x = floor((screenWidth - windowWidth)/2)
		y = floor((screenHeight - windowHeight)/2)
	window.geometry(f"{windowWidth}x{windowHeight}+{x}+{y}")
	imgLable.place(x = 0,y = 0,width = windowWidth,height = windowHeight)
	image = ImageTk.PhotoImage(img)
	imgLable.config(image = image)
	if interval != 0:
		timer = window.after(interval*1000,showNext)
