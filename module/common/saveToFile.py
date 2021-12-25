#-*- coding : utf-8 -*-
from .. import core
import traceback

def saveFile(input,path,type):
	path = core.replaceFileName(path)
	outDir = core.getOutputDirPath(path,"None","list","checkDir","file")
	if not outDir:
		print(f"目标路径错误:{path}")
		return
	for out in outDir:
		print(out)
		try:
			if type == "image":
				input.save(out,quality = 95)
			elif type == "xlsx":
				input.save(out)
			elif type == "txt":
				core.writeTXT(out,input)
		except Exception as e:
			print("保存文件错误")
			traceback.print_exc()