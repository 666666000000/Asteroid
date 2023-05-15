#-*- coding : utf-8 -*-
import win32clipboard
from io import BytesIO
from tkinter import colorchooser,Toplevel,Canvas
from PIL import Image as PilImage,ImageGrab,ImageTk
from ..core import core

commands = {"ps","pc","gs"}
describe = "屏幕截图，拾色，获取屏幕区域尺寸"

tmpX = 0
tmpY = 0
startX = 0
startY = 0
endX = 0
endY = 0

screenWidth = 0
screenHeight = 0

screenShot = ""
canvas = ""
lastDraw = ""
lastRect = ""
drawing = False
tmpImg = ""
capWindow = ""
background = ""
mask = ""
mode = ""
color = ""
rgb = ""

boxSize = 30
savePath = ""

def init(arg):
	global screenWidth,screenHeight
	screenWidth = arg.screenWidth
	screenHeight = arg.screenHeight


def resolve(line,isReturn):
	global savePath
	arg,argLen = core.getArgList(line)
	if arg[0] == "ps":
		if argLen == 2:
			savePath = arg[1]
		else:
			savePath = ""
		capture(arg[0])
	elif arg[0] == "pc":
		if argLen == 1:
			capture(arg[0])
		elif arg[1] == "c":
			choose = colorchooser.askcolor()
			if choose[0]:
				rgb = [ int(v) for v in choose[0] ]
				core.appedClipboardText(f"{choose[1][1:]} {rgb}")
	elif arg[0] == "gs":
		capture(arg[0])

def onLeftButtonDown(event):
	global tmpX,tmpY,drawing
	drawing = True
	tmpX = event.x
	tmpY = event.y
	
def onLeftButtonMove(event):
	global tmpX,tmpY,startX,endX,startY,endY,drawing,canvas,tmpImg,lastDraw,lastRect
	if drawing:
		startX,endX = sorted((tmpX,event.x))
		startY,endY = sorted((tmpY,event.y))
		canvas.delete(lastDraw)
		canvas.delete(lastRect)
		tmpImg = ImageTk.PhotoImage(screenShot.crop((startX,startY,endX,endY)))
		lastDraw = canvas.create_image(startX, startY ,anchor = "nw",image = tmpImg)
		lastRect = canvas.create_rectangle(startX, startY ,endX,endY,outline = "#007acc",fill = "")

def onLeftButtonUp(event):
	global drawing
	drawing = False
	
def getColor(x,y):
	global color,rgb
	rgb = screenShot.getpixel((x,y))
	color = ("%02x%02x%02x" % rgb)

def onRightButtonUp(event):
	global screenShot,capWindow,startX,endX,startY,endY,savePath
	if mode == "ps":
		if savePath:
			core.saveFile(screenShot.crop((startX,startY,endX,endY)),savePath,True,"image")
		else:
			output = BytesIO()
			screenShot.crop((startX,startY,endX,endY)).save(output,'BMP')
			data = output.getvalue()[14:]
			output.close()
			win32clipboard.OpenClipboard()
			win32clipboard.EmptyClipboard()
			win32clipboard.SetClipboardData(win32clipboard.CF_DIB,data)
			win32clipboard.CloseClipboard()
	elif mode == "pc":
		core.appedClipboardText(f"{color} {rgb}")
	elif mode == "gs":
		core.appedClipboardText(f"-s {endX-startX}x{endY-startY} -offset_x {startX} -offset_y {startY}")
	capWindow.destroy()

def onMouseMove(event):
	global lastDraw
	getColor(event.x, event.y)
	canvas.delete(lastDraw)
	endx = event.x + boxSize if (event.x + boxSize) < screenWidth else event.x - boxSize
	endy = event.y + boxSize if (event.y + boxSize) < screenHeight else event.y - boxSize
	lastDraw = canvas.create_rectangle(event.x, event.y ,endx,endy,outline = "#007acc",fill = f"#{color}")

def closeWindow(event):
	capWindow.destroy()

def capture(m):
	global screenShot,capWindow,canvas,background,mask,startX,endX,startY,endY,mode
	startX = 0
	startY = 0
	endX = screenWidth
	endY = screenHeight
	mode = m

	screenShot = ImageGrab.grab()
	capWindow = Toplevel(width = screenWidth,height = screenHeight)
	capWindow.attributes("-toolwindow",1)
	capWindow.wm_attributes("-topmost",1)
	capWindow.overrideredirect(True)
	capWindow.geometry(f"{screenWidth}x{screenHeight}+{0}+{0}")
	capWindow.bind("<Escape>",closeWindow)
	canvas = Canvas(capWindow,bg = "#FFFFFF",width = screenWidth,height = screenHeight,highlightthickness = 0)

	background = ImageTk.PhotoImage(screenShot)
	canvas.create_image(0, 0 ,anchor = "nw",image = background)
	mask = ImageTk.PhotoImage(PilImage.new(mode = "RGBA",size = (screenWidth,screenHeight),color = (30,30,30,100)))
	canvas.create_image(0, 0 ,anchor = "nw",image = mask)

	canvas.place(width = screenWidth , height = screenHeight)
	if mode == "ps" or mode == "gs":
		canvas.bind("<Button-1>",onLeftButtonDown)
		canvas.bind("<B1-Motion>",onLeftButtonMove)
		canvas.bind("<ButtonRelease-1>",onLeftButtonUp)
	elif mode == "pc":
		canvas.bind("<Motion>",onMouseMove)
	canvas.bind("<ButtonRelease-3>",onRightButtonUp)
	capWindow.focus()