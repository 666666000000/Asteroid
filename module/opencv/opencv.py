#-*- coding : utf-8 -*-
import cv2
import threading
from PIL import Image
from numpy import array
from ..core import core

commands = {"cmap","den","sa"}
describe = "图片转伪彩、降噪,读取摄像头保存到文件"

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "cmap":
		return colorMap(arg,argLen,isReturn)
	elif arg[0] == "den":
		return denoise(arg,argLen,isReturn)
	elif arg[0] == "sa":
		return saveAs(arg,argLen)

#伪彩
name = {
		"au":cv2.COLORMAP_AUTUMN,"bo":cv2.COLORMAP_BONE,"ci":cv2.COLORMAP_CIVIDIS,
		"co":cv2.COLORMAP_COOL,"ho":cv2.COLORMAP_HOT,"hs":cv2.COLORMAP_HSV,
		"in":cv2.COLORMAP_INFERNO,"je":cv2.COLORMAP_JET,"ma":cv2.COLORMAP_MAGMA,
		"oc":cv2.COLORMAP_OCEAN,"pa":cv2.COLORMAP_PARULA,"pi":cv2.COLORMAP_PINK,
		"pl":cv2.COLORMAP_PLASMA,"ra":cv2.COLORMAP_RAINBOW,"sp":cv2.COLORMAP_SPRING,
		"su":cv2.COLORMAP_SUMMER,"ts":cv2.COLORMAP_TWILIGHT_SHIFTED,"tu":cv2.COLORMAP_TURBO,
		"tw":cv2.COLORMAP_TWILIGHT,"vi":cv2.COLORMAP_VIRIDIS,"wi":cv2.COLORMAP_WINTER
	}

def colorMap(arg,argLen,isReturn):
	if not core.checkArgLength(arg,4):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
	if arg[3] not in name:
		print("参数错误:",arg[3])
		return
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		img = Image.open(s)
		if len(img.getbands()) !=1:
			print(f"跳过图片{s}")
			continue
		cvImage = cv2.applyColorMap(array(img),name[arg[3]])
		pil = Image.fromarray(cv2.cvtColor(cvImage,cv2.COLOR_BGR2RGB))
		dstPath = core.getOutputFilePath(outDir,s,"checkDir","file")
		pil.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst


#降噪
def denoise(arg,argLen,isReturn):
	if not core.checkArgLength(arg,3):
		return
	src = core.getInputPath(arg[1])
	if not src:
		return
	outDir = core.getOutputDirPath(arg[2],src[0],"file","first")
	if not outDir:
		return
		
	p = [6,10,7,21]
	for i in range(min(len(arg[3:]),len(p))):
		p[i] = int(arg[3+i])
	dst = list()
	for s in src:
		if core.getFileType(s) != "image":
			continue
		cvImage = cv2.cvtColor(array(Image.open(s)),cv2.COLOR_RGB2BGR)
		dnImage = cv2.fastNlMeansDenoisingColored(cvImage,None,p[0],p[1],p[2],p[3])
		pil = Image.fromarray(cv2.cvtColor(dnImage,cv2.COLOR_BGR2RGB))

		dstPath = core.getOutputFilePath(outDir,s,"checkDir","file")
		pil.save(dstPath,quality = 95)
		if isReturn:
			dst.append(dstPath)
	return dst

#打开摄像头保存图片
def saveAs(arg,argLen):
	if not core.checkArgLength(arg,2):
		return
	if arg[1].endswith(('.bmp','.jpe','.jpeg','.jpg','.png')):
		if argLen >= 3 and (arg[2] == "c" or arg[2].startswith("c@")):
			threading.Thread(target = cameraThread,args = (arg,argLen,)).start()
			return
	return "continue"

def cameraThread(arg,argLen):
	count = 0
	loop = False
	p = [30,0]
	
	for i in range(min(len(arg[3:]),len(p))):
		p[i] = int(arg[3+i])
	
	waitTime = p[0]
	maxCount = p[1]

	cv2.namedWindow("camera",cv2.WINDOW_AUTOSIZE)
	cam = cv2.VideoCapture(core.selectCamera(arg[2]))
	while True:
		ret,frame = cam.read()
		cv2.imshow("camera",frame)
		key = cv2.waitKey(waitTime)
		if key == 27:
			break
		elif key == 13:
			core.saveFile(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),arg[1],True,"image")
		elif loop:
			core.saveFile(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),arg[1],True,"image")
			if maxCount > 0:
				count += 1
				if count >= maxCount:
					break
	cam.release()
	cv2.destroyAllWindows()
