#-*- coding : utf-8 -*-
from PIL import ImageGrab
from . import core
from .common import saveToFile as stf

keywords = {"sa"}
describe = "保存剪贴板、桌面到文件"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "sa":
		return saveAs(arg,argLen)

def saveAs(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return
	if arg[1].endswith(('.bmp','.jpe','.jpeg','.jpg','.png')):
		if argLen == 2:
			stf.saveFile(ImageGrab.grabclipboard(),arg[1],"image")
		elif argLen >= 3 :
			if arg[2] == "s":
				stf.saveFile(ImageGrab.grab(),arg[1],"image")
			elif arg[2] == "c" or arg[2].startswith("c@"):
				return core.msg("continue")
	elif arg[1].endswith(('.xlsx')):
		return core.msg("continue")
	else:
		stf.saveFile(core.getOriClipboard(),arg[1],"txt")
