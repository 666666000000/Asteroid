#-*- coding : utf-8 -*-

from math import *
from ..core import core
from tkinter import Toplevel,Label,ANCHOR,INSERT,END

mode = "cal"
modecolor = "#02b683"
commands = {"cal"}
describe = "计算器"

main = ""
window = ""
row = 12
windowWidth = 550
windowHeight = 550
hide = False
data = ""
funcs = dict()
custom = dict()
lableList = list()

def clear():
	closewindow(isClose = "close")

def exit():
	closewindow()

def init(arg):
	global main,windowWidth,windowHeight,data,funcs
	main = arg
	windowWidth = arg.entryWidth
	windowHeight = 25 + row*60 + 15
	data = core.loadDict("module\\calculator\\calculator.txt")
	for key,value in data.items():
		if key != "color" and key != "0":
			core.splitList(value,sym = "#",num = 3)
			for val in value:
				if len(val) == 3:
					tmp = dict()
					tmp["parm"] = val[1]
					tmp["desc"] = val[2]
					funcs[val[0]] = tmp
				elif len(val) == 4:
					tmp = dict()
					tmp["parm"] = val[1]
					tmp["val"] = val[2]
					tmp["desc"] = val[3]
					custom[val[0]] = tmp

def resolve(line,isReturn):
	if main.currentMode != mode:
		line = line[3:].lstrip()
		if not line:
			main.resetMode(mode)
			return
	if line == "on":		
		showWindow()
	elif line == "h":		
		closewindow()
	elif line == "off":
		closewindow(isClose = "close")
	elif line == "rc":
		reloadColor()
	elif line.startswith("l "):
		arg,argLen = core.getArgList(line)
		printFunction(arg)
	else:
		cal(line)

def printFunction(arg):
	if not core.checkArgLength(arg,2):
		return
	if arg[1] in funcs:
		print(f"{arg[1]}{funcs[arg[1]]['parm']} : {funcs[arg[1]]['desc']}")
	elif arg[1] in custom:
		print(f"{arg[1]}{custom[arg[1]]['parm']} : {custom[arg[1]]['val']} : {custom[arg[1]]['desc']}")
	else:
		main.setEntry(f"未找到:{arg[1]}")

def cal(input,event = None):
	if not input:
		return
	try:
		val = str(eval(input))
		print(f"{input}={val}")
		core.appedClipboardText(val)
		main.setEntry(val)
	except:
		main.setEntry(f"输入错误:{input}")
			
def closewindow(event = None,isClose = "hide"):
	global window,hide
	if window in core.windows:
		core.windows.remove(window)
	if isClose == "close" and window:
		window.destroy()
		window = ""
		main.resetMode(core.normalMode)
	elif isClose == "hide" and not hide and window:
		window.withdraw()
		hide = True

def getIndex():
	start = main.inputEntry.index(ANCHOR)
	end = main.inputEntry.index(INSERT)
	if start < end:
		return [start,end]
	elif start > end:
		return [end,start]
	else:
		return [0,len(main.inputEntry.get())]

def replaceParm(buttonText):
	isSelected = main.inputEntry.select_present()
	if isSelected:
		text = main.inputEntry.get()
		selectedStr = main.inputEntry.selection_get()
		index = getIndex()
		if not index:
			return
		parm = funcs[buttonText]['parm'][1:-1].split(",")
		parmLen = len(parm)
		if parmLen == 1:
			if parm[0] == "iterable":
				parm = f"(({selectedStr.replace(' ',',')}))"
			else:
				if selectedStr.find(" ") != -1:
					print("所选参数过多")
					return
				parm = f"({selectedStr})"
		else:
			tmp = selectedStr.split()
			if len(tmp) > parmLen:
				print("所选参数过多")
				return
			for i in range(len(tmp)):
				parm[i] = tmp[i]
			if len(tmp) < parmLen:
				for i in range(len(tmp),parmLen):
					if parm[i].strip().startswith("["):
						del parm[i]
			parm = f"({','.join(parm)})"
		main.setEntry(f"{text[0:index[0]]}{buttonText}{parm}{text[index[1]:]}")	
	else:
		main.inputEntry.insert('insert', f"{buttonText}{funcs[buttonText]['parm']}")

def replaceCustomParm(buttonText):
	isSelected = main.inputEntry.select_present()
	val = custom[buttonText]['val']
	if isSelected:
		text = main.inputEntry.get()
		selectedStr = main.inputEntry.selection_get()
		index = getIndex()
		parm = custom[buttonText]['parm'].split(",")
		tmp = selectedStr.split()
		if len(tmp) > len(parm):
			print("所选参数过多")
			return
		for i in range(len(tmp)):
			val = val.replace(parm[i], tmp[i])
		main.setEntry(f"{text[0:index[0]]}{val}{text[index[1]:]}")	
	else:
		main.inputEntry.insert('insert', val)

def replaceSymbol(buttonText):
	isSelected = main.inputEntry.select_present()
	if isSelected:
		text = main.inputEntry.get()
		index = getIndex()
		main.setEntry(f"{text[0:index[0]]}{buttonText}{text[index[1]:]}")	
		main.inputEntry.icursor(len(text[0:index[0]])+len(buttonText))
	else:
		main.inputEntry.insert('insert', buttonText)

def eventHandler(event):
	if str(event.type) == "ButtonPress":
		text = event.widget["text"]
		if event.num == 1:
			if  text == "=":
				cal(main.inputEntry.get())
			elif text == "←":
				if main.inputEntry.select_present():
					index = getIndex()
					main.inputEntry.delete(index[0],index[1])
				else:
					main.inputEntry.delete(main.inputEntry.index(INSERT)-1)
			elif text in funcs:
				replaceParm(text)
			elif text in custom:
				replaceCustomParm(text)
			else:
				replaceSymbol(text)
		else:
			if  text == "=":
				main.inputEntry.insert('insert', " ")
			elif text == "←":
				main.inputEntry.delete(0,END)
				
		core.preColor = event.widget["bg"]
		event.widget["bg"] = "#"+data["color"][0]
	else:
		event.widget["bg"] = core.preColor

def reloadColor():
	lableIndex = 0
	colorIndex = 1
	for key,value in core.loadDict("module\\calculator\\calculator.txt").items():
		if key == "color":
			data["color"] = value
			continue
		for i in range(len(value)):
			c = data["color"][colorIndex].split("#",1)
			lableList[lableIndex].config(bg = f"#{c[0].strip()}",fg = f"#{c[1].strip()}")
			lableIndex += 1
		colorIndex += 1
	
def showWindow():
	global window,hide
	if not window:
		hide = False
		window = Toplevel()
		window.overrideredirect(True)
		window.geometry(f"{windowWidth}x{windowHeight}+{main.entryXPos}+{main.yPos}")
		xpos = 25
		ypos = 25
		count = 0
		index = 0
		for key,value in data.items():
			if key == "color":
				continue
			index += 1
			for val in value:
				if isinstance(val,str):
					t = val
					width = 50
				else:
					t = val[0]
					width = 110
				c = data["color"][index].split("#")
				b = Label(window,text = t,bg = f"#{c[0].strip()}",fg = f"#{c[1].strip()}",font = ("Microsoft YaHei Light", 15))
				lableList.append(b)
				b.place(x = xpos,y = ypos,width = width , height = 50)
				b.bind("<ButtonPress-1>", eventHandler)
				b.bind("<ButtonRelease-1>", eventHandler)
				if t=="←" or t=="=":
					b.bind("<ButtonPress-3>", eventHandler)
					b.bind("<ButtonRelease-3>", eventHandler)
				count += 1
				if isinstance(val,str):
					xpos += 60
					maxCount = 10
				else:
					xpos += 120
					maxCount = 5
				if count == maxCount:
					count = 0
					xpos = 25
					ypos += 60
		window.bind("<Escape>", closewindow)
		window.bind("<Return>", lambda event:cal(main.inputEntry.get(),event))
		core.windows.append(window)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)
	
