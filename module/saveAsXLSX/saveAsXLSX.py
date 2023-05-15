#-*- coding : utf-8 -*-
from openpyxl import Workbook
from ..core import core

commands = {"sa"}
describe = "从剪贴板读取数据保存到XLSX文件"

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if not core.checkArgLength(arg,2):
		return
	if not arg[1].endswith(('.xlsx')):
		return "continue"

	wb = Workbook()
	ws = wb.active
	sym = arg[2] if argLen == 3 else " "
	for line in core.getClipboard("list"):
		ws.append( line.split(sym) )
	return core.saveFile(wb,arg[1],True,"xlsx")	


