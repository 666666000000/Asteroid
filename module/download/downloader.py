import os
import time
import requests

def start(parm,header):
	data = parm['data']
	length = len(data["urls"])
	for index in range(parm['current'], length):
		parm['current'] = index
		if os.path.exists(f"{parm['dst']}/{data['names'][index]}"):
			print(f"线程: {parm['index']} 下载 {index + 1}/{length} {data['names'][index]} : 已存在")
			continue
		print(f"线程: {parm['index']} 下载 {index + 1}/{length} : {data['urls'][index]} : {data['names'][index]}")
		if "ref" in data:
			print(data["ref"][index])
			header["Referer"] = data["ref"][index]
		count = 1
		while True:
			if not parm["event"].is_set():
				return
			try:
				response = requests.get(data["urls"][index], headers=header, timeout=30)
			except:
				count += 1
				if count > 7:
					print(f"<--------------------线程: {parm['index']} 下载错误 {index + 1}/{length} : {data['names'][index]}-------------------->")
					break
				print(f"线程: {parm['index']} 第 {count} 次重新下载 {index + 1}/{length} : {data['names'][index]}")
				time.sleep(5)
				continue
				
			print(f"线程: {parm['index']} 下载 {index + 1}/{length} 状态码 : {response.status_code}")
			if response.status_code != 200:
				print(f"线程: {parm['index']} 下载失败 {index + 1}/{length} : {data['names'][index]}")
				break
			try:
				with open (f"{parm['dst']}/{data['names'][index]}",'wb') as f:
					f.write(response.content)
					f.close()
				break
			except:
				print(f"线程: {parm['index']} 保存文件错误 {index + 1}/{length} : {parm['dst']}/{data['names'][index]}")
		time.sleep(5)

		
		
		
		
		
		
		