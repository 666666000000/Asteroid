#-*- coding : utf-8 -*-
import re
import uuid
import base64
import random
import string
from ..core import core

describe = "运行cmd、powershell命令，进制转换，base64编码解码，快捷打开网址，快捷搜索，快捷打开系统设置，生成随机字符串，截取字符串，提取字符串的某一列，加行号，生成请求头，提取html文本，转大小写，执行python代码片段，关机，重启"

main = ""
control = ""
url = ""
search = ""
cmd = ""
functions = dict()

def init(arg):
	global main,url,search,control,cmd
	main = arg
	url = core.loadDict("module\\tool\\url.txt")
	search = core.loadDict("module\\tool\\search.txt")
	control = core.loadDict("module\\tool\\control.txt")
	cmd = core.loadCommand("module\\tool\\command.txt")

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	return functions[arg[0]](arg,argLen,isReturn)


#! self !#
def openSelf(arg,argLen,isReturn):
	if argLen == 1:
		core.runCommand(f"start \"\" \"{core.selfPath}\"")
	else:
		for m in main.moduleList:
			if m.find(arg[1]) != -1:
				core.runCommand(f"start \"\" \"{core.selfPath}\\module\\{m}\"")
				return

#! < > !#
def openCmd(arg,argLen,isReturn):
	global cmd
	if arg[1] == "r":
		cmd = core.loadCommand("module\\tool\\command.txt")
		return
	if not core.checkArgLength(arg,3):
		return
	if arg[1] == "\\":
		dst = None
	else:
		dst = core.getOutputDirPath(arg[1],None,None,"list","checkDir","dir")
		if not dst:
			return
	if arg[2] in cmd:
		command = cmd[arg[2]]+" "
		command = replaceParm(arg[3:],command)
		if not command:
			return
	else:
		command = " ".join(arg[2:])
	if dst:
		for d in dst:
			if arg[0] == ">":
				core.runCommand(f"start cmd /k \"cd /d \"{d}\" & {command} \"",True)
			else:
				core.runCommand(f"start powershell -NoExit -Command cd \\\"{d}\\\" ; \"{command}\"",True)
	else:
		if arg[0] == ">":
			core.runCommand(f"start cmd /k \"{command}\"",True)
		else:
			core.runCommand(f"start powershell -NoExit -Command \"{command}\"",True)

def replaceParm(arg,preset):
	params = re.findall(r"Input.*? |OutputDir",preset)
	if len(params) > len(arg):
		return main.setEntry(f"缺少参数")
	for i in range(len(params)):
		if params[i].startswith("InputArg"):
			preset = preset.replace(params[i].rstrip(),arg[i],1)
		elif params[i].startswith("Input"):
			src = core.getInputPath(arg[i])
			if not src:
				return main.setEntry(f"参数错误:{arg[i]}")
			preset = preset.replace(params[i].rstrip(),src[0],1)
		elif params[i].startswith("Output"):
			output = core.getOutputDirPath(arg[i],None,None,"first","checkDir","dir")
			if output:
				preset = preset.replace(params[i],f"\"{output}\"",1)
			else:
				return main.setEntry(f"参数错误:{arg[i]}")		
	return preset

def doConvert(src,dst,number):
	src = int(number,int(src))
	if dst == "2":
		return bin(src)[2:].zfill(8)
	elif dst == "8":
		return oct(src)[2:]
	elif dst == "10":
		return str(src)
	elif dst == "16":
		return hex(src)[2:].zfill(2)

def getRet(src,dst,number,output):
	try:
		out = doConvert(src,dst,number)
	except:
		print(f"输入错误:{number}")
		return
	print(f"{number} ===> {out}")
	output.append(out)
	return

#! 2 8 10 16 !#
def convert(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = arg[0]
	dst = arg[1]
	if src == dst:
		return main.setEntry(f"参数错误:{arg}")
	if dst not in {"2","8","10","16"}:
		return main.setEntry(f"目标类型错误:{dst}")
	out = list()
	for num in arg[2:]:
		if num == "*":
			number = core.getClipboard("list")
			for i in number:
				if i.find(" ") != -1:
					for n in i.split():
						getRet(src,dst,n,out)
					out.append("\n")
				else:
					getRet(src,dst,i,out)
					out.append("\n")
		else:
			getRet(src,dst,num,out)
	if isReturn:
		return out
	else:
		core.appedClipboardText(" ".join(out))

#! e64 d64 !#
def b64(arg,argLen,isReturn):
	if arg[0] == "e64":
		data = base64.b64encode(core.getClipboard("ori").encode("utf-8"))
	else:
		data = base64.b64decode(core.getClipboard("ori")).decode("utf-8")
	if isReturn:
		return [ data ]
	else:
		core.appedClipboardText(data)

def startFirst(dic,start = 0,arg = None):
	for val in dic.values():
		if arg:
			[ core.runCommand(f"start {v}".format(query=arg)) for v in val ]
		else:
			[ core.runCommand(f"start {v}") for v in val[start:] ]
		return

def getURL(arg,dic):
	if arg == "*":
		return core.getClipboard("list")
	elif arg in dic:
		return url[arg]
	else:
		return []

#! @ ￥ $ . !#			
def quickStart(arg,argLen,isReturn):
	global url, search, control
	if  argLen == 1:
		if arg[0] == "@":
			startFirst(url)
		elif arg[0] == ".":
			startFirst(control,1)
		else:
			startFirst(search,arg = core.getClipboard("strip").replace(" ", "%20"))
	
	elif arg[1] == "l":
		if arg[0] == "@":
			dic = url
		elif arg[0] == ".":
			dic = control
		else:
			dic = search
		if argLen == 2:
			[ core.printList(k,v) for k,v in dic.items() ]	
		else:
			[ core.printList(k,v) for k,v in dic.items() if k.find(arg[2]) != -1 ]

	elif arg[1] == "r":
		if arg[0] == "@":
			url = core.loadDict("module\\tool\\url.txt")
		elif arg[0] == ".":
			control = core.loadDict("module\\tool\\control.txt")
		else:
			search = core.loadDict("module\\tool\\search.txt")

	elif arg[0] == "@":
		if argLen == 2:
			[ core.runCommand(f"start {w}") for w in getURL(arg[1],url) ]
			
		elif argLen == 3 and arg[1] in core.programDict:
			[ core.runCommand(f"\"{core.programDict[arg[1]][0]}\" {w}") for w in getURL(arg[2],url) ]
			
	elif arg[0] == "￥" or arg[0] == "$":
		if not core.checkArgLength(arg,2):
			return
		if argLen == 2:
			if arg[1] in search:
				[ core.runCommand(f"start {s}".format(query = core.getClipboard("strip").replace(" ", "%20"))) for s in search[arg[1]] ]
			else:
				startFirst(search,arg = core.getClipboard("strip").replace(" ", "%20") if arg[1] == "*" else arg[1])
		else:
			if arg[1] in core.programDict and arg[2] in search and argLen >= 4:
				[ core.runCommand(f"\"{core.programDict[arg[1]][0]}\" {s}".format(query = core.getClipboard("strip").replace(" ", "%20") if arg[3] == "*" else " ".join(arg[3:]).replace(" ", "%20") )) for s in search[arg[2]] ]
			elif arg[1] in search:
				[ core.runCommand(f"start {s}".format(query = core.getClipboard("strip").replace(" ", "%20") if arg[2] == "*" else " ".join(arg[2:]).replace(" ", "%20") )) for s in search[arg[1]] ]
			else:
				startFirst(search,arg = " ".join(arg[1:]).replace(" ", "%20"))
		
	elif arg[1] in control:
		for c in control[arg[1]][1:]:
			core.runCommand(c)
	else:
		for key in control.keys():
			if key.find(arg[1]) != -1:
				print(f"未找到{arg[1]},打开{key}")
				for c in control[key][1:]:
					core.runCommand(c)
				return
		main.setEntry(f"未找到:{arg[1]}")

def stringGenerator(length,chars):
	return ''.join(random.choice(chars) for x in range(length))

#! str !#
def getStr(arg,argLen,isReturn):
	defaultLength = 16
	if argLen == 1:
		s = stringGenerator(defaultLength, string.digits + string.ascii_letters + string.punctuation)
	else:
		if arg[1] not in {"u3","u5"}:
			length = defaultLength if argLen == 2 else int(arg[2])
		if arg[1] == "r":
			s = stringGenerator(length, string.digits + string.ascii_letters + string.punctuation)
		elif arg[1] == "rs":
			s = stringGenerator(length, string.ascii_letters)
		elif arg[1] == "rn":
			s = stringGenerator(length, string.digits)
		elif arg[1] == "i":
			if not core.checkArgLength(arg,4):
				return
			s = arg[3]
			start = int(arg[3])
			step = int(arg[4]) if argLen >= 5 else 1
			width = len(arg[3])
			for i in range(length):
				start += step
				s += f"\n{str(start).zfill(width)}"
		elif arg[1] == "u1":
			s = uuid.uuid1()
		elif arg[1] == "u3":
			if not core.checkArgLength(arg,3):
				return
			s = uuid.uuid3(uuid.NAMESPACE_DNS, arg[2])
		elif arg[1] == "u4":
			s = uuid.uuid1()
		elif arg[1] == "u5":
			if not core.checkArgLength(arg,3):
				return
			s = uuid.uuid5(uuid.NAMESPACE_DNS, arg[2])
		elif arg[1] in {"d","dt","t","ts"}:
			s = core.replaceFileName(f"<{arg[1]}>")
		else:
			return main.setEntry(f"参数错误:{arg[1]}")
	if isReturn:
		return [ s ]
	else:
		core.appedClipboardText(s)

#! substr col !#
def substrColumn(arg,argLen,isReturn):
	if not core.checkArgLength(arg,4):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	if arg[0] == "substr":
		start = int(arg[2]) - 1
		end = int(arg[3])
		dst = [ s[start:end] for s in src ]
	else:
		index = int(arg[2])
		dst = [ s.split(arg[3],index)[index-1] for s in src ]
	if isReturn:
		return dst
	else:
		core.appedClipboardText("\n".join(dst))

#! num !#
def appendNum(arg,argLen,isReturn):
	p = ["*",1,"、",1]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[1+i]
	src = core.getInputPath(arg[1])
	if not src:
		return
	start = int(p[1])
	step = int(p[3])
	for index in range(len(src)):
		src[index] = f"{start}{p[2]}{src[index]}"
		start += step
	if isReturn:
		return src
	else:
		core.appedClipboardText("\n".join(src))

#! header !#
def getHeader(arg,argLen,isReturn):
	data = core.getClipboard("list")
	if not data:
		return main.setEntry("剪贴板无数据")
	header = "header = {\n"
	try:
		for d in data:
			if d.startswith(":"):
				t = d[1:].split(":",1)
				header += f"\t':{t[0]}': '{t[1].strip()}',\n"
			else:
				t = d.split(":",1)
				header += f"\t'{t[0]}': '{t[1].strip()}',\n"
		header += "}"
	except:
		return main.setEntry("数据错误")
	core.appedClipboardText(header)

#! inner !#
def getInner(arg,argLen,isReturn):
	data = core.getClipboard("strip")
	if not data:
		return main.setEntry("剪贴板无数据")

	pattern = re.compile(r'<style.*?/style>',re.DOTALL)
	text = pattern.sub('', data)
	
	pattern = re.compile(r'<.*?>',re.DOTALL)
	text = pattern.sub('', text.replace("<p>","\n").replace("<br>","\n"))
	core.appedClipboardText(text)

#! upper lower !#
def upperLower(arg,argLen,isReturn):
	data = core.getClipboard("strip")
	if not data:
		return
	if arg[0] == "upper":
		if argLen == 1:
			data = data.upper()
		elif arg[1] == "f":
			tmp = list()
			for line in data.split("\n"):
				line = line.split(" ")
				for l in line:
					l = l.strip()
					if l:
						tmp.append(l[0].upper()+l[1:]+" ")

				tmp.append("\n")
			data = "".join(tmp)
	else:
		data = data.lower()
	if isReturn:
		return [ data ]
	else:
		core.appedClipboardText(data)

#! exec !#
def execCode(arg,argLen,isReturn):
	c = core.getClipboard("ori")
	print(c)
	exec(c)

#! gj cq !#	
def shutdown(arg,argLen,isReturn):
	waitTime = 0
	m = "s" if arg[0] == "gj" else "r"
	if argLen == 2:
		if arg[1]=="a":
			core.runCommand(f"start cmd /c \"shutdown /a\"")
			return
		else:
			waitTime = core.getSeconds(arg[1])
			if waitTime == -1:
				return
	main.quit()
	core.runCommand(f"start cmd /c \"shutdown /{m} /t {waitTime}\"")



		
	
	
	

