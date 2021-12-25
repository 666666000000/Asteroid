#-*- coding : utf-8 -*-
import os
import re
import time
import base64
import socket
import requests
import threading
from . import core
from .common import funcs

keywords = {"dl","aa"}
describe = "调用命令行下载器，RPC添加Aria2c下载任务，接收浏览器批量下载"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "dl":
		download(arg,argLen)
	elif arg[0] == "aa":
		aria2(arg,argLen)

def download(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return
	preset,parallel = funcs.loadPreset(arg[1],"downloadPreset.txt")
	if preset == "error":
		print(f"载入配置错误:{arg[1]}")
		return
	params = re.findall(r"Input.*? |OutputDir",preset)
	plen = len(params)
	minLen = plen + 2
	if argLen < minLen:
		print(f"缺少参数:{argLen}---{minLen}")
		return
	argIndex = 1
	files = []
	urls = []
	for parm in params:
		if parm != "OutputDir":
			parm = parm[:-1]
		argIndex += 1
		if parm == "InputArg":
			preset = preset.replace(parm,arg[argIndex],1)
		elif parm == "InputFile":
			inputFile = core.getInputPath(arg[argIndex])
			if inputFile:
				[ files.append(f"\"{file}\" ") for file in inputFile ]
			else:
				print(f"参数错误:{arg[argIndex]}")
				return
		elif parm == "OutputDir":
			dir = core.getOutputDirPath(arg[argIndex],"None","first","checkDir","dir")
			if dir:
				print(f"下载路径:{dir}")
				preset = preset.replace(parm,f"\"{dir}\"",1)
			else:
				print(f"参数错误:{arg[argIndex]}")
				return
		elif parm == "InputURL":
			addIndex = False
			inputs = core.getInputPath(arg[argIndex])
			if inputs:
				for input in inputs:
					if input.find("<i>") != -1:
						if argLen < minLen+2:
							print(input)
							print(f"缺少序号:{argLen}---{minLen+2}")
							return
						addIndex = True
						start = int(arg[argIndex+1])
						end = int(arg[argIndex+2])
						for index in range(start,end+1):
							urls.append("\""+input.replace("<i>",str(index))+"\" ")
					else:
						urls.append(f"\"{input}\" ")
				if addIndex:
					argIndex += 2
			else:
				print(f"参数错误:{arg[argIndex]}")
				return

	if preset.startswith("aria"):
		if files:
			preset = preset.replace("InputFile"," ".join(files))
		if urls:
			preset = preset.replace("InputURL"," ".join(urls))
		#print(preset)
		core.runCommand(f"start cmd /k \"{preset}\"")
	else:
		command = ""
		if files:
			for f in files:
				command += preset.replace("InputFile",f) + " & "
		elif urls:
			for u in urls:
				command += preset.replace("InputURL",u) + " & "
		#print(command)
		if parallel == "true":
			[ core.runCommand(f"start cmd /k \"{c}\"") for c in command.split(" & ") ]
		else:
			core.runCommand(f"start cmd /k \"{command}\"")

token = ""
rpcURL = ""
def getRpcURL():
	global token,rpcURL
	if rpcURL:
		return
	rpc = core.config["rpc"][0].strip()
	p = rpc.split()
	if not p:
		rpcURL = rpc
	elif len(p) == 2:
		rpcURL = p[0].strip()
		token = p[1].strip()
	#print(token)
	#print(rpcURL)
	return True


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

def prepareData(uri,files,type,option,position):
	data = {
		"jsonrpc":"2.0",
		"id":0,
		"method":"",
		"params":[]
	}
	if type == "uri":
		data["method"] = "aria2.addUri"
	elif type == "torrent":
		data["method"] = "aria2.addTorrent"
	else:
		data["method"] = "aria2.addMetalink"

	if type == "uri":
		for u in uri:
			postRequest(data,[u],None,option,position)
			data["params"].clear()
			time.sleep(0.1)
	else:
		for file in files:
			postRequest(data,uri,file,option,position)
			data["params"].clear()
			time.sleep(0.1)

def response(data,password):
	if password and data[0] != password:
		print("密码错误")
		return
	if password:
		uri = data[1:]
	else:
		uri = data
	core.printValue("下载链接",uri)
	option = dict()
	if core.downloadPath:
		option["dir"] = core.downloadPath
	prepareData(uri,None,"uri",option,100)

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
		print("udp...")
		try:
			data,client_addr = udpServer.recvfrom(BUFSIZE)
			data = data.decode("utf-8").split(",")
			response(data,password)
		except:
			print("退出UDP线程")
			udpServer = ""
			return

def startServer():
	if udpServer:
		print("已启动")
		return
	udpIP,udpPort,password = funcs.splitAddress(core.config["udp"][0])
	if not udpIP:
		return
	getRpcURL()
	threading.Thread(target = udpRecv,args = (udpIP,udpPort,password,)).start()
	
def stopServer():
	global udpServer
	if udpServer:
		udpServer.close()
	else:
		print("未启动")

def aria2(arg,argLen):
	if argLen == 2:
		if arg[1] == "on":
			startServer()
			return
		elif arg[1] == "off":
			stopServer()
			return
	getRpcURL()
	isFile = False
	uri = []
	position = 100
	torrent = list()
	metalink = list()
	option = dict()
	if argLen >= 2:
		dst = core.getOutputDirPath(arg[1],"None","first","checkDir","dir")
		if not dst:
			print(f"输出路径错误:{arg[1]}")
			return
		option["dir"] = dst
	tmp = core.getClipboard()
	if not tmp:
		print("缺少下载链接")
		return
	if os.path.exists(tmp[0]):
		for s in core.getFilePath(tmp):
			if s.endswith(".torrent"):
				torrent.append( base64.b64encode(open(s,"rb").read()).decode("utf-8") )
			elif s.endswith(".meta4",".metalink"):
				metalink.append( base64.b64encode(open(s,"rb").read()).decode("utf-8") )

		if len(torrent) == 0 and len(metalink) == 0:
			print("缺少下载文件")
			return
		isFile = True
		if argLen >= 4:
			position = int(arg[2])
			uri = core.getInputPath(arg[3])
		elif argLen == 3:
			if arg[2].isnumeric():
				position = int(arg[2])
			else:
				uri = core.getInputPath(arg[2])
	else:
		uri = [ s.strip() for s in tmp if s.strip() ]
		if argLen >= 4:
			position = int(arg[2])
			option["out"] = arg[3]
		elif argLen == 3:
			if arg[2].isnumeric():
				position = int(arg[2])
			else:
				option["out"] = arg[2]
	if isFile:
		if torrent:
			prepareData(uri,torrent,"torrent",option,position)
		if metalink:
			prepareData(uri,metalink,"metalink",option,position)
	else:
		prepareData(uri,None,"uri",option,position)

