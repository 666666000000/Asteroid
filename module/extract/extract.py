#-*- coding : utf-8 -*-
import re
from ..core import core

commands = {"ext","rem","ret"}
describe = "提取元素"
result = list()
pattern = ""
last = ""
main = ""

def init(arg):
	global main,pattern
	main = arg
	pattern = core.loadCommand("module\\extract\\pattern.txt")


def resolve(line,isReturn):
	global result,last,pattern
	arg,argLen = core.getArgList(line)
	repeat = False
	append = False
	src = "*"
	p = ["","","0","0","0"]
	for i in range(min(len(arg),len(p))):
		p[i] = arg[i]
	if p[0] == "ext":
		if not core.checkArgLength(arg,2):
			return
		if p[1] == "r":
			pattern = core.loadCommand("module\\extract\\pattern.txt")
			return
		if p[1] == "<l>":
			p[1] = last
		
		if last != p[1]:
			last = p[1]
		for i in range(2,5):
			if p[i] == "r":
				repeat = True
			elif p[i] == "a":
				append = True
			elif p[i] != "0":
				src = p[i]
		if src == "*":
			data = core.getClipboard("strip")
		else:
			data = core.getInputPath(src)
		if not data:
			return main.setEntry("无数据")
		if isinstance(data,list):
			data = "".join(data)
		if not append:
			result.clear()

		if p[1].find("+") != -1:
			for t in p[1].split("+"):
				if t in pattern:
					addData(result,re.findall(pattern[t],data,re.DOTALL),repeat)
				else:
					print(f"参数错误:{t}")
		else:
			if p[1] == "ori":
				if repeat:
					result.append(data)
				elif data not in result:
					result.append(data)
			elif p[1] not in pattern:
				return main.setEntry(f"参数错误:{p[1]}")
			else:
				addData(result,re.findall(pattern[p[1]],data,re.DOTALL),repeat)
		if not result:
			return main.setEntry(f"未提取到元素")
		print("提取元素:",len(result))
		if isReturn:
			return result

	elif p[0] == "rem":
		r = core.getClipboard("strip") if not p[1] else p[1]
		for i in range(len(result)):
			if result[i].find(r) != -1:
				print(f"删除第 {i+1} 个元素:",result[i])
				del result[i]
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


def addData(ret,data,repeat):
	if not data:
		return
	if repeat:
		ret.extend(data)
	else:
		[ ret.append(d) for d in data if d not in ret ]
				

