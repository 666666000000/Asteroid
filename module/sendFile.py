#-*- coding : utf-8 -*-
import os
import time
import socket
from . import core
keywords = {"sf"}
describe = "局域网发送文件"

exitThread = False
def resolve(line):
	import threading
	arg,argLen = core.getArgList(line)

	if argLen < 2:
		print("缺少参数")
		return
	if arg[1] == "off":
		stopSend()
		return
	src = core.getInputPath(arg[1])
	if not src:
		print("缺少源路径")
		return
	if argLen == 3:
		dst = core.getInputPath(arg[2])
		if not dst:
			print(f"目标地址错误:{arg[2]}")
			return
	else:
		dst = [" ".join(arg[2:])]
	threading.Thread(target = sendThread,args = (src,dst,str(round(time.time()*1000000)),)).start()
	
def stopSend():
	global exitThread
	exitThread = True

def sendThread(src,dst,id):
	global exitThread
	print("发送线程")
	for d in dst:
		print(f"连接到: {d}")
		if exitThread:
			print("退出发送线程")
			return
		control,transfer = login(d,id)
		if not control:
			continue
		for s in src:
			if os.path.isfile(s):
				if not sendMsg(f"file \\{os.path.basename(s)}",control):
					continue
				if not sendFile(control,transfer,s):
					continue
			else:
				sendDir(control,transfer,s)
		sendMsg("finish",control)
		closeSocket(control)
		closeSocket(transfer)
	print("发送完成")

def login(dst,id):
	d = dst.split(" ")
	dlen = len(d)
	if dlen < 2:
		return None,None
	control = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	transfer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	ip = d[0]
	port = int(d[1])
	pw = d[2] if dlen == 3 else "None"
	try:
		control.connect((ip,port))
		transfer.connect((ip,port))
	except:
		return None,None
	time.sleep(1)
	if sendMsg(f"login 0 {id} {pw}",control):
		time.sleep(1)
		if sendMsg(f"login 1 {id} {pw}",transfer):
			return control,transfer
	closeSocket(control)
	closeSocket(transfer)
	return None,None

def sendMsg(msg,control):
	print(f"发送:{msg}")
	control.send(msg.encode("utf-8"))
	print("接收")
	data = control.recv(16)
	print(data.decode("utf-8"))
	if data == b"success":
		print("success")
		return True 
	else:
		print("error")
		return False

def sendFile(control,transfer,path):
	file = open(path,"rb")
	data = file.read(1024000)
	while data:
		datalen = len(data)
		transfer.send(data)
		recvlen = 0
		while True:
			t = int(transfer.recv(32).decode("utf-8"))
			print(t)
			if recvlen + t == datalen:
				print("接收完成")
				break
			else:
				print("等待接收")
		data = file.read(1024000)
	file.close()
	if not sendMsg("done",control):
		return False
	return True

def sendDir(control,transfer,path):
	basename = os.path.basename(path)
	if not sendMsg(f"dir \\{basename}",control):
		return
	for root,dirs,files in os.walk(path,True):
		for name in dirs:
			dstDir = "\\" + basename + os.path.join(root,name).replace(path,"")
			if not sendMsg(f"dir {dstDir}",control):
				continue
		for name in files:
			srcFile = os.path.join(root,name)
			dstFile = "\\" + basename + srcFile.replace(path,"")
			if not sendMsg(f"file {dstFile}",control):
				continue
			if not sendFile(control,transfer,srcFile):
				continue

def closeSocket(sock):
	print(f"close socket :{sock}")
	sock.shutdown(socket.SHUT_RDWR)
	sock.close()

