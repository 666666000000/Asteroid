#-*- coding : utf-8 -*-
from ..core import core

mode = "log"
modecolor = "#d2fc69"
commands = {"log"}
describe = "写文件"
shortcut = "Control-l"
writefile = ""
main = ""

def init(arg):
	global main
	main = arg

def exit():
	global writefile
	print("退出")
	if writefile:
		print("关闭文件")
		writefile.close()
		writefile = ""

def clear():
	exit()

def resolve(line,isReturn):
	global writefile
	if writefile:
		if line:
			print(len(line))
			writefile.write(line)
		else:
			print("\n")
			writefile.write("\n")
	else:
		if not line:
			return
		arg,argLen = core.getArgList(line)
		if arg[0] == "log":
			if argLen == 1:
				main.resetMode(mode)
			else:
				files = core.getInputPath(arg[1])
				if files:
					try:
						writefile = open(files[0],"a")
					except:
						return main.setEntry("打开文件错误")
					print(f"打开文件:{files[0]}")
					main.resetMode(mode)
				else:
					main.setEntry("无文件")
		else:
			main.setEntry(f"命令错误:{arg[0]}")

