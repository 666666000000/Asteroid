#-*- coding : utf-8 -*-
from ..core import core

commands = {"saveh","loadh","clearh"}
describe = "保存、加载、清空命令历史"

class Node:
	def __init__(self):
		self.val = None
		self.pre = None
		self.next = None

class History:
	def __init__(self,length = 19):
		self.cNode = Node()
		self.vNode = self.cNode
		for i in range(length):
			tmp = Node()
			tmp.pre = self.vNode
			self.vNode.next = tmp
			self.vNode = tmp
		self.vNode.next = self.cNode
		self.cNode.pre = self.vNode
		
	def add(self,line):
		if self.cNode.pre.val != line:
			self.cNode.val = line
			self.cNode = self.cNode.next
		self.vNode = self.cNode

	def clear(self):
		while self.cNode.pre.val:
			self.cNode = self.cNode.pre
			self.cNode.val = ""

	def save(self,dst):
		self.vNode = self.cNode.next
		while True:
			if self.vNode.val:
				dst.write(self.vNode.val+"\n")
			self.vNode = self.vNode.next
			if self.vNode.pre == self.cNode:
				break
		self.vNode = self.cNode

	def getPre(self):
		if self.vNode.pre.val:
			self.vNode = self.vNode.pre
			return self.vNode.val

	def getNext(self):
		if self.vNode.next.val:
			self.vNode = self.vNode.next
			return self.vNode.val

main = ""
history = ""
def init(arg):
	global main,history
	main = arg
	history = arg.hy

def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "clearh":
		if argLen == 1:
			for value in history.values():
				value.clear()
		elif arg[1] in history:
			history[arg[1]].clear()
		else:
			main.setEntry(f"未找到:{arg[1]}")
	elif arg[0] == "saveh":
		with open("module\\history\\history.txt", "w", encoding = 'utf-8', errors = 'ignore') as file:
			for key,value in history.items():
				file.write(f"<{key}>\n")
				history[key].save(file)
				file.write("\n")
			file.close()
	elif arg[0] == "loadh":
		tmp = core.loadDict("module\\history\\history.txt")
		if not tmp:
			return
		for key,value in tmp.items():
			if key in history:
				for val in value:
					history[key].add(val)