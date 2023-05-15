import zerorpc
import pytesseract
from PIL import Image
from io import BytesIO

class ocr(object):
	num = 1
	def decode(self,img,language):
		try:
			text = pytesseract.image_to_string(Image.open(BytesIO(img)),language)
		except:
			return "error"
		print(self.num)
		self.num += 1
		return text

s = zerorpc.Server(ocr())
s.bind("tcp://0.0.0.0:6900")
s.run()