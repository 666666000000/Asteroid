#-*- coding : utf-8 -*-
from PIL import ImageGrab
from ..core import core

commands = {"sa"}
describe = "保存剪贴板、桌面到文件"

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	return saveAs(arg,argLen)

def saveAs(arg,argLen):
	if not core.checkArgLength(arg,2):
		return
	p = ["","w"]
	for i in range(min(len(arg[1:]),len(p))):
		p[i] = arg[1+i]
	
	if p[0].endswith('.xlsx') or p[1] == "c" or p[1].startswith("c@"):
		return "continue"
	
	if p[0].endswith(('.bmp','.jpe','.jpeg','.jpg','.png')):
		dataType = 	"image"
		if p[1] == "s":
			data = ImageGrab.grab()
		else:
			data = ImageGrab.grabclipboard()
	else:
		dataType = "text"
		data = core.getClipboard("ori")
	return core.saveFile(data,p[0],True,dataType,p[1])	
	