#-*- coding : utf-8 -*-
import os
import sys
import time
import win32api
import win32con
import win32gui
import keyboard
import importlib
from math import floor
from tkinter import Tk,Entry,END
from history import History
from module import core

modules = dict()
moduleList = list()
modeModules = dict()
modeShortcut = {"Control-n":core.normalMode}
commandShortcut = dict()

def clearEntry():
	input.delete(0,END)

def setEntry(line):
	if not line:
		return
	clearEntry()
	if line.startswith("cal "):
		input.insert(0,line[:4])
	else:
		input.insert(0,line)

def sendShortcut(key):
	if key.startswith("[") and key.endswith("]"):
		time.sleep(float(key[1:-1]))
	else:
		keyboard.send(key)

def resolveShortcut(key):
	shotcut = commandShortcut[key][0]
	if shotcut != "None":
		if shotcut.find("#") == -1:
			sendShortcut(shotcut.strip())
		else:
			for s in shotcut.split("#"):
				sendShortcut(s.strip())
	command = commandShortcut[key][1]
	mode = commandShortcut[key][2]
	isRun = commandShortcut[key][3]
	if mode == "None":
		mode = None
	if mode and mode not in modeModules:
		setEntry(f"模式错误:{mode}")
		return
	if isRun == "run" or isRun == "runs":
		if command.find(";;") == -1:
			submit(None,command,mode)
		else:
			for c in command.split(";;"):
				submit(None,c,mode)
		if isRun == "run":
			return True
	else:
		if command != "None":
			setEntry(command)

def globalEventHandler(arg):
	global hide
	if resolveShortcut(arg):
		return
	if hide == True:
		window.update()
		window.deiconify()
		hide = False
	keyboard.send("alt")
	win32gui.ShowWindow(handle,win32con.SW_SHOW)
	win32gui.BringWindowToTop(handle)
	win32gui.SetForegroundWindow(handle)
	input.focus()

def localEventHandler(event):
	if event.keysym == "Up":
		setEntry(hy[currentMode].getPre())
	elif event.keysym == "Down":
		setEntry(hy[currentMode].getNext())
	elif event.keysym == "Escape":
		clearEntry()
		if currentMode != core.normalMode:
			modeModules[currentMode]["module"].exit()
			resetMode(core.normalMode,core.normalColor)
	elif event.keysym == "space":
		resetMode(lastMode,lastColor)
	elif event.keysym == "BackSpace":
		clearEntry()
	else:
		if event.keysym.isnumeric():
			event.keysym = f"Key-{event.keysym}"
		if event.state == 131080:
			key = f"Alt-{event.keysym}"
		elif event.state == 12:
			key = f"Control-{event.keysym}"
		else:
			key = event.keysym
		if key in commandShortcut:
			resolveShortcut(key)
		elif key in modeShortcut:
			resetMode(modeShortcut[key])

######################################### 模块 ###########################################
def loadShortcut():
	global commandShortcut
	commandShortcut = core.loadDict("shortcut.txt")
	if not commandShortcut:
		return
	for key,value in commandShortcut.items():
		if value[4] == "local":
			input.bind(f"<{key}>", localEventHandler)
		else:
			isSuppress = True if value[5] == "suppress" else False
			keyboard.add_hotkey(key, globalEventHandler, args = [key], suppress = isSuppress )

def resetMode(mode,color = None):
	global currentMode,lastMode,currentColor,lastColor
	if mode == currentMode:
		return True
	if mode not in modeModules:
		setEntry(f"模式错误:{mode}")
		return False
	if not color:
		color = modeModules[mode]["color"]
	lastMode = currentMode
	lastColor = currentColor
	currentMode = mode
	currentColor = color
	input.configure(highlightcolor = color)
	return True

def printModuleList():
	id = 1
	for m in moduleList:
		print(f"{id} {m.ljust(20,' ')} {'加载' if m in modules else '未加载'}")
		id += 1

def printKeywords(arg,argLen):
	if argLen == 1:
		[ print(f"{key} {value['mode']} {value['color']} {value['shortcut']}\n{value['kw']}\n{value['desc']}\n") for key,value in modules.items() ]
	elif not [ print(f"{key} {value['mode']} {value['color']} {value['shortcut']}\n{value['kw']}\n{value['desc']}\n") for key,value in modules.items() if arg[1] in value['kw'] ]:
		print(f"未找到:{arg[1]}")

def importModule(name,isReload = False):
	if isReload:
		rl = getattr(modules[name]["module"],"reload",False)
		if rl:
			modules[name]["module"].reload()
		del sys.modules[f"module.{name}"]
	print(f"导入: {name}")
	m = importlib.import_module(f"module.{name}")
	if not isReload and name not in moduleList:
		moduleList.append(f"{name}")
	initArg = getattr(m,"initArg",False)
	if initArg:
		m.init([ globals()[arg] for arg in initArg ])
	modules[name] = dict()
	modules[name]["module"] = m
	modules[name]["kw"] = getattr(m,"keywords",{})
	mode = getattr(m,"mode","")
	modules[name]["mode"] = mode
	modules[name]["color"] = getattr(m,"modecolor","")
	modules[name]["shortcut"] = getattr(m,"shortcut","")
	modules[name]["desc"] = getattr(m,"describe","")
	if mode:
		modeModules[mode] = dict()
		modeModules[mode]["module"] = m
		modeModules[mode]["color"] = m.modecolor
		hy[mode] = History()
		shortcut = getattr(m,"shortcut","")
		if not shortcut or shortcut in commandShortcut:
			return
		if shortcut not in modeShortcut:
			input.bind(f"<{shortcut}>", localEventHandler)
		modeShortcut[shortcut] = mode
	
def checkModuleExist(name):
	if name in modules:
		importModule(name,True)
	elif os.path.isfile(f"module\\{name}.py"):
		importModule(name)
	else:	
		return False
	return True

def checkModuleName(name):
	if checkModuleExist(name):
		return True
	elif name.isnumeric() or (name.startswith("-") and name[1:].isnumeric()):
		index = core.checkIndex(int(name),len(moduleList))
		if index != "error":
			return checkModuleExist(moduleList[index])
	elif name.startswith("-"):
		for v in moduleList:
			if v.find(name[1:]) != -1:
				return checkModuleExist(v)

def reloadModule(arg,argLen):
	if argLen == 1:
		loadModule("all")
	elif arg[1] =="n":
		loadModule("new")
	elif arg[1] =="l":
		printModuleList()
	elif checkModuleName(arg[1]):
		return
	elif arg[1] in core.config:
		[ print(f"{m}:不存在") for m in core.config[arg[1]] if not checkModuleName(m) ]
	else:
		mlist = core.getInputPath(arg[1])
		if not mlist:
			setEntry(f"参数错误:{arg[1]}")
			return
		[ print(f"{m}:不存在") for m in mlist if not checkModuleName(m) ]

def loadModule(type = "auto"):
	filelist = os.listdir("module")
	autoLoadList = core.config["autoload"]
	for file in filelist:
		if os.path.isfile(f"module\\{file}") and file.endswith(".py") and file != "__init__.py":
			name = file[:-3]
			if type == "new" and name in moduleList:
				continue
			if type == "auto" and autoLoadList and name not in autoLoadList:
				moduleList.append(name)
				continue
			if type == "all" and name in modules:
				continue
			importModule(name)

def resolveResult(ret):
	if not ret:
		return True
	if ret[0] == "se":
		setEntry(ret[1])
	elif ret[0] == "sm":
		resetMode(ret[1])
	else:
		return False
	return True

def modeResolve(line,mode):
	ret = modeModules[mode]["module"].resolve(line)
	resolveResult(ret)

def keywordsResolve(line):
	p = line.find(" ")
	arg = line if p == -1 else line[:p]
	for value in modules.values():
		if arg in value["kw"]:
			ret = value["module"].resolve(line)
			if resolveResult(ret):
				return True
			if ret[0] == "continue":
				continue
			return True
	return False

def runCommandList(arg,argLen):
	if argLen < 2:
		setEntry("缺少参数")
		return
	mode = None
	if argLen >= 3:
		if arg[2] not in modeModules:
			setEntry(f"模式错误:{arg[2]}")
			return	
		mode = arg[2]
	for command in core.getInputPath(arg[1]):
		submit(None,command,mode)

def resolve(line):
	global hide
	arg,argLen = core.getArgList(line)
	if arg[0] == "run":
		runCommandList(arg,argLen)
	elif arg[0] == "kw":
		printKeywords(arg,argLen)
	elif arg[0] == "lm":
		reloadModule(arg,argLen)
	elif arg[0] == "h":
		hide = True
		window.withdraw()
	elif arg[0] == "q":
		window.destroy()
	elif argLen == 2 and arg[1] == "*":
		[ core.runCommand(f"start {arg[0]} \"{path}\"",True) for path in core.getClipboard() ]
	elif core.openDictPath(arg,argLen):
		return
	else:
		core.runCommand(f"start {line}")

######################################### 模块 ###########################################

def submit(event,line,runMode = None):
	clearEntry()
	mode = runMode if runMode else currentMode
	if line and line != "printClip":
		hy[mode].add(line)
	if mode != core.normalMode:
		modeResolve(line,mode)
		return
	line = line.strip()
	if not line:
		return
	if keywordsResolve(line):
		return
	resolve(line)

hide = False
currentMode = core.normalMode
currentColor = core.normalColor
lastMode = core.normalMode
lastColor = core.normalColor
hy = {currentMode:History()}
modeModules[core.normalMode] = {"color":core.normalColor}

window = Tk()
window.overrideredirect(True)
handle = window.winfo_id()
screenWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screenHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
entryWidth = 640
entryHeight = 50
entryXPos = floor((screenWidth-entryWidth)/2)
entryYPos = floor(0.1*screenHeight)
window.geometry(f"{entryWidth}x{entryHeight}+{entryXPos}+{entryYPos}")

input = Entry(window, bd = 0, highlightbackground = "#F0F0F0", highlightcolor = core.normalColor, highlightthickness = 1, insertwidth = 1, justify = "center", font = ("Microsoft YaHei Light", 25))
input.place(width = entryWidth, height = entryHeight)
input.focus()
input.bind("<Up>", localEventHandler)
input.bind("<Down>", localEventHandler)
input.bind("<Escape>", localEventHandler)
input.bind("<Control-n>", localEventHandler)
input.bind("<Control-space>", localEventHandler)
input.bind("<Control-BackSpace>", localEventHandler)
input.bind("<Return>", lambda event:submit(event,input.get()))

core.loadConfig()
loadShortcut()
loadModule()
window.mainloop()