
header = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
	}

def getUrl(arg,argLen,src,dst,srcType):
	data = dict()
	data["urls"] = list()
	data["names"] = list()

	if srcType == "str":
		src = src.split() 
	for url in src:
		data["urls"].append(url)
		data["names"].append(url.rsplit("/",1)[-1]) 
	if data["urls"]:
		return data


		