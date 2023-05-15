import time
import subprocess


def getUrl(arg,argLen,src,dst,srcType):
	data = dict()
	data["urls"] = list()
	for line in src.split():
		data["urls"].append(line)
	if data["urls"]:
		return data


def start(parm):
	data = parm['data']
	length = len(data["urls"])
	for index in range(parm['current'],length):
		parm['current'] += 1
		if not parm["event"].is_set():
			return
		print(f"线程: {parm['index']} 下载 {index+1}/{length} {data['urls'][index]}")
		command = f"cmd /c \"you-get -o {parm['dst']} {data['urls'][index]}\""
		process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		stdout,stderr = process.communicate()
		print(stdout.decode("utf-8"))
		if process.returncode  ==  0:
			print(f"线程: {parm['index']} 下载成功 {index+1}/{length}")
		else:
			print(f"线程: {parm['index']} 下载错误 {index+1}/{length} {stderr}")
		time.sleep(5)


		
		
		
		
		
		
		