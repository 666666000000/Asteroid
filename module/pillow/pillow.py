#-*- coding : utf-8 -*-
import os
from math import floor,ceil
from PIL import Image,ImageFilter
from ..core import core

describe = "图片批量缩放、旋转、转灰度、模糊、裁剪、加水印、裁切、统一尺寸、合并、gif转图片序列、图片序列转gif"

functions = dict()

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	return functions[arg[0]](arg,argLen,isReturn)

#缩放图片
#! rs !#
def resizeImg(arg,argLen,isReturn):
	if not core.checkArgLength(arg,4):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	width = height = 0
	scale = -1
	if arg[3].find("*") == -1:
		scale = float(arg[3])
		if scale <= 0:
			print(f"参数错误:{arg[3]}")
			return
	else:
		t = arg[3].split("*")
		width = int(t[0])
		height = int(t[1])
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		img = Image.open(s)
		(w, h) = img.size
		if scale != -1:
			width = int(w*scale)
			height = int(h*scale)
		else:
			if width == -1 and height != -1:
				width = floor(w*height/h)
			elif width != -1 and height == -1:
				height = floor(h*width/w)
		out = img.resize((width, height), Image.ANTIALIAS)
		dstPath = core.getOutputFilePath(outDir,s,"checkDir","file")
		out.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst

#图片旋转/转灰度图/模糊
#! ro gray blur !#
def rotateGrayBlur(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		if arg[0] == "ro":
			angle = 90 if argLen == 3 else int(arg[3])
			img = Image.open(s).rotate(angle,expand = True)
		elif arg[0] == "gray":
			img = Image.open(s).convert('L')
		elif arg[0] == "blur":
			parm = 10 if argLen == 3 else int(arg[3])
			img = Image.open(s).filter(ImageFilter.GaussianBlur(parm))
		
		dstPath = core.getOutputFilePath(outDir,s,"checkDir","file")
		img.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst

#剪裁图片
#! crop !#
def cropImg(arg,argLen,isReturn):
	if not core.checkArgLength(arg,4):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	p = [0,0,0,0]
	for i in range(min(len(arg[3:]),len(p))):
		p[i] = int(arg[3+i])
	left = p[0]
	top = p[1]
	right = p[2]
	bottom = p[3]
	src = core.getFilePathFromClipboard()
	if not src: 
		print("源路径错误")
		return
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		img = Image.open(s)
		width = img.width
		height = img.height
		if (left+right) > width or (top+bottom) > height :
			print("剪裁尺寸错误")
			continue
		out = img.crop([ left,top,width - right,height - bottom ])
		dstPath = core.getOutputFilePath(outDir,s,"checkDir","file")
		out.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst

#图片添加水印
#! wm !#
def waterMark(arg,argLen,isReturn):
	if not core.checkArgLength(arg,5):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	markPath = core.getInputPath(arg[3])
	if not markPath:
		return
	if core.getFileType(markPath[0]) != "image":
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	markImg = Image.open(markPath[0])
	if markImg.mode != "RGBA":
		markImg = markImg.convert("RGBA")
	mWidth,mHeight = markImg.size
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
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
		dstPath = core.getOutputFilePath(outDir,s,"checkDir","file")
		if not dstPath.endswith(".png"):
			out = out.convert("RGB")
		out.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst

#切割图片
#! cut !#
def cutImage(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return	
	p = [3,3]
	for i in range(min(len(arg[3:]),len(p))):
		p[i] = int(arg[3+i])
	w = p[0]
	h = p[1]
	dst = list()	
	for s in src:
		if core.getFileType(s) != "image":
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
		dstPath = core.getOutputFilePath(outDir, s, "checkDir","file")
		filename,suffix = os.path.splitext(dstPath)
		id = 1
		for y in range(h):
			for x in range(w):
				out = img.crop([ xStart + x*xStep, yStart + y*yStep, xStart + x*xStep + xStep, yStart + y*yStep + yStep ])
				out.save(f"{filename}-{id}{suffix}",quality = 95)
				id += 1
				if isReturn:
					dst.append(f"{filename}-{id}{suffix}")
	return dst

#统一尺寸
#! unis !#
def unisize(arg,argLen,isReturn):
	if not core.checkArgLength(arg,4):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	p = ["","c"]
	for i in range(min(len(arg[3:]),len(p))):
		p[i] = arg[3+i]
	try:
		if p[0].find("*") == -1:
			dstWidth = int(p[0])
			dstHeight = dstWidth
		else:
			t = p[0].split("*")
			dstWidth = int(t[0])
			dstHeight = int(t[1])
	except:
		print(f"参数错误:{p[0]}")
		return
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		img = Image.open(s)
		(w, h) = img.size
		if w/h > dstWidth/dstHeight:
			rWidth = ceil(w*dstHeight/h)
			rHeight = dstHeight
			img = img.resize((rWidth,rHeight), Image.ANTIALIAS)
			if p[1] == "l":
				x = 0
			elif p[1] == "r":
				x = rWidth - dstWidth
			else:
				x = floor((rWidth - dstWidth)/2)
			img = img.crop([ x, 0, x + dstWidth, dstHeight ])
		elif w/h < dstWidth/dstHeight:
			rWidth = dstWidth
			rHeight = ceil(dstWidth*h/w)
			img = img.resize((rWidth,rHeight), Image.ANTIALIAS)
			if p[1] == "t":
				y = 0
			elif p[1] == "b":
				y = rHeight - dstHeight
			else:
				y = floor((rHeight - dstHeight)/2)
			img = img.crop([ 0, y, dstWidth, y + dstHeight ])
		elif w != dstWidth:
			img = img.resize((dstWidth,dstHeight), Image.ANTIALIAS)
		dstPath = core.getOutputFilePath(outDir, s, "checkDir","file")
		img.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst
		
#合并图片
#! merge !#
def merge(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	p = [1,10,10]
	for i in range(min(len(arg[3:]),len(p))):
		p[i] = int(arg[3+i])	
	col = p[0]
	row = ceil(len(src)/col)
	bg = ""
	width = 0
	height = 0
	x = p[2]
	y = p[2]
	index = 0
	wStep = 0
	hStep = 0
	for s in src:
		if core.getFileType(s) != "image":
			continue
		img = Image.open(s)
		if not bg:
			(w, h) = img.size
			wStep = w
			hStep = h
			width = col*w + (col-1)*p[1] + p[2]*2
			height = row*h + (row-1)*p[1] + p[2]*2
			if outDir.endswith("png"):
				bg = Image.new("RGBA", (width,height))
			else:
				bg = Image.new("RGB", (width,height), (255,255,255))
		bg.paste(img, (x, y))
		index += 1
		if index >= col:
			x = p[2]
			y += hStep + p[1]
			index = 0
		else:
			x += wStep + p[1]
	dstPath = core.getOutputFilePath(outDir, src[0], "checkDir","file")
	bg.save(dstPath,quality = 95)	
	if isReturn:
		return [dstPath]	
	
#gif转图片序列
#! g2s !#
def gif2Sequence(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	step = 1
	if argLen >=4 :
		try:
			step = int(arg[3])
		except:
			step = 1
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		try:
			fp = open(s,"rb")
			img = Image.open(fp)
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
				dstPath = core.getOutputFilePath(outDir, s, "checkDir","file")
				newImg.save(dstPath,quality = 95)
				if isReturn:
					dst.append(dstPath)
				if step == 0:
					break
				img.seek(img.tell() + step)
		except EOFError:
			pass
		fp.close()
	return dst

#图片序列转gif
#! s2g !#
def sequence2Gif(arg,argLen,isReturn):
	if not core.checkArgLength(arg,4):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	try:
		d = int(arg[3])
	except:
		print("时间错误：" + arg[3])
		return
	dst = list()
	frames = []
	for s in src:
		images = os.listdir(s)
		if not images:
			print("未找到图片")
			continue
		for img in images:
			if core.getFileType(s) != "image":
				continue
			frames.append(Image.open(os.path.join(s,img)))
		dstPath = core.getOutputFilePath(outDir, s, "checkDir","file")
		print(dstPath)
		if isReturn:
			dst.append(dstPath)
		frames[0].save(dstPath, format = 'GIF', append_images = frames[1:], save_all = True, duration = d,loop = 0)
		frames.clear()
	return dst	
	