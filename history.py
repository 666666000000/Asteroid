#-*- coding : utf-8 -*-
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
