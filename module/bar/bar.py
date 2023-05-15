#-*- coding : utf-8 -*-
import re
from math import floor
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from PIL import Image,ImageTk
from tkinter import Toplevel,Label
from tkinter.filedialog import asksaveasfilename
from ..core import core

commands = {"bar"}
describe = "从剪贴板、文本批量生成条码"

xPos = 0
yPos = 0
width = 0
barImg = ""
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
	if not core.checkArgLength(arg,2):
		return 
	if arg[1] not in barcode.PROVIDED_BARCODES:
		print(f"条码类型错误:{arg[1]}")
		print(barcode.PROVIDED_BARCODES)
		return
	if argLen <= 3 :
		if argLen == 3:
			dstPath = core.getOutputDirPath(arg[2],None,None,"first","checkDir","file")
		showBarcode(arg[1])
	elif argLen >= 4:
		if arg[2] == "*":
			src = core.getClipboard("strip")
			if not src.split("\n"):
				srcType = "str"
			else:
				src = src.split("\n")
				srcType = "strs"
		elif arg[2] == "f":
			src = core.getFilePathFromClipboard()
			srcType = "file"
		else:
			print(f"参数错误:{arg[2]}")
			return
		if not src:
			print(f"源路径无效:{arg[2]}")
			return
		outDir = core.getOutputDirPath(arg[3],src[0],"file","first","checkDir","file")
		if not outDir:
			return
		return encodeToFile(arg[1],src,srcType,outDir)

def barCodeImage(type,input):
	output = BytesIO()
	EAN = barcode.get_barcode_class(type)
	try:
		EAN(input,writer=ImageWriter()).write(output)
	except:
		print("内容错误")
		return
	return Image.open(output)

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

def showBarcode(arg):
	global barImg
	img = barCodeImage(arg,core.getClipboard("strip"))
	if not img:
		return
	window = Toplevel(bg = "white")
	window.overrideredirect(True)
	window.geometry(f"{width}x{width}+{xPos}+{yPos}")
	height = floor(width*img.height/img.width)
	resized = img.resize((width,height),Image.ANTIALIAS)
	barImg = ImageTk.PhotoImage(resized)
	ypos = floor(width-height)/2
	imgLabel = Label(window,image = barImg)
	imgLabel.place(y = ypos,width = width , height = height)
	window.bind("<ButtonRelease-3>",lambda event:saveImg(event,img))
	window.bind("<Double-Button-1>",lambda event:exit(event,window))

def encodeToFile(codeType,src,srcType,dst):
	if type == "str":
		encodeStr(codeType,src,"None",dst)
	if srcType == "strs":
		[ encodeStr(codeType,s.strip(),"None",dst) for s in src ]	
	elif srcType == "file":
		for s in src:
			if s.endswith(".xlsx"):
				return "continue"
		for s in src:
			readTXT(codeType,s,dst)

def readTXT(codeType,path,dst):
	with open(path, 'r',encoding = 'utf-8', errors = 'ignore') as file:
		for line in file:
			encodeStr(codeType,line.strip(),"None",dst)
		file.close()

def encodeStr(codeType,src,name,dst):
	if not src:
		print("字符串错误")
		return
	img = barCodeImage(codeType,src)
	if not img:
		return
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









