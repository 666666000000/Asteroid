import os
import zerorpc
from PIL import ImageGrab
from . import core
from io import BytesIO

keywords = {"wocr"}
describe = "网络ocr客户端"

langList = {"cs":"chi_sim","ct":"chi_tra","en":"eng"}

def resolve(line):
	arg,argLen = core.getArgList(line)
	if argLen == 1:
		t,i,l = "img",ImageGrab.grabclipboard(),"chi_sim"
	elif argLen == 2:
		if arg[1] == "on":
			core.runCommand(f"start \"\" \"{os.path.dirname(__file__)}\\common\\ocrServer.py\"")
			return
		if arg[1] in langList:
			t,i,l = "img",ImageGrab.grabclipboard(),langList[arg[1]]
		else:
			l = "chi_sim"
			if arg[1] == "f":
				t,i = "file",core.getFilePathFromClipboard()
			elif arg[1] == "s":
				t,i = "img",ImageGrab.grab()
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
			else:
				print(f"参数错误:{arg[1]}")
				return
		else:
			print(f"参数错误:{arg[2]}")
			return
	decode(t,i,l)

def decode(type,image,language):
	c = zerorpc.Client()
	c.connect(core.config["webocr"])
	if type == "img":
		with BytesIO() as out:
			image.save(out,format='JPEG')
			core.appedClipboardText(c.decode(out.getvalue(),language))
			out.close()
	elif type == "file":
		text = ""
		for path in image:
			if path.endswith(('.bmp','.png','.jpg','.jpeg','.jpe')):
				text += c.decode(open(path,'rb').read(),language)
		core.appedClipboardText(text)
	c.close()
