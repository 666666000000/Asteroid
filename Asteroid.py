#-*- coding : utf-8 -*-
import os
import re
import sys
import time
import inspect
import win32api
import win32con
import win32gui
import keyboard
import importlib
import threading
from math import floor
from queue import Queue
from history import History
from module.core import core
from tkinter import Tk,Entry,END

class Asteroid:
	def __init__(self):
		self.modules = dict()
		self.moduleList = list()
		self.modeModules = dict()
		self.modeShortcut = {"Control-n":core.normalMode}
		self.localShortcutHash = dict()
		self.globalShortcutHash = dict()
		self.commandShortcut = dict()
		self.inputEntry = ""
		self.hide = False
		self.currentMode = core.normalMode
		self.currentColor = core.normalColor
		self.lastMode = core.normalMode
		self.lastColor = core.normalColor
		self.hy = {self.currentMode:History()}
		self.modeModules[core.normalMode] = {"color":core.normalColor}

		self.window = Tk()
		self.window.overrideredirect(True)
		self.handle = self.window.winfo_id()
		self.screenWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
		self.screenHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
		self.workArea = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0))).get("Work")
		self.entryWidth = 640
		self.entryHeight = 50
		self.entryXPos = floor((self.screenWidth-self.entryWidth)/2)
		self.entryYPos = floor(0.1*self.screenHeight)
		self.window.geometry(f"{self.entryWidth}x{self.entryHeight}+{self.entryXPos}+{self.entryYPos}")
		self.yPos = self.entryYPos + self.entryHeight + 10
		
		self.inputEntry = Entry(self.window, bd = 0, highlightbackground = "#F0F0F0", fg = core.fontColor, highlightcolor = core.normalColor, highlightthickness = 1, insertwidth = 1, justify = "center", font = ("Microsoft YaHei Light", 25))
		self.inputEntry.place(width = self.entryWidth, height = self.entryHeight)
		self.inputEntry.focus()
		self.inputEntry.bind("<Up>", self.localEventHandler)
		self.inputEntry.bind("<Down>", self.localEventHandler)
		self.inputEntry.bind("<Escape>", self.localEventHandler)
		self.inputEntry.bind("<Control-n>", self.localEventHandler)
		self.inputEntry.bind("<Control-m>", self.localEventHandler)
		self.inputEntry.bind("<Control-BackSpace>", self.localEventHandler)
		self.inputEntry.bind("<Return>", lambda event:self.submit(event,self.inputEntry.get()))
		
		self.loadShortcut()
		self.commandList = core.loadDict("command.txt")
		self.config = core.loadDict("config.txt")
		self.q = Queue()


######################################### 界面操作 ###########################################

	def clearEntry(self):
		self.inputEntry.delete(0,END)

	def setEntry(self,line):
		if not line:
			return
		self.clearEntry()
		self.inputEntry.insert(0,line)

	def showEntry(self):
		if self.hide == True:
			self.window.update()
			self.window.deiconify()
			self.hide = False
		keyboard.send("alt")
		win32gui.ShowWindow(self.handle,win32con.SW_SHOW)
		win32gui.BringWindowToTop(self.handle)
		win32gui.SetForegroundWindow(self.handle)
		self.inputEntry.focus()
		if core.windows:
			core.windows[-1].focus()
			self.inputEntry.focus()

######################################### 界面操作 ###########################################	

######################################### 快捷键处理 ###########################################	

	def sendShortcut(self,key):
		if key.startswith("[") and key.endswith("]"):
			time.sleep(float(key[1:-1]))
		else:
			keyboard.send(key)

	def runShortcutCmd(self,commandList):
		mode = None
		for val in commandList:
			if val[0] == "mode":
				mode = val[1]
			elif val[0] == "show":
				if val[1] == "True":
					self.showEntry()
			elif val[0] == "sleep":
				time.sleep(float(val[1]))
			elif val[0] == "insert":
				self.setEntry(val[1])
			elif val[0] == "send":
				if val[1].find("#") == -1:
					self.sendShortcut(val[1])
				else:
					for v in val[1].split("#"):
						self.sendShortcut(v.strip())
			elif val[0] == "command":
				if mode and mode not in self.modeModules:
					self.setEntry(f"模式错误:{mode}")
					return
				self.submit(None,val[1],mode)

	def eventHandler(self,key):
		self.q.put(key)

	def localEventHandler(self,event):
		if event.keysym == "Up":
			self.setEntry(self.hy[self.currentMode].getPre())
		elif event.keysym == "Down":
			self.setEntry(self.hy[self.currentMode].getNext())
		elif event.keysym == "Escape":
			self.clearEntry()
			if self.currentMode != core.normalMode:
				if callable(getattr(self.modeModules[self.currentMode]["module"],"exit","")):
					try:
						self.modeModules[self.currentMode]["module"].exit()
					except:
						core.getError()
				self.resetMode(core.normalMode,core.normalColor)
		elif event.keysym == "BackSpace":
			self.clearEntry()
		elif event.keysym == "m":
			self.resetMode(self.lastMode,self.lastColor)
		else:
			key = core.getShortcut(event)
			if key in self.commandShortcut:
				self.eventHandler(key)
			elif key in self.modeShortcut:
				self.resetMode(self.modeShortcut[key])
			else:
				print("未知的快捷键:",key)

	def eventProcessThread(self):
		while True:
			try:
				key = self.q.get()
				if key == "exit":
					print("退出事件处理线程")
					return
				i = 1 if self.commandShortcut[key][0][1] == "False" else 2
				self.runShortcutCmd(self.commandShortcut[key][i:])
			except:
				core.getError()
				continue
			
######################################### 快捷键处理 ###########################################		
		
######################################### 加载快捷键 ###########################################

	def loadShortcut(self,keyType = "lg",shortcut = None):
		if not shortcut:
			shortcut = core.loadDict("shortcut.txt")
			if not shortcut:
				return
		for key,value in shortcut.items():
			if value[0].endswith("False") and (keyType == "l" or keyType == "lg"):
				self.localShortcutHash[key] = hash(tuple(value))
				core.splitList(value)
				self.inputEntry.bind(f"<{key}>", self.localEventHandler)
				self.commandShortcut[key] = value
			elif value[0].endswith("True") and (keyType == "g" or keyType == "lg"):
				self.globalShortcutHash[key] = hash(tuple(value))
				core.splitList(value)
				keyboard.add_hotkey(key, self.eventHandler, args = [key], suppress = True if value[1][1] == "True" else False)
				self.commandShortcut[key] = value	
	
	def reloadShortcut(self,keyType = "lg",loadType = "c"):
		shortcut = core.loadDict("shortcut.txt")
		if not shortcut:
			return
		#清空所有快捷键，重新加载
		if loadType == "c":
			if keyType == "l" or keyType == "lg":
				for key in self.localShortcutHash.keys():
					print("删除:",key)
					self.inputEntry.unbind(key)
					del self.commandShortcut[key]
				self.localShortcutHash.clear()
				self.loadShortcut("l",shortcut)
			if keyType == "g" or keyType == "lg":	
				for key in self.globalShortcutHash.keys():
					print("删除:",key)
					keyboard.remove_hotkey(key)
					del self.commandShortcut[key]
				self.globalShortcutHash.clear()
				self.loadShortcut("g",shortcut)
			return
		#对比快捷键差异
		tmpGlobalHash = dict()
		tmpLocalHash = dict()
		for key,value in shortcut.items():
			h = hash(tuple(value))
			if value[0].endswith("True"):
				tmpGlobalHash[key] = h
			else:
				tmpLocalHash[key] = h	
		core.splitDict(shortcut)
		#删除去掉的局部快捷键
		if keyType == "l" or keyType == "lg":
			for key in list(self.localShortcutHash.keys()):
				if key not in tmpLocalHash:
					print("删除:",key)
					self.inputEntry.unbind(key)
					del self.localShortcutHash[key]
					del self.commandShortcut[key]
		#删除去掉的全局快捷键
		if keyType == "g" or keyType == "lg":
			for key in list(self.globalShortcutHash.keys()):
				if key not in tmpGlobalHash:
					print("删除:",key)
					keyboard.remove_hotkey(key)
					del self.globalShortcutHash[key]
					del self.commandShortcut[key]	
		for key,value in shortcut.items():
			#加载新的或修改的局部快捷键
			if value[0][1] == "False" and (keyType == "l" or keyType == "lg"):
				if key in self.localShortcutHash:
					if self.localShortcutHash[key] != tmpLocalHash[key]:
						print("修改:",key)
						self.localShortcutHash[key] =  tmpLocalHash[key]
						self.commandShortcut[key] = value
					continue
				print("添加:",key)
				self.inputEntry.bind(f"<{key}>", self.localEventHandler)
				self.localShortcutHash[key] =  tmpLocalHash[key]
				self.commandShortcut[key] = value
			#加载新的或修改的全局快捷键
			if value[0][1] == "True" and (keyType == "g" or keyType == "lg"):
				if key in self.globalShortcutHash:
					if self.globalShortcutHash[key] != tmpGlobalHash[key]:
						print("修改:",key)
						self.globalShortcutHash[key] = tmpGlobalHash[key]
						self.commandShortcut[key] = value
					continue
				print("添加:",key)
				keyboard.add_hotkey(key, self.eventHandler, args = [key], suppress = True if value[1][1] == "True" else False)
				self.globalShortcutHash[key] = tmpGlobalHash[key]
				self.commandShortcut[key] = value

######################################### 加载快捷键 ###########################################

######################################### 加载模块 ###########################################

	def importModule(self,name,isReload = False):
		if isReload:
			if callable(getattr(self.modules[name]["module"],"clear","")):
				try:
					self.modules[name]["module"].clear()
				except:
					core.getError()
			del sys.modules[f"module.{name}.{name}"]
			if self.modules[name]["mode"]:
				del self.hy[ self.modules[name]["mode"] ]
				del self.modeModules[ self.modules[name]["mode"] ] 
			if self.modules[name]["shortcut"]:
				self.inputEntry.unbind(f"<{self.modules[name]['shortcut']}>")
				del self.modeShortcut[ self.modules[name]['shortcut'] ]
			del self.modules[name]		
		print("导入:",name)
		try:
			m = importlib.import_module(f"module.{name}.{name}")
		except:
			core.getError()
			return
		if not isReload and name not in self.moduleList:
			self.moduleList.append(name)
		if callable(getattr(m,"init","")):
			try:
				m.init(main)
			except:
				core.getError()
				del sys.modules[f"module.{name}.{name}"]
				return	
		self.modules[name] = dict()
		self.modules[name]["module"] = m
		f = getattr(m,"functions","")
		if isinstance(f,dict):
			self.modules[name]["cmd"] = set()
			dic = m.__dict__
			for value in re.findall("#! .*? !#.*?def .*?\(",inspect.getsource(m),re.DOTALL):
				value = value.split("\n")
				if len(value) == 2:
					cmd = value[0].strip()[3:-3].split()
					func = value[1][3:-1].strip()
					for c in cmd:
						f[c] = dic[func]
					self.modules[name]["cmd"].update(cmd)
		else:
			self.modules[name]["cmd"] = getattr(m,"commands",{})
		print(self.modules[name]["cmd"])
		mode = getattr(m,"mode","")
		self.modules[name]["mode"] = mode
		self.modules[name]["color"] = ""
		self.modules[name]["shortcut"] = ""
		self.modules[name]["desc"] = getattr(m,"describe","")
		if mode:
			self.modeModules[mode] = dict()
			self.modeModules[mode]["module"] = m
			self.modeModules[mode]["color"] = m.modecolor
			self.hy[mode] = History()
			shortcut = getattr(m,"shortcut","")
			if not shortcut or shortcut in self.commandShortcut:
				return
			if shortcut not in self.modeShortcut and isinstance(shortcut,str):
				self.inputEntry.bind(f"<{shortcut}>", self.localEventHandler)
				self.modules[name]["shortcut"] = shortcut
				self.modeShortcut[shortcut] = mode			
	
	def checkModuleExist(self,name):
		if name in self.modules:
			self.importModule(name,True)
		elif os.path.isfile(f"module\\{name}\\{name}.py"):
			self.importModule(name)
		else:	
			return False
		return True

	def checkModuleName(self,name):
		if self.checkModuleExist(name):
			return True
		elif name.isnumeric() or (name.startswith("-") and name[1:].isnumeric()):
			index = core.checkIndex(int(name),len(self.moduleList))
			if index != "error":
				return self.checkModuleExist(self.moduleList[index])
		elif name.startswith("-"):
			for v in self.moduleList:
				if v.find(name[1:]) != -1:
					return self.checkModuleExist(v)

	def reloadModule(self,arg,argLen):
		if argLen == 1:
			self.loadModule("all")
		elif arg[1] =="n":
			self.loadModule("new")
		elif arg[1] =="l":
			self.printModuleList()
		elif self.checkModuleName(arg[1]):
			return
		elif arg[1] in self.config:
			[ print(m,":不存在") for m in self.config[arg[1]] if not self.checkModuleName(m) ]
		else:
			mlist = core.getInputPath(arg[1])
			if not mlist:
				self.setEntry(f"参数错误:{arg[1]}")
				return
			[ print(m,":不存在") for m in mlist if not self.checkModuleName(m) ]

	def loadModule(self,type = "auto"):
		modules = [ d for d in os.listdir("module") if os.path.exists(f"module\\{d}\\{d}.py") ]
		autoLoadList = self.config["autoload"]
		for m in modules:
			if type == "new" and m in self.moduleList:
				continue
			if type == "auto" and autoLoadList and m not in autoLoadList:
				self.moduleList.append(m)
				continue
			if type == "all" and m in self.modules:
				continue
			self.importModule(m)

######################################### 加载模块 ###########################################

	def resetMode(self,mode,color = None):
		if mode == self.currentMode:
			return True
		if mode not in self.modeModules:
			self.setEntry(f"模式错误:{mode}")
			return False
		if not color:
			color = self.modeModules[mode]["color"]
		self.lastMode = self.currentMode
		self.lastColor = self.currentColor
		self.currentMode = mode
		self.currentColor = color
		self.inputEntry.configure(highlightcolor = color)
		return True

	def printModuleList(self):
		[ print(f"{i} {v.ljust(20,' ')} {'加载' if v in self.modules else '未加载'}") for i,v in enumerate(self.moduleList,1) ]

	def printCommands(self,arg,argLen):
		if argLen == 1:
			[ print(f"{key} {value['mode']} {value['color']} {value['shortcut']}\n{value['cmd']}\n{value['desc']}\n") for key,value in self.modules.items() ]
		elif not [ print(f"{key} {value['mode']} {value['color']} {value['shortcut']}\n{value['cmd']}\n{value['desc']}\n") for key,value in self.modules.items() if arg[1] in value['cmd'] ]:
			print("未找到:",arg[1])

	def reloadConfig(self,arg,argLen):
		if not core.checkArgLength(arg,2):
			return
		p = ["","c"]
		for i in range(min(len(arg[1:]),len(p))):
			p[i] = arg[1+i]
		if p[0] == "c":
			self.config = core.loadDict("config.txt")
		elif p[0] in {"l","g","lg"}:
			self.reloadShortcut(p[0],p[1])
	
	def autoRun(self):
		try:
			autoRunList = self.config["autorun"]
			if autoRunList:
				core.splitList(autoRunList)
				self.runShortcutCmd(autoRunList)	
		except:
			core.getError()

	def call(self,mod,fname,args):
		if mod not in self.modules:
			return
		func = getattr(self.modules[mod]["module"],fname,"")
		if func and callable(func):
			try:
				return func(*args)
			except:
				pass
	
	def commandResolve(self,line):
		p = line.find(" ")
		arg = line if p == -1 else line[:p]
		isReturn = None
		index = line.rfind("|")
		if index != -1:
			key = line[index+1:].lstrip()
			if line[index-1] == "|":
				isReturn = "ap"
				line = line[:index-1]
			else:
				isReturn = "ad"
				line = line[:index]
		for value in self.modules.values():
			if arg in value["cmd"]:
				ret = value["module"].resolve(line,isReturn)
				if ret == "continue":
					continue
				if isReturn and ret:
					if key.find("\\") != -1:
						mode = "w" if isReturn == "ad" else "a"
						core.saveFile(ret,key,True,"list",mode)
					elif key == "*":
						core.appedClipboardText("\n".join(ret),isReturn)
					elif key in {"s","d","t"}:
						if isReturn == "ap":
							key = key*2
						core.setSelectedPath([key,"l"],2,value = ret,checkRepeat = False,printVal = False)
					elif key == "dp":
						core.downloadPath = ret[0]
					else:
						core.appendDict(key,core.tmpDict,isReturn,value = ret,checkRepeat = False,printVal = False)
				return True

	def runCommandList(self,arg,argLen):
		if not core.checkArgLength(arg,2):
			return
		p = ["",""]
		for i in range(min(len(arg[1:]),len(p))):
			p[i] = arg[1+i]
		if p[0] == "r":
			self.commandList = core.loadDict("command.txt")
			return
		if p[1] and p[1] not in self.modeModules:
			self.setEntry(f"模式错误:{p[1]}")
			return	
		if p[0] == "*":
			commands = core.getClipboard("list")
			if not commands:
				return
		elif p[0] in self.commandList:
			commands = self.commandList[p[0]]
		else:
			self.setEntry(f"参数错误:{p[0]}")
			return
		index = 3
		for command in commands:
			while True:
				if command.find("InputArg") != -1:
					if index >= argLen:
						print("缺少参数")
						return
					else:
						command = command.replace("InputArg",arg[index],1)
						index += 1
				else:
					break
			self.submit(None,command,p[1])

	def quit(self):
		for value in self.modules.values():
			if callable(getattr(value["module"],"clear","")):
				try:
					value["module"].clear()
				except:
					pass
		self.eventHandler("exit")
		self.window.destroy()

	def resolve(self,line):
		arg,argLen = core.getArgList(line)
		if arg[0] == "run":
			self.runCommandList(arg,argLen)
		elif arg[0] == "cmd":
			self.printCommands(arg,argLen)
		elif arg[0] == "i":
			self.reloadModule(arg,argLen)
		elif arg[0] == "r":
			self.reloadConfig(arg,argLen)
		elif arg[0] == "h":
			self.hide = True
			self.window.withdraw()
		elif arg[0] == "q":
			self.quit()
		elif core.openPath(["/"] + arg,argLen + 1):
			return
		elif core.openProgram(["e"] + arg,argLen + 1):
			return
		elif self.call("search","find",[ ["f",arg[0]],2,False ]):
			return
		else:
			core.runCommand(f"start {line}")

	def submit(self,event,line,runMode = None):
		try:
			self.clearEntry()
			mode = runMode if runMode else self.currentMode
			if line and line != "printClip":
				self.hy[mode].add(line)
			if mode != core.normalMode:
				self.modeModules[mode]["module"].resolve(line,False)
				return
			line = line.strip()
			if not line:
				return
			if self.commandResolve(line):
				return
			self.resolve(line)
		except:
			core.getError()

	def start(self):
		self.loadModule()
		self.autoRun()
		threading.Thread(target = self.eventProcessThread).start()
		self.window.mainloop()

main = Asteroid()
main.start()