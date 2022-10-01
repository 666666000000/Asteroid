#-*- coding : utf-8 -*-
import os
import time
import shlex

initArg = ["window"]
keywords = {"s","ss","d","dd","t","tt","ad","ap","clr","del","sp","list","index","dp","gd","sleep","printClip"}
describe = "操作路径字典及临时路径"

window = ""
selectedSrc = list()
selectedDst = list()
selectedTmp = list()
indexNum = 0
indexLen = 0
downloadPath = ""
config = ""
pathDict = ""
webDict = ""
searchDict = ""
normalMode = "n"
normalColor = "#0078D7"

def resolve(line):
	global pathDict
	arg,argLen = getArgList(line)
	if arg[0] in {"s","ss","d","dd","t","tt"}:
		setSelectedPath(arg,argLen)
	elif arg[0]	in {"ad","ap","clr","del","list","sp"}:
		setPath(arg,argLen)
	elif arg[0] == "index":
		setIndex(arg,argLen)
	elif arg[0] == "dp":
		setDownloadPath(arg,argLen)
	elif arg[0] == "gd":
		copyDictToClipboard(arg,argLen)
	elif arg[0] == "sleep":
		time.sleep(int(arg[1]))
	elif arg[0] == "printClip":
		printClipboard()

def init(w):
	global window,pathDict,webDict,searchDict
	window = w[0]
	pathDict = loadDict("pathDict.txt")
	webDict = loadURL("web.txt")
	searchDict = loadURL("search.txt")

def loadConfig():
	global config
	config = loadDict("config.txt")

def splitStr(line):
	lex = shlex.shlex(line)
	lex.whitespace = ' '
	lex.quotes = '"'
	lex.whitespace_split = True
	return list(lex)

def getArgList(line):
	arg = splitStr(line)
	if line.find("\"") != -1:
		arg = [ a.replace("\"","") for a in arg ]
	return arg,len(arg)

def loadURL(path):
	dic = dict()
	try:
		with open(path, 'r', encoding = 'utf-8', errors = 'ignore') as file:
			for line in file: 
				line = line.split()
				if len(line) == 2: 
					dic[line[0]] = line[1]	
	except:
		print(f"读取 {path} 错误")
	return dic

def loadDict(path):
	dic = dict()
	key = ""
	try:
		with open(path, 'r', encoding = 'utf-8', errors = 'ignore') as file:
			skip = False
			for line in file: 
				line = line.strip()
				if not line:
					continue
				if line[0] == "#":
					skip = True
					continue
				if line[0] == "<" and line[-1] == ">":
					key = line[1:-1]
					dic[key] = list()
					skip = False
				else:
					if skip:
						continue
					val = line.strip()
					if val:
						dic[key].append(val)
					
	except:
		print(f"读取 {path} 错误")
	return dic

def saveDict(path,dic):
	with open(path, "w", encoding = 'utf-8', errors = 'ignore') as file:
		for key,value in dic.items():
			file.write(f"<{key}>\n")
			for v in value:
				file.write(f"{v}\n")
			file.write("\n")


def writeTXT(path,input,overWrite = False):
	mode = "w" if overWrite else "a"
	with open(path, mode, encoding = 'utf-8', errors = 'ignore') as file:
		file.write(input)

def runCommand(command,sleep = False):
	print(command)
	os.popen(command)
	if sleep: 
		time.sleep(0.5)

def setIndex(arg,argLen):
	global indexNum , indexLen
	if argLen == 1:
		print("序号："+ str(indexNum).zfill(indexLen))
		return
	indexNum = int(arg[1])
	indexLen = len(arg[1])
	print("序号："+ str(indexNum).zfill(indexLen))

def setDownloadPath(arg,argLen):
	global downloadPath
	isOpen = False
	if argLen == 1:
		path = getOutputDirPath("*","None","first","checkDir","dir")
	elif argLen == 2:
		if arg[1] == "o":
			path = getOutputDirPath("*","None","first","checkDir","dir")
			isOpen = True
		else:
			path = getOutputDirPath(arg[1],"None","first","checkDir","dir")
	else:
		path = getOutputDirPath(arg[1],"None","first","checkDir","dir")
		isOpen = True
	if path:
		downloadPath = path
		print(f"下载路径: {path}")
		if isOpen:
			runCommand(f"start \"\" \"{path}\"")

def openDictPath(arg,argLen):
	path = getPathFromDict(arg[0])
	if path:
		target = arg[1] if argLen == 2 else "start \"\""
		if target == "od":
			lastPath = ""
			for p in path:
				dirpath = os.path.dirname(p)
				if lastPath == dirpath:
					continue
				lastPath = dirpath
				runCommand(f"start \"\" \"{dirpath}\"")
		else:
			[ runCommand(f"{target} \"{p}\"",True) for p in path ]
		return True
	return False

def copyDictToClipboard(arg,argLen):
	if argLen < 2:
		print("缺少参数")
		return
	path = getPathFromDict(arg[1])
	if path:
		appedClipboardText("\n".join(path))

def checkTmpDir():
	if not os.path.exists("tmp"): 
		os.makedirs("tmp")
			
def replaceFileName(file):
	global indexNum , indexLen
	t = time.localtime()
	if file.find("<i>") != -1:
		file = file.replace("<i>",str(indexNum).zfill(indexLen))
		indexNum += 1
	file = file.replace("<dt>",time.strftime("%Y-%m-%d-%H-%M-%S",t))
	file = file.replace("<d>",time.strftime("%Y-%m-%d",t))
	file = file.replace("<t>",time.strftime("%H-%M-%S",t))
	file = file.replace("<ts>",str(round(time.time()*1000000)))
	return file

def getOriClipboard():
	try:
		return window.clipboard_get()
	except:
		print("读取剪贴板错误")

def getClipboard():
	try:
		path = window.clipboard_get().replace("\"","").split("\n")
		return [ p.strip() for p in path if p.strip() ]
	except:
		print("读取剪贴板错误")

def printClipboard():
	printValue("剪贴板",getClipboard())

def clearClipboard():
	window.clipboard_clear()

def appedClipboardText(text,clear = True):
	if clear: 
		window.clipboard_clear()
	print(text)
	window.clipboard_append( text )

def checkDstDir(path):
	if not os.path.exists(path):
		os.makedirs(path)
		print(f"建立文件夹: {path}")
	elif os.path.isfile(path):
		print(f"无效的目标路径:{path}")
		return False
	return True
	
def getFileType(path):
	path = path.lower()
	if os.path.isdir(path):
		return "dir"
	elif path.endswith(('.bmp','.gif','.ico','.jpe','.jpeg','.jpg','.png','.webp')):
		return "image"
	elif path.endswith(('.aac','.ac3','.amr','.ape','.flac','.m4r','.mmf','.mp3','.ogg','.wma','.wav')):
		return "audio"
	elif path.endswith(('.3gp','.avi','.flv','.h264','.mkv','.mov','.mp4','.mpeg','.mpg','.swf','.ts','.webm','.wmv','.yuv')):
		return "video"
	elif path.endswith(('.ass','.srt','.ssa','.vtt')):
		return "subtitle"
	elif path.startswith(('ftp://','http://','https://','rtmp://','rtp://','rtsp://','srt://','tcp://','udp://')):
		return "url"
	else:
		return "error"


#########################################操作路径字典###########################################
def printValue(key,val):
	if key:
		print(key)
	[ print(i + 1,val[i],sep = " ") for i in range(len(val)) ]
	print("\n")

def addDict(name,dic):
	path = getClipboard()
	if not path:
		print("路径错误")
		return
	dic[name] = path
	printValue(name,dic[name])

def appendDict(name,dic):
	if name not in dic:
		addDict(name,dic)
		return
	target = dic[name]
	[ target.append(path) for path in getClipboard() if path not in target ]
	printValue(name,target)

def delDict(name,dic):
	if name in dic:
		del dic[name]
		print("删除成功")
	else:
		print(f"名称错误:{name}")

def delPath(name,dic,index):
	if name not in dic:
		print(f"名称错误:{name}")
		return
	target = dic[name]
	index = checkIndex(index,len(target))
	if index == "error":
		print(f"序号错误:{index}")
		return
	del target[index]
	printValue(name,target)

def printDict(arg,argLen,dic,ispath):
	if argLen == 1:
		[ printValue(key,value) for key,value in dic.items() ]	
	else:
		k = arg[1]
		if ispath and k in {"s","d","t","dp","web","search"}:
			if k == "s":
				printValue("s",selectedSrc)
			elif k == "d":
				printValue("d",selectedDst)
			elif k == "t":
				printValue("t",selectedTmp)
			elif k == "dp":
				print(downloadPath)
			elif k == "web":
				[ print(key,value,sep = " ") for key,value in webDict.items() ]		
			elif k == "search":
				[ print(key,value,sep = " ") for key,value in searchDict.items() ]	
			return
		if k in dic:
			printValue(k,dic[k])
		else:
			findkey = False
			for key,value in dic.items():
				if key.find(k) != -1:
					findkey = True
					printValue(key,value)
			if not findkey:
				print(f"{k}不存在")

#设置路径
def setPath(arg,argLen):
	global pathDict
	if arg[0] == "list":
		printDict(arg,argLen,pathDict,True)
		return
	elif arg[0] == "clr":
		pathDict.clear()
	elif arg[0] == "sp":
		saveDict('pathDict.txt',pathDict)
	elif argLen == 2:
		if arg[0] == "ad":
			addDict(arg[1],pathDict)
		elif arg[0] == "del":
			delDict(arg[1],pathDict)
		elif arg[0] == "ap":
			appendDict(arg[1],pathDict)
	elif argLen == 3:
		if arg[0] == "del":
			delPath(arg[1],pathDict,int(arg[2]))
	
#########################################操作路径字典###########################################


#########################################操作临时路径###########################################

#添加临时路径
def addSelected(target,clear,checkDir,checkRepeat):
	if clear == "clear": 
		target.clear()
	for path in getClipboard():
		if checkDir == "checkdir":
			if not os.path.isdir(path):
				continue
		if checkRepeat == "checkrepeat":
			if path in target: 
				continue
		target.append(path)
	printValue(None,target)


#设置临时路径
def setSelectedPath(arg,argLen):
	global selectedSrc , selectedDst , selectedTmp
	if arg[0] == "s" :
		addSelected(selectedSrc,"clear","","")
	elif arg[0] == "ss" :
		addSelected(selectedSrc,"","","checkrepeat")
	elif arg[0] == "d" :
		addSelected(selectedDst,"clear","checkdir","")
	elif arg[0] == "dd" :
		addSelected(selectedDst,"","checkdir","checkrepeat")
	elif arg[0] == "t" :
		addSelected(selectedTmp,"clear","","")
	elif arg[0] == "tt" :
		addSelected(selectedTmp,"","","checkrepeat")
#########################################操作临时路径###########################################


#########################################获取路径###########################################
	
def getFilePath(path):
	return [ p for p in path if os.path.isfile(p) ]

def getDirPath(path):
	return [ p for p in path if os.path.isdir(p) ]

def getExistPath(path):
	return [ p for p in path if os.path.exists(p) ]

#从剪贴板获取文件夹路径
def getDirPathFromClipboard():
	return getDirPath(getClipboard())

#从剪贴板获取文件路径
def getFilePathFromClipboard():
	return getFilePath(getClipboard())

#从剪贴板获取路径
def getPathFromClipboard():
	return getExistPath(getClipboard())

def getFirstPath(path): 
	if not path:
		return
	for p in path:
		if os.path.exists(p):
			return p

def checkIndex(index,length):
	if abs(index) > length:
		print(f"序号错误:{index}--{length}")
		return "error"
	if index > 0:
		index -= 1
	return index

def getPathByIndex(key,type):
	global pathDict
	tmp = key.split("@")
	if len(tmp) == 2:
		if tmp[0] in pathDict:
			tmpPath = pathDict[tmp[0]]
			outPath = ""
			if tmp[1] == "0":
				outPath = tmpPath
			elif (tmp[1].startswith("-") and tmp[1][1:].isnumeric()) or tmp[1].isnumeric():
				index = checkIndex(int(tmp[1]),len(tmpPath))
				if index == "error":
					return -1
				outPath = [ tmpPath[index] ]
			else:
				for t in tmpPath:
					if os.path.basename(t).find(tmp[1]) != -1:
						outPath = [ t ]
						break
				if not outPath:
					return -1
			
			if type == "getDir":
				return [ p for p in outPath if os.path.isdir(p) ]
			elif type == "getFile":
				return [ p for p in outPath if os.path.isfile(p) ]
			elif type == "getAll":
				return outPath
		return -1
	return 0

def getPathByKey(path):
	global pathDict
	key = path[:path.find("\\")]
	base = path[path.find("\\"):]
	if key in pathDict:
		tmp = getDirPath(pathDict[key])
		if tmp:
			if len(tmp) == 1:
				return [ f"{tmp[0]}{base}" ]
			else:
				dir = os.path.dirname(tmp[0]) 
				return [ f"{dir}{base}" ]		
	else:
		tmp = getPathByIndex(key,"getDir")
		if tmp == 0 : 
			if len(key) == 1 and key.isalpha() : 
				return [ f"{key}:{base}" ]
		elif isinstance(tmp,list) :
			return[ f"{t}{base}" for t in tmp ]
	return []


#从路径字典获取文件路径
def getFilePathFromDict(path):
	global pathDict
	if path.find(":\\") != -1:
		return [path]

	elif path in pathDict:
		return getFilePath(pathDict[path])

	elif path.find("\\") != -1:
		return getPathByKey(path)

	elif path.find("@") != -1 and not path.startswith("@"):
		tmp = getPathByIndex(path,"getFile")
		if tmp and isinstance(tmp,list) :
			return tmp
	return []

#从路径字典获取文件夹路径
def getDirPathFromDict(path):
	global pathDict
	if path.find(":\\") != -1:
		return [path]

	elif path in pathDict:
		return getDirPath(pathDict[path])

	elif path.find("\\") != -1:
		return getPathByKey(path)

	elif path.find("@") != -1 and not path.startswith("@"):
		tmp = getPathByIndex(path,"getDir")
		if tmp and isinstance(tmp,list) :
			return tmp
	return []

#从路径字典获取路径
def getPathFromDict(path):
	global pathDict
	if path.find(":\\") != -1:
		return [path]

	elif path in pathDict:
		return pathDict[path]

	elif path.find("\\") != -1:
		return getPathByKey(path)

	elif path.find("@") != -1 and not path.startswith("@"):
		tmp = getPathByIndex(path,"getAll")
		if tmp and isinstance(tmp,list) :
			return tmp
	return []

#########################################获取已保存的路径###########################################

def getInputPath(arg):
	global selectedSrc , selectedTmp
	if arg == "s":
		return selectedSrc
	elif arg == "t":
		return selectedTmp
	elif arg == "*":
		return getClipboard()
	else:
		return getPathFromDict(arg)

def checkDir(path,isfile):
	dst = os.path.dirname(path) if isfile == "file" else path
	if checkDstDir(dst): 
		return path
	return []
			
def getOutputDirPath(dstPath,src,outType,check,isfile):
	global selectedDst , selectedTmp , downloadPath
	outPath = ""
	#当前文件所在路径
	if dstPath.startswith("\\"):
		if src != "None":
			if os.path.exists(src):
				outPath = [ os.path.dirname(src) + dstPath ]
	# d标记的路径
	elif dstPath.startswith("d\\") or dstPath == "d":
		outPath = [ f"{t}{dstPath[1:]}" for t in selectedDst ]
	# t标记的路径
	elif dstPath.startswith("t\\") or dstPath == "t":
		if check == "checkDir":
			outPath = [ f"{t}{dstPath[1:]}" for t in getDirPath(selectedTmp) ] 
		else:
			outPath = [ f"{t}{dstPath[1:]}" for t in selectedTmp ]	
	#下载用路径
	elif dstPath.startswith("dp\\") or dstPath == "dp":
		outPath = [ f"{downloadPath}{dstPath[2:]}" ]
	#剪贴板获取路径
	elif dstPath.startswith("*\\") or dstPath == "*":
		if check == "checkDir":
			outPath = [ f"{t}{dstPath[1:]}" for t in getDirPathFromClipboard() ]
		else:
			outPath = [ f"{t}{dstPath[1:]}" for t in getClipboard() ]
	#字典获取路径
	else:
		if check == "checkDir":
			outPath = getDirPathFromDict(dstPath)
		else:
			outPath = getPathFromDict(dstPath)
	if outPath:
		if outType == "first":
			if check == "checkDir":
				return checkDir(outPath[0],isfile)
			else:
				return outPath[0]
		else:
			if check == "checkDir":
				for out in outPath:
					if not checkDir(out,isfile):
						return []
			return outPath
	return []

def getOutputFilePath(outDir,inputPath,check):
	if inputPath:
		name,suffix = os.path.splitext( os.path.basename(inputPath) )
		if outDir.find(".*") != -1:
			outDir = outDir.replace(".*",suffix,1)
		if outDir.find("*") != -1:
			outDir = outDir.replace("*",name)
	if check == "checkDir":
		if not checkDir(outDir,"file"):
			return
	return replaceFileName(outDir)

def msg(*args):
	return args

def setEntry(text):
	return ["se",text]

def setMode(mode):
	return ["sm",mode]

def changeMode(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return
	else:
		return setMode(arg[1])
