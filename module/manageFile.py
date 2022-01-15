#-*- coding : utf-8 -*-
import os
import re
import time
import random
import string
from . import core
keywords = {"cp","ms","nf","nd","enc","dec","zip","uzip","ftp","dav","m5","s1","s2","s3","s5","r1","rn"}
describe = "复制文件，镜像同步文件夹，新建文件或文件夹，加密解密文件，压缩解压缩文件，ftp/dav上传文件，Hash文件，批量重命名"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "cp":
		cp(arg,argLen)
	elif arg[0] == "ms":
		mirrorSync(arg,argLen)		
	elif arg[0] in {"nf","nd"}:
		create(arg,argLen)
	elif arg[0] in {"enc","dec"}:
		openssl(arg,argLen)
	elif arg[0] in {"zip","uzip"}:
		zipFile(arg,argLen)
	elif arg[0] in {"ftp","dav"}:
		upload(arg,argLen)
	elif arg[0] in {"m5","s1","s2","s3","s5","r1"}:
		hash(arg[0])
	elif arg[0] == "rn":
		renameFile(arg,argLen)

#########################################复制文件###########################################
def copyFile(src,dst):
	arg = ""
	for s in src:
		if os.path.isdir(s):
			dir = os.path.basename(s)
			arg += f"echo y | xcopy \"{s}\" " + "\"{0}" + f"\\{dir}\" /E /V /S /R /I /H & "
		else :
			arg += f"echo y | xcopy \"{s}\" " + "\"{0}\\\" /V /H & "
	command = ""
	for d in dst:
		command += arg.format(d)
	core.runCommand(f"start cmd /c \"{command}\"")

def cp(arg,argLen):
	if argLen != 3:
		print(f"参数错误:{arg}")
		return
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],"None","list","checkDir","dir")
	if not outDir:
		print("目标路径错误")
		return
	core.printValue("源路径",src)
	core.printValue("目标路径",outDir)
	copyFile(src,outDir)
	
#########################################复制文件###########################################


def mirrorSync(arg,argLen):
	if argLen != 3:
		print(f"参数错误:{arg}")
		return	
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],"None","list","checkDir","dir")
	if not outDir:
		print("目标路径错误")
		return
	core.printValue("源路径",src)
	core.printValue("目标路径",outDir)
	[ core.runCommand(f"start sync.bat \"{src[i]}\" \"{outDir[i]}\"") for i in range( min(len(src),len(outDir)) ) ]


########################################### 新建文件/文件夹 #############################################

def newFile(dst,isOpen,target):
	print(dst)
	template = True
	suffix = os.path.splitext(dst[0])[-1]
	if not os.path.exists(f".\\template\\t{suffix}"): 
		template = False
	command = ""
	for d in dst:
		if template:
			command += f"echo f | xcopy \"template\\t{suffix}\" \"{d}\" /Y /V & "
		else:
			command += f"cd . > \"{d}\" & "	
	core.runCommand(f"start cmd /c \"{command}\"")
	if isOpen == "False":
		return
	time.sleep(1)
	for d in dst:
		if isOpen == "o":
			core.runCommand(f"{target}\"{d}\"",True)
		elif isOpen == "od":
			dirname = os.path.dirname(d)
			core.runCommand(f"{target}\"{dirname}\"",True)

	
def create(arg,argLen):
	if argLen == 1: 
		return
	arg[1] = core.replaceFileName(arg[1])
	if arg[0] == "nd":
		isOpen = False
		if argLen == 3 and arg[2] == "o":
			isOpen = True
		dst = core.getOutputDirPath(arg[1],"None","list","checkDir","dir")
		if dst:
			core.printValue("目标路径",dst)
			if isOpen:
				[ core.runCommand(f"start \"\" \"{d}\"",True) for d in dst ]
		else:
			print(f"无效的目标路径:{arg[1]}")
	else:
		isOpen = "False"
		if argLen >= 3:
			if arg[2] == "o" or arg[2] == "od": 
				isOpen = arg[2]
		target = "start \"\" "
		if argLen == 4 and arg[2] == "o": 
			target = f"{arg[3]} "
		dst = core.getOutputDirPath(arg[1],"None","list","checkDir","file")
		if dst:
			newFile(dst,isOpen,target)	
		else:
			print(f"无效的目标路径:{arg[1]}")

########################################### 新建文件/文件夹 #############################################
def openssl(arg,argLen):
	if argLen != 4:
		print("缺少参数")
		return
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"list","checkDir","file")
	if not outDir:
		print("目标路径错误")
		return
	command = ""
	type = "e" if arg[0] == "enc" else "d"
	for out in outDir:
		for s in src:
			if os.path.isfile(s):
				dstPath = core.getOutputFilePath(out,s,"None")
				command += f"openssl enc -{type} -aes-256-cbc -in \"{s}\" -out \"{dstPath}\" -pass pass:{arg[3]} & "
	core.runCommand(f"start cmd /c \"{command}\"")
	
def hash(arg):
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

########################################### 压缩/解压缩 #############################################
def getZipDst(path):
	filepath,filename = os.path.split(path)
	name = os.path.splitext(filename)[0]
	return f"{filepath}\\{name}"

def zipFile(arg,argLen):	
	if argLen <= 2:
		command = ""
		password = f"-p{arg[1]}" if argLen == 2 and arg[1] != "*" else ""
		if arg[0] == "zip":
			src = core.getPathFromClipboard()
			if not src:
				print("源路径错误")
				return
			if argLen == 2 and arg[1] == "*":
				for s in src:
					dstPath = getZipDst(s)+".zip"
					command += f"7zG a \"{dstPath}\" \"{s}\" & "
			else :
				dstPath = getZipDst(src[0])+".zip"
				files = ""
				for f in src:
					files += f" \"{f}\""
				command = f"7zG a \"{dstPath}\"{files} {password}"				
		else:
			src = core.getFilePathFromClipboard()
			if not src:
				print("源路径错误")
				return
			if argLen == 2 and arg[1] == "*":
				for s in src:
					dstPath = getZipDst(s)
					command += f"7zG x \"{s}\" -o\"{dstPath}\" & "
			else:
				dstPath = os.path.split(src[0])[0]
				for s in src:
					command += f"7zG x \"{s}\" -o\"{dstPath}\" {password} & "
		core.runCommand(f"start cmd /c \"{command}\"")
		return
	src = core.getInputPath(arg[1])
	if arg[0] == "uzip":
		src = core.getFilePath(src)
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"list","checkDir","file")
	if not outDir:
		print("目标路径错误")
		return
	password = f"-p{arg[3]}" if argLen >= 4 else ""
	command = ""
	if arg[0] == "zip":
		if outDir[0].find("*") == -1:
			files = ""
			for f in src:
				files += f" \"{f}\""
			for out in outDir:
				command += f"7zG a \"{out}\"{files} {password} &"
		else:
			for out in outDir:
				for s in src:
					dstPath = core.getOutputFilePath(out,s,"None")
					command += f"7zG a \"{dstPath}\" \"{s}\" {password} & "
	else:
		if outDir[0].find("*") == -1:
			for out in outDir:
				for s in src:
					command += f"7zG x \"{s}\" -o\"{out}\" {password} & "
		else:
			for out in outDir:
				for s in src:
					dstPath = core.getOutputFilePath(out,s,"None")
					command += f"7zG x \"{s}\" -o\"{dstPath}\" {password} & "
	core.runCommand(f"start cmd /c \"{command}\"")
########################################### 压缩/解压缩 #############################################


######################################### FTP/DAV上传文件 ###########################################
def upload(arg,argLen):
	command = ""
	dir = arg[1] if argLen == 2 else ""
	for p in core.getPathFromClipboard():
		filename = os.path.basename(p)
		command += f"\"put \"\"{p}\"\" \"\"{dir}/{filename}\"\"\"?"
	if arg[0] == "ftp":
		core.runCommand(f"start ftp.bat {command}")
	elif arg[0] == "dav":
		core.runCommand(f"start dav.bat {command}")
######################################### FTP/DAV上传文件 ###########################################

########################################### 重命名 #############################################
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
		pos = int(tmp[0])
		return name[0:pos] + tmp[1] + name[pos:]

def replaceName(name,arg):
	if arg.find(":") == -1:
		return arg
	else:
		tmp = arg.split(":")
		return re.sub(tmp[0], tmp[1], name)

def renameFile(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return
	for srcPath in core.getPathFromClipboard():
		filepath,filename = os.path.split(srcPath)
		name,suffix = os.path.splitext(filename)
		if arg[1] == "r":
			length = 16 if argLen == 2 else int(arg[2])
			dstPath = filepath + "\\" + "".join(random.sample(string.ascii_letters + string.digits,length)) + suffix
		else:
			for i in range(1,argLen):
				if arg[i]=="l":
					name = name.lower()
				elif arg[i]=="u":
			 		name = name.upper()
				elif arg[i].startswith("."):
					suffix = arg[i]
				elif arg[i].startswith("c:"):
					name = cutName(name,arg[i][2:])
				elif arg[i].startswith("i:"):
					name = insertName(name,arg[i][2:])
				elif arg[i].startswith("r:"):
					name = replaceName(name,arg[i][2:])
			if name.find("<") != -1:
				name = core.replaceFileName(name)
			dstPath = f"{filepath}\\{name}{suffix}"
		print(f"源路径: {srcPath}")
		print(f"目标路径: {dstPath}")
		os.rename( srcPath , dstPath )
########################################### 重命名 #############################################
