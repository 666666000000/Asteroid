#-*- coding : utf-8 -*-
import cv2
import threading
import pytesseract
from numpy import array
from PIL import Image,ImageGrab
from . import core
from .common import funcs

keywords = {"ocr"}
describe = "从剪贴板、图片、桌面、摄像头识别文字"

langList = {"cs":"chi_sim","ct":"chi_tra","en":"eng"}

def resolve(line):
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		t,i,l = "img",array(ImageGrab.grabclipboard()),"chi_sim"
	elif argLen == 2:
		if arg[1] in langList:
			t,i,l = "img",array(ImageGrab.grabclipboard()),langList[arg[1]]
		else:
			l = "chi_sim"
			if arg[1] == "f":
				t,i = "file",core.getFilePathFromClipboard()
			elif arg[1] == "s":
				t,i = "img",ImageGrab.grab()
			elif arg[1] == "c" or arg[1].startswith("c@"):
				t,i = arg[1],"",
			else:
				print(f"参数错误:{arg[1] }")
				return
	elif argLen >= 3:
		if arg[2] in langList:
			l = langList[arg[2]]
			if arg[1] == "f":
				t,i = "file",core.getFilePathFromClipboard()
			elif arg[1] == "s":
				t,i = "img",ImageGrab.grab()
			elif arg[1] == "c" or arg[1].startswith("c@"):
				t,i = arg[1],""
			else:
				print(f"参数错误:{arg[1]}")
				return
		else:
			print(f"参数错误:{arg[2]}")
			return
	decode(t,i,l)

def decode(type,image,language):
	if type == "img":
		core.appedClipboardText(pytesseract.image_to_string(image,language))
	elif type == "file":
		text = ""
		for path in image:
			if path.endswith(('.bmp','.png','.jpg','.jpeg','.jpe')):
				text +=  pytesseract.image_to_string(Image.open(path),language)
		core.appedClipboardText(text)
	else:
		threading.Thread(target = cameraThread,args = (type,language,)).start()

def cameraThread(type,language):
	cv2.namedWindow("camera",cv2.WINDOW_AUTOSIZE)
	cam = cv2.VideoCapture(funcs.selectCamera(type))
	while True:
		ret,frame = cam.read()
		cv2.imshow("camera",frame)
		key = cv2.waitKey(30)
		if key == 27:
			break
		elif key == 13:
			text = pytesseract.image_to_string(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),language)
			core.appedClipboardText(text)
	cam.release()
	cv2.destroyAllWindows()