#-*- coding : utf-8 -*-
import os
import sys
import time
import base64
import socket
import requests
import importlib
import threading
from tkinter import Toplevel,Label,Entry
from ..core import core
from . import downloader

commands = {"aa","dl","du"}
describe = "批量下载"

main = ""
filters = dict()
filterList = list()
config = ""
hide = ""
window = ""
inputLabel = list()
inputEntry = list()
labelText = ["下载命令","过滤器","源路径","保存路径","参数","运行"]

def clear():
	if filters:
		for value in filters.values():
			print(f"删除 {value['filename']}")
			del sys.modules[f"module.download.filter.{value['filename']}"]
		filters.clear()
		filterList.clear()
	stopServer()
	exitThread()
	closewindow(isClose = "close")

def init(arg):
	global main,config
	main = arg
	config = core.loadDict("module\\download\\config.txt")
	serachFilter()
				
def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "aa":
		return aria2(arg,argLen, r = isReturn)
	elif arg[0] == "dl":
		return download(arg,argLen, r = isReturn)
	elif arg[0] == "du":
		du(arg,argLen)

threads = list()
def exitThread():
	for t in threads:
		t["off"] = True
		t["event"].set()
	threads.clear()

def download(arg,argLen,s = None,r = None):
	parm = getParm(arg,argLen,s)	
	if not parm:
		return
	if r and "names" in parm[1]:
		dst = list()
		for index in range(len(parm[1]["names"])):
			dst.append(f"{parm[2]}\\{parm[1]['names'][index]}")
	
	#传递参数到下载线程
	for t in threads:
		if not t["event"].is_set():
			#下载参数
			t["filter"] = parm[0]
			t["data"] = parm[1]
			t["dst"] = parm[2]
			t["current"] = 0
			
			t["event"].set()
			if r:
				return dst
			return
	t = dict()
	t["off"] = False
	t["index"] = len(threads)+1
	t["event"] = threading.Event()
	#下载参数
	t["filter"] = parm[0]
	t["data"] = parm[1]
	t["dst"] = parm[2]
	t["current"] = 0
	
	t["event"].set()
	threads.append(t)
	threading.Thread(target = downloadThread,args = (t,)).start()
	if r:
		return dst

def importModule(name):
	module = importlib.import_module(f"module.download.filter.{name}")
	tmp = dict()
	tmp["filename"] = name
	tmp["module"] = module
	filters[name.split("-",1)[0]] = tmp

def serachFilter(name = None):
	filelist = os.listdir("module/download/filter")
	found = False
	for file in filelist:
		if os.path.isfile(f"module/download/filter/{file}") and file.endswith(".py") and file != "__init__.py":
			filterName = file[:-3]
			if name:
				if filterName not in filterList:
					filterList.append(filterName)
					if not found and filterName.startswith(f"{name}-"):
						importModule(filterName)
						found = True
			else:
				filterList.append(filterName)	
	return found
	
def importFilter(name):
	for f in filterList:
		if f.startswith(f"{name}-"):
			print(f"导入:{f}")
			importModule(f)
			return True
	return serachFilter(name)

def downloadThread(parm):
	while True:
		if not parm["event"].is_set():
			print(f"线程 {parm['index']} 等待任务")
			parm["event"].wait()
		if parm["off"]:
			print(f"退出线程 {parm['index']}")
			return
		print(f"线程 {parm['index']} 开始下载")
		if callable(getattr(filters[parm["filter"]]["module"],"start","")):
			filters[parm["filter"]]["module"].start(parm)
		else:
			header = getattr(filters[parm["filter"]]["module"],"header","")
			if not header:
				parm["event"].clear()
				continue
			downloader.start(parm,header)
		parm["event"].clear()

def getParm(arg,argLen,s):
	p = ["dl","d","*","dp"]
	for i in range(min(len(arg),len(p))):
		p[i] = arg[i]
	if p[0] == "dl":
		if p[1] == "off":
			exitThread()
			return
		elif p[1] == "l":
			for t in threads:
				if t["event"].is_set():
					print(f"线程: {t['index']}: 正在运行 {t['current'] + 1}/{len(t['data']['urls'])}")
				else:
					print(f"线程: {t['index']}: 等待任务")
			return
		elif p[1] in {"s","re","rs"}:
			if p[2] != "*":
				try:
					p[2] = int(p[2])
				except:
					main.setEntry(f"参数错误:{p[2]}")
					return
			for t in threads:
				if p[2] != "*" and p[2] != t["index"]:
					continue
				if p[1] == "s":
					t["event"].clear()
				elif p[1] == "re":
					t["event"].set()
				elif p[1] == "rs":
					t["current"] = 0
					t["event"].set()
			return
	elif p[0] == "aa":
		if p[1] == "on":
			startServer()
			return
		elif p[1] == "off":
			stopServer()
			return
		
	if p[1] not in filters and not importFilter(p[1]):
		main.setEntry(f"参数错误:{p[1]}")
		return
	if p[2] == "*":
		src = core.getClipboard("strip")
		srcType = "str"
	elif p[2] == "u":
		src = s
		srcType = "urls"
	elif p[2] == "h":
		src = s
		srcType = "htmls"	
	else:
		src = core.getInputPath(p[2])
		srcType = "htmls"
	if not src:
		print("未找到下载链接")
		return
	dst = core.getOutputDirPath(p[3],None,None,"first","checkDir","dir")
	if not dst:
		return
	data = filters[p[1]]["module"].getUrl(arg,argLen,src,dst,srcType)
	if not data:
		main.setEntry("未找到下载链接")
		return
	return [p[1],data,dst] + arg[4:]

udpServer = ""
def udpRecv(udpIP,udpPort,password):
	global udpServer
	BUFSIZE = 8192
	if not udpIP or udpPort == 0:
		print("udp地址错误")
		return
	try:
		udpServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		udpServer.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFSIZE)
		udpServer.bind((udpIP, udpPort))
	except:
		print("网络错误")
		return
	while True:
		print("等待数据...")
		try:
			data,client_addr = udpServer.recvfrom(BUFSIZE)
		except:
			print("退出UDP线程")
			udpServer = ""
			return
			
		data = data.decode("utf-8").split(" ")
		if data[0] != password:
			print("密码错误")
			continue
		argLen = int(data[1])
		arg = data[2:argLen+2]
		uri = data[argLen+2:]
		print(arg)
		print(uri)
		try:
			if arg[0] == "aa":
				aria2(arg,argLen,uri)
			else:
				download(arg,argLen,uri)
		except:
			print("下载错误")
			
token = ""
rpcURL = ""
def getRpcURL():
	global token,rpcURL
	if rpcURL:
		return
	rpc = config["rpc"][0].split()
	rpcURL = rpc[0].strip()
	if len(rpc) == 2:
		token = rpc[1].strip()
	
def startServer():
	if udpServer:
		print("已启动")
		return
	tmp = config["udp"][0].split()
	if len(tmp) != 3:
		return
	getRpcURL()
	threading.Thread(target = udpRecv,args = (tmp[0],tmp[1],tmp[2],)).start()
	
def stopServer():
	global udpServer
	if udpServer:
		udpServer.close()
	else:
		print("未启动")

def postRequest(data,uri,file,option,position):
	global token,rpcURL
	data["id"] = str(round(time.time()*1000000))
	if token:
		data["params"].append(f"token:{token}")
	if file:
		data["params"].append(file)
	data["params"].append(uri)
	data["params"].append(option)
	data["params"].append(position)
	ret = requests.post(rpcURL, json = data)
	print(ret.status_code)
	if ret.status_code != 200:
		print("requests 错误")
	time.sleep(2)

def prepareData(uri,files,uriType,option,position,names = None):
	data = {
		"jsonrpc":"2.0",
		"id":0,
		"method":"",
		"params":[]
	}
	if uriType == "uri":
		data["method"] = "aria2.addUri"
	elif uriType == "torrent":
		data["method"] = "aria2.addTorrent"
	else:
		data["method"] = "aria2.addMetalink"

	if uriType == "uri":
		for index in range(len(uri)):
			if names:
				option["out"] = names[index]
			postRequest(data,[uri[index]],None,option,position)
			data["params"].clear()
	else:
		for file in files:
			postRequest(data,uri,file,option,position)
			data["params"].clear()

def aria2(arg,argLen,s = None,r = None):
	#获取链接		
	parm = getParm(arg,argLen,s)
	if not parm:
		return
	argLen = len(parm)
	#获取rpc地址
	getRpcURL()
	
	#下载参数
	dst = list()
	uri = []
	position = 100
	torrent = list()
	metalink = list()
	option = dict()
	names = ""
	
	#下载数据是一个列表
	if isinstance(parm[1],list):
		src = parm[1]
	#下载数据是一个字典
	elif isinstance(parm[1],dict):
		src = parm[1]["urls"]
		if "names" in parm[1]:
			names = parm[1]["names"]
			if r:
				for index in range(len(names)):
					dst.append(f"{parm[2]}\\{names[index]}")
	else:
		main.setEntry("输入类型错误")
		
	#保存文件夹
	option["dir"] = parm[2]
	#文件路径
	if parm[0] == "f":
		for s in core.getFilePath(src):
			if s.endswith(".torrent"):
				torrent.append( base64.b64encode(open(s,"rb").read()).decode("utf-8") )
			elif s.endswith(".meta4",".metalink"):
				metalink.append( base64.b64encode(open(s,"rb").read()).decode("utf-8") )

		if len(torrent) == 0 and len(metalink) == 0:
			main.setEntry("缺少下载文件")
			return
		if argLen >= 4:
			uri = core.getInputPath(parm[3])
		if torrent:
			prepareData(uri,torrent,"torrent",option,position)
		if metalink:
			prepareData(uri,metalink,"metalink",option,position)	
		
	#网络链接
	else:
		uri = [ s.strip() for s in src if s.strip() ]
		prepareData(uri,None,"uri",option,position,names)
	return dst

def du(arg,argLen):
	if not core.checkArgLength(arg,2):
		return
	if arg[1] == "h":
		closewindow()
	elif arg[1] == "on":
		showWindow()
	elif arg[1] == "off":
		closewindow(isClose = "close")
	else:
		main.setEntry(f"参数错误:{arg[1]}")

def eventHandler(event):
	if str(event.type) == "ButtonPress":
		core.preColor = event.widget["bg"]
		event.widget["bg"] = core.clickColor
		
		arg = [ "dl","","*","dp","" ]
		for i in range(5):
			val = inputEntry[i].get().strip()
			if val:
				arg[i] = val
		if arg[0] not in {"dl","aa"}:
			main.setEntry(f"参数错误:{arg[0]}")
			return
		if not arg[1]:
			main.setEntry("缺少参数")
			return
		main.submit(None," ".join(arg),core.normalMode)
	else:
		event.widget["bg"] = core.preColor

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

def showWindow():
	global window,hide
	if not window:
		hide = False
		inputLabel.clear()
		inputEntry.clear()

		labelXpos = 25
		labelYpos = 25
		labelWidth = 100
		labelHeight = 50
		enterXpos = 25 + labelWidth + 10
		entryWidth = main.entryWidth - enterXpos -25
		widowHeight = 25 + 60*6 + 15

		window = Toplevel()
		window.overrideredirect(True)
		window.geometry(f"{main.entryWidth}x{widowHeight}+{main.entryXPos}+{main.yPos}")

		for i in range(len(labelText)):
			if i < 5:
				l = Label(window,text = labelText[i], bg = "#BFBFBF", font = ("Microsoft YaHei Light", 15))
				l.place(x = labelXpos, y = labelYpos, width = labelWidth , height = labelHeight)

				e = Entry(window, bd = 0, bg = "#E5E5E5", fg = core.fontColor, highlightbackground = "#F0F0F0", highlightcolor = core.normalColor, highlightthickness = 1, insertwidth = 1, justify = "center", font = ("Microsoft YaHei Light", 20))
				e.place(x = enterXpos, y = labelYpos, width = entryWidth, height = labelHeight)
				
				labelYpos += 60
				inputLabel.append(l)
				inputEntry.append(e)
			else:
				l = Label(window,text = labelText[i], bg = "#474747",fg = "#FFFFFF", font = ("Microsoft YaHei Light", 15))
				l.place(x = labelXpos, y = labelYpos, width = 590 , height = labelHeight)
				l.bind("<ButtonPress-1>", eventHandler)
				l.bind("<ButtonRelease-1>", eventHandler)
		window.bind("<Double-Button-1>",closewindow)
		core.windows.append(window)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)

