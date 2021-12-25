#-*- coding : utf-8 -*-
import os
from PyPDF2 import PdfFileMerger
import traceback
from . import core

keywords = {"mpdf"}
describe = "合并pdf"

def resolve(line):
	arg,argLen = core.getArgList(line)
	if arg[0] == "mpdf":
		return core.setEntry(mergePDF(arg,argLen))

def mergePDF(arg,argLen):
	if argLen < 3:
		return "缺少参数"
	src = core.getInputPath(arg[1])
	if not src:
		return "缺少源文件"
	dst = core.getOutputDirPath(arg[2],src[0],"first","checkDir","file")
	if not dst:
		return "目标路径错误"
	pdfList = list()
	for s in src:
		if os.path.isfile(s):
			if s.endswith(".pdf"):
				pdfList.append(s)
		else:
			for f in os.listdir(s):
				if os.path.isfile(os.path.join(s,f)) and f.endswith(".pdf"):
					pdfList.append(os.path.join(s,f))
	if not pdfList:
		return "未找到pdf文件"
	merger = PdfFileMerger()
	try:
		for pdf in pdfList:
			merger.append(pdf)
		merger.write(dst)
	except:
		merger.close()
		traceback.print_exc()
		return "合并错误"
	merger.close()
	return "合并完成"
