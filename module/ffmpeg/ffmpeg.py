#-*- coding : utf-8 -*-
import os
import re
import time
import random
import subprocess
from tkinter import Toplevel,Text,Label,Entry,END,WORD
from ..core import core

describe = "调用ffmpeg批量操作视频"
presets = ""
main = ""
hide = ""
window = ""
commandText = ""
inputLabel = list()
inputEntry = list()
labelText = ["命令","并行","输入","循环输入","输出","运行"]
target = "ffmpeg"

functions = dict()

def clear():
	closewindow(isClose = "close")

def init(arg):
	global main,presets,target
	main = arg
	presets = core.loadCommand("module\\ffmpeg\\ffmpeg.txt")
	if "ffmpeg" in core.programDict and core.programDict["ffmpeg"]:
		target = f"\"{core.programDict['ffmpeg'][0]}\""

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	return functions[arg[0]](arg,argLen,isReturn)

def getFileSequence(dir):
	files = os.listdir(dir)
	if files:
		name,suffix = os.path.splitext(files[0])
		nameLen = len(name)
		return f"{dir}\\%{nameLen}d{suffix}"

def getInputList(inputs,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL):
	for s in inputs:
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

def getIO(preset,inputPath,outputArg):
	io = list()
	firstPath =	core.getFirstPath(inputPath)
	if not firstPath : 
		firstPath = core.selfPath
	for line in preset.split("&&"):
		parm = dict()
		parm["i"] = list()
		parm["o"] = list()
		pattern = re.compile(r"Input.*? ",re.DOTALL)
		inputs = pattern.findall(line)
		if len(inputs) > 0:
			[ parm["i"].append(i[:-1]) for i in inputs ]
		pattern = re.compile(r"Output.*? ",re.DOTALL)
		outputs = pattern.findall(line)
		outlen = len(outputs)
		if outlen > 0:
			if outlen > len(outputArg):
				print(f"输出参数错误:{len(outputArg)}:{outlen}")
				return
			outIndex = 0
			for output in outputs:
				dst = core.getOutputDirPath(outputArg[outIndex],firstPath,"file","list")
				if not dst:
					return
				outIndex += 1
				t = dict()
				t["pattern"] = output[:-1]
				t["path"] = dst
				t["dstindex"] = 0
				parm["o"].append(t)
		io.append(parm)
	print(f"\nio参数:{io}\n")
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
			print("参数错误:",pattern)
			return "error",""
		try:
			inputCount = int(tmp[1])
			src = locals()[tmp[0]] if inputCount >= 0 else locals()[tmp[0].replace("Input","Loop")]
		except:
			print("配置错误:",pattern)
			return "error",""
		if not src["path"]:
			print("缺少输入:",pattern)
			return "error",""

		updateID(fid,sid,src)
		srcIndex = src["tmpindex"]
		srcPath = src["path"]
		srcLen = len(srcPath)
		if inputCount >= 0: 
			print(f"序号:{srcIndex}--文件数:{srcLen}")
			if srcIndex >= srcLen:
				print("结束循环 1")
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
				print("结束循环 2")
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
	
def replaceOutput(line,outputs,firstInputPath):
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
			print(f"输出类型错误:{argType}:{outType}")
			return "error"
		if outType != "url": 
			dstPath = core.getOutputFilePath(dstPath,firstInputPath,"checkDir","file")
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
			print("退出 1")
			return tmpLine,""

		tmpLine = replaceOutput(tmpLine,io[index]["o"],firstInputPath)
		if tmpLine == "error": 
			print("退出 2")
			return tmpLine,""
		if index == icount - 1:
			command += f"{target} {tmpLine} & "
			if not io[index]["i"]: 
				print("退出 3")
				loop = "end"	
		else:
			command += f"{target} {tmpLine} && "
		index += 1
	return loop,command

def initParm():
	t = dict()
	t["path"] = list()
	t["index"] = 0
	t["tmpindex"] = 0
	t["fid"] = 0
	t["sid"] = 0
	return t

def getCommand(c,inputs,loopInputs,preset,io,parallel):
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
	if inputs:
		getInputList(inputs,InputDir,InputImage,InputAudio,InputVideo,InputSubtitle,InputURL)
		print(f"\n输入:\n{InputDir}\n{InputImage}\n{InputAudio}\n{InputVideo}\n{InputSubtitle}\n{InputURL}")
	if loopInputs:
		getInputList(loopInputs,LoopDir,LoopImage,LoopAudio,LoopVideo,LoopSubtitle,LoopURL)
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
	if c == "fft":
		print(command)
		return
	if command:
		if parallel == "1":
			[ core.runCommand(f"start cmd /c \"{c}\"",True) for c in command.split(" & ") ]
		else:
			core.runCommand(f"start cmd /c \"{command}\"")

#! ff fft !#
def ff(arg,argLen,isReturn):
	if not core.checkArgLength(arg,2):
		return
	start = 3
	presets = core.loadCommand("module\\ffmpeg\\ffmpeg.txt")
	if not presets:
		return
	if arg[1] not in presets:
		main.setEntry(f"未找到:{arg[1]}")
		return
	inputs = ""
	if argLen >= 3 :
		inputs = core.getInputPath(arg[2])

	loopInputs = ""
	if argLen > 4 and arg[3].startswith("@"):
		start = 4
		if len(arg[3][1:]) > 0:
			loopInputs = core.getInputPath(arg[3][1:])
			if not loopInputs:
				return
		else:
			main.setEntry(f"参数错误:{arg[3]}")
			return
	io = getIO(presets[arg[1]] + " ",inputs,arg[start:])
	if not io: 
		return
	getCommand(arg[0],inputs,loopInputs,presets[arg[1]],io,presets["parallel"])

def eventHandler(event):
	if str(event.type) == "ButtonPress":
		core.preColor = color = event.widget["bg"]
		event.widget["bg"] = core.clickColor
		
		preset = commandText.get(1.0,END).strip()+" "
		c = inputEntry[0].get().strip()
		parallel = inputEntry[1].get().strip()
		inputs = inputEntry[2].get().strip()
		loopInputs = inputEntry[3].get().strip()
		outputs = inputEntry[4].get().strip()
		if inputs:
			inputs = core.getInputPath(inputs)
		if loopInputs:
			loopInputs = core.getInputPath(loopInputs)
		if outputs:
			outputs = outputs.split()
		io = getIO(preset,inputs,outputs)
		if not io:
			return
		getCommand(c,inputs,loopInputs,preset,io,parallel)
	else:
		event.widget["bg"] = core.preColor

def closewindow(event = None,isClose = "hide"):
	global window,hide
	if window in core.windows:
		core.windows.remove(window)
	if isClose == "close" and window:
		window.destroy()
		window = ""
	elif isClose == "hide" and not hide and window:
		window.withdraw()
		hide = True

def showWindow(arg):
	global window,hide,commandText
	if not window:
		hide = False
		inputLabel.clear()
		inputEntry.clear()
		textHeight = 300
		labelXpos = 25
		labelYpos = 25 + textHeight + 10
		labelWidth = 100
		labelHeight = 50
		enterXpos = 25 + labelWidth + 10
		entryWidth = main.entryWidth - enterXpos -25
		widowHeight = 25 + textHeight + 60*len(labelText) + 25

		window = Toplevel()
		window.overrideredirect(True)
		window.geometry(f"{main.entryWidth}x{widowHeight}+{main.entryXPos}+{main.yPos}")

		commandText = Text(window,bd = 0, bg = "#F6F6F6", highlightbackground = "#363636", highlightcolor = core.normalColor, highlightthickness = 1, font = ("Microsoft YaHei Light", 15), wrap = WORD)
		commandText.place(x = 25, y = 25, width = 590 , height = textHeight)
		for i in range(len(labelText)):
			if i < 5:
				l = Label(window,text = labelText[i], bg = "#BFBFBF", font = ("Microsoft YaHei Light", 15))
				l.place(x = labelXpos, y = labelYpos, width = labelWidth , height = labelHeight)

				e = Entry(window, bd = 0, bg = "#E5E5E5", fg = core.fontColor, highlightbackground = "#F0F0F0", highlightcolor = core.normalColor, highlightthickness = 1, insertwidth = 1, justify = "center", font = ("Microsoft YaHei Light", 20))
				e.place(x = enterXpos, y = labelYpos, width = entryWidth, height = labelHeight)

				labelYpos += 60
				inputLabel.append(l)
				inputEntry.append(e)
			else:
				l = Label(window,text = labelText[i], bg = "#474747",fg = "#FFFFFF", font = ("Microsoft YaHei Light", 15))
				l.place(x = labelXpos, y = labelYpos, width = 590 , height = labelHeight)
				l.bind("<ButtonPress-1>", eventHandler)
				l.bind("<ButtonRelease-1>", eventHandler)
		window.bind("<Double-Button-1>",closewindow)
		core.windows.append(window)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)
	inputEntry[0].delete(0,END)		
	inputEntry[0].insert(0,"ff")
	inputEntry[1].delete(0,END)	
	inputEntry[1].insert(0,presets["parallel"])
	commandText.delete("1.0","end")
	commandText.insert('1.0',presets[arg])

#! fu !#
def fu(arg,argLen,isReturn):
	if argLen == 1:
		for val in presets.values():
			showWindow(val)
			return
	if arg[1] == "h":
		closewindow()
	elif arg[1] == "off":
		closewindow(isClose = "close")
	elif arg[1] not in presets:
		main.setEntry(f"未找到:{arg[1]}")
		return
	else:
		showWindow(arg[1])

##############合并视频###############
def toTs(src):
	dst = list()
	command = ""
	for s in src:
		name = os.path.splitext(os.path.basename(s))[0]
		d = f"{core.selfPath}\\tmp\\{name}.ts"
		dst.append(d)
		command += f"ffmpeg -i \"{s}\" -c copy -vbsf h264_mp4toannexb \"{d}\" & "
	return command,dst

#! mv !#
def mergeVideo(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = [ s for s in core.getInputPath(arg[1]) if core.getFileType(s) == "video" ]
	if not src:
		return
	core.checkTmpDir()
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first","checkDir","file")
	if not outDir: 
		return
	dstfile = core.getOutputFilePath(outDir,src[0])
	tmpfile = ".\\tmp\\" + str(time.time()) + "-merge.txt"
	tsCommand = ""
	if not src[0].endswith(".ts"):
		tsCommand,src = toTs(src)
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
	delCommand = f"& del /q \"{core.selfPath}\\tmp\\*.*\" "
	command = f"{tsCommand}ffmpeg -f concat -safe 0 -i \"{core.selfPath}{tmpfile[1:]}\" -c copy -y \"{dstfile}\" {delCommand}"
	core.runCommand(f"start cmd /c \"{command}\"")
	if isReturn:
		return [dstfile]
##############合并视频###############

##############场景切割###############
def runFFmpeg(command):
	print(command)
	process = subprocess.Popen(command, stderr = subprocess.PIPE)
	stderr = process.communicate()
	if process.returncode  ==  0:
		return True
	else:
		print("ffmpeg错误:" , stderr.decode("utf-8"))
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
		print("读取文件错误:",path)

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

#! sc !#	
def sceneCut(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = [ s for s in core.getInputPath(arg[1]) if core.getFileType(s) == "video" ]
	if not src:
		return
	core.checkTmpDir()
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first","checkDir","dir")
	if not outDir: 
		return
	threshold = 0.3
	if argLen >= 4:
		if 0 <= float(arg[3]) <= 1: 
			threshold = float(arg[3])
	delCommand = f"del /q \"{core.selfPath}\\tmp\\*.*\""
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
				print("未找到剪切点:",s)
	if cutCommand: 
		core.runCommand(f"start cmd /c \"{cutCommand}{delCommand}\"")
		
##############场景切割###############
