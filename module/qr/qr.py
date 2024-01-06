#-*- coding : utf-8 -*-
import re
import qrcode
from PIL import Image,ImageTk
from tkinter import Toplevel,Label
from tkinter.filedialog import asksaveasfilename
from ..core import core

commands = {"qr"}
describe = "从剪贴板、文本批量生成二维码"

xPos = 0
yPos = 0
width = 0
qrImg = ""
dstPath = ""

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	return encode(arg,argLen)

def init(arg):
	global xPos,yPos,width
	xPos = arg.entryXPos
	yPos = arg.yPos
	width = arg.entryWidth

def encode(arg,argLen):
	global dstPath
	p = [0,0]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[1+i]
	if p[0] == 0:
		showQR()
		return
	elif p[0] == "*":
		src = core.getClipboard("strip")
		srcType = "str"
	elif p[0] == "**":
		src = core.getClipboard("list")
		srcType = "strs"
	elif p[0] == "f":
		src = core.getFilePathFromClipboard()
		srcType = "file"
	else:
		if p[1] != 0:
			dstPath = core.getOutputDirPath(p[1],None,None,"first","checkDir","file")
		showQR(p[0])
		return
	if p[1] == 0:
		print("缺少保存路径")
		return
	else:
		outDir = core.getOutputDirPath(p[1],src[0],"file","first","checkDir","file")
		if not outDir:
			return
	return encodeToFile(src,srcType,outDir)

def saveImg(event,img):
	global dstPath
	if not dstPath:
		files = [('Image Files','*.jpg *.jpeg *.png *.bmp')]
		dstPath = asksaveasfilename(filetypes = files,defaultextension = files)
		if not dstPath:
			return
	print(f"保存至 :{dstPath}")
	img.save(dstPath)
	dstPath = ""

def showQR(src = None):
	global qrImg
	window = Toplevel()
	window.overrideredirect(True)
	window.geometry(f"{width}x{width}+{xPos}+{yPos}")
	img = qrcode.make(src) if src else qrcode.make(window.clipboard_get().strip())
	resized = img.resize((width,width),Image.ANTIALIAS)
	qrImg = ImageTk.PhotoImage(resized)
	imgLabel = Label(window,image = qrImg)
	imgLabel.place(width = width , height = width)
	window.bind("<ButtonRelease-3>",lambda event:saveImg(event,img))
	window.bind("<Double-Button-1>",lambda event:exit(event,window))
	core.windows.append(window)
	return True

def encodeToFile(src,srcType,dst):
	if srcType == "str":
		encodeStr(src,"None",dst)
	elif srcType == "strs":
		[ encodeStr(s.strip(),"None",dst) for s in src ]	
	elif srcType == "file":
		for s in src:
			if s.endswith(".xlsx"):
				return "continue"
		for s in src:
			readTXT(s,dst)

def readTXT(path,dst):
	with open(path, 'r',encoding = 'utf-8', errors = 'ignore') as file:
		for line in file:
			encodeStr(line.strip(),"None",dst)
		file.close()

def encodeStr(src,name,dst):
	if not src:
		print("字符串错误")
		return
	img = qrcode.make(src)
	dst = core.replaceFileName(dst)
	if dst.find("*") != -1:
		if name == "None":
			dst = dst.replace("*",checkName(src)[0:127])
		else:
			dst = dst.replace("*",checkName(name)[0:127])
	print(f"保存至 :{dst}")
	img.save(dst)

def exit(event,window):
	core.windows.remove(window)
	window.destroy()

def checkName(name):
	rstr = r'[\\/:*?"<>|\r\n]+'
	new_name = re.sub(rstr, "", name)
	return new_name.strip()