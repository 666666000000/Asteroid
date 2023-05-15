#-*- coding : utf-8 -*-
import os
from math import floor
from tkinter import Toplevel,Label
from ..core import core

commands = {"df","f"}
describe = "搜索桌面及指定文件夹内的文件"


publicPath = os.environ['HOMEDRIVE']+"\\Users\\Public\\Desktop"
userPath = os.environ['HOMEDRIVE']+os.environ['HOMEPATH']+"\\Desktop"

config = ""
main = ""
hide = ""
window = ""
windowWidth = 1280
windowXpos = 0
lableList = list()
infoLabel = ""
labelXpos = 25
labelYpos = 25 
labelWidth = 0
labelHeight = 40


defaultPath = dict()
dirs = dict()
files = dict()
deepFiles = dict()
isDeepSearch = False

filters = set()
filterDir = True
filterFile = True

maxRow = 15
start = 0
end = 0
openList = list()
openListLen = 0


audio = {'aac','ac3','amr','ape','flac','m4r','mmf','mp3','ogg','wma','wav'}
video = {'3gp','avi','flv','h264','mkv','mov','mp4','mpeg','mpg','swf','ts','webm','wmv','yuv'}
image = {'bmp','gif','ico','jfif','jpe','jpeg','jpg','png','tif','tiff','webp'}
document = {"doc","docx","pdf","ppf","pptx","txt","wps","xls","xlsx"}
compressed = {"7z","gz","gzip","iso","rar","tar","zip"}
exe = {"bat","cmd","com","exe"}

def clear():
	dirs.clear()
	files.clear()
	deepFiles.clear()
	defaultPath.clear()
	closewindow(isClose = "close")
	

def init(arg):
	global main,config
	main = arg
	config = core.splitDict(core.loadDict("module\\search\\config.txt"))
	defaultPath["user"] = userPath
	defaultPath["public"] = publicPath

	for p in config["defaultpath"]:
		defaultPath[p[0]] = p[1]
	getFileList()

def resolve(line,isReturn):
	filters.clear()
	if line.find("@") != -1:
		line = line.split("@",1)
		getFilter(line[1])
		line = line[0]
		
	arg,argLen = core.getArgList(line)
	if not core.checkArgLength(arg,2):
		return
	if arg[1] == "r":
		if arg[0] == "f":
			getFileList()
		else:
			getDeepFileList()
	else:
		return find(arg,argLen,r = isReturn)


def getFilter(line):
	global filterDir,filterFile
	filterDir = True
	filterFile = True
	for f in line.split():
		if f == "a":
			filters.update(audio)
		elif f == "v":
			filters.update(video)
		elif f == "i":
			filters.update(image)
		elif f == "d":
			filters.update(document)
		elif f == "c":
			filters.update(compressed)
		elif f == "e":
			filters.update(exe)
		elif f == "file":
			filterDir = False
			filterFile = True
		elif f == "dir":
			filterDir = True
			filterFile = False
		else:
			filters.add(f)
	print(filters)


def find(arg,argLen,msg = True,r = False):
	global start,end,openListLen,isDeepSearch,openList
	openList.clear()
	isDeepSearch = False

	p = ["default","default"]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[1+i]
	if p[1] == "default":
		key = "default"
		searchName = p[0].lower()
	else:
		key = p[0]
		searchName = p[1].lower()
	if arg[0] == "f":
		openList = search(key,searchName)
	else:
		openList = deepSearch(key,searchName)
		
	if not openList:
		if msg:
			main.setEntry(f"未找到:{searchName}")
		return
	if len(openList) == 1:
		if not isDeepSearch:
			openFile(path = openList[0])
			closewindow()
			if r:
				p = openList[0].split(":")
				return [ f"{dirs[p[0]]}\\{p[1]}" ]
			return True
	openListLen = len(openList)

	start = 0
	if openListLen > maxRow:
		end = maxRow
	else:
		end = openListLen
	showFileList()
	if r:
		if isDeepSearch:
			return openList
		else:
			tmp = list()
			for p in openList:
				p = p.split(":")
				tmp.append(f"{dirs[p[0]]}\\{p[1]}")
			return tmp
	return True


def compare(filename,searchName):
	filename = filename.rsplit(".",1)
	if filters:
		if len(filename) == 1 or filename[1] not in filters:
			return False
	if filename[0].find(searchName) == -1:
		return False
	return True
		
######################################### 浅搜索 #########################################

def getFileList():
	dirs.clear()
	files.clear()
	if window:
		closewindow()
	for key,value in defaultPath.items():
		listdirs(key,value)
	for p in config["custompath"]:
		listdirs(p[0],p[1])
	

def listdirs(pathKey,path):
	if pathKey == "user" or pathKey == "public":
		tmplist = list()
		for p in os.listdir(path):
			if p.endswith(".ini"):
				continue
			if p.endswith(".lnk"):
				tmplist.append(p.rsplit(".",1)[0].lower())
			else:
				tmplist.append(p.lower())
		dirs[pathKey] = path
		files[pathKey] = tmplist
	else:
		dirs[pathKey] = path
		files[pathKey] = [ p.lower() for p in os.listdir(path) ]	
	
	
def search(keyName,searchName):
	fileList = list()
	if keyName == "default":
		for key in defaultPath.keys():
			searchFile(key,searchName,fileList)
	elif keyName in files:
		searchFile(keyName,searchName,fileList)
	elif keyName.find("+") != -1:
		for key in keyName.split("+"):
			if key in files:
				searchFile(key,searchName,fileList)
	elif keyName == "*":
		for key in files.keys():
			searchFile(key,searchName,fileList)
	else:
		main.setEntry(f"参数错误:{keyName}")
	return fileList
		

def searchFile(keyName,searchName,fileList):
	for val in files[keyName]:
		if compare(val,searchName):
			fileList.append(f"{keyName}:{val}")
		

######################################### 浅搜索 #########################################

######################################### 深搜索 #########################################

def getDeepFileList():
	deepFiles.clear()
	for key,value in defaultPath.items():
		walkdir(key,value)
	for p in config["custompath"]:
		walkdir(p[0],p[1])
		
		
def walkdir(pathKey,path):
	if pathKey not in deepFiles:
		deepFiles[pathKey] = dict()
	for root,dirs,files in os.walk(path,True):
		for i in range(len(dirs)):
			dirs[i] = dirs[i].lower()
		for i in range(len(files)):
			files[i] = files[i].lower()
		deepFiles[pathKey][root] = dict()
		deepFiles[pathKey][root]["dirs"] = dirs
		deepFiles[pathKey][root]["files"] = files


def deepSearch(keyName,searchName):
	global isDeepSearch
	isDeepSearch = True
	fileList = list()
	if keyName == "default":
		for key in defaultPath.keys():
			deepSearchFile(key,searchName,fileList)
	elif keyName in deepFiles:
		deepSearchFile(keyName,searchName,fileList)
	elif keyName.find("+") != -1:
		for key in keyName.split("+"):
			if key in deepFiles:
				deepSearchFile(key,searchName,fileList)
	elif keyName == "*":
		for key in deepFiles.keys():
			deepSearchFile(key,searchName,fileList)
	else:
		main.setEntry(f"参数错误:{keyName}")
	return fileList


def deepSearchFile(keyName,searchName,fileList):
	for key,value in deepFiles[keyName].items():
		if filterDir and not filters:
			for d in value["dirs"]:
				if compare(d,searchName):
					fileList.append(f"Dir # {os.path.join(key,d)}")
		if filterFile:
			for file in value["files"]:
				if compare(file,searchName):
					fileList.append(f"File # {os.path.join(key,file)}")

######################################### 深搜索 #########################################
	
def showFileList():
	global window, hide, infoLabel,windowWidth,windowXpos,labelWidth
	if isDeepSearch:
		t = floor(main.screenWidth/6)
		windowWidth = t*4
		windowXpos = t
	else:
		windowWidth = main.entryWidth
		windowXpos = main.entryXPos
	labelWidth = windowWidth - 50

	if not window:
		hide = False
		window = Toplevel()
		window.overrideredirect(True)
		infoLabel = Label(window, bg = "#E0DEE1", fg="#363636",font = ("Microsoft YaHei Light", 15))
		for i in range(maxRow):
			l = Label(window, bg = "#E0DEE1", fg="#363636",font = ("Microsoft YaHei Light", 15))
			l.bind("<Double-Button-1>", openFile)
			l.bind("<ButtonPress-3>", copyPath)
			lableList.append(l)	
		window.bind("<Escape>",closewindow)
		window.bind("<Left>",turnPage)
		window.bind("<Right>",turnPage)
		core.windows.append(window)
	else:
		if hide:
			hide = False
			window.update()
			window.deiconify()
			core.windows.append(window)
	resizeWindow()

def turnPage(event):
	global start,end
	if event.keysym == "Left":
		if (start - maxRow) >= 0:
			start -= maxRow
			end = start + maxRow
		else:
			main.setEntry("已到第一页")
			return
	else:
		if (start + maxRow) < len(openList):
			start += maxRow
			if (end + maxRow) <= len(openList):
				end += maxRow
			else:
				end = len(openList)
		else:
			main.setEntry("已到最后一页")
			return
	resizeWindow()

def resizeWindow():
	fileLen = end - start
	infoLabel.place(x = labelXpos, y = labelYpos, width = labelWidth , height = labelHeight)
	infoLabel.config(text=f"{start + 1} - {end} / {openListLen}")
	widowHeight = 25 + (fileLen + 1)*(labelHeight + 10) + 15
	window.geometry(f"{windowWidth}x{widowHeight}+{windowXpos}+{main.yPos}")

	yPos = labelYpos + (labelHeight + 10)
	for i in range(fileLen):
		lableList[i].place(x = labelXpos, y = yPos, width = labelWidth , height = labelHeight)
		if isDeepSearch:
			lableList[i].config(text=f"{i + 1 + start} : {openList[i + start]}")
		else:
			lableList[i].config(text=f"{i + 1 + start} : {openList[i + start].split(':',1)[1]}")
		yPos += (labelHeight + 10)
	if maxRow > fileLen:
		lableList[fileLen].place( y = yPos + 15 )

def getPath(event = None,path = None):
	if isDeepSearch:
		return event.widget["text"].split("#",1)[-1].lstrip()
	else:
		if not path:
			index = int(event.widget["text"].split(":",1)[0]) - 1
			path = openList[index].split(":",1)
		else:
			path = path.split(":",1)
		path = f"{dirs[path[0]]}\\{path[1]}"
		return path

def copyPath(event):
	core.appedClipboardText(getPath(event))

def openFile(event = None,path = None):
	path = getPath(event ,path)
	core.runCommand(f"start \"\" \"{path}\"")

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
	



					
