#-*- coding : utf-8 -*-
import win32clipboard
from io import BytesIO
from math import floor
from tkinter import colorchooser,Toplevel,Canvas
from PIL import Image as PilImage,ImageGrab,ImageDraw,ImageTk
from . import core
from .common import saveToFile as stf

initArg = ["screenWidth","screenHeight"]
keywords = {"ps","pc","gs"}
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
colorStep = 0
wstep = 40
hstep = 30

savePath = ""

def init(arg):
	global screenWidth,screenHeight,colorStep
	screenWidth = arg[0]
	screenHeight = arg[1]
	wcount = screenWidth/wstep
	hcount = screenHeight/hstep
	colorStep = floor(255/((wcount*hcount)**(1/3)))

def resolve(line):
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
		elif arg[1] == "p":
			capture("pal")
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
			stf.saveFile(screenShot.crop((startX,startY,endX,endY)),savePath,"image")
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
	elif mode == "pal":
		getColor(event.x,event.y)
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

def closeWindows(event):
	capWindow.destroy()

def drawPalettes(draw):
	x = 0
	y = 0
	for r in range(colorStep,255,colorStep):
		for g in range(colorStep,255,colorStep):
			for b in range(colorStep,255,colorStep):
				draw.rectangle((x, y ,x + wstep,y + hstep),width = 0,fill = (r,g,b))
				if x + wstep>screenWidth:
					x = 0
					y += hstep
					if y>screenWidth:
						return
				else:
					x += wstep

def capture(m):
	global screenShot,capWindow,canvas,background,mask,startX,endX,startY,endY,mode
	startX = 0
	startY = 0
	endX = screenWidth
	endY = screenHeight
	mode = m
	if mode == "ps" or mode =="pc" or mode =="gs":
		screenShot = ImageGrab.grab()
	capWindow = Toplevel(width = screenWidth,height = screenHeight)
	capWindow.attributes("-toolwindow",1)
	capWindow.wm_attributes("-topmost",1)
	capWindow.overrideredirect(True)
	capWindow.geometry(f"{screenWidth}x{screenHeight}+{0}+{0}")
	capWindow.bind("<Escape>",closeWindows)
	canvas = Canvas(capWindow,bg = "#FFFFFF",width = screenWidth,height = screenHeight,highlightthickness = 0)
	if mode == "ps" or mode =="pc" or mode =="gs":
		background = ImageTk.PhotoImage(screenShot)
		canvas.create_image(0, 0 ,anchor = "nw",image = background)
		mask = ImageTk.PhotoImage(PilImage.new(mode = "RGBA",size = (screenWidth,screenHeight),color = (30,30,30,100)))
		canvas.create_image(0, 0 ,anchor = "nw",image = mask)
	elif mode == "pal":
		screenShot = PilImage.new("RGB",(screenWidth,screenHeight),(255,255,255))
		draw = ImageDraw.ImageDraw(screenShot)
		drawPalettes(draw)
		background = ImageTk.PhotoImage(screenShot)
		canvas.create_image(0, 0 ,anchor = "nw",image = background)
	canvas.place(width = screenWidth , height = screenHeight)
	if mode == "ps" or mode == "gs":
		canvas.bind("<Button-1>",onLeftButtonDown)
		canvas.bind("<B1-Motion>",onLeftButtonMove)
		canvas.bind("<ButtonRelease-1>",onLeftButtonUp)
	elif mode == "pc":
		canvas.bind("<Motion>",onMouseMove)
	canvas.bind("<ButtonRelease-3>",onRightButtonUp)
	capWindow.focus()