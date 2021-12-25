#-*- coding : utf-8 -*-
import socket
import threading
from . import core
from .common import funcs

keywords = {"rf"}
describe = "局域网接收文件"

tcpServer = ""
ids = dict()
savePath = ""

def resolve(line):
	global tcpServer,savePath
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		if tcpServer:
			print("接收线程已启动")
		else:
			print("接收线程未启动")
		return
	if arg[1] == "off":
		stopServer()
	elif arg[1] == "on":
		startServer(arg,argLen)
	else:
		savePath = core.getOutputDirPath(arg[1],"None","first","checkDir","dir")
		if not savePath:
			print(f"保存路径错误:{arg[1]}")
			return
		print(f"保存路径:{savePath}")

def stopServer():
	global tcpServer
	if tcpServer:
		tcpServer.close()
	else:
		print("接收线程未启动")	

def startServer(arg,argLen):
	global tcpServer,savePath
	if tcpServer:
		print("接收线程已启动")
		return
	if not savePath:	
		print("保存路径错误")
		return
	if argLen == 2:
		ip,port,pw = funcs.splitAddress(core.config["tcp"][0])
	elif argLen == 3:
		address = core.getInputPath(arg[2])
		if not address:
			print("ip地址错误")
			return
		ip,port,pw = funcs.splitAddress(address[0])
	else:
		ip = arg[2]
		port = arg[3]
		pw = arg[4] if argLen == 5 else ""
	print(ip,port,pw,sep=" ")	
	threading.Thread(target = acceptThread,args = (savePath,ip,port,pw,)).start()

def acceptThread(dstpath,ip,port,pw):
	global tcpServer,ids
	tcpServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	tcpServer.bind((ip,port))
	tcpServer.listen(2)
	while True:
		print("等待连接...")
		try:
			client,addr = tcpServer.accept()
		except:
			print("accept error")
			tcpServer = ""
			ids.clear()
			return
		threading.Thread(target = recvThread,args = (client,pw,dstpath,)).start()

def addID(id,type,val):
	global ids
	if id not in ids:
		ids[id] = dict()
	if type == 0:
		ids[id]["control"] = val
	elif type == 1:
		ids[id]["transfer"] = val
	else:
		ids[id]["file"] = val

def delID(id):
	global ids
	if id in ids:
		del ids[id]
		
def closeSocket(sock):
	sock.shutdown(socket.SHUT_RDWR)
	sock.close()

def recvThread(client,pw,dstpath):
	global ids
	login = False
	mode = ""
	id = ""
	print(f"接收线程 :{client}")
	while True:
		try:
			msg = client.recv(1024000)
		except:
			print("recv error")
			return
		if not msg:
			print("recv 0")
			return
		if not login:
			if msg.startswith(b"login"):
				tmp = msg.split(b" ")
				if pw and tmp[-1] != pw.encode("utf-8"):
					print("密码错误")
					closeSocket(client)
					return
				login = True
				mode = tmp[1]
				id = tmp[2]
				if mode == b"0":
					addID(id,0,client)
					addID(id,2,"")
				else:
					addID(id,1,client)
				client.send(b"success")
			else:
				print("参数错误")
				client.send(b"error")
				closeSocket(client)
				return	
		else:
			if mode == b"0":
				if msg.startswith(b"dir"):
					dst = dstpath + msg[7:].decode("utf-8").rstrip()
					print("目标文件夹:"+dst)
					if core.checkDstDir(dst):
						client.send(b"success")
					else:
						client.send(b"error")
				elif msg.startswith(b"file"):
					dst = dstpath + msg[8:].decode("utf-8").rstrip()
					print("目标文件:"+dst)
					if ids[id]["file"]:
						ids[id]["file"].close()
					try:
						ids[id]["file"] = open(dst,"wb")
					except:
						client.send(b"error")
						ids[id]["file"] = ""
						continue
					client.send(b"success")
				elif msg.startswith(b"done"):
					if ids[id]["file"]:
						ids[id]["file"].close()
						ids[id]["file"] = ""
					client.send(b"success")
				elif msg.startswith(b"finish"):
					client.send(b"success")
					closeSocket(client)
					closeSocket(ids[id]["transfer"])
					delID(id)
					return
				else:
					print("参数错误:"+msg.decode("utf-8"))	
			else:
				recvLen = len(msg)
				ids[id]["file"].write(msg)
				client.send(str(recvLen).encode("utf-8"))



