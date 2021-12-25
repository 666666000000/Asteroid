#-*- coding : utf-8 -*-
from . import core
keywords = {"saveh","loadh","clearh"}
describe = "保存、加载、清空命令历史"
initArg = ["hy"]

history = ""
def init(hy):
	global history
	history = hy[0]

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "clearh":
		if argLen == 1:
			for value in history.values():
				value.clear()
		elif arg[1] in history:
			history[arg[1]].clear()
		else:
			return core.setEntry(f"未找到:{arg[1]}")
	elif arg[0] == "saveh":
		with open("history.txt", "w", encoding = 'utf-8', errors = 'ignore') as file:
			for key,value in history.items():
				file.write(f"<{key}>\n")
				history[key].save(file)
				file.write("\n")
			file.close()
	elif arg[0] == "loadh":
		mode = "" if argLen == 1 else arg[1]
		with open("history.txt", 'r', encoding = 'utf-8', errors = 'ignore') as file:
			key = ""
			skip = True
			for line in file:
				line = line.strip()
				if not line:
					continue
				if line[0] == "<" and line[-1] == ">":
					key = line[1:-1]
					if mode and key != mode:
						skip = True
						continue
					skip = False if key in history else True
				else:
					if not skip:
						history[key].add(line)
			file.close()
