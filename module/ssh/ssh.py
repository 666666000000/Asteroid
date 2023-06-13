#-*- coding : utf-8 -*-
import os
import re
import time
import paramiko
import threading
from math import floor
from queue import Queue
from tkinter import ttk,Toplevel,Label,Entry,Frame,Text,WORD,END
from tkinter.constants import HORIZONTAL
from tkinter.ttk import PanedWindow
from ..history.history import History
from ..core import core

commands = {"ssh"}
describe = "SSH客户端"

main = ""
hide = ""
window = ""

sshCommand = ""
sshHost = ""
hosts = dict()

pad = 10
buttonHeight = 50
outerFrame = ""
outerWidth = 160
hostFrame = ""
hostYpos = 0
hostHeight = 30
hostPad = 2
allHostHeight = 0
centerHeight = 0
centerFrame = ""
paned = ""
outputFrame = ""
fileFrame = ""
inputEntry = ""
labels = list()
isPreset = False
currentHost = ""
selectedHost = list()
selectedBackup = list()
buttonColor = "#474747"
defaultColor = "#FAFAFA"
hy = History()

pattern1 = re.compile("\\033\[.*?m|\\033\[0m")
pattern2 = re.compile("\\r\\r|\\r\\n|\\r")

class SSH:
	def __init__(self):
		self.ip = ""
		self.port = ""
		self.username = ""
		self.password = ""
		self.connected = False
		self.transport = ""
		self.channel = ""
		self.sshClient = ""
		self.sftpClient = ""
		self.path = ""
		self.selected = False
		self.label = ""
		self.text = ""
		self.fileTree = ""
		self.ypos = 0
		self.q = Queue()
		self.pause = False
		self.stop = False
		self.fileCount = 0
		self.commands = []
		self.index = 0
		self.length = 0
		
	def connect(self):
		if self.connected:
			insertOutput(self,"\n已连接")
			return
		insertOutput(self,"连接服务器...")
		try:
			self.transport = paramiko.Transport((self.ip,self.port))
			self.transport.connect(username = self.username,password = self.password)
			self.transport.set_keepalive(60)
		except:
			insertOutput(self,core.getError(False))
			return
		self.channel = self.transport.open_session()
		self.channel.get_pty()
		self.channel.invoke_shell()
		self.sshClient = paramiko.SSHClient()
		self.sshClient._transport = self.transport
		insertOutput(self,"\n连接成功")
		self.connected = True
		if not self.selected:
			self.label.config(bg = defaultColor)
		self.fileCount = 0
		self.pause = False
		self.stop = False
		self.receive(True)
		return True

	def disconnect(self,isExit):
		if self.connected:
			if self.channel:
				self.channel.close()
				self.channel = ""
			if self.sshClient:
				self.sshClient.close()
				self.sshClient = ""
			if self.sftpClient:
				self.sftpClient.close()
				self.sftpClient = ""
			if self.transport:
				self.transport.close()
				self.transport = ""
			self.index = 0
			self.commands = []
			self.connected = False
			if not isExit:
				insertOutput(self,"\n断开连接")
				if not self.selected:
					self.label.config(bg = "red")
	
	def send(self,cmd,isAll):
		if isAll:
			self.channel.sendall(cmd + "\n")
		else:
			self.channel.send(cmd)
		self.receive(True)

	def receive(self,wait):
		if wait:
			count = 0
			while True:
				if count < 10:
					time.sleep(0.1)
					if self.channel.recv_ready():
						break
					count += 1
				else:
					return
		while self.channel.recv_stderr_ready():
			insertOutput(self,re.sub(pattern1,"",self.channel.recv_stderr(1500).decode("utf-8")),False)
		while self.channel.recv_ready():
			result = re.sub(pattern2,"\\n", re.sub(pattern1,"",self.channel.recv(1500).decode("utf-8")) )
			insertOutput(self,result,False)
			if not self.q.empty():
				return
			if self.commands:
				if not checkPause(self):
					return
				num = int(self.text.index("end").split(".")[0]) - 1
				line = self.text.get(f"{num}.0",f"{num}.0 lineend")
				if not line:
					continue
				if line.find(self.commands[self.index][1]) != -1:
					if self.index + 1 <= self.length - 1:
						sendPresetCommand(self,self.commands,self.index + 1)
					else:
						self.index = 0
						self.commands.clear()
					
def clear():
	disconnectAll()
	
def init(arg):
	global main,hy,sshCommand,sshHost
	main = arg
	sshCommand = core.splitDict(core.loadDict("module\\ssh\\command.txt"))
	sshHost = core.loadDict("module\\ssh\\host.txt")

def resolve(line,isReturn):
	global sshCommand,sshHost
	if not line:
		return
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		showWindow()
	elif arg[1] == "r":
		sshCommand = core.splitDict(core.loadDict("module\\ssh\\command.txt"))
		sshHost = core.loadDict("module\\ssh\\host.txt")
	else:
		if not core.checkArgLength(arg,3):
			return
		preset = True if arg[1] == "1" else False
		submit(None,line.split(maxsplit = 2)[2],preset)

def submit(event,line,preset):
	if not line:
		return
	try:
		if preset:
			arg,argLen = core.getArgList(line)
			if arg[0] == "del":
				delSelectedHost()
			elif arg[0] == "s":
				stopTask()
			elif arg[0] == "r":
				dispatchTask(["r"])
			elif arg[0] == "p":
				pauseTask()
			elif arg[0] == "k":
				sendControlKey(arg,argLen)
			elif arg[0] == "off":
				disconnectAll()
			else:
				dispatchTask(["send",[True,True,line]])
		else:
			dispatchTask(["send",[False,True,line]])
	except:
		core.getError()

def stopTask():
	if currentHost.pause:
		currentHost.q.put(["s"])
	else:
		currentHost.stop = True
	for host in selectedHost:
		if host.pause:
			host.q.put(["s"])
		else:
			host.stop = True

def pauseTask():
	currentHost.pause = True
	for host in selectedHost:
		host.pause = True

def sendControlKey(arg,argLen):
	if argLen < 2:
		print("缺少参数")
		return
	try:
		key = int(arg[1])
	except:
		print("参数错误:",arg[1])
		return
	dispatchTask(["send",[False,False,chr(key)]])

def disconnectAll():
	if hosts:
		selectedHost = list(hosts.values())
		selectedHost.remove(currentHost)
		dispatchTask(["exit"])
		hosts.clear()
	closewindow(isClose = "close")

def delSelectedHost():
	global currentHost
	dispatchTask(["exit"])
	delHost(currentHost)
	for host in selectedHost:
		delHost(host)
	selectedHost.clear()
	selectedBackup.clear()
	if hosts:
		ypos = hostPad
		for host in hosts.values():
			if host.ypos != ypos:
				host.label.place(y = ypos)
				host.ypos = ypos
			if ypos == hostPad:
				currentHost = host
				setCurrent(host,True)
			ypos += (hostHeight + hostPad)
	else:
		currentHost = ""
			
def delHost(host):
	ip = host.ip
	host.label.destroy()
	host.text.destroy()
	if host.fileTree:
		host.fileTree.destroy()
	del hosts[ip]
	print("删除:",ip)

def insertOutput(host,data,end = True):
	host.text.insert(END,data)
	num = int(host.text.index("end").split(".")[0])
	if num > 200:
		for i in range(1,num - 200):
			host.text.delete(f"{i}.0",f"{i}.0 lineend+1c")	
	if end:
		host.text.insert(END,"\n")
	host.text.see(END)

################ 工作线程 ################	
def workThread(host):
	host.connect()
	while True:
		try:
			try:
				data = host.q.get(timeout = 1)
			except:
				if host.connected:
					host.receive(False)
				continue
			if data[0] == "exit":
				if host.connected:
					host.disconnect(True)
				print("退出线程:",host.ip)
				return
			elif data[0] == "connect":
				host.connect()
			if not host.connected:
				continue
			if data[0] == "send":
				sendCommand(host,data[1],data[2])
			elif data[0] == "list":
				listFiles(host,data[1])
			elif data[0] == "put":
				uploadFiles(host,data[1],data[2])
			elif data[0] == "get":
				downloadFiles(host,data[1],data[2])
			elif data[0] == "disconnect":
				host.disconnect(False)
		except:
			insertOutput(host,core.getError(False))
			continue

def replaceArg(host,inputArg,command):
	alen = len(inputArg)
	argIndex = 0
	for index in range(len(command)):
		while True:
			if command[index][1].find("[ip]") != -1:
				command[index][1] = command[index][1].replace("[ip]",host.ip,1)
			if command[index][1].find("[username]") != -1:
				command[index][1] = command[index][1].replace("[username]",host.username,1)
			if command[index][1].find("[password]") != -1:
				command[index][1] = command[index][1].replace("[password]",host.password,1)
			if command[index][1].find("InputArg") == -1:
				break
			else:
				if argIndex >= alen:
					insertOutput(host,f"缺少输入参数:{command[index][1]}")
					return
				command[index][1] = command[index][1].replace("InputArg",inputArg[argIndex],1)
				argIndex += 1
	return True

def checkPause(host):
	if host.pause:
		insertOutput(host,"已暂停")
		while True:
			data = host.q.get()
			if data[0] == "r":
				insertOutput(host,"恢复任务")
				host.pause = False
				return True
			elif data[0] == "s":
				insertOutput(host,"终止任务")
				host.pause = False
				return False
			continue
	if host.stop:
		host.stop = False
		return False
	return True

def sendCommand(host,data,index):
	if host.commands:
		host.commands = []
	if not data[2]:
		host.send("\n",False)
		return
	if not data[1]:
		host.send(data[2],False)
		return
	elif not data[0]:
		host.send(data[2],True)
	else:
		arg = data[2].split()
		if arg[0].find("+") != -1:
			arg[0] = getParmByIndex(arg[0].split("+"),index)
		if arg[0] in sshCommand:
			commands = [] + sshCommand[arg[0]]
			if not replaceArg(host,arg[1:],commands):
				return
		elif arg[0] == "*":
			cmd = core.getClipboard("strip")
			if cmd:
				host.send(cmd,True)
			return
		elif arg[0] == "**":
			commands = core.splitList(core.getClipboard("list"))
			if not commands:
				return
		else:
			insertOutput(host,f"未找到:{arg[0]}")
			return
		if len(commands) > 1:
			host.commands = commands
		sendPresetCommand(host,commands,0)
		
def sendPresetCommand(host,commands,start):
	host.length = len(commands)
	for index in range(start,host.length):
		command = commands[index]
		if command[0] == "send":
			if index < host.length - 1:
				host.index = index + 1
			else:
				host.index = 0
				host.commands.clear()
			host.send(command[1],True)
			return
		elif command[0] in {"put","get"}:
			tmp = [ t.strip() for t in command[1].split(">") ]
			if len(tmp) != 2:
				continue
			if command[0] == "put":
				uploadFiles(host,[[[ tmp[0] ]],[ tmp[1] ]],1)
			else:
				downloadFiles(host,[[[ tmp[0] ]],[ tmp[1] ]],1)
	host.index = 0
	host.commands.clear()
################ 工作线程 ################	

################ 显示文件 ################	
def execCommand(host,cmd):
	stdin,stdout,stderr = host.sshClient.exec_command(cmd)
	result = stdout.read().decode("utf-8")
	error = stderr.read().decode("utf-8")
	if error:
		insertOutput(host,"错误:" + error)
	else:
		return result
					
def onDoubleClick(event):
	for item in currentHost.fileTree.selection():
		values = currentHost.fileTree.item(item, "values")
		if not values:
			return
		if values[0] == "..":
			if currentHost.path == "/":
				return
			path = os.path.dirname(currentHost.path)
			currentHost.q.put(["list",[False,path]])
			return
		values = values[0].split()
		if values[0].startswith("d"):
			if currentHost.path == "/":
				path = f"/{values[-1]}"
			else:
				path = f"{currentHost.path}/{values[-1]}"
			currentHost.q.put(["list",[False,path]])
		else:
			insertOutput(currentHost,f"路径不是文件夹:{values[-1]}")
			return

def createTree(host):
	host.fileTree = ttk.Treeview(fileFrame, show = "headings", columns = [ "1" ])
	host.fileTree.bind('<Double-1>', onDoubleClick)
	host.fileTree.insert('', 0, values = [".."])
	if host == currentHost:
		host.fileTree.pack(fill = "both",expand = "1")

def listFiles(host,data):
	if data[1]:
		if data[0]:
			src = core.getInputPath(data[1])
			if not src:
				return
			path = src[0]
		else:
			path = data[1]
	else:
		path = "/"
	result = execCommand(host,f"ls -l {path}")
	if not result:
		return
	host.path = path
	result = result.split("\n")[:-1]
	insertOutput(currentHost,result[0])
	resultCount = len(result)
	if not host.fileTree:
		createTree(host)
	host.fileTree.heading("1", text = path)
	items = host.fileTree.get_children()
	if resultCount == 1:
		for i in range(1,host.fileCount):
			host.fileTree.item(items[i],values = [])
		return
	rowCount = len(items)
	if rowCount == 1:
		for i in range(1,resultCount):
			host.fileTree.insert('', i,values = [ result[i] ])
			
	elif resultCount == rowCount:
		for i in range(1,resultCount):
			host.fileTree.item(items[i],values = [ result[i] ])
			
	elif resultCount > rowCount:
		for i in range(1,rowCount):
			host.fileTree.item(items[i],values = [ result[i] ])
		for i in range(rowCount,resultCount):
			host.fileTree.insert('', i,values = [ result[i] ])
			
	elif resultCount < rowCount:
		for i in range(1,resultCount):
			host.fileTree.item(items[i],values = [ result[i] ])
		if host.fileCount > resultCount:
			for i in range(resultCount,host.fileCount):
				host.fileTree.item(items[i],values = [])		
	host.fileCount = resultCount
################ 显示文件 ################	

################ 上传/下载 ################	
def getParmByIndex(parm,index):
	length = len(parm)
	if length == 1:
		return parm[0]
	else:
		if index > length:
			index = index%length
		return parm[index - 1]

def testPath(host,cmd):
	result = execCommand(host,cmd)
	if not result:
		return
	result = result.split("\n")
	if len(result) != 2:
		return
	return result	 

def uploadFiles(host,data,index):
	src = getParmByIndex(data[0],index)
	dst = getParmByIndex(data[1],index)
	print("上传:")
	print("源路径:",src)
	print("目标路径:",dst)
	if dst == "select":
		if host.fileTree:
			for item in host.fileTree.selection():
				values = host.fileTree.item(item, "values")
				if not values or values[0] == "..":
					continue
				values = values[0].split()
				if values[0].startswith("d"):
					if host.path == "/":
						dst = f"/{values[-1]}"
					else:
						dst = f"{host.path}/{values[-1]}"
					break
	if dst == "select":
		return
	result = testPath(host,f"test -e {dst} && echo 1 || echo 0")
	if not result or result[0] == "0":
		insertOutput(host,f"路径 {dst} 不存在")
		return
	result = testPath(host,f"test -d {dst} && echo 1 || echo 0")
	if not result or result[0] == "0":
		insertOutput(host,f"路径 {dst} 不是文件夹")
		return
	if not host.sftpClient:
		host.sftpClient = paramiko.SFTPClient.from_transport(host.transport)
	for s in src:
		if not checkPause(host):
			return
		basename = os.path.basename(s)
		if os.path.isfile(s):
			insertOutput(host,f"{s} => {dst}/{basename}")
			host.sftpClient.put(s,f"{dst}/{basename}")
		else:
			execCommand(host,f"mkdir -p {dst}/{basename}")
			for root,dirs,files in os.walk(s,True):
				for name in dirs:
					dstDir = dst + "/" + basename + os.path.join(root,name).replace(s,"").replace("\\","/")
					execCommand(host,f"mkdir -p {dstDir}")
				for name in files:
					srcFile = os.path.join(root,name)
					dstFile = dst + "/" + basename + srcFile.replace(s,"").replace("\\","/")
					insertOutput(host,f"{srcFile} => {dstFile}")
					host.sftpClient.put(srcFile,dstFile)
	
def downloadFiles(host,data,index):	
	src = getParmByIndex(data[0],index)
	dst = getParmByIndex(data[1],index)
	print("下载:")
	print("源路径:",src)
	print("目标路径:",dst)
	if not host.sftpClient:
		host.sftpClient = paramiko.SFTPClient.from_transport(host.transport)
	if src == "select":
		if host.fileTree:
			for item in host.fileTree.selection():
				values = host.fileTree.item(item, "values")
				if not values or values[0] == "..":
					continue
				values = values[0].split()
				if values[0].startswith("d"):
					if getFiles(host,host.path,values[-1],dst,"dir") == -1:
						return
				elif values[0].startswith("-"):
					if getFiles(host,host.path,values[-1],dst,"file") == -1:
						return
	else:
		for s in src:
			if not checkPause(host):
				return
			result = testPath(host,f"test -e {s} && echo 1 || echo 0")
			if not result or result[0] == "0":
				continue
			result = testPath(host,f"test -d {s} && echo 1 || echo 0")
			if not result:
				continue
			base,name = os.path.split(s)
			if result[0] == "1":
				if getFiles(host,base,name,dst,"dir") == -1:
					return
			else:
				if getFiles(host,base,name,dst,"file") == -1:
					return
	
def getFiles(host,base,name,dst,isFile):
	if not checkPause(host):
		return -1
	if base == "/":
		currentPath = f"/{name}"
	else:
		currentPath = f"{base}/{name}"
	dstPath = f"{dst}\\{name}"
	
	if isFile == "dir":
		if not core.checkDirExist(dstPath,"dir"):
			return
		result = execCommand(host,f"ls -l {currentPath}")
		if not result:
			return
		result = result.split("\n")[:-1]
		resultCount = len(result)
		if resultCount == 1:
			return
		for i in range(1,resultCount):
			files = result[i].split()
			if files[0].startswith("d"):
				if getFiles(host,currentPath,files[-1],dstPath,"dir") == -1:
					return -1
			elif files[0].startswith("-"):
				if getFiles(host,currentPath,files[-1],dstPath,"file") == -1:
					return -1
	else:
		insertOutput(host,f"{currentPath} => {dstPath}")
		host.sftpClient.get(f"{currentPath}",dstPath)
################ 上传/下载 ################	
					
def changeColor(event):
	if str(event.type) == "ButtonPress":
		core.preColor = event.widget["bg"]
		event.widget["bg"] = core.clickColor
	else:
		event.widget["bg"] = core.preColor

def multiSelect(host,isSelect):
	if isSelect:
		host.selected = True
		host.label.config(bg = buttonColor)
		selectedHost.append(host)
	else:
		host.selected = False
		if not host.connected:
			host.label.config(bg = "red")
		else:
			host.label.config(bg = defaultColor)
		selectedHost.remove(host)

def setCurrent(host,isSelect):
	if isSelect:
		host.selected = True
		host.label.config(bg = core.clickColor)
		host.text.pack(fill = "both",expand = "1")
		if host.fileTree:
			host.fileTree.pack(fill = "both",expand = "1")
	else:
		host.selected = False
		if not host.connected:
			host.label.config(bg = "red")
		else:
			host.label.config(bg = defaultColor)
		host.text.forget()
		if host.fileTree:
			host.fileTree.forget()
	
def reverseSelect(event):
	for host in hosts.values():
		if host != currentHost:
			if host.selected:
				multiSelect(host,False)
			else:
				multiSelect(host,True)
			
def reSelect(event):
	if not selectedBackup:
		return
	clearSelect()
	for host in selectedBackup:
		if host != currentHost:
			multiSelect(host,True)
	
def clearSelect():
	if selectedHost:
		if not selectedBackup:
			selectedBackup.extend(selectedHost)	
		length = len(selectedHost)
		while length > 0:
			multiSelect(selectedHost[0],False)
			length -= 1
		selectedHost.clear()

################ 事件 ################

def onHostClick(event):
	global currentHost
	ip = event.widget["text"]
	if hosts[ip] == currentHost:
		if event.num == 1:
			clearSelect()
		return
	if event.num == 1:
		clearSelect()
		setCurrent(currentHost,False)
		currentHost = hosts[ip]
		setCurrent(currentHost,True)
	else:
		if selectedBackup:
			selectedBackup.clear()
		if hosts[ip].selected:
			multiSelect(hosts[ip],False)
		else:
			multiSelect(hosts[ip],True)

def onAddClick(event):
	global currentHost,allHostHeight
	changeColor(event)
	if str(event.type) == "ButtonPress":
		line = getInputLine()
		if not line:
			return
		if isPreset:
			if line == "*":
				host = core.getClipboard("list")
			elif line in sshHost:
				host = sshHost[line]
			else:
				return
			if not host:
				return
		else:
			host = [ line ]
		ypos = hostPad + (hostHeight + hostPad)*len(hosts)
		for h in host:
			h = h.split()
			if len(h) != 4:
				continue
			l = Label(hostFrame,text = h[0], font = ("Microsoft YaHei Light", 15))
			l.place(x = 0,y = ypos, width = outerWidth, height = hostHeight) 
			l.bind("<ButtonPress-1>", onHostClick)
			l.bind("<ButtonPress-3>", onHostClick)
			ip = h[0]
			host = SSH()
			host.ip = h[0]
			host.port = int(h[1])
			host.username = h[2]
			host.password = h[3]
			host.label = l
			host.ypos = ypos
			hosts[ip] = host
			ypos += (hostHeight + hostPad)
			if currentHost:
				setCurrent(currentHost,False)
			currentHost = host
			currentHost.text = Text(outputFrame, bd = 0, bg = "#343434", fg = "#FFFFFF", highlightbackground="#828790", highlightthickness = 1, font = ("Courier New", 13), wrap = WORD)
			insertOutput(currentHost,ip)
			setCurrent(currentHost,True)
			threading.Thread(target = workThread,args = (currentHost,)).start()

		height = hostPad + (hostHeight + hostPad)*len(hosts)
		if height > allHostHeight:
			allHostHeight = height
			hostFrame.place(height = height)
		
def dispatchTask(data):
	index = 1
	if currentHost:
		print(data,index,"=>",currentHost.ip)
		currentHost.q.put(data + [index])
	for host in selectedHost:
		index += 1
		print(data,index,"=>",host.ip)
		host.q.put(data + [index])

def onConnectClick(event):
	changeColor(event)
	if str(event.type) == "ButtonPress":
		dispatchTask(["connect"])

def onDisconnectClick(event):
	changeColor(event)
	if str(event.type) == "ButtonPress":
		stopTask()
		dispatchTask(["disconnect"])

def onControlClick(event):
	changeColor(event)
	if str(event.type) == "ButtonPress":
		key = getInputLine()
		try:
			key = int(key)
		except:
			print("参数错误:",key)
			return
		dispatchTask(["send",[False,False,chr(key)]])
				
def transferFiles(isdownload):
	line = getInputLine()
	if not line:
		return
	line = [ l.strip() for l in line.split(">") ]
	src = []
	if len(line) == 1:
		if isPreset:
			if isdownload:
				src = [ "select" ]
				dst = core.getOutputDirPath(line[0],None,None,"list","checkDir","dir")
			else:
				for l in line[0].split("+"):
					src.append(core.getInputPath(l))
				dst = [ "select" ]
		else:
			if isdownload:
				src = [ "select" ]
				dst = [ line[0] ]
			else:
				src = [[ line[0] ]]
				dst = [ "select" ]
	elif len(line) == 2:
		if isPreset:
			for l in line[0].split("+"):
				src.append(core.getInputPath(l))	
			if isdownload:
				dst = core.getOutputDirPath(line[1],None,None,"list","checkDir","dir")
			else:
				dst = core.getInputPath(line[1])
		else:
			src = [[ line[0] ]]
			dst = [ line[1] ]
	else:
		return
	if not src or not dst:
		return
	if isdownload:
		dispatchTask(["get",[src,dst]])
	else:
		dispatchTask(["put",[src,dst]])

def onUploadClick(event):
	changeColor(event)
	if str(event.type) == "ButtonPress":
		transferFiles(False)

def onDownloadClick(event):
	changeColor(event)
	if str(event.type) == "ButtonPress":
		transferFiles(True)

def onListClick(event):
	changeColor(event)
	if str(event.type) == "ButtonPress":
		dispatchTask(["list",[isPreset,getInputLine()]])

def onPresetClick(event):
	global isPreset
	if isPreset:
		labels[-1].config(bg = buttonColor)
		isPreset = False
	else:
		labels[-1].config(bg = core.clickColor)
		isPreset = True

def onScroll(event):
	global hostYpos
	if event.delta > 0:
		if hostYpos < 0:
			hostYpos += (hostHeight + hostPad)
			hostFrame.place(y = hostYpos)
	else:
		if (allHostHeight + hostYpos ) > centerHeight:
			hostYpos -= (hostHeight + hostPad)
			hostFrame.place(y = hostYpos)
		
def resizeWindow(event = None):
	global centerHeight
	windowWidth = window.winfo_width()
	windowHeight = window.winfo_height()
	length = len(rightButton)
	centerWidth = windowWidth - outerWidth - pad*3
	buttonWidth = floor((centerWidth - pad*(length - 1)) / length)
	xpos = outerWidth + pad*2
	lastWidth = centerWidth - pad*(length - 1) - buttonWidth*(length - 1)
	for i in range(length):
		if i == length - 1:
			labels[i].place(x = xpos, width = lastWidth)
		else:
			labels[i].place(x = xpos, width = buttonWidth)
			xpos += (buttonWidth + pad)
	inputEntry.place(width = centerWidth) 
	ypos = buttonHeight*2 + pad*3
	centerHeight = windowHeight - ypos - pad
	outerFrame.place(height = centerHeight)
	centerFrame.place(width = centerWidth, height = centerHeight)

	
################ 事件 ################

leftButton = {"连接":onConnectClick,"断开":onDisconnectClick}
rightButton= {"添加":onAddClick,"控制键":onControlClick,"上传文件":onUploadClick,"下载文件":onDownloadClick,"显示文件":onListClick,"预设":onPresetClick}

def setEntry(line):
	if not line:
		return
	inputEntry.delete(0,END)
	inputEntry.insert(0,line)

def eventHandler(event):
	if event.keysym == "Up":
		setEntry(hy.getPre())
	elif event.keysym == "Down":
		setEntry(hy.getNext())

def getInputLine():
	line = inputEntry.get().strip()
	if not line:
		return
	inputEntry.delete(0,END)
	hy.add(line)
	return line

def showWindow():
	global window,hide,inputEntry,outerFrame,hostFrame,centerFrame,paned,outputFrame,fileFrame,currentHost,isPreset,allHostHeight
	if not window:
		window = Toplevel()
		t = floor(main.screenWidth/6)
		windowWidth = t*4
		windowXpos = t
		widowHeight = 800
		window.geometry(f"{windowWidth}x{widowHeight}+{windowXpos}+{main.yPos}")
		window.bind("<Configure>",resizeWindow)
		window.bind("<Control-r>",reverseSelect)
		window.bind("<Control-s>",reSelect)
		window.bind("<Control-d>",onPresetClick)
		window.protocol("WM_DELETE_WINDOW",closewindow)
		xpos = pad
		ypos = pad
		labels.clear()
		hide = False
		isPreset = False
		currentHost = ""
		selectedHost.clear()
		selectedBackup.clear()
		for key,value in leftButton.items():
			l = Label(window,text = key, bg = buttonColor,fg = "#FFFFFF", font = ("Microsoft YaHei Light", 15))
			l.place(x = xpos, y = ypos, width = outerWidth , height = buttonHeight)
			ypos += (buttonHeight + pad)
			l.bind("<ButtonPress-1>", value)
			l.bind("<ButtonRelease-1>", value)    
		ypos = pad
		for key,value in rightButton.items():
			l = Label(window,text = key, bg = buttonColor,fg = "#FFFFFF", font = ("Microsoft YaHei Light", 15))
			l.place(y = ypos, height = buttonHeight)
			labels.append(l)
			l.bind("<ButtonPress-1>", value)
			if key != "预设":
				l.bind("<ButtonRelease-1>", value) 
		xpos = outerWidth + pad*2
		ypos = buttonHeight + pad*2
		inputEntry = Entry(window, bd = 0, highlightbackground = "#F0F0F0", fg = core.fontColor, highlightcolor = core.normalColor, highlightthickness = 1, insertwidth = 1, justify = "center", font = ("Microsoft YaHei Light", 25))
		inputEntry.place(x = xpos,y = ypos, height = buttonHeight) 
		inputEntry.bind("<Up>", eventHandler)
		inputEntry.bind("<Down>", eventHandler)
		inputEntry.bind("<Return>", lambda event:submit(event,getInputLine(),isPreset))
		#inputEntry.bind("<Return>", submit)

		xpos = pad
		ypos = buttonHeight*2 + pad*3
		allHostHeight = widowHeight - ypos - pad

		outerFrame = Frame(window)
		outerFrame.place(x = xpos,y = ypos, width = outerWidth)
		hostFrame = Frame(outerFrame)
		hostFrame.place(x = 0,y = 0, width = outerWidth, height = allHostHeight)
		inputEntry.bind("<MouseWheel>",onScroll)
		
		xpos = outerWidth + pad*2
		centerFrame = Frame(window)
		centerFrame.place(x = xpos, y = ypos)

		paned = PanedWindow(centerFrame, orient = HORIZONTAL)
		paned.pack(fill = "both",expand="1")

		outputFrame = Frame(paned)
		fileFrame = Frame(paned)

		paned.add(outputFrame,weight = 1)
		paned.add(fileFrame,weight = 1)

		style = ttk.Style()
		style.configure("Treeview", font = ("Courier New",13))
		style.configure("Treeview.Heading", font = ("Courier New",13))	
		resizeWindow()
		core.windows.append(window)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)

def closewindow(event = None,isClose = "hide"):
	global window,hide
	if window in core.windows:
		core.windows.remove(window)
	if isClose == "close" and window:
		window.destroy()
		window = ""
	elif isClose == "hide" and not hide and window:
		window.withdraw()
		hide = True


