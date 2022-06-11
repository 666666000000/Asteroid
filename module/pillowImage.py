#-*- coding : utf-8 -*-
import os
from math import floor,sqrt
from PIL import Image
from . import core
from .common import funcs

keywords = {"rs","ro","crop","gray","wm","cut","g2s","s2g"}
describe = "图片批量缩放、旋转、裁剪、转灰度、加水印、九宫格、gif转图片序列、图片序列转gif"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "rs":
		resizeImg(arg,argLen)
	elif arg[0] == "ro":
		rotateImg(arg,argLen)	
	elif arg[0] == "crop":
		cropImg(arg,argLen)
	elif arg[0] == "gray":
		grayImg(arg,argLen)
	elif arg[0] == "wm":
		waterMark(arg,argLen)
	elif arg[0] == "cut":
		cutImage(arg,argLen)
	elif arg[0] == "g2s":
		gif2Sequence(arg,argLen)
	elif arg[0] == "s2g":
		sequence2Gif(arg,argLen)

#缩放图片
def resizeImg(arg,argLen):
	if argLen != 2:
		print(f"参数错误:{arg}")
		return
	filePath = core.getFilePathFromClipboard()
	if not filePath: 
		return
	width = height = 0
	scale = -1
	if arg[1].find("*") == -1:
		scale = float(arg[1])
		if scale <= 0:
			print(f"参数错误:{arg[1]}")
			return
	else:
		t = arg[1].split("*")
		width = int(t[0])
		height = int(t[1])
	for path in filePath:
		if not funcs.checkImg(path):
			print(f"图片错误{path}")
			continue
		img = Image.open(path)
		(w, h) = img.size
		if scale != -1:
			width = int(w*scale)
			height = int(h*scale)
		out = img.resize((width, height), Image.ANTIALIAS)
		filename,suffix = os.path.splitext(path)
		out.save(f"{filename}-resize{suffix}",quality = 95)


#旋转图片
def rotateImg(arg,argLen):
	if argLen != 2:
		print(f"参数错误:{arg}")
		return
	filePath = core.getFilePathFromClipboard()
	if not filePath: 
		return
	for path in filePath:
		if not funcs.checkImg(path):
			print(f"图片错误{path}")
			continue
		img = Image.open(path)
		if arg[1] == "90":
			out = img.transpose(Image.ROTATE_90)
		elif arg[1] == "180":
			out = img.transpose(Image.ROTATE_180)
		elif arg[1] == "270":
			out = img.transpose(Image.ROTATE_270)
		else :
			print(f"参数错误:{arg[1]}")
			return
		filename,suffix = os.path.splitext(path)
		out.save(f"{filename}-rotate{suffix}",quality = 95)

def checkValue(val):
	v = int(val)
	return v if v > 0 else 0
#剪裁图片
def cropImg(arg,argLen):
	if argLen != 5:
		print(f"参数错误:{arg}")
		return
	left = checkValue(arg[1])
	top = checkValue(arg[2])
	right = checkValue(arg[3])
	bottom = checkValue(arg[4])
	filePath = core.getFilePathFromClipboard()
	if not filePath: 
		return
	for path in filePath:
		if not funcs.checkImg(path):
			print(f"图片错误{path}")
			continue
		img = Image.open(path)
		width = img.width
		height = img.height
		if (left+right) > width or (top+bottom) > height :
			print("剪裁尺寸错误")
			continue
		out = img.crop([ left,top,width - right,height - bottom ])
		filename,suffix = os.path.splitext(path)
		out.save(f"{filename}-crop{suffix}",quality = 95)


#转灰度图
def grayImg(arg,argLen):
	filePath = core.getFilePathFromClipboard()
	if not filePath:
		return
	for path in filePath:
		if not funcs.checkImg(path):
			print(f"图片错误{path}")
			continue
		img = Image.open(path).convert('L')
		filename,suffix = os.path.splitext(path)
		img.save(f"{filename}-gray{suffix}",quality = 95)


#图片添加水印
def waterMark(arg,argLen):
	if argLen != 5:
		print(f"参数错误:{arg}")
		return
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	markPath = core.getInputPath(arg[3])
	if not markPath:
		print(f"参数错误:{arg[3]}")
		return
	if not funcs.checkImg(markPath[0]):
		print(f"水印错误:{markPath[0]}")
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"first","checkDir","file")
	if not outDir:
		return
	markImg = Image.open(markPath[0])
	if markImg.mode != "RGBA":
		markImg = markImg.convert("RGBA")
	mWidth,mHeight = markImg.size
	for s in src:
		if not funcs.checkImg(s):
			print(f"图片错误:{s}")
			continue
		background = Image.open(s)
		if background.mode != "RGBA":
			background = background.convert("RGBA")
		x = 0
		y = 0
		pos = arg[4]
		bWidth,bHeight = background.size
		if pos == "lt":
			x = 0
		elif pos == "t":
			x = int((bWidth - mWidth)/2)
		elif pos == "rt":
			x = bWidth - mWidth
		elif pos == "lb":
			y = bHeight - mHeight
		elif pos == "b":
			x = int((bWidth - mWidth)/2)
			y = bHeight - mHeight
		elif pos == "rb":
			x = bWidth - mWidth
			y = bHeight - mHeight
		elif pos == "c":
			x = int((bWidth - mWidth)/2)
			y = int((bHeight - mHeight)/2)
		elif pos.find("*") != -1:
			pos = pos.split("*")
			if len(pos) != 2:
				print(f"参数错误:{pos}")
				return
			tmpX = int(pos[0])
			tmpY = int(pos[1])
			x = tmpX if tmpX > 0 else bWidth + tmpX
			y = tmpY if tmpY > 0 else bHeight + tmpY

		layer = Image.new("RGBA",background.size,(0,0,0,0))
		layer.paste(markImg,(x,y))
		out = Image.composite(layer,background,layer)
		dstPath = core.getOutputFilePath(outDir,s,"None")
		if not dstPath.endswith(".png"):
			out = out.convert("RGB")
		out.save(dstPath,quality = 95)

#切割图片
def cutImage(arg,argLen):
	if argLen < 3:
		print(f"参数错误:{arg}")
		return
	if argLen == 3:
		w = 3
		h = 3
	elif argLen == 4:
		w = int(arg[3])
		h = w
	else:
		w = int(arg[3])
		h = int(arg[4])
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"first","checkDir","dir")
	if not outDir:
		return
	for s in src:
		if not funcs.checkImg(s):
			print(f"图片错误{s}")
			continue
		img = Image.open(s)
		xStart = 0
		yStart = 0
		length = min(img.width,img.height)
		xStep = floor(length/w)
		yStep = floor(length/h)
		if img.width != img.height:	
			if img.width > img.height:
				xStart = floor((img.width - length)/2)
			else:
				yStart = floor((img.height - length)/2)
		filename,suffix = os.path.splitext(os.path.split(s)[1])
		id = 1
		for y in range(h):
			for x in range(w):
				out = img.crop([ xStart + x*xStep, yStart + y*yStep, xStart + x*xStep + xStep, yStart + y*yStep + yStep ])
				out.save(f"{outDir}\\{filename}-{id}{suffix}",quality = 95)
				id += 1

#gif转图片序列
def gif2Sequence(arg,argLen):
	if argLen < 3:
		print(f"参数错误:{arg}")
		return
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"first","none","none")
	if not outDir:
		return
	step = 0
	if argLen >=4 :
		try:
			step = int(arg[3])
		except:
			step = 1
	for s in src:
		try:
			img = Image.open(s)
		except IOError:
			print("打开文件失败：" + s)
			continue
		palette = img.getpalette()
		try:
			while True:
				img.putpalette(palette)
				if outDir.endswith(".gif") or outDir.endswith(".png"):
					newImg = Image.new("RGBA", img.size)
				else:
					newImg = Image.new("RGB", img.size)
				newImg.paste(img)
				dstPath = core.getOutputFilePath(outDir, s, "checkDir")
				newImg.save(dstPath)
				if step == 0:
					break
				img.seek(img.tell() + step)
		except EOFError:
			pass

#图片序列转gif
def sequence2Gif(arg,argLen):
	if argLen < 4:
		print(f"参数错误:{arg}")
		return
	src = core.getInputPath(arg[1])
	if not src:
		print("源路径错误")
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"first","none","none")
	if not outDir:
		return
	try:
		d = int(arg[3])
	except:
		print("时间错误：" + arg[3])
		return
	frames = []
	for s in src:
		images = os.listdir(s)
		if not images:
			print("未找到图片")
			continue
		for img in images:
			frames.append(Image.open(os.path.join(s,img)))
		dstPath = core.getOutputFilePath(outDir, s, "checkDir")
		print(dstPath)
		frames[0].save(dstPath, format='GIF', append_images=frames[1:], save_all=True, duration=d, loop=0)
		frames.clear()
