#-*- coding : utf-8 -*-
import os
from ..core import core

commands = {"self"}
describe = "打开软件所在目录及文件"
dirs = list()

def init(arg):
	global dirs
	dirs = [ p for p in os.listdir(f"{core.selfPath}\\module") if os.path.isdir(f"{core.selfPath}\\module\\{p}") ]

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		core.runCommand(f"start \"\" \"{core.selfPath}\"")
	else:
		for d in dirs:
			if d.find(arg[1]) != -1:
				core.runCommand(f"start \"\" \"{core.selfPath}\\module\\{d}\"")
				return
