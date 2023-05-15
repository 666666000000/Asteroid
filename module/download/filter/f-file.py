
def getUrl(arg,argLen,src,dst,srcType):
	if srcType == "clipboard":
		src = [ p.strip() for p in src.replace("\"","").split("\n") if p.strip() ]
	if src:
		return src



		
		
		
		
		
		
		