#-*- coding : utf-8 -*-
from ..core import core
from tkinter import Toplevel,Label

commands = {"td"}
describe = "待办"


main = ""
hide = ""
window = ""
lableList = list()
infoLabel = ""
labelXpos = 25
labelYpos = 25 
labelWidth = 0
labelHeight = 40

maxRow = 15
start = 0
end = 0
todoList = ""
todoLen = 0
currentName = ""

def clear():
	closewindow(isClose = "close")
	
def init(arg):
	global main,todoList,labelWidth
	main = arg
	labelWidth = main.entryWidth - 50
	todoList = core.loadDict("module\\todo\\todo.txt")

def resolve(line,isReturn):
	global start,end,todoLen
	arg,argLen = core.getArgList(line)
	p = ["default","default",""]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[1+i]
	
	if p[0] == "ad":
		if p[1] not in todoList:
			todoList[p[1]] = list()
	elif p[0] == "d":
		if p[1] in todoList:
			del todoList[p[1]]
			if currentName == p[1]:
				closewindow()
	elif p[0] == "c":
		todoList["default"].clear()
		if currentName == "default":
			closewindow()
	elif p[0] == "s":
		core.saveFile(todoList,'module\\todo\\todo.txt',False,"dict")
		#core.saveDict("module\\todo\\todo.txt",todoList)
	elif p[0] in todoList:
		if p[1] == "c":
			todoList[p[0]].clear()
			if currentName == p[0]:
				closewindow()
				return
		elif p[1] == "default":
			start = 0
			todoLen = len(todoList[p[0]])
			if todoLen == 0:
				main.setEntry("无数据")
				return
			if todoLen > maxRow:
				end = maxRow
			else:
				end = todoLen
			showTodoList(p[0])
			return
		elif p[1] == "*":
			if p[2] == "o":
				todoList[p[0]].append(core.getClipboard("strip"))
			else:
				[ todoList[p[0]].append(s) for s in core.getClipboard("list") ]
		else:		
			todoList[p[0]].append(" ".join(arg[2:]))
		if currentName == p[0]:
			addTodo()
	else:
		if p[0] == "*":
			if p[1] == "o":
				todoList["default"].append(core.getClipboard("strip"))
			else:
				[ todoList["default"].append(s) for s in core.getClipboard("list") ]
		else:
			todoList["default"].append(" ".join(arg[1:]))
		if currentName == "default":
			addTodo()
		


		
def closewindow(event = None,isClose = "hide"):
	global window,hide,currentName
	currentName = ""
	if window in core.windows:
		core.windows.remove(window)
	if isClose == "close" and window:
		window.destroy()
		window = ""
		main.resetMode(core.normalMode)
	elif isClose == "hide" and not hide and window:
		window.withdraw()
		hide = True
	

def eventHandler(event):
	i = int(event.widget["text"].split(":",1)[0]) - 1
	if event.num == 1:
		if todoList[currentName][i].endswith("\\0"):
			todoList[currentName][i] = todoList[currentName][i][:-2]
			lableList[i].config(font = ("Microsoft YaHei Light", 15,))
		else:
			todoList[currentName][i] = todoList[currentName][i]+"\\0"
			lableList[i].config(font = ("Microsoft YaHei Light", 15,"overstrike"))
	else:
		del todoList[currentName][i]
		delTodo()



def addTodo():
	global start,end,todoLen
	todoLen = len(todoList[currentName])
	if start + maxRow >= todoLen:
		end = todoLen
	else:
		if end == start + maxRow:
			infoLabel.config(text=f"{start + 1} - {end} / {todoLen}")
			return
		end = start + maxRow
	resizeWindow()
		

def delTodo():
	global start,end,todoLen
	todoLen = len(todoList[currentName])
	if todoLen == 0:
		closewindow()
		return
	if start >= todoLen:
		start -= maxRow
		end -= maxRow
	else:
		if (start+maxRow) > todoLen:
			end = todoLen
		else:
			end = start + maxRow
	resizeWindow()



def showTodoList(name):
	global window, hide, infoLabel,currentName,start
	currentName = name
	if not window:
		hide = False
		window = Toplevel()
		window.overrideredirect(True)
		infoLabel = Label(window, bg = "#E0DEE1", fg="#363636",font = ("Microsoft YaHei Light", 15))
		for i in range(maxRow):
			l = Label(window, bg = "#E0DEE1", fg="#363636",font = ("Microsoft YaHei Light", 15))
			l.bind("<Double-Button-1>", eventHandler)
			l.bind("<ButtonPress-3>", eventHandler)
			lableList.append(l)	
		window.bind("<Escape>",closewindow)
		core.windows.append(window)
		window.bind("<Left>",turnPage)
		window.bind("<Right>",turnPage)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)
	resizeWindow()
	
def turnPage(event):
	global start,end
	if event.keysym == "Left":
		if (start - maxRow) >= 0:
			start -= maxRow
			end = start + maxRow
		else:
			main.setEntry("已到第一页")
			return
	else:
		if (start + maxRow) < todoLen:
			start += maxRow
			if (end + maxRow) <= todoLen:
				end += maxRow
			else:
				end = todoLen
		else:
			main.setEntry("已到最后一页")
			return
	resizeWindow()


def resizeWindow():
	showLen = end - start
	infoLabel.place(x = labelXpos, y = labelYpos, width = labelWidth , height = labelHeight)
	infoLabel.config(text=f"{start + 1} - {end} / {todoLen}")
	widowHeight = 25 + (showLen + 1)*(labelHeight + 10) + 15
	window.geometry(f"{main.entryWidth}x{widowHeight}+{main.entryXPos}+{main.yPos}")

	yPos = labelYpos + (labelHeight + 10)
	for i in range(showLen):
		lableList[i].place(x = labelXpos, y = yPos, width = labelWidth , height = labelHeight)
		if todoList[currentName][i + start].endswith("\\0"):
			lableList[i].config(font = ("Microsoft YaHei Light", 15,"overstrike"))
			lableList[i].config(text=f"{i + 1 + start} : {todoList[currentName][i + start][:-2]}")
		else:
			lableList[i].config(font = ("Microsoft YaHei Light", 15,))
			lableList[i].config(text=f"{i + 1 + start} : {todoList[currentName][i + start]}")
		yPos += (labelHeight + 10)
	if maxRow > showLen:
		lableList[showLen].place( y = yPos + 15 )
		



					
