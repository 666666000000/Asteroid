#-*- coding : utf-8 -*-
import os
import re
import time
import random
import subprocess
from . import core
from .common import funcs

keywords = {"ff","sc","mv"}
describe = "调用ffmpeg拼接视频、场景切割、批量转换视频"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "ff":
		ff(arg,argLen)
	elif arg[0] == "mv":
		mergeVideo(arg,argLen)
	elif arg[0] == "sc":
		sceneCut(arg,argLen)

def getFileSequence(dir):
	files = os.listdir(dir)
	if files:
		name,suffix = os.path.splitext(files[0])
		nameLen = len(name)
		return f"{dir}\\%{nameLen}d{suffix}"

def getInputList(src,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL):
	for s in src:
		t = core.getFileType(s)
		if t == "error": 
			continue
		if t == "dir":
			seq = getFileSequence(s)
			if seq :
				InputDir["path"].append(seq)
		elif t == "image":
			InputImage["path"].append(s)
		elif t == "audio":
			InputAudio["path"].append(s)
		elif t == "video":
			InputVideo["path"].append(s)
		elif t == "subtitle":
			InputSubtitle["path"].append(s)
		elif t == "url":
			InputURL["path"].append(s)

def getIO(preset,src,arg,argLen,outStart):
	io = list()
	for tmp in preset.split("&&"):
		parm = dict()
		parm["i"] = list()
		parm["o"] = list()
		pattern = re.compile(r"Input.*? ",re.DOTALL)
		inputs = pattern.findall(tmp)
		if len(inputs) > 0:
			[ parm["i"].append(i[:-1]) for i in inputs ]
		pattern = re.compile(r"Output.*? ",re.DOTALL)
		outputs = pattern.findall(tmp)
		outlen = len(outputs)
		if outlen > 0:
			if outlen > argLen - outStart:
				print(f"输出参数错误:{argLen - outStart}---{outlen}")
				return
			outIndex = outStart
			for output in outputs:
				dst = core.getOutputDirPath(arg[outIndex],src,"list","None","None")
				if not dst:
					print(f"输出路径错误:{arg[outIndex]}")
					return
				outIndex += 1
				t = dict()
				t["pattern"] = output[:-1]
				t["path"] = dst
				t["dstindex"] = 0
				parm["o"].append(t)
		io.append(parm)
	return io

def updateID(fid,sid,src):
	if src["fid"] != fid:
		src["fid"] = fid
		src["sid"] = sid
		src["index"] = src["tmpindex"]
	else:
		if src["sid"] != sid:
			src["sid"] = sid
			src["tmpindex"] = src["index"]

def replaceInput(input,line,fid,sid,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL,LoopDir,LoopImage,LoopAudio,LoopVideo,LoopSubtitle,LoopURL):
	firstInputPath = ""
	for pattern in input["i"]:
		tmp = list()
		if pattern.find("*") == -1:
			tmp.append(pattern)
			tmp.append(1)
		else:
			tmp = pattern.split("*")
		if len(tmp) != 2:
			print(f"参数错误:{pattern}")
			return "error",""
		try:
			inputCount = int(tmp[1])
			src = locals()[tmp[0]] if inputCount >= 0 else locals()[tmp[0].replace("Input","Loop")]
		except:
			print(f"配置错误:{pattern}")
			return "error",""
		if not src["path"]:
			print(f"缺少输入:{pattern}")
			return "error",""

		updateID(fid,sid,src)
		srcIndex = src["tmpindex"]
		srcPath = src["path"]
		srcLen = len(srcPath)
		if inputCount >= 0: 
			print(f"srcIndex:{srcIndex}--srcLen:{srcLen}")
			if srcIndex >= srcLen:
				print("break -1")
				return "break",""
			if not firstInputPath:
				firstInputPath = srcPath[srcIndex]
		if inputCount == 0:
			for i in range(srcIndex,srcLen):
				if i == srcLen-1:
					line = line.replace(f"{pattern}",f"-i \"{srcPath[i]}\"",1)
				else:
					line = line.replace(f"{pattern}",f"-i \"{srcPath[i]}\" {pattern}",1)
			src["tmpindex"] = srcLen	
		elif inputCount > 0:
			if (srcIndex + inputCount) > srcLen:
				print("break -2")
				return "break",""
			for i in range(inputCount):
				if i == inputCount-1:
					line = line.replace(f"{pattern}",f"-i \"{srcPath[srcIndex+i]}\"",1)
				else:
					line = line.replace(f"{pattern}",f"-i \"{srcPath[srcIndex+i]}\" {pattern}",1)
			src["tmpindex"] += inputCount
		else:
			inputCount = abs(inputCount)
			for i in range(inputCount):
				if i == inputCount-1:
					line = line.replace(f"{pattern}",f"-i \"{srcPath[srcIndex]}\"",1)
				else:
					line = line.replace(f"{pattern}",f"-i \"{srcPath[srcIndex]}\" {pattern}",1)
				srcIndex += 1
				if srcIndex >= srcLen:
					srcIndex = 0
			src["tmpindex"] = srcIndex
	return line,firstInputPath
	
def replaceOutput(line,outputs,inputPath):
	for output in outputs:
		dstindex = output["dstindex"]
		outLen = len(output["path"])
		dstPath = output["path"][dstindex]
		if outLen > 1:
			output["dstindex"] += 1
			if output["dstindex"] == outLen: 
				output["dstindex"] = 0	
		outType = output['pattern'].replace("Output","").lower()
		argType = core.getFileType(dstPath)
		if argType != outType:
			print(f"输出类型错误:{argType}---{outType}")
			return "error"
		if outType != "url": 
			dstPath = core.getOutputFilePath(dstPath,inputPath,"checkDir")
			if not dstPath:
				return "error"
		line = line.replace(f"{output['pattern']}",f"\"{dstPath}\"",1)
	return line

def replaceIO(io,preset,fid,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL,LoopDir,LoopImage,LoopAudio,LoopVideo,LoopSubtitle,LoopURL):
	icount = len(io)
	index = 0
	command = ""
	loop = "loop"
	sid = 0
	for line in preset.split("&&"):
		tmpLine,firstInputPath = replaceInput(io[index],line,fid,sid,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL,LoopDir,LoopImage,LoopAudio,LoopVideo,LoopSubtitle,LoopURL)
		sid += 1
		if tmpLine in {"break","error"}:
			print("exit -1")
			return tmpLine,""

		tmpLine = replaceOutput(tmpLine,io[index]["o"],firstInputPath)
		if tmpLine == "error": 
			print("exit -2")
			return tmpLine,""
		if index == icount-1:
			command += f"ffmpeg {tmpLine} & "
			if not io[index]["i"]: 
				print("exit -3")
				loop = "end"	
		else:
			command += f"ffmpeg {tmpLine} && "
		index += 1
	return loop,command

def checkInputArg(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return "error","","","",""
	outStart = 3
	preset,parallel = funcs.loadPreset(arg[1],"ffmpegPreset.txt")
	if preset=="error":
		print(f"载入配置错误:{arg[1]}")
		return "error","","","",""
	src = ""
	if argLen >= 3 :
		src = core.getInputPath(arg[2])
		if not src: 
			print(f"缺少源文件:{arg[2]}")
	loop = ""
	if argLen > 4 and arg[3].startswith("@"):
		outStart = 4
		if len(arg[3][1:]) > 0:
			loop = core.getInputPath(arg[3][1:])
			if not loop:
				print(f"源文件错误:{arg[3]}")
				return "error","","","",""
		else:
			print(f"参数错误:{arg[3]}")
			return "error","","","",""
	first =	core.getFirstPath(src)
	if not first : 
		first = os.path.dirname(__file__)
	io = getIO(preset,first,arg,argLen,outStart)
	if not io: 
		return "error","","","",""
	return src,loop,preset,io,parallel


def initParm():
	t = dict()
	t["path"] = list()
	t["index"] = 0
	t["tmpindex"] = 0
	t["fid"] = 0
	t["sid"] = 0
	return t

def ff(arg,argLen):
	src,loop,preset,io,parallel = checkInputArg(arg,argLen)
	if src == "error": 
		return
	InputDir = initParm()
	InputImage = initParm()
	InputAudio = initParm()
	InputVideo = initParm()
	InputSubtitle = initParm()
	InputURL = initParm()

	LoopDir = initParm()
	LoopImage = initParm()
	LoopAudio = initParm()
	LoopVideo = initParm()
	LoopSubtitle = initParm()
	LoopURL = initParm()
	if src:
		getInputList(src,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL)
		print(f"\n输入:\n{InputDir}\n{InputImage}\n{InputAudio}\n{InputVideo}\n{InputSubtitle}\n{InputURL}")
	if loop:
		getInputList(loop,LoopDir,LoopImage,LoopAudio,LoopVideo,LoopSubtitle,LoopURL)
		print(f"\n循环输入:\n{LoopDir}\n{LoopImage}\n{LoopAudio}\n{LoopVideo}\n{LoopSubtitle}\n{LoopURL}")
	print(f"\nio参数:{io}\n")
	command = ""
	fid = 0
	while True:
		loop,line = replaceIO(io,preset,fid,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL,LoopDir,LoopImage,LoopAudio,LoopVideo,LoopSubtitle,LoopURL)
		fid += 1
		print(loop)
		print(line)
		if loop == "error":
			return
		elif loop == "break":
			break
		elif loop == "loop":
			command += line
		elif loop == "end":
			command += line
			break
	if command:
		if parallel == "true":
			[ core.runCommand(f"start cmd /c \"{c}\"",True) for c in command.split(" & ") ]
		else:
			core.runCommand(f"start cmd /c \"{command}\"")


##############合并视频###############
def toTs(src,currentPath):
	dst = list()
	command = ""
	for s in src:
		name = os.path.splitext(os.path.basename(s))[0]
		d = f"{currentPath}\\tmp\\{name}.ts"
		dst.append(d)
		command += f"ffmpeg -i \"{s}\" -c copy -vbsf h264_mp4toannexb \"{d}\" & "
	return command,dst


def mergeVideo(arg,argLen):
	if argLen < 3 :
		print(f"参数错误:{arg}")
		return
	src = [ s for s in core.getInputPath(arg[1]) if core.getFileType(s) == "video" ]
	if not src:
		print(f"源文件错误:{arg[1]}")
		return
	core.checkTmpDir()
	outDir = core.getOutputDirPath(arg[2],src[0],"first","checkDir","file")
	if not outDir: 
		return
	dstfile = core.getOutputFilePath(outDir,src[0],"None")
	currentPath = os.path.dirname(os.path.dirname(__file__))
	tmpfile = ".\\tmp\\" + str(time.time()) + "-merge.txt"
	tsCommand = ""
	if not src[0].endswith(".ts"):
		tsCommand,src = toTs(src,currentPath)
		if not tsCommand or not src:
			print("临时文件错误")
			return
	if argLen >= 4 and arg[3] == "r": 
		random.shuffle(src)	
	try:
		with open(f"{tmpfile}", 'w', encoding='utf-8', errors='ignore') as file:
			[ file.write(f"file \'{s}\'\n") for s in src ]	
			file.close()
	except:
		print("写入临时文件失败")
		return
	delCommand = f"& del /q \"{currentPath}\\tmp\\*.*\" "
	command = f"{tsCommand}ffmpeg -f concat -safe 0 -i \"{currentPath}{tmpfile[1:]}\" -c copy -y \"{dstfile}\" {delCommand}"
	core.runCommand(f"start cmd /c \"{command}\"")
##############合并视频###############


##############场景切割###############
def runFFmpeg(command):
	print(command)
	process = subprocess.Popen(command, stderr = subprocess.PIPE)
	stderr = process.communicate()
	if process.returncode  ==  0:
		return True
	else:
		print("ffmpeg错误:" + stderr.decode("utf-8"))
		return False

def getPtsTime(path,threshold):
	output = list()
	try:
		with open(path, 'r', encoding = 'utf-8', errors = 'ignore') as file:
			while True:
				frame = file.readline().strip()
				lavfi = file.readline().strip()
				if not frame or not frame.startswith("frame") or not lavfi or not lavfi.startswith("lavfi"):
					break
				pts_time = frame[frame.rfind(":") + 1:]
				scene_score = lavfi[lavfi.rfind("=") + 1:]
				if float(scene_score) >= threshold: 
					output.append(pts_time)	
			file.close()
			print(output)
			return output	
	except:
		print(f"读取文件错误:{path}")

def cutVideo(video,pts,output):
	starttime = 0
	count = len(pts)
	name,suffix = os.path.splitext(os.path.basename(video))
	command = ""
	to = "-to {0} "
	tmptime = ""
	for i in range(count + 1):
		if i == count :
			endtime = ""
		else:
			tmptime = pts[i]
			endtime = to.format(tmptime)

		dstfile = f"{output}\\{name}-{i+1}{suffix}"
		command += f"ffmpeg -i \"{video}\" -ss {starttime} {endtime}-y \"{dstfile}\" & "
		starttime = tmptime
	return command
	
def sceneCut(arg,argLen):
	if argLen < 3 :
		print(f"参数错误:{arg}")
		return
	src = [ s for s in core.getInputPath(arg[1]) if core.getFileType(s) == "video" ]
	if not src:
		print(f"源文件错误:{arg[1]}")
		return
	core.checkTmpDir()
	outDir = core.getOutputDirPath(arg[2],src[0],"first","checkDir","dir")
	if not outDir: 
		return
	threshold = 0.3
	if argLen >= 4:
		if 0 <= float(arg[3]) <= 1: 
			threshold = float(arg[3])
	delCommand = f"del /q \"{os.path.dirname(os.path.dirname(__file__))}\\tmp\\*.*\""
	cutCommand = ""
	for s in src:
		tmpfile = "./tmp/" + str(time.time()) + "-split.txt"
		command = f"ffmpeg -i \"{s}\" -vf select='gte(scene,0)',metadata=print:file=\"{tmpfile}\" -an -f null -"
		if not runFFmpeg(command): 
			return
		ptsTime = getPtsTime(tmpfile,threshold)
		if ptsTime: 
			cutCommand += cutVideo(s,ptsTime,outDir)
		else:
			if isinstance(ptsTime,list):
				print(f"{s}:未找到剪切点")
	if cutCommand: 
		core.runCommand(f"start cmd /c \"{cutCommand}{delCommand}\"")
		
##############场景切割###############
