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
import RPi.GPIO as GPIO
import serial
import smbus
bus = smbus.SMBus(1)
address = 0x68

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

        self.photo = tk.PhotoImage(file = './thermometer.gif')
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
        self.timeLabel = tk.Label(self.master, text = '{}: 00/00/00 00:00:00'.format(self.label), font = ('Arial', 20))
        self.timeLabel.pack()
        #self.updateTime()
        
    def updateTime(self, temperature):
        self.timeLabel['text'] = "{}: {:0>2}/{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(self.label, config.MONTH_CONFIGURE, config.DAY_CONFIGURE, config.YEAR_CONFIGURE, config.HOUR, config.MINUTE, config.SECOND)
        
class ConfigureTimeFrame(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.label = tk.Label(self, font = ('Arial', 20))
        self.label['text'] = 'Configuration Settings'
        self.label.pack(side=tk.TOP)
        #self.label.grid(row = 0)
        self.timeInput = ''
        
        self.timeConfigBox = Entry(self.master)
        self.timeConfigBox.pack()
        
        #Configure Seconds Button
        self.btnConfigureSecond = Button(self.master, text = 'Configure Second', command = self.configureSecond)
        self.btnConfigureSecond.pack()
        #self.btnConfigureSecond.grid(row = 1, column = 0)
        
        #Configure Minutes Button
        self.btnConfigureMinute = Button(self.master, text = 'Configure Minute', command = self.configureMinute)
        self.btnConfigureMinute.pack()
        #self.btnConfigureMinute.grid(row = 1, column = 1)
        
        #Configure Hours Button
        self.btnConfigureHour = Button(self.master, text = 'Configure Hour', command = self.configureHour)
        self.btnConfigureHour.pack()
        #self.btnConfigureHour.grid(row = 1, column = 2)
        
        #Configure Days Button
        self.btnConfigureDay = Button(self.master, text = 'Configure Day', command = self.configureDay)
        self.btnConfigureDay.pack()
        #self.btnConfigureDay.grid(row = 2, column = 0)
        
        #Configure Months Button
        self.btnConfigureMonth = Button(self.master, text = 'Configure Month', command = self.configureMonth)
        self.btnConfigureMonth.pack()
        #self.btnConfigureMonth.grid(row = 2, column = 1)
        
        #Configure Year Button
        self.btnConfigureYear = Button(self.master, text = 'Configure Year', command = self.configureYear)
        self.btnConfigureYear.pack()
        #self.btnConfigureYear.grid(row = 2, column = 2)
        
    def configureSecond(self):
        print('Configuring Seconds...')
        self.timeInput = self.timeConfigBox.get()
        config.SECOND_CONFIGURE = int(self.timeInput)
        print(config.SECOND_CONFIGURE)
        config.SECOND = convertTime(config.SECOND_CONFIGURE)
        bus.write_byte_data(address,0,config.SECOND)
        
    def configureMinute(self):
        print('Configuring Minutes...')
        self.timeInput = self.timeConfigBox.get()
        config.MINUTE_CONFIGURE = int(self.timeInput)
        print(config.MINUTE_CONFIGURE)
        config.MINUTE = convertTime(config.MINUTE_CONFIGURE)
        bus.write_byte_data(address,1,config.MINUTE)
    
    def configureHour(self):
        print('Configuring Hours...')
        self.timeInput = self.timeConfigBox.get()
        config.HOUR_CONFIGURE = int(self.timeInput)
        print(config.HOUR_CONFIGURE)
        config.HOUR = convertTime(config.HOUR_CONFIGURE)
        bus.write_byte_data(address,2,config.HOUR)
        
    def configureDay(self):
        print('Configuring Days...')
        self.timeInput = self.timeConfigBox.get()
        config.DAY_CONFIGURE = int(self.timeInput)
        print(config.DAY_CONFIGURE)
        config.DAY = convertTime(config.DAY_CONFIGURE)
        bus.write_byte_data(address,3,config.DAY)
        
    def configureMonth(self):
        print('Configuring Months...')
        self.timeInput = self.timeConfigBox.get()
        config.MONTH_CONFIGURE = int(self.timeInput)
        print(config.MONTH_CONFIGURE)
        config.MONTH = convertTime(config.MONTH_CONFIGURE)
        bus.write_byte_data(address,4,config.MONTH)
        
    def configureYear(self):
        print('Configuring Year...')
        self.timeInput = self.timeConfigBox.get()
        config.YEAR_CONFIGURE = int(self.timeInput)
        print(config.YEAR_CONFIGURE)
        config.YEAR = convertTime(config.YEAR_CONFIGURE)
        print(config.YEAR)
        bus.write_byte_data(address,5,config.YEAR)

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
        self.configurationFrame = ConfigureTimeFrame(self)
        self.configurationFrame.pack()
        
    def windowFlash(self, temperature):
        self.master.configure(background = 'black')
        
class Threads(threading.Thread):
    def __init__(self, threadID, threadType, temperature, newTemperature, window, ser):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadType = threadType
        self.temperature = temperature
        self.newTemperature = newTemperature
        self.window = window
        time.sleep(.1)
        
    def run(self):
        if (self.threadType == 'temperature'):
            x = ser.read(4)
            bytes=x.rstrip(b'\x00')
            self.newTemperature = int(bytes.decode('utf-8'))
        elif (self.threadType == 'gui'):
            self.window.update_idletasks()
            self.window.update()
            
    def getTemp(self):
        return self.newTemperature

def int_to_bcd(x):
    if (x < 0):
        raise ValueError("Cannot be a negative integer")
    
    bcdstring = ''
    while (x > 0):
        nibble = x % 16
        bcdstring = str(nibble) + bcdstring
        x >>= 4
    
    if (bcdstring == ''):
        bcdstring = 0
        
    return int(bcdstring)
    

def convertTime(x):
    x = (int(x)//10)*16+(int(x)%10)
    return (x)

def reset(pin):
    config.YEAR_CONFIGURE = 2018
    config.MONTH_CONFIGURE = 1
    config.DAY_CONFIGURE = 1
    config.HOUR_CONFIGURE = 12

if __name__ == '__main__':
    window = tk.Tk()
    window.wm_title('Temperature')
    window.geometry('1200x600')
    temperature = Temperature()
    app = Application(temperature, master = window)
    newTemperature = 0
    defaultBackgroundColor = window.cget('bg')
    ser=serial.Serial('/dev/ttyAMA0')

    config.SECOND = convertTime(datetime.now().second)
    config.MINUTE = convertTime(datetime.now().minute)
    config.HOUR = convertTime(datetime.now().hour)
    config.MONTH = convertTime(datetime.now().month)
    config.DAY = convertTime(datetime.now().day)
    config.YEAR = convertTime(datetime.now().year - 2000)

    config.DAY_CONFIGURE = datetime.now().day
    config.MONTH_CONFIGURE = datetime.now().month
    config.YEAR_CONFIGURE = datetime.now().year
    config.HOUR_CONFIGURE = datetime.now().hour
    
    bus.write_byte_data(address,0,config.SECOND)
    bus.write_byte_data(address,1,config.MINUTE)
    bus.write_byte_data(address,2,config.HOUR)
    bus.write_byte_data(address,3,config.DAY)
    bus.write_byte_data(address,4,config.MONTH)
    bus.write_byte_data(address,5,config.YEAR)
    bus.write_byte_data(address,6,0)
    bus.write_byte_data(address,14,0)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.IN)
    GPIO.setup(24, GPIO.IN)
    GPIO.add_event_detect(23, GPIO.RISING)
    GPIO.add_event_callback(23, reset)

    while True:
        config.SECOND = int_to_bcd((bus.read_byte_data(address,0)))
        config.MINUTE = int_to_bcd(bus.read_byte_data(address,1))
        config.HOUR = int_to_bcd(bus.read_byte_data(address,2))
        if (config.APPLICATION_STATE == 'running'):
            x = ser.read(4)
            bytes=x.rstrip(b'\x00')
            newTemperature = int(bytes.decode('utf-8'))
            
            if (newTemperature >= config.CRITICAL_TEMPERATURE):
                os.system('aplay ./boing_x.wav')
                window.configure(background = 'black')
                time.sleep(.05)
            
            temperature.setTemperature(int(newTemperature))

        window.update_idletasks()
        window.update()
        
        time.sleep(.05)
        
        window.configure(background = defaultBackgroundColor)  
        window.update()