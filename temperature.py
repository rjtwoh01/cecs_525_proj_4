import random
import tkinter as tk
from tkinter import Tk, Entry, Button, INSERT, Text
from tkinter.ttk import *
import subprocess
import time
import io
import os
import dis
import threading
import config
from time import sleep
from datetime import datetime

class Temperature(object):
	def __init__(self):
		self.temperature = 0
		self.obeservers = []

	def setTemperature(self, newTemperature):
		self.temperature = newTemperature
		for callback in self.obeservers:
			callback(self.temperature)

	def bind(self, callback):
		self.obeservers.append(callback)

class CriticalFrame(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.createBox()
		#temperature.bind(self.criticalTemp())
		
	def createBox(self):
		self.critTempLabel = tk.Label(self.master, font=('Arial', 25))
		self.critTempLabel.pack()
		self.critTempLabel['text'] = "Enter a \nCritical Temperature"
		self.critTempLabel['fg'] = 'black'
		self.critTempBox = Entry(self.master)
		self.critTempBox.pack()
		self.btnCritTemp = Button(self.master, text = 'Enter', command = self.applyTemp)
		self.btnCritTemp.pack()
		
	def applyTemp(self):
		self.critTemperature = self.critTempBox.get()
		config.CRITICAL_TEMPERATURE = int(self.critTemperature)
		print(config.CRITICAL_TEMPERATURE)

	#def criticalTemp(self):
		#temperature = Temperature()

		#e = Entry(self)
		#e.pack(side='top', anchor='n')
		#b = Button(root, text='Set Critical Temperature', command=app)
		#b.pack(side='top', fill="y", expand=True)

class TemperatureFrame(tk.Frame):
	def __init__(self, temperature, master=None):
		super().__init__(master)
		self.createText()
		temperature.bind(self.updateTemperature)
		self.degree_sign= u'\N{DEGREE SIGN}'
		self.flashCounter = 0

	def createText(self):
		self.temperatureLabel = tk.Label(self.master, font=('Arial', 50))
		self.temperatureLabel.pack(side = tk.LEFT)

	def updateTemperature(self, temperature):
		self.celsius = (temperature - 32) * (5/9)
		self.celsius = float("{0:.2f}".format(self.celsius))
		self.text = str(temperature) + self.degree_sign + 'F\n' + str(self.celsius) + self.degree_sign + 'C'
		self.temperatureLabel['text'] = format(self.text)
		if (temperature >= config.CRITICAL_TEMPERATURE):
			self.temperatureLabel['fg'] = 'red'
			#self.flash()
			#print("After flash")
		elif (temperature >= 60):
			self.temperatureLabel['fg'] = 'green'
		else:
			self.temperatureLabel['fg'] = 'blue'
			
	def flash(self):
		print("In flash")
		#self.temperatureLabel['fg'] = 'red'
		#time.sleep(0.5)
		#self.temperatureLabel['fg'] = 'black'
		#time.sleep(0.5)
		#self.temperatureLabel['fg'] = 'red'
		if (self.flashCounter == 0):
			self.temperatureLabel.config(fg = 'red')
			self.after(500, self.flash)
		elif(self.flashCounter == 1):
			self.temperatureLabel.config(fg = 'black')
			self.after(500, self.flash)
		else:
			self.flashCounter = 0
		
						
class ThermometerFrame(tk.Frame):
	def __init__(self, temperature, master=None):
		super().__init__(master)
		self.canvas = tk.Canvas(self, width = 200, height = 800)
		self.canvas.pack()

		self.photo = tk.PhotoImage(file = '/home/ryan/thermometer.gif')
		self.canvas.create_image(100, 300, image = self.photo)
		self.canvas.create_oval(100 - 42, 530 - 42, 100 + 42, 530 + 42, fill = 'red')
		temperature.bind(self.drawMercury)

	def drawMercury(self, temperature):
		self.canvas.delete('line')
		self.critTemp = config.CRITICAL_TEMPERATURE
		self.drawHeight = 530 - temperature * 4
		if (self.drawHeight <= 80):
			self.drawHeight = 80
		self.canvas.create_line(100, 530, 100, self.drawHeight, width = 35, fill = 'red', tag = 'line')
		
class TimeFrame(tk.Frame):
	def __init__(self, temperature, label = None, master = None, toggeling = False):
		super().__init__(master)
		self.label = label
		self.createText()
		temperature.bind(self.updateTime)
		
	def createText(self):
		self.timeLabel = tk.Label(self.master, text = '{}: 00:00:00'.format(self.label), font = ('Arial', 20))
		self.timeLabel.pack()
		#self.updateTime()
		
	def updateTime(self, temperature):
		self.timeLabel['text'] = "{}: {:0>2}:{:0>2}:{:0>2}".format(self.label, datetime.now().hour, datetime.now().minute, datetime.now().second)

class Pause(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.createButton()
		self.applicationState = config.APPLICATION_STATE
		
	def createButton(self):
		self.btnPause = Button(self.master, text = 'PAUSE', command = self.pause)
		self.btnPause.pack()
		
	def pause(self):
		if (self.applicationState == 'running'):
			self.applicationState = 'paused'
		elif (self.applicationState == 'paused'):
			self.applicationState = 'running'
			
		config.APPLICATION_STATE = self.applicationState
		print(config.APPLICATION_STATE)
	
	def getApplicationState(self):
		return self.applicationState

class Application(tk.Frame):
	def __init__(self, temperature, master = None):
		super().__init__(master)
		self.pack()
		self.initFrames(temperature)

	def initFrames(self, temperature):
		self.thermometerFrame = ThermometerFrame(temperature, self)
		self.thermometerFrame.pack(side = tk.LEFT)
		self.temperatureFrame = TemperatureFrame(temperature, self)
		self.temperatureFrame.pack(side = tk.LEFT)		
		self.critFrame = CriticalFrame(self)
		self.critFrame.pack()	
		self.pauseButton = Pause(self)
		self.pauseButton.pack()
		self.timeFrame = TimeFrame(temperature, 'Clock', self)
		self.timeFrame.pack()
		
	def windowFlash(self, temperature):
		self.master.configure(background = 'black')
		
class Threads(threading.Thread):
	def __init__(self, threadID, threadType, temperature, newTemperature, window):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.threadType = threadType
		self.temperature = temperature
		self.newTemperature = newTemperature
		self.window = window
		time.sleep(1)
		
	def run(self):
		if (self.threadType == 'temperature'):	
			self.newTemperature = random.uniform(30, 106)
		elif (self.threadType == 'gui'):
			self.window.update_idletasks()
			self.window.update()
			
	def getTemp(self):
		return self.newTemperature

def intToBCD(x):
	if (x < 0):
		raise ValueError("Cannot be a negative integer")
	
	bcdString = ''
	while (x > 0):
		nibble = x % 16
		bcdString = str(nibble) + bcdString
		x >>= 4
	
	if (bcdString == ''):
		bcdString = 0
		
	bcdInt = int(bcdString)	
	return bcdInt
	

if __name__ == '__main__':
	window = tk.Tk()
	window.wm_title('Temperature')
	window.geometry('1200x600')
	temperature = Temperature()
	app = Application(temperature, master = window)
	newTemperature = 0
	defaultBackgroundColor = window.cget('bg')

	while True:
		if (config.APPLICATION_STATE == 'running'):
			temperatureThread = Threads(1, 'temperature', temperature, newTemperature, window)
			temperatureThread.daemon = True #this allows the thread to get killed after it runs
			temperatureThread.start()
			newTemperature = temperatureThread.getTemp()
			
			if (newTemperature >= config.CRITICAL_TEMPERATURE):
				window.configure(background = 'black')
				time.sleep(.05)
			
			#temperatureThread._stop() #undocumented way to stop a thread
			#newTemperature = random.uniform(30, 106)
			temperature.setTemperature(int(newTemperature))
			#print(config.CRITICAL_TEMPERATURE)
			
						
		#guiThread = Threads(1, 'gui', temperature, newTemperature, window)  
		window.update_idletasks()
		window.update()
		
		time.sleep(.05)
		
		window.configure(background = defaultBackgroundColor)  
		window.update()
		
		#guiThread.start()

		#time.sleep(5) #5 second delay
