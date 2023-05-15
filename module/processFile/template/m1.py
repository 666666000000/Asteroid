#-*- coding : utf-8 -*-

from ..core import core

describe = ""
main = ""

functions = dict()

def init(arg):
	global main
	main = arg


def resolve(line,isReturn):
	arg,argLen = core.getArgList(line)
	functions[arg[0]](arg,argLen,isReturn)

