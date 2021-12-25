#-*- coding : utf-8 -*-
import base64
from math import *
from . import core
from .common import funcs

keywords = {"ca","pa","<",">","2","8","10","16","cal","e64","d64","@","￥","$","gj","cq"}
describe = "在所选文件夹打开cmd或powershell，运行cmd命令，进制转换，计算器，base64编码解码，打开常用网站或搜索关键字，定时关机或重启"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] in {"ca","pa","<",">"}:
		openCmd(arg,argLen,line)
	elif arg[0] in {"2","8","10","16"}:
		convert(arg,argLen)
	elif arg[0] == "cal":
		return cal(line[4:].strip())
	elif arg[0] in {"e64","d64"}:
		b64(arg,argLen)
	elif arg[0] in {"@","￥","$"}:
		browser(arg,argLen)
	elif arg[0]in {"gj","cq"}:
		shutdown(arg,argLen)

def shutdown(arg,argLen):
	waitTime = 0
	if argLen == 2:
		if arg[1]=="a":
			core.runCommand(f"start cmd /c \"shutdown /a\"")
			return
		else:
			waitTime = funcs.getSeconds(arg[1])
			if waitTime == -1:
				return
	
	m = "s" if arg[0] == "gj" else "r"
	core.runCommand(f"start cmd /c \"shutdown /{m} /t {waitTime}\"")

def browser(arg,argLen):
	if arg[0] == "@":
		if argLen == 2 and arg[1] in core.webDict:
			core.runCommand(f"start {core.webDict[arg[1]]}")
		elif argLen == 3 and arg[2] in core.webDict:
			core.runCommand(f"start {arg[1]} {core.webDict[arg[2]]}")
	elif arg[0] == "￥" or arg[0] == "$":
		if argLen == 3 and arg[1] in core.searchDict:
			core.runCommand(f"start {core.searchDict[arg[1]]}".format(query=arg[2]))
		elif argLen == 4 and arg[2] in core.searchDict:
			core.runCommand(f"start {arg[1]} {core.searchDict[arg[2]]}".format(query=arg[3]))

def openCmd(arg,argLen,line):
	if arg[0] == "<":
		core.runCommand(f"start cmd /c \"{line[2:]}\"")
	elif arg[0] == ">":
		core.runCommand(f"start cmd /k \"{line[2:]}\"")
	else:
		dst = core.getDirPathFromClipboard() if argLen == 1 else core.getOutputDirPath(arg[1],"None","list","checkDir","dir")
		for d in dst:
			if arg[0] == "ca":
				core.runCommand(f"start cmd /k cd /d \"{d}\"",True)
			else:
				d = d.replace("\\","\\\\")
				core.runCommand(f"start powershell -NoExit -Command cd  \\\"{d}\\\"",True)	

def doConvert(src,dst,input):
	if src == "2":
		src = int(input,2)
		if dst == "8":
			return oct(src)[2:]
		elif dst == "10":
			return str(src)
		elif dst == "16":
			return hex(src)[2:].zfill(2)
	elif src == "8":
		src = int(input,8)
		if dst == "2":
			return bin(src)[2:].zfill(8)
		elif dst == "10":
			return str(src)
		elif dst == "16":
			return hex(src)[2:].zfill(2)
	elif src == "10":
		src = int(input,10)
		if dst == "2":
			return bin(src)[2:].zfill(8)
		elif dst == "8":
			return oct(src)[2:]
		elif dst == "16":
			return hex(src)[2:].zfill(2)
	elif src == "16":
		src = int(input,16)
		if dst == "2":
			return bin(src)[2:].zfill(8)
		elif dst == "8":
			return oct(src)[2:]
		elif dst == "10":
			return str(src)

def getConvered(src,dst,input,output):
	if input.isnumeric():
		try:
			out = doConvert(src,dst,input)
		except:
			print(f"输入错误:{input}")
			return "error"
		print(f"{input} ===> {out}")
		output.append(out)
		return "true"
	return "false"

def convert(arg,argLen):
	if argLen < 3:
		print(f"参数错误:{arg}")
		return
	src = arg[0]
	dst = arg[1]
	if src == dst:
		print(f"参数错误:{arg}")
		return
	if dst not in {"2","8","10","16"}:
		print(f"目标类型错误:{dst}")
		return
	paste = list()
	for num in arg[2:]:
		ret = getConvered(src,dst,num,paste)
		if ret == "true":
			continue
		elif ret == "false":
			input = core.getInputPath(num)
			for i in input:
				if i.find(" ") != -1:
					for n in i.split():
						getConvered(src,dst,n,paste)
				else:
					getConvered(src,dst,i,paste)
	core.appedClipboardText(" ".join(paste))

def cal(input):
	try:
		return core.setEntry(str(eval(input)))
	except:
		return core.setEntry(f"输入错误:{input}")

def b64(arg,argLen):
	if arg[0] == "e64":
		core.appedClipboardText(base64.b64encode(core.getOriClipboard().encode("utf-8")))
	else:
		core.appedClipboardText(base64.b64decode(core.getOriClipboard()).decode("utf-8"))