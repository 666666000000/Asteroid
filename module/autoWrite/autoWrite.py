#-*- coding : utf-8 -*-
import os
import time
import keyboard
import threading
from queue import Queue
from ..core import core

commands = {"w"}
describe = "自动输出预设的文本"
content = ""
running = False
q = Queue()

def clear():
	if running:
		q.put(["exit"])

def init(arg):
	global content
	content = core.loadDict("module\\autoWrite\\content.txt")
	threading.Thread(target = writeThread).start()

def resolve(line,isReturn):
	global content
	line = line.split()
	if len(line) != 2:
		print("参数错误")
		return
	if line[1] == "r":
		content = core.loadDict("module\\autoWrite\\content.txt")
		return
	elif line[1] == "on":
		if not running:
			threading.Thread(target = writeThread).start()
		else:
			print("正在运行")
		return
	elif line[1] == "off":
		if running:
			q.put(["exit"])
		else:
			print("已停止")
		return
	if not running:
		print("未启动")
		return
	data = ["",""]
	if line[1] == "*":
		data[0] = "*"
	elif os.path.exists(f"module\\autoWrite\\{line[1]}.txt"):
		data[0] = "file"
		data[1] = f"module\\autoWrite\\{line[1]}.txt"
	elif line[1] in content:
		data[0] = "key"
		data[1] = line[1]
	else:
		for k in content.keys():
			if k.find(line[1]) != -1:
				data[0] = "key"
				data[1] = k
				break
		if not data[0]:
			return
	q.put(data)

def writeThread():
	global running
	running = True
	print("进入线程")
	while True:
		try:
			data = q.get()
			if data[0] == "exit":
				running = False
				print("退出线程")
				return
			if data[0] == "*":
				d = core.getClipboard("ori")
			elif data[0] == "file":
				with open(data[1], 'r', encoding = 'utf-8', errors = 'ignore') as file:
					d = file.read()
					file.close()	
			elif data[0] == "key":
				d = "\n".join(content[data[1]])
			if not d:
				continue
			for i in range(1,4):
				print(i)
				time.sleep(1)
			keyboard.write(d,0.05)
		except:
			core.getError()
			continue