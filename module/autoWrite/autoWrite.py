#-*- coding : utf-8 -*-
import os
import time
import keyboard
from ..core import core

commands = {"write"}
describe = "自动输出预设的文本"

def resolve(line,isReturn):
	line = line.split()
	if len(line) != 2:
		print("参数错误")
		return
	p = f"module\\autoWrite\\{line[1]}.txt"
	if not os.path.exists(p):
		print(p,"不存在")
		return
	try:
		with open(p, 'r', encoding = 'utf-8', errors = 'ignore') as file:
			data = file.read()
			time.sleep(2)
			keyboard.write(data,0.05)
			file.close()
	except:
		core.getError()
