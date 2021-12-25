#-*- coding : utf-8 -*-
import os

def getNum(s,sym):
	if not s:
		return 0,0
	t = s.split(sym)
	if len(t) == 2:
		return t[0],t[1]
	else:
		if sym == "s":
			return s,0
		return 0,s

def getSeconds(arg):
	h,tmp = getNum(arg,"h")
	m,tmp = getNum(tmp,"m")
	s,tmp = getNum(tmp,"s")
	try:
		seconds = int(float(h)*3600 + int(m)*60 + int(s))
	except:
		print(f"参数错误:{arg}")
		return -1
	return seconds

def getHMS(count):
	m,s = divmod(count,60)
	h,m = divmod(m,60)
	return h,m,s

def loadPreset(name,path):
	parallel = "false"
	with open(path, 'r', errors = 'ignore') as file:
		for line in file:
			if line.strip().startswith("#"): 
				continue
			tmp = line.split("#")
			if len(tmp) >= 2 :
				t = tmp[0].strip()
				if t == "parallel":
					parallel = tmp[1].strip()
				elif t == name:
					preset = tmp[1].strip()
					if len(preset) == 0:
						continue
					file.close()
					return preset+" ",parallel
		file.close()
		return "error",""

def selectCamera(arg):
	if arg.find("@") != -1:
		tmp = arg.split("@")
		if len(tmp) == 2:
			try:
				if int(tmp[1])>0: 
					return int(tmp[1])	
			except:
				print(f"参数错误:{tmp[1]}")
	return 0

def checkImg(path):
	if os.path.isfile(path) and path.lower().endswith(('.bmp','.png','.jpg','.jpeg','.jpe')): 
		return True
	return False

def splitAddress(address):
	if not address:
		return None,None,None
	address = address.split()
	if len(address) < 2:
		print("地址错误:{address}")
		return None,None,None
	ip = address[0]
	port = int(address[1])
	pw = address[2] if len(address) > 2 else ""
	return ip,port,pw