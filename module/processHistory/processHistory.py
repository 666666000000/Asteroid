#-*- coding : utf-8 -*-
from ..core import core

commands = {"saveh","loadh","clearh"}
describe = "保存、加载、清空命令历史"

main = ""
history = ""
def init(arg):
	global main,history
	main = arg
	history = arg.hy

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "clearh":
		if argLen == 1:
			for value in history.values():
				value.clear()
		elif arg[1] in history:
			history[arg[1]].clear()
		else:
			main.setEntry(f"未找到:{arg[1]}")
	elif arg[0] == "saveh":
		with open("history.txt", "w", encoding = 'utf-8', errors = 'ignore') as file:
			for key,value in history.items():
				file.write(f"<{key}>\n")
				history[key].save(file)
				file.write("\n")
			file.close()
	elif arg[0] == "loadh":
		tmp = core.loadDict("history.txt")
		if not tmp:
			return
		for key,value in tmp.items():
			if key in history:
				for val in value:
					history[key].add(val)