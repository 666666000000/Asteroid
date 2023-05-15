#-*- coding : utf-8 -*-

from ..core import core

commands = {""}
describe = ""

main = ""
def init(arg):
	global main
	main = arg


def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	if arg[0] == "":
		pass

