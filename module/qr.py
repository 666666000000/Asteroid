#-*- coding : utf-8 -*-
import re
import qrcode
from PIL import Image,ImageTk
from tkinter import Toplevel,Label
from tkinter.filedialog import asksaveasfilename
from . import core

initArg = [ "entryXPos","entryYPos","entryHeight","entryWidth" ]
keywords = {"qr"}
describe = "从剪贴板、文本批量生成二维码"

xPos = 0
yPos = 0
size = 0
qrImg = ""
dstPath = ""

def resolve(line):
	arg,argLen = core.getArgList(line)
	return encode(arg,argLen)

def init(arg):
	global xPos,yPos,size
	xPos = arg[0]
	yPos = arg[1] + arg[2] + 10
	size = arg[3]

def encode(arg,argLen):
	global dstPath
	if argLen <= 2 :
		if argLen == 2:
			dstPath = core.getOutputDirPath(arg[1],"None","first","checkDir","file")
		showQR()
	elif argLen >= 3:
		if arg[1] == "*":
			src = core.getOriClipboard().strip()
			type = "str"
		elif arg[1] == "**":
			src = core.getOriClipboard().strip().split("\n")
			type = "strs"
		elif arg[1] == "f":
			src = core.getFilePathFromClipboard()
			type = "file"
		else:
			print(f"参数错误:{arg[1]}")
			return
		if not src:
			print(f"源路径无效:{arg[1]}")
			return
		outDir = core.getOutputDirPath(arg[2],src[0],"first","checkDir","file")
		if not outDir:
			return
		return encodeToFile(src,type,outDir)

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

def showQR():
	global qrImg
	window = Toplevel()
	window.overrideredirect(True)
	window.geometry(f"{size}x{size}+{xPos}+{yPos}")	
	img = qrcode.make(window.clipboard_get().strip())
	resized = img.resize((size,size),Image.ANTIALIAS)
	qrImg = ImageTk.PhotoImage(resized)
	imgLabel = Label(window,image = qrImg)
	imgLabel.place(width = size , height = size)
	window.bind("<ButtonRelease-3>",lambda event:saveImg(event,img))
	window.bind("<Double-Button-1>",lambda event:exit(event,window))

def encodeToFile(src,type,dst):
	if type == "str":
		encodeStr(src,"None",dst)
	elif type == "strs":
		[ encodeStr(s.strip(),"None",dst) for s in src ]	
	elif type == "file":
		for s in src:
			if s.endswith(".xlsx"):
				return core.msg("continue")
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
	window.destroy()

def checkName(name):
	rstr = r'[\\/:*?"<>|\r\n]+'
	new_name = re.sub(rstr, "", name)
	return new_name.strip()