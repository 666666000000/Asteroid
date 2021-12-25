#-*- coding : utf-8 -*-
import os
import cv2
import threading
from PIL import Image
from numpy import array
from . import core
from .common import saveToFile as stf,funcs

keywords = {"cmap","den","sa"}
describe = "图片转伪彩、降噪,读取摄像头保存到文件"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "cmap":
		colorMap(arg,argLen)
	elif arg[0] == "den":
		denoise(arg,argLen)
	elif arg[0] == "sa":
		return saveAs(arg,argLen)

#伪彩
def getName(t):
	name = [ "autumn","bone","cividis","cool","hot","hsv","inferno","jet","magma","ocean","parula","pink","plasma","rainbow","spring","summer","tshifted","turbo","twilight","viridis","winter" ]
	for n in name:
		if n.startswith(t):
			return n

def colorMap(arg,argLen):
	filePath = core.getFilePathFromClipboard()
	if not filePath:
		return
	for path in filePath:
		if not funcs.checkImg(path):
			print(f"图片错误{path}")
			continue
		img = Image.open(path)
		if len(img.getbands()) !=1:
			print(f"跳过图片{path}")
			continue
		type = "hsv"
		cvImage = None
		if argLen == 2:
			type = getName(arg[1])
			if not type:
				print(f"参数错误:{type}")
				return
		if type == "autumn":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_AUTUMN)
		elif type == "bone":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_BONE)
		elif type == "cividis":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_CIVIDIS)
		elif type == "cool":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_COOL)
		elif type == "hot":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_HOT)
		elif type == "hsv":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_HSV)
		elif type == "inferno":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_INFERNO)
		elif type == "jet":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_JET)
		elif type == "magma":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_MAGMA)
		elif type == "ocean":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_OCEAN)
		elif type == "parula":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_PARULA)
		elif type == "pink":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_PINK)
		elif type == "plasma":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_PLASMA)
		elif type == "rainbow":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_RAINBOW)
		elif type == "spring":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_SPRING)
		elif type == "summer":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_SUMMER)
		elif type == "tshifted":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_TWILIGHT_SHIFTED)		
		elif type == "twilight":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_TWILIGHT)
		elif type == "turbo":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_TURBO)
		elif type == "viridis":
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_VIRIDIS)
		else:
			cvImage = cv2.applyColorMap(array(img),cv2.COLORMAP_WINTER)

		pil = Image.fromarray(cv2.cvtColor(cvImage,cv2.COLOR_BGR2RGB))
		filename,suffix = os.path.splitext(path)
		pil.save(f"{filename}-{type}{suffix}",quality = 95)

#降噪
def denoise(arg,argLen):
	parm = [6,10,7,21]
	if 1 < argLen <= 5:
		for i in range(1,argLen):
			t = int(arg[i])
			if t>0:
				parm[i-1] = t
	filePath = core.getFilePathFromClipboard()
	if not filePath:
		return
	for path in filePath:
		if not funcs.checkImg(path):
			print(f"图片错误{path}")
			continue
		cvImage = cv2.cvtColor(array(Image.open(path)),cv2.COLOR_RGB2BGR)
		dnImage = cv2.fastNlMeansDenoisingColored(cvImage,None,parm[0],parm[1],parm[2],parm[3])
		pil = Image.fromarray(cv2.cvtColor(dnImage,cv2.COLOR_BGR2RGB))

		filename,suffix = os.path.splitext(path)
		pil.save(f"{filename}-denoise-{parm[0]}{suffix}",quality = 95)


def saveAs(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return
	if arg[1].endswith(('.bmp','.jpe','.jpeg','.jpg','.png')):
		if argLen >= 3 and (arg[2] == "c" or arg[2].startswith("c@")):
			threading.Thread(target = cameraThread,args = (arg,argLen,)).start()
			return
	return core.msg("continue")

def cameraThread(arg,argLen):
	maxCount = 0
	count = 0
	loop = False
	waitTime = 30
	if argLen >= 4 and int(arg[3]) > 0:
		waitTime = int(arg[3])
		loop = True
	if argLen >= 5 and int(arg[4]) > 0:
		maxCount = int(arg[4])
	cv2.namedWindow("camera",cv2.WINDOW_AUTOSIZE)
	cam = cv2.VideoCapture(funcs.selectCamera(arg[2]))
	while True:
		ret,frame = cam.read()
		cv2.imshow("camera",frame)
		key = cv2.waitKey(waitTime)
		if key == 27:
			break
		elif key == 13:
			stf.saveFile(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),arg[1],"image")
		elif loop:
			stf.saveFile(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),arg[1],"image")
			if maxCount > 0:
				count += 1
				if count >= maxCount:
					break
	cam.release()
	cv2.destroyAllWindows()
