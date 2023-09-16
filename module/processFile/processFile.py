#-*- coding : utf-8 -*-
import os
import re
import time
import random
import string
from ..core import core

describe = "复制文件，镜像同步文件夹，新建文件或文件夹，加密解密文件，压缩解压缩文件，计算文件Hash，批量重命名"

functions = dict()

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	return functions[arg[0]](arg,argLen,isReturn)

#! cp !#
def copyFile(arg,argLen,isReturn):
	if argLen != 3:
		print(f"参数错误:{arg}")
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],None,None,"list","checkDir","dir")
	if not outDir:
		return
	core.printList("源路径",src)
	core.printList("目标路径",outDir)
	
	cmd = ""
	for s in src:
		if os.path.isdir(s):
			dir = os.path.basename(s)
			cmd += f"echo y | xcopy \"{s}\" " + "\"{0}" + f"\\{dir}\" /E /V /S /R /I /H & "
		else :
			cmd += f"echo y | xcopy \"{s}\" " + "\"{0}\\\" /V /H & "
	command = ""
	for d in outDir:
		command += cmd.format(d)
	core.runCommand(f"start cmd /c \"{command}\"")	

#! ms !#
def mirrorSync(arg,argLen,isReturn):
	if argLen != 3:
		print(f"参数错误:{arg}")
		return	
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],None,None,"list","checkDir","dir")
	if not outDir:
		return
	core.printList("源路径",src)
	core.printList("目标路径",outDir)
	[ core.runCommand(f"start cmd /c \"robocopy \"{src[i]}\" \"{outDir[i]}\" /MIR /DCOPY:T /COPY:DAT /A-:SH /V /XD \"System Volume Information\" $RECYCLE.BIN /R:3 /W:3\"") for i in range( min(len(src),len(outDir)) ) ]

#! nf nd !#
def create(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	p = ["","","",""]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[1+i]
	p[0] = core.replaceFileName(p[0])
	if arg[0] == "nd":
		tmp = core.getOutputDirPath(p[0],core.selfPath,"dir","list","checkDir","dir")
		if not tmp:
			return
		name = core.getClipboard("list") if p[1] == "*" else [p[1]] 
		if not name:
			return
		dst = []
		for t in tmp:
			for n in name:
				path = f"{t}\\{n}"
				if core.checkDirExist(path,"dir") and isReturn:
					dst.append(path)
		if p[2] == "o":
			[ core.runCommand(f"start \"\" \"{d}\"",True) for d in dst ]
	else:
		dst = core.getOutputDirPath(p[1],core.selfPath,"dir","list","checkDir","file")
		if not dst:
			return
		src = f".\\module\\processFile\\template\\{p[0]}{os.path.splitext(dst[0])[-1]}"
		if not os.path.exists(src): 
			src = None
		command = ""
		for d in dst:
			if src:
				command += f"echo f | xcopy \"{src}\" \"{d}\" /Y /V & "
			else:
				command += f"cd . > \"{d}\" & "	
		core.runCommand(f"start cmd /c \"{command}\"")
		if p[2]:
			time.sleep(0.5)
			p[3] = f"\"{core.programDict[p[3]][0]}\"" if p[3] in core.programDict else "start \"\" "
			if p[2] == "o":
				[ core.runCommand(f"{p[3]} \"{d}\"",True) for d in dst ]
			elif p[2] == "od":
				core.openDirPath(dst)
	if isReturn:
		return dst

#! enc dec !#
def encrypt(arg,argLen,isReturn):
	if "openssl" not in core.programDict or not core.programDict["openssl"]:
		print("openssl 路径未配置")
		return
	target = f"\"{core.programDict['openssl'][0]}\""
	if argLen != 4:
		print("缺少参数")
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","list")
	if not outDir:
		return
	dst = list()
	command = ""
	type = "e" if arg[0] == "enc" else "d"
	for out in outDir:
		for s in src:
			if os.path.isfile(s):
				dstPath = core.getOutputFilePath(out,s,"checkDir","file")
				if isReturn:
					dst.append(dstPath)
				command += f"{target} enc -{type} -aes-256-cbc -in \"{s}\" -out \"{dstPath}\" -pass pass:{arg[3]} & "
	core.runCommand(command)
	if isReturn:
		return dst

#! m5 s1 s2 s3 s5 r1 !#
def hashFile(arg,argLen,isReturn):
	command = ""
	if arg == "m5":
		alg = "md5"
	elif arg == "s1":
		alg = "sha1"
	elif arg == "s2":
		alg = "sha256"
	elif arg == "s3":
		alg = "sha384"
	elif arg == "s5":
		alg = "sha512"
	else :
		alg = "ripemd160"
	for f in core.getFilePathFromClipboard():
		command += f"get-filehash \\\"{f}\\\" -algorithm {alg}; "
	core.runCommand(f"start powershell -NoExit -Command {command}")

#! zip uzip !#
def zipFile(arg,argLen,isReturn):
	if "7zG" not in core.programDict or not core.programDict["7zG"]:
		print("7zG 路径未配置")
		return
	target = f"\"{core.programDict['7zG'][0]}\""
	ret = list()
	p = ["","*","",""]
	for i in range(min(len(arg),len(p))):
		p[i] = arg[i]
	src = ""
	if argLen <= 2:
		src = core.getPathFromClipboard()
		if not src:
			print("源路径错误")
			return	
		if p[0] == "zip":
			name = os.path.basename(src[0])
			if argLen == 1:
				p[2] = f"\\{name.rsplit('.',1)[0]}.zip"
			else:
				if p[1] == "*" :
					p[2] = "\\*.zip"
				else:
					p[1] = "*"
					p[2] = f"\\{name.rsplit('.',1)[0]}.zip"
					p[3] = p[1]
		else:
			if argLen == 1:
				p[2] = "\\"
			else:
				if p[1] == "*":
					p[2] = "\\*"
				else:
					p[1] = "*"
					p[2] = "\\"
					p[3] = p[1]			
	if not src:
		src = core.getInputPath(p[1])
		if not src:
			return
	outDir = core.getOutputDirPath(p[2],src[0],"file","list")
	if not outDir:
		return	
	if p[3]:
		p[3] = f"-p{p[3]}"
	
	command = ""
	single = True if p[2].find("*") == -1 else False
	if p[0] == "zip":
		if single:
			files = ""
			for f in src:
				files += f" \"{f}\""
			for out in outDir:
				dstPath = core.getOutputFilePath(out,src[0],"checkDir","file")
				command += f"{target} a \"{dstPath}\"{files} {p[3]} &"
				if isReturn:
					ret.append(dstPath)
		else:
			for out in outDir:
				for s in src:
					dstPath = core.getOutputFilePath(out,s,"checkDir","file")
					command += f"{target} a \"{dstPath}\" \"{s}\" {p[3]} & "
					if isReturn:
						ret.append(dstPath)
	else:
		if single:
			for out in outDir:
				if isReturn:
					ret.append(out)
				for s in src:
					command += f"{target} x \"{s}\" -o\"{out}\" {p[3]} & "
		else:
			for out in outDir:
				for s in src:
					dstPath = core.getOutputFilePath(out,s,"checkDir","dir")
					command += f"{target} x \"{s}\" -o\"{dstPath}\" {p[3]} & "
					if isReturn:
						ret.append(dstPath)
	core.runCommand(command)
	if isReturn:
		return ret

def cutName(name,arg):
	if arg.find(":") == -1:
		start = int(arg)
		if start > 0:
			name = name[start:]
		else:
			name = name[:start]
	else:
		t = arg.split(":")
		name = name[int(t[0]):int(t[1])]
	return name

def insertName(name,arg):
	if arg.find(":") == -1:
		return name + arg
	else:
		tmp = arg.split(":")
		try:
			pos = int(tmp[0])
		except:
			if tmp[0].startswith("[") and tmp[0].endswith("]"):
				tmp[0] = tmp[0][1:-1]
			pos = name.find(tmp[0])
			if pos == -1:
				print("未找到:" + tmp[0])
				return -1
			pos += len(tmp[0])
		return name[0:pos] + tmp[1] + name[pos:]

def replaceName(name,arg):
	if arg.find(":") == -1:
		return arg
	else:
		tmp = arg.split(":")
		return re.sub(tmp[0], tmp[1], name)

#! rn !#
def renameFile(arg,argLen,isReturn):
	if not core.checkArgLength(arg,2):
		return
	dst = list()
	for srcPath in core.getPathFromClipboard():
		filepath,filename = os.path.split(srcPath)
		name,suffix = os.path.splitext(filename)
		if arg[1] == "r":
			length = 16 if argLen == 2 else int(arg[2])
			dstPath = filepath + "\\" + "".join(random.sample(string.ascii_letters + string.digits,length)) + suffix
		else:
			for i in range(1,argLen):
				if arg[i] == "l":
					name = name.lower()
				elif arg[i] == "u":
					name = name.upper()
				elif arg[i].startswith("."):
					suffix = arg[i]
				elif arg[i].startswith("c:"):
					name = cutName(name,arg[i][2:])
				elif arg[i].startswith("i:"):
					name = insertName(name,arg[i][2:])
				elif arg[i].startswith("r:"):
					name = replaceName(name,arg[i][2:])
				if name == -1:
					return
			if name.find("<") != -1:
				name = core.replaceFileName(name)
			dstPath = f"{filepath}\\{name}{suffix}"
		print(f"源路径: {srcPath}")
		print(f"目标路径: {dstPath}")
		os.rename( srcPath , dstPath )
		if isReturn:
			dst.append(dstPath)
	return dst
