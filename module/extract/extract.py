#-*- coding : utf-8 -*-
import re
from ..core import core

commands = {"ext","rem","ret"}
describe = "提取html元素"
result = list()
pattern = ""
last = ""
main = ""

def init(arg):
	global main,pattern
	main = arg
	pattern = core.loadCommand("module\\extract\\config.txt")


def resolve(line,isReturn):
	global result,last,pattern
	arg,argLen = core.getArgList(line)
	p = ["","","0"]
	for i in range(min(len(arg),len(p))):
		p[i] = arg[i]
	if p[0] == "ext":
		if not core.checkArgLength(arg,2):
			return
		if p[1] == "r":
			pattern = core.loadCommand("module\\extract\\config.txt")
			return
		if p[1] == "<l>":
			p[1] = last
		
		if last != p[1]:
			last = p[1]

		data = core.getClipboard("strip")
		if not data:
			return main.setEntry("剪贴板无数据")

		if p[2] == "0":
			result.clear()

		if p[1].find("+") != -1:
			for t in p[1].split("+"):
				if t in pattern:
					result.extend(re.findall(pattern[t],data,re.DOTALL))
				else:
					print(f"参数错误:{t}")
		else:
			if p[1] not in pattern:
				return main.setEntry(f"参数错误:{p[1]}")
			result.extend(re.findall(pattern[p[1]],data,re.DOTALL))

		if not result:
			return main.setEntry(f"未提取到元素")
		print("提取元素:",len(result))
		if isReturn:
			return result

	elif p[0] == "rem":
		r = core.getClipboard("strip")
		for i in range(len(result)):
			if result[i].find(r) != -1:
				del result[i]
				print("删除:",i+1)
				return
		print("未找到元素")

	elif p[0] == "ret":
		if not p[1]:
			print("返回:",len(result))
			return result
		else:
			start = int(p[1])
			end = int(p[2])
			if end == 0:
				print(f"返回 {start}:{len(result)}",)
				return result[start-1:]
			else:
				print(f"返回 {start}:{end}",)
				return result[start-1:end]



