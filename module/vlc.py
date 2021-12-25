#-*- coding : utf-8 -*-
import re
import os
import time
import socket
from urllib.parse import unquote
from . import core

mode = "vlc"
modecolor = "#f57d00"
keywords = {"vlc"}
describe = "控制VLC播放器"
shortcut = "Control-m"

playlist = dict()
player = None

playerError = False
pause = False
on = False

repeat = False
loop = False
rand = False
fullScreen = False

def exit():
	turnOff()

def reload():
	turnOff()

def resolve(line):
	global pause,repeat,loop,rand,on,fullScreen
	if not line:
		return
	arg,argLen = core.getArgList(line)
	if arg[0] == "vlc":
		if argLen == 1:
			return core.setMode(mode)
		arg = arg[1:]
		argLen -= 1
		line = line[4:]
	if arg[0] == "play":
		if pause:
			sendData("pause",True,False)
			pause = False
		else:
			sendData("play",True,False)
	elif arg[0] == "pause":
		if pause:
			pause = False
		else:
			pause = True
		sendData("pause",True,False)
	elif arg[0] == "stop":
		sendData("stop",True,False)
	elif arg[0] == "repeat":
		setRepeat(True)
	elif arg[0] == "loop":
		setRepeat(False)
		setRand(False)
		setLoop(True)
	elif arg[0] == "rand":
		setRepeat(False)
		setLoop(True)
		setRand(True)
	elif arg[0] == "n":
		sendData("next",True,False)
	elif arg[0] == "p":
		sendData("prev",True,False)
	elif arg[0] == "pl":
		[ print(f"{key}:{value}") for key,value in playlist.items() ]
	elif arg[0] == "on":
		return turnOn(arg,argLen)
	elif arg[0] == "off":
		return turnOff()
	elif arg[0] == "fs":
		if fullScreen:
			fullScreen = False
			sendData("f off",False,False)
		else:
			fullScreen = True
			sendData("f on",False,False)
	elif argLen == 2 and arg[0] in {"l","sk","v","vu","vd","f","t","go","cm","sleep"}:
		if arg[0] == "l":
			return loadList(arg[1])
		elif arg[0] == "sk":
			sendData(f"seek {arg[1]}",True,False)
		elif arg[0] == "v":
			sendData(f"volume {arg[1]}",True,False)
		elif arg[0] == "vu":
			sendData(f"volup {arg[1]}",True,False)
		elif arg[0] == "vd":
			sendData(f"voldown {arg[1]}",True,False)
		elif arg[0] == "f" or arg[0] == "b":
			seek(arg[0],int(arg[1]))
		elif arg[0] == "t":
			getTime()
		elif arg[0] == "go":
			index = int(arg[1])
			if index not in playlist:
				return core.setEntry("序号错误")
			sendData(f"goto {index}",True,False)
		elif arg[0] == "cm":
			return core.setMode(arg[1])
		elif arg[0] == "sleep":
			time.sleep(int(arg[1]))
	else:
		name = line.replace("*",".*?")
		l = list(filter( lambda x : re.match(f".*{name}.*",x[1],flags = re.IGNORECASE) != None, playlist.items()))
		if not l:
			return core.setEntry(f"未找到:{line}")
		[ print(value) for value in l ]
		sendData(f"goto {l[0][0]}",True,False)

def getPlayList(path):
	global playlist
	playlist.clear()
	with open(path, 'r', encoding = 'utf-8') as file:
		items = re.findall("\<location\>.*?\<",file.read())
		id = 1
		for item in items:
			playlist[id] = unquote(item[item.rfind("/")+1:-1], 'utf-8')
			id += 1
	[ print(f"{key}:{value}") for key,value in playlist.items() ]

def sendData(msg,recvData,returnData):
	global playerError,player
	if playerError:
		return "error"
	if not on:
		print("VLC未启动")
		return
	print(f"send :{msg}")
	player.send((f"{msg}\n").encode())
	if recvData:
		print("recv...")
		try:
			data = player.recv(1024)
		except socket.timeout as e:
			err = e.args[0]
			if err == 'timed out':
				print("接收超时")
				return "error"
			else:
				playerError = True
				return "error"
		except socket.error as e:
			print("scoket 错误:") 
			print(e)
			playerError = True
			return "error"
		else:
			print(data.decode())
			if returnData:
				return data.decode()
			
def loadList(name,start = False):
	if not on:
		return core.setEntry("VLC未启动")
	inputpath = core.getInputPath(name)
	if not inputpath:
		return core.setEntry("未找到文件")
	path = ""
	for p in inputpath:
		if os.path.isfile(p) and p.endswith("xspf"):
			path = p
			break
	if not path:
		return core.setEntry("未找到播放列表")
	sendData("clear",True,False)
	getPlayList(path)
	sendData(f"add \"{path}\"",True,False)
	if start:
		time.sleep(2)
		sendData("play",True,False)

def turnOn(arg,argLen):
	global player,playerError,on
	if playerError:
		return core.setEntry("播放器错误")
	if on:
		return core.setEntry("VLC已启动")
	os.popen("start /min vlc -I rc --rc-host localhost:65500")
	time.sleep(1)
	player = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	player.settimeout(5)

	try:
		player.connect(("localhost",65500))
	except:
		playerError = True
		return core.setEntry("连接错误")
	on = True
	if argLen >= 2:
		start = True if argLen == 3 and arg[2] == "p" else False
		loadList(arg[1],start)

def turnOff():
	global on,pause,repeat,loop,rand,fullScreen,player
	if on:
		sendData("quit",False,False)
		time.sleep(0.2)
		player.close()
		player = ""
		on = False
		pause = False
		repeat = False
		loop = False
		rand = False
		fullScreen = False
	else:
		return core.setEntry("播放器未启动")
	return core.setMode(core.normalMode)

def getTime():
	msg = ""
	while True:
		msg = sendData("get_time",True,True)
		if msg == "error":
			return
		if msg.find("End") != -1 or msg.find("stop") != -1:
			print("重新获取时间")	
			continue
		else:
			break
	msg = msg.split("\n")
	if len(msg)<2:
		print("消息错误")
		return -1
	t = int(msg[-2])
	return t

def seek(forword,step):
	current = getTime()
	if not current or current<0:
		print("时间错误")
		return
	if forword == "f":
		current += step
	else:
		current -= step
		if current<0:
			current=0
	sendData(f"seek {current}",True,False)

def setRepeat(isOn):
	global repeat
	if isOn:
		if not repeat:
			repeat = True
			sendData("repeat on",True,False)
	else:
		if repeat:
			repeat = False
			sendData("repeat off",True,False)

def setLoop(isOn):
	global loop
	if isOn:
		if not loop:
			loop = True
			sendData("loop on",True,False)
	else:
		if loop:
			loop = False
			sendData("loop off",True,False)

def setRand(isOn):
	global rand
	if isOn:
		if not rand:
			rand = True
			sendData("random on",True,False)
	else:
		if rand:
			rand = False
			sendData("random off",True,False)

