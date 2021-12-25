#-*- coding : utf-8 -*-
from openpyxl import Workbook
from . import core
from .common import saveToFile as stf
keywords = {"sa"}
describe = "从剪贴板读取数据保存到XLSX文件"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "sa":
		return saveAs(arg,argLen)

def saveAs(arg,argLen):
	if argLen < 2:
		print(f"参数错误:{arg}")
		return
	if arg[1].endswith(('.xlsx')):
		wb = Workbook()
		ws = wb.active
		sym = arg[2] if argLen == 3 else " "
		for line in core.getOriClipboard().split("\n"):
			ws.append( line.split(sym) )
		stf.saveFile(wb,arg[1],"xlsx")
	else:
		return core.msg("continue")
