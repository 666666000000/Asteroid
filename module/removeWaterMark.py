#-*- coding : utf-8 -*-
import os
import cv2
import threading
from PIL import Image 
from numpy import zeros,uint8,array,copy
from tkinter.filedialog import asksaveasfilename
from . import core

keywords = {"rwm"}
describe = "Opencv去水印"

drawing = False
imgList = None
drawImg = None
oriImg = None
mask = None
dstImg = None
imgCount = 0
currentImg = 0
dstPath = ""

def resolve(line):
	global mask,drawImg,oriImg,imgCount,currentImg,imgList,dstPath
	arg,argLen = core.getArgList(line)
	imgList = core.getFilePathFromClipboard()
	if not imgList: 
		print("未找到图片")
		return
	if argLen >= 2:
		dstPath = core.getOutputDirPath(arg[1],imgList[0],"first","checkDir","file")
	else:
		dstPath = ""
	imgCount = len(imgList)
	threading.Thread(target = cvThread).start()

def cvThread():
	global mask,drawImg,oriImg
	cv2.namedWindow("Src",cv2.WINDOW_AUTOSIZE)
	cv2.namedWindow("Dst",cv2.WINDOW_AUTOSIZE)
	cv2.setMouseCallback("Src",mouseEvent)
	loadImg(0)
	while True:
		cv2.imshow("Src",drawImg)
		key = cv2.waitKey(30)
		if key==27:
			break
		elif key==13:
			drawImg = copy(oriImg)
			sp = oriImg.shape
			mask = cv2.rectangle(mask,(0,0),(sp[1],sp[0]),(0),-1)
			cv2.imshow("Src",drawImg)
			update()
		elif key == 97:
			loadImg(-1)
		elif key == 100:
			loadImg(1)
	cv2.destroyAllWindows()

def checkImg(path):
	if os.path.isfile(path) and path.lower().endswith(('.bmp','.png','.jpg','.jpeg','.jpe')):
		return True
	return False

def saveImg():
	global dstImg,dstPath
	if dstPath:
		file = core.getOutputFilePath(dstPath,imgList[currentImg],"None")
	else:
		files = [('Image Files','*.jpg *.jpeg *.png')]
		file = asksaveasfilename(filetypes=files,defaultextension=files)
		if not file:
			return
	print(f"保存至 :{file}")
	pil = Image.fromarray(cv2.cvtColor(dstImg,cv2.COLOR_BGR2RGB))
	pil.save(file)

def update():
	global oriImg,dstImg
	dstImg = cv2.inpaint(oriImg,mask,3,cv2.INPAINT_TELEA)#INPAINT_NS
	cv2.imshow("Dst",dstImg)

def mouseEvent(event,x,y,flags,param):
	global drawing,mask,drawImg,oriImg,dstImg
	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
	elif event == cv2.EVENT_MOUSEMOVE:
		if drawing:
			cv2.circle(drawImg,(x,y),2,(0,0,0),-1)
			cv2.circle(mask,(x,y),2,(255,255,255),-1)
	elif event == cv2.EVENT_LBUTTONUP:
		drawing = False
		update()
	elif event == cv2.EVENT_RBUTTONUP:
		saveImg()

def loadImg(type):
	global mask,drawImg,oriImg,imgCount,currentImg,imgList
	if type==0:
		currentImg = 0
	elif type==1:
		if currentImg+1 >= imgCount:
			print("最后一张")
			return
		else:
			currentImg+=1
	elif type==-1:
		if currentImg<=0:
			print("第一张")
			return
		else:
			currentImg-=1
	if not checkImg(imgList[currentImg]):
		print(f"参数错误:{imgList[currentImg]}")
		return
	img = Image.open(imgList[currentImg])
	mask = zeros((img.height,img.width),uint8)
	oriImg = cv2.cvtColor(array(img),cv2.COLOR_RGB2BGR)
	drawImg = copy(oriImg)
	update()


