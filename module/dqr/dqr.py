#-*- coding : utf-8 -*-
import os
import cv2
import threading
from numpy import array
from PIL import Image,ImageGrab
from ..core import core

commands = {"dqr"}
describe = "从桌面、图片、摄像头扫描二维码"

lastDetect = ""
detector = cv2.wechat_qrcode_WeChatQRCode("module\\dqr\\detect.prototxt","module\\dqr\\detect.caffemodel","module\\dqr\\sr.prototxt","module\\dqr\\sr.caffemodel")

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "dqr":
		decode(arg,argLen)

def decode(arg, argLen):
	if argLen == 1:
		info = detectQR(array(ImageGrab.grab().convert('L')),"Screen")
		text = f"扫描屏幕结果:{info}"
		core.appedClipboardText(text)
	elif argLen == 2:
		if arg[1] == "f":
			text = ""
			files = core.getFilePathFromClipboard()
			if not files:
				print("输入文件错误")
				return
			for f in files:
				if os.path.isfile(f) and (f.lower().endswith(('.bmp','.png','.jpg','.jpeg','.jpe'))):
					info = detectQR(array(Image.open(f).convert('L')),"File")
					text += f"扫描文件:{f}\n扫描结果:{info}\n\n"
			core.appedClipboardText(text)
		elif arg[1] == "c" or arg[1].startswith("c@"):
			threading.Thread(target = cameraThread,args = (arg[1],)).start()

def detectQR(gray,type):
	global lastDetect
	codeinfo,points = detector.detectAndDecode(gray)
	if type == "Camera" and codeinfo:
		if codeinfo == lastDetect:
			return
		lastDetect = codeinfo
	return codeinfo

def cameraThread(arg):
	global lastDetect
	lastDetect = ""
	cv2.namedWindow("cam",cv2.WINDOW_AUTOSIZE)
	cam = cv2.VideoCapture(core.selectCamera(arg))
	while True:
		ret,frame = cam.read()
		cv2.imshow("cam",frame)
		info = detectQR(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),"Camera")
		if info:
			core.appedClipboardText(f"扫描摄像头结果:{info}")
		if cv2.waitKey(200) == 27:
			break
	cam.release()
	cv2.destroyAllWindows()
