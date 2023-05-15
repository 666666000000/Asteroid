#-*- coding : utf-8 -*-
import os
import re
import time
import shlex
import traceback

describe = "操作常用路径及临时路径"

main = ""
selectedSrc = list()
selectedDst = list()
selectedTmp = list()
indexNum = 0
indexLen = 0
downloadPath = ""
pathDict = ""
programDict = ""
tmpDict = dict()
normalMode = "n"
normalColor = "#0078D7"
fontColor = "#606060"
clickColor = "#2797E3"
preColor = ""
selfPath = ""
windows = list()

functions = dict()

def resolve(line,isReturn):
	arg,argLen = getArgList(line)
	functions[arg[0]](arg,argLen)

def init(arg):
	global main,pathDict,programDict,selfPath
	main = arg
	selfPath = os.getcwd()
	pathDict = loadDict("module\\core\\path.txt")
	programDict = loadDict("module\\core\\program.txt")

#! s ss d dd t tt !#
def setSelectedPath(arg,argLen,value = None,checkRepeat = True,printVal = True):
	dataType = "path"
	if argLen == 2 :
		if arg[1] == "l":
			dataType = "list"
		elif arg[1] == "s":
			dataType = "strip"
		elif arg[1] == "o":
			dataType = "ori"
	if arg[0] == "s" :
		addSelected(selectedSrc,True,False,False,dataType,value,printVal)
	elif arg[0] == "ss" :
		addSelected(selectedSrc,False,False,checkRepeat,dataType,value,printVal)
	elif arg[0] == "d" :
		addSelected(selectedDst,True,True,False,dataType,value,printVal)
	elif arg[0] == "dd" :
		addSelected(selectedDst,False,True,checkRepeat,dataType,value,printVal)
	elif arg[0] == "t" :
		addSelected(selectedTmp,True,False,False,dataType,value,printVal)
	elif arg[0] == "tt" :
		addSelected(selectedTmp,False,False,checkRepeat,dataType,value,printVal)

def addSelected(target,clear,checkDir,checkRepeat,dataType,value,printVal):
	if clear: 
		target.clear()
	if not value:
		value = getClipboard(dataType)
		if not value:
			return
	if dataType == "ori" or dataType == "strip" :
		target.append(value)
	else:
		if checkDir or checkRepeat:
			for val in value:
				if checkDir and not os.path.isdir(val):
					continue
				if checkRepeat and val in target: 
					continue
				target.append(val)
		else:
			target.extend(value)
	if printVal:
		printList(None,target)

#! ad ap sp !#
def setPath(arg,argLen):
	if arg[0] == "sp":
		saveFile(pathDict,'module\\core\\path.txt',False,"dict")
	elif argLen == 2:
		appendDict(arg[1],pathDict,arg[0])

def appendDict(name,dic,mode,value = None,checkRepeat = True,printVal = True):
	if not value:
		value = getClipboard()
		if not value:
			return
	if mode == "ad" or name not in dic:
		dic[name] = [] + value
	else:
		if checkRepeat:
			[ dic[name].append(v) for v in value if v not in dic[name] ]
		else:
			dic[name].extend(value)
	if printVal:
		printList(name,dic[name])
	
#! del !#
def delDict(arg,argLen):
	if argLen == 1:
		return
	p = ["","*"]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[i+1]
	if p[0] not in pathDict:
		print("不存在:",p[0])
		return
	if p[1] == "*":
		print("删除:",p[0])
		del pathDict[p[0]]
	else:
		try:
			index = checkIndex(int(p[1]),len(pathDict[p[0]]))
		except:
			print("序号错误:",p[1])
			return
		if index == "error":
			return
		print("删除:",pathDict[p[0]][index])
		del pathDict[p[0]][index]

#! ls !#
def printDict(arg,argLen):
	p = ["","t"]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[i+1]
	if not p[0]:
		[ printList(key,value) for key,value in pathDict.items() ]	
	else:
		k = p[0]
		if k in {"s","d","t","dp","web","search","tmp"}:
			if k == "s":
				printList("s",selectedSrc,p[1])
			elif k == "d":
				printList("d",selectedDst,p[1])
			elif k == "t":
				printList("t",selectedTmp,p[1])
			elif k == "dp":
				print("下载路径:",downloadPath)
			elif k == "tmp":
				[ printList(key,value,p[1]) for key,value in tmpDict.items() ]	
			return
		if k in pathDict:
			printList(k,pathDict[k],p[1])
		elif k in tmpDict:
			printList(k,tmpDict[k],p[1])
		else:
			findkey = False
			for key,value in pathDict.items():
				if key.find(k) != -1:
					findkey = True
					printList(key,value,p[1])
			if not findkey:
				print("未找到:",k)
				
#! clr !#				
def clearPath(arg,argLen):
	if not checkArgLength(arg,2):
		return
	if arg[1] == "s":
		selectedSrc.clear()
	elif arg[1] == "d":
		selectedDst.clear()
	elif arg[1] == "t":
		selectedTmp.clear()
	elif arg[1] == "p":
		pathDict.clear()
	elif arg[1] == "tmp":
		tmpDict.clear()

#! dp !#
def setDownloadPath(arg,argLen):
	global downloadPath
	isOpen = False
	if argLen == 1:
		path = getOutputDirPath("*",None,None,"first","checkDir","dir")
	elif argLen == 2:
		if arg[1] == "o":
			path = getOutputDirPath("*",None,None,"first","checkDir","dir")
			isOpen = True
		else:
			path = getOutputDirPath(arg[1],None,None,"first","checkDir","dir")
	else:
		path = getOutputDirPath(arg[1],None,None,"first","checkDir","dir")
		isOpen = True
	if path:
		downloadPath = path
		print("下载路径:",path)
		if isOpen:
			runCommand(f"start \"\" \"{path}\"")

#! / !#
def openPath(arg,argLen):
	global pathDict
	if argLen == 1:
		arg.append("*")
		argLen = 2
	if arg[1] == "r":
		pathDict = loadDict("module\\core\\path.txt")
		return True
	path = getInputPath(arg[1])
	if path:
		if argLen == 2:
			target = "start \"\""
		elif argLen >= 3:
			if arg[2] == "od":
				openDirPath(path)
				return True
			else:
				if arg[2] in programDict:
					target = f"\"{programDict[arg[2]][0]}\""
				else:
					print("路径未配置:",arg[2])
					return False
		[ runCommand(f"{target} \"{p}\"",True) for p in path ]
		return True

def openDirPath(path):
	tmp = set()
	for p in path:
		dirpath = os.path.dirname(p)
		if dirpath in tmp:
			continue
		tmp.add(dirpath)
		runCommand(f"start \"\" \"{dirpath}\"")

#! e !#
def openProgram(arg,argLen):
	global programDict
	if not checkArgLength(arg,2):
		return
	if arg[1] == "r":
		programDict = loadDict("module\\core\\program.txt")
	elif arg[1] not in programDict:
		return
	elif argLen == 2:
		[ runCommand(f"\"{path}\"",True) for path in programDict[arg[1]] ]
	elif arg[2] == "od":
		openDirPath(programDict[arg[1]])
	else:
		src = getInputPath(arg[2])
		if not src:
			return
		[ runCommand(f"\"{programDict[arg[1]][0]}\" \"{s}\"",True) for s in src ]
	return True

#! index !#
def setIndex(arg,argLen):
	global indexNum , indexLen
	if argLen == 1:
		print("序号:",str(indexNum).zfill(indexLen))
		return
	indexNum = int(arg[1])
	indexLen = len(arg[1])
	print("序号:",str(indexNum).zfill(indexLen))

#! gd !#
def getDict(arg,argLen):
	if not checkArgLength(arg,2):
		return
	path = getPathFromDict(arg[1])
	if path:
		appedClipboardText("\n".join(path))

#! printClip !#
def printClipboard(arg,argLen):
	printList("剪贴板",getClipboard())

#! sleep !#
def sleeping(arg,argLen):
	if argLen == 1:
		return
	try: 
		time.sleep(float(arg[1]))
	except:
		pass

def printList(key,val,showNum = "t"):
	if key:
		print(key)
	if showNum == "t":
		[ print(i,v) for i,v in enumerate(val,1) ]
	else:
		[ print(v) for v in val ]
	print("\n")

def getClipboard(t = "path"):
	try:
		data = main.window.clipboard_get()
	except:
		print("读取剪贴板错误")
		getError()
		return []
	if t == "path":
		return [ p.strip() for p in data.replace("\"","").split("\n") if p.strip() ]
	elif t == "list":
		return [ p.strip() for p in data.split("\n") if p.strip() ]
	elif t == "strip":
		return data.strip()
	elif t == "ori":
		return data
	return []

def getFilePath(path):
	return [ p for p in path if os.path.isfile(p) ]

def getDirPath(path):
	return [ p for p in path if os.path.isdir(p) ]

def getExistPath(path):
	return [ p for p in path if os.path.exists(p) ]

def getDirPathFromClipboard():
	return getDirPath(getClipboard())

def getFilePathFromClipboard():
	return getFilePath(getClipboard())

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
		print(f"序号错误:{index}:{length}")
		return "error"
	if index > 0:
		index -= 1
	return index

def getPathByIndex(key):
	tmp = key.split("@",1)
	if len(tmp) == 2:
		if tmp[0] in pathDict:
			tmpPath = pathDict[tmp[0]]
			outPath = ""
			if tmp[1] == "0":
				outPath = tmpPath
			elif tmp[1] == "p":
				outPath = [ os.path.dirname(tmpPath[0]) ]
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
			return outPath
		return -1
	return 0

def getPathByKey(path):
	key = path[:path.find("\\")]
	base = path[path.find("\\"):]
	if key in pathDict:
		tmp = getDirPath(pathDict[key])
		if tmp:
			return [ f"{t}{base}" for t in tmp ]	
	else:
		tmp = getPathByIndex(key)
		if tmp == 0 : 
			if len(key) == 1 and key.isalpha() : 
				return [ f"{key}:{base}" ]
		elif isinstance(tmp,list) :
			return[ f"{t}{base}" for t in tmp ]
	return []

def getPathFromDict(path):
	if path.find(":\\") != -1:
		return [path]

	elif path in pathDict:
		return pathDict[path]

	elif path.find("\\") != -1:
		return getPathByKey(path)

	elif path.find("@") != -1 and not path.startswith("@"):
		tmp = getPathByIndex(path)
		if tmp and isinstance(tmp,list) :
			return tmp
	return []

def getPath(arg):
	if arg == "s":
		return selectedSrc
	elif arg == "t":
		return selectedTmp
	elif arg == "*":
		return getClipboard()
	elif arg == "dp":
		return [downloadPath]
	elif arg in tmpDict:
		return tmpDict[arg]
	else:
		return getPathFromDict(arg)

def getInputPath(arg):
	if arg.find("+") == -1:
		return getPath(arg)
	arg = arg.split("+")
	path = list()
	for a in arg:
		path.extend(getPath(a))
	if not path:
		print("源路径错误:",arg)
	return path

def checkDirExist(path,dstType):
	dst = os.path.dirname(path) if dstType == "file" else path
	if not os.path.exists(dst):
		try:
			os.makedirs(dst)
			print("建立文件夹:",dst)
		except:
			return False
	elif os.path.isfile(dst):
		print("无效的目标路径:",dst)
		return False
	return True

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
			
def getOutputDirPath(dstPath,inputPath,inputType,returnType,check = None,dstType = None):
	#当前文件所在路径
	if dstPath.startswith("\\") and inputPath and os.path.exists(inputPath):
		dirPath = os.path.dirname(inputPath) if inputType == "file" else inputPath
		outPath = [ dirPath + dstPath ]
	# d标记的路径
	elif dstPath.startswith("d\\") or dstPath == "d":
		outPath = [ f"{t}{dstPath[1:]}" for t in selectedDst ]
	# t标记的路径
	elif dstPath.startswith("t\\") or dstPath == "t":
		outPath = [ f"{t}{dstPath[1:]}" for t in selectedTmp ]	
	#下载用路径
	elif dstPath.startswith("dp\\") or dstPath == "dp" and downloadPath:
		outPath = [ f"{downloadPath}{dstPath[2:]}" ]
	#剪贴板获取路径
	elif dstPath.startswith("*\\") or dstPath == "*":
		outPath = [ f"{t}{dstPath[1:]}" for t in getClipboard() ]
	#字典获取路径
	else:
		outPath = getPathFromDict(dstPath)
	if outPath:
		if returnType == "first":
			if check == "checkDir":
				if not checkDirExist(outPath[0],dstType):
					return []
			return outPath[0]
		else:
			if check == "checkDir":
				for out in outPath:
					if not checkDirExist(out,dstType):
						return []
			return outPath
	print("目标路径错误:",dstPath)
	return []

def getOutputFilePath(outDir,inputPath,check = None,dstType = None):
	if inputPath:
		name,suffix = os.path.splitext( os.path.basename(inputPath) )
		if outDir.find(".*") != -1:
			outDir = outDir.replace(".*",suffix,1)
		if outDir.find("*") != -1:
			outDir = outDir.replace("*",name)
	if check == "checkDir" and not checkDirExist(outDir,dstType):
		return
	return replaceFileName(outDir)

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

def checkArgLength(arg,length):
	if len(arg) < length:
		main.setEntry(f"缺少参数:{arg}")
		return False
	return True

def getError(isPrint = True):
	r = re.sub(r"  File \".*\\|  File \"|\",","",traceback.format_exc())
	if isPrint:
		print(r)
	else:
		return r

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
				if line.startswith("//"):
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
			file.close()
					
	except:
		print(f"读取 {path} 错误")
	return dic

def loadCommand(path):
	dic = dict()
	try:
		with open(path, 'r', encoding = 'utf-8', errors = 'ignore') as file:
			for line in file: 
				line = line.strip()
				if not line:
					continue
				if line[0] == "#":
					continue
				line = line.split("#")
				if len(line) < 2:
					continue
				dic[line[0].strip()] = line[1].strip()
			file.close()			
	except:
		print(f"读取 {path} 错误")
	return dic

def saveFile(data,path,preset,dataType,m = "w"):
	if preset:
		path = replaceFileName(path)
		dst = getOutputDirPath(path,selfPath,"dir","list","checkDir","file")
		if not dst:
			return
	else:
		dst = [ path ]
	for d in dst:
		print(d)
		try:
			if dataType == "image":
				data.save(d,quality = 95)
			elif dataType == "xlsx":
				data.save(d)
			elif dataType in {"text","list","dict"}:
				with open(d, m, encoding = 'utf-8', errors = 'ignore') as file:
					if dataType == "text":
						file.write(data)
					elif dataType == "list":
						[ file.write(line + "\n") for line in data ]
					elif dataType == "dict":
						for key,value in data.items():
							file.write(f"<{key}>\n")
							[ file.write(f"{val}\n") for val in value ]	
							file.write("\n")
					file.close()
		except:
			getError()
	return dst

def splitList(val,sym = ":",num=1):
	for i in range(len(val)):
		val[i] = [v.strip() for v in val[i].split(sym,num)]
	return val

def splitDict(dic,sym = ":",num=1):
	if not dic:
		return
	for value in dic.values():
		splitList(value,sym,num)  
	return dic

def getShortcut(event):
	event = str(event).split(" ")[2:]
	#有Control或Alt
	if event[0].startswith("state"):
		#Control 或 Control Alt
		if event[0].find("Control") != -1:
			mod = "Control-" if event[0].find("0x20000") == -1 else "Control-Alt-"
			sym = event[1].split("=")
			key = f"{mod}Key-{sym[1]}" if sym[1].isnumeric() else f"{mod}{sym[1]}"
		#Alt
		elif event[0].find("0x20000") != -1:
			key = f"Alt-{event[1].split('=')[1]}"
		#无Control和Alt，state=Mod1
		elif event[0].find("Control") == -1 and event[0].find("0x20000") == -1:
			key = event[1].split("=")[1]
	#无Control或Alt
	elif event[0].startswith("keysym"):
		sym = event[0].split("=")
		key = f"Key-{sym[1]}" if sym[1].isnumeric() else sym[1]
	return key

def runCommand(command,sleep = False):
	print(command)
	os.popen(command)
	if sleep: 
		time.sleep(0.5)

def clearClipboard():
	main.window.clipboard_clear()

def appedClipboardText(text,mode = "ad"):
	if mode == "ad": 
		main.window.clipboard_clear()
	print(text)
	main.window.clipboard_append( text )
	
def getFileType(path):
	path = path.lower()
	if os.path.isdir(path):
		return "dir"
	elif path.endswith(('bmp','gif','ico','jfif','jpe','jpeg','jpg','png','tif','tiff','webp')):
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
		return

def selectCamera(arg):
	if arg.find("@") != -1:
		tmp = arg.split("@",1)
		try:
			n = int(tmp[1])
			return n
		except:
			print("参数错误:",tmp[1])
	return 0

def getNum(s,sym):
	if not s:
		return 0,0
	t = s.split(sym)
	if len(t) == 2:
		return t[0],t[1]
	else:
		if sym == "s":
			return s,0
		return 0,s
		
def getSeconds(arg):
	h,tmp = getNum(arg,"h")
	m,tmp = getNum(tmp,"m")
	s,tmp = getNum(tmp,"s")
	try:
		seconds = int(float(h)*3600 + int(m)*60 + int(s))
	except:
		print("参数错误:",arg)
		return -1
	return seconds

def checkTmpDir():
	if not os.path.exists("tmp"): 
		os.makedirs("tmp")
