#-*- coding : utf-8 -*-
from . import core

mode = "txt"
modecolor = "#d2fc69"
keywords = {"wt"}
describe = "写txt"
shortcut = "Control-t"

writefile = ""

def exit():
	global writefile
	print("退出")
	if writefile:
		print("关闭文件")
		writefile.close()
		writefile = ""

def reload():
	exit()

def resolve(line):
	global writefile
	if writefile:
		writeToFile(line)
	else:
		if not line:
			return
		arg,argLen = core.getArgList(line)
		if arg[0] == "wt":
			if argLen == 1:
				return core.setMode(mode)
			else:
				files = core.getInputPath(arg[1])
				if files:
					try:
						writefile = open(files[0],"a")
					except:
						return core.setEntry("打开文件错误")
					print(f"打开文件:{files[0]}")
					return core.setMode(mode)
				else:
					return core.setEntry("无文件")
		elif arg[0] == "cm":
			return core.changeMode(arg,argLen)

def writeToFile(line):
	global writefile
	if line:
		print(len(line))
		writefile.write(line)
	else:
		print(f"\\n")
		writefile.write("\n")
