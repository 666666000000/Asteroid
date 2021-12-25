#-*- coding : utf-8 -*-
import os
import paramiko
from . import core

mode = "ssh"
modecolor = "#000000"
keywords = {"ex","bex","ssh"}
describe = "SSH客户端"
shortcut = "Control-s"

trans = ""
ssh = ""
sftpClient = ""

commandDict = core.loadDict("sshPreset.txt")

def exit():
	disconnect()

def reload():
	disconnect()

def resolve(line):
	if not line:
		return
	arg,argLen = core.getArgList(line)
	if arg[0] in {"s","ss","d","dd","t","tt"}:
		core.setSelectedPath(arg,argLen)
	elif arg[0] == "ssh":
		return core.setMode(mode)
	elif arg[0] == "ex":
		exec(arg,argLen,line)
	elif arg[0] == "bex":
		batchExec(arg,argLen)
	elif arg[0] == "put":
		upload(arg,argLen)
	elif arg[0] == "get":
		download(arg,argLen)
	elif arg[0] == "con":
		connect(arg[1:],argLen)
	elif arg[0] == "dis":
		disconnect()
		return core.setMode(core.normalMode)
	elif arg[0] == "cm":
		return core.changeMode(arg,argLen)
	else:
		sendCommand(line)

def connect(arg,argLen):
	if argLen < 5:
		print("缺少参数")
		return
	global trans,ssh
	try:
		trans = paramiko.Transport((arg[0],int(arg[1])))
		trans.connect(username = arg[2],password = arg[3])
	except:
		print("连接失败")
		return
	ssh = paramiko.SSHClient()
	ssh._transport = trans
	print("连接成功")
	return True

def sendCommand(line):
	stdin,stdout,stderr = ssh.exec_command(line)
	print(stdout.read().decode())

def disconnect():
	global trans,sftpClient
	if sftpClient:
		sftpClient.close()
		sftpClient = ""
	if trans:
		trans.close()
		trans = ""
	print("断开连接")
	
def upload(arg,argLen):
	global sftpClient
	if argLen < 3:
		print(f"参数错误:{arg}")
		return None,None
	src = core.getInputPath(arg[1])
	if not src:
		print("源文件错误")
		return
	dst = arg[2]

	if not sftpClient:
		sftpClient = paramiko.SFTPClient.from_transport(trans)
	for s in src:
		basename = os.path.basename(s)
		if os.path.isfile(s):
			print(f"{s} ======> {dst}/{basename}")
			sftpClient.put(s,f"{dst}/{basename}")
		else:
			sendCommand(f"mkdir -p {dst}/{basename}")
			for root,dirs,files in os.walk(s,True):
				print(f"root dir:{root}")
				for name in dirs:
					dstDir = dst + "/" + basename + os.path.join(root,name).replace(s,"").replace("\\","/")
					command = f"mkdir -p {dstDir}"
					print(command)
					sendCommand(command)
				for name in files:
					srcFile = os.path.join(root,name)
					dstFile = dst + "/" + basename + srcFile.replace(s,"").replace("\\","/")
					print(f"{srcFile} ======> {dstFile}")
					sftpClient.put(srcFile,dstFile)

def getDownloadList():
	files = core.getFilePathFromClipboard()
	if not files:
		print("参数错误")
		return
	try:
		with open(files[0], 'r',errors = 'ignore') as file:
			outlist = [ line.strip() for line in file if line.strip() ]
			file.close()
	except:
		print(f"读取文件失败:{files[0]}")
		return
	return outlist

def download(arg,argLen):
	global sftpClient
	if argLen < 3:
		print(f"参数错误:{arg}")
		return None,None
	if (arg[1] == "*" or arg[1] == "f") and arg[2] == "*":
		print("源路径不能和目标路径相同")
		return
	if arg[1] == "f":
		src = getDownloadList()
	else:
		src = core.getInputPath(arg[1])
	dst = core.getOutputDirPath(arg[2],"None","first","checkDir","dir")
	if not src or not dst:
		print(f"路径错误:{src}--{dst}")
		return
	if not sftpClient:
		sftpClient = paramiko.SFTPClient.from_transport(trans)
	for s in src:
		filename = os.path.basename(s)
		print(f"{s} ======> {dst}\\{filename}")
		sftpClient.get(s,f"{dst}\\{filename}")

def replaceArg(inputArg,command):
	alen = len(inputArg)
	argIndex = 0
	for index in range(len(command)):
		while True:
			if command[index].find("InputArg") == -1:
				break
			else:
				if argIndex >= alen:
					print(f"缺少输入参数:{command[index]}")
					return "error"
				command[index] = command[index].replace("InputArg",inputArg[argIndex],1)
				argIndex += 1
	return argIndex

def getCommandByIndex(arg):
	global commandDict
	tmp = arg.split("@")
	if len(tmp) != 2:
		return "none"
	key = tmp[0]
	try:
		index = int(tmp[1])
	except:
		return "none"
	if key in commandDict:
		length = len(commandDict[key])
		if abs(index) > length:
			print(f"序号错误:{index}--{length}")
			return "error"
		if index > 0:
			index -= 1
		return [ commandDict[key][index] ]
	return "none"

def execList(command):
	if not command:
		print("缺少命令")
		return
	for c in command:
		print(c)
		resolve(c)

def exDictCommand(arg,count = 0):
	if arg[0] in commandDict:
		command = commandDict[arg[0]].copy()
		if replaceArg(arg[1+count:],command) == "error":
			return True
		execList(command)
		return True
	elif arg[0].find("@") != -1:
		command = getCommandByIndex(arg[0])
		if command == "none":
			return False
		elif command != "error":
			if replaceArg(arg[1+count:],command) == "error":
				return True
			execList(command)
		return True
	return False

def exec(arg,argLen,line):
	global commandDict
	if argLen == 1:
		execList(core.getClipboard())	
	else: 
		if arg[1] == "r":
			commandDict = core.loadDict("sshPreset.txt")
		elif arg[1] == "l":
			core.printDict(arg[1:],argLen-1,commandDict,False)
		elif arg[1] == "*":
			command = core.getClipboard()
			if not command or replaceArg(arg[1:],command) == "error":
				return
			execList(command)		
		elif exDictCommand(arg[1:]):
			return
		else:
			c = line[3:].strip()
			if c:
				resolve(c)

def batchExec(arg,argLen):
	if argLen < 3:
		print("缺少错误")
		return
	ips = core.getInputPath(arg[1])
	if not ips:
		print(f"参数错误:{arg[1]}")
		return
	for ip in ips:
		address = ip.split()
		if len(address) != 4:
			print(f"ip错误:{ip}")
			continue
		ret = replaceArg(arg[3:],address)
		if ret == "error":
			continue
		if not connect(address,5):
			continue
		if arg[2] == "*":
			command = core.getClipboard()
			if not command or replaceArg(arg[3+ret:],command) == "error":
				disconnect()
				continue
			execList(command)	
		elif not exDictCommand(arg[2:],ret):
			print(f"参数错误{arg[2]}")
		disconnect()




