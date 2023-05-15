import re


header = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9',
	'cache-control': 'max-age=0',
	'referer': 'https://m.weibo.cn/',
	'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
	'sec-ch-ua-mobile': '?0',
	'sec-ch-ua-platform': '"Windows"',
	'sec-fetch-dest': 'document',
	'sec-fetch-mode': 'navigate',
	'sec-fetch-site': 'cross-site',
	'sec-fetch-user': '?1',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

def getUrl(arg,argLen,src,dst,srcType):
	data = dict()
	data["urls"] = list()
	data["names"] = list()

	if srcType == "htmls":
		src = "".join(src)
	if srcType == "str" or srcType == "htmls":
		src = [ t[:-1].replace("orj360","large") for t in re.findall("https://.*?[\"\n]",src,re.DOTALL) ]
	else:
		src = [ t.replace("orj360","large") for t in src ]
	for url in src:		
		data["urls"].append(url)
		data["names"].append(url.rsplit("/",1)[-1]) 	
	print(data)
	if data["urls"]:
		return data
