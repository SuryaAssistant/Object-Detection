#!/bin/python
#Simple script for start program of Raspberry Pi

import RPi.GPIO as GPIO
import time
import os

#Use Broadcome SOC Pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#when button is pressed
def StartDetection(channel):
    print("Program pendeteksian bola sedang berjalan")
    time.sleep(2)
    os.system("python3 deteksi_bola.py")

#When button pressed event happens
GPIO.add_event_detect(11, GPIO.FALLING, callback=StartDetection, bouncetime=2000)

#Wait until program loaded
while 1:
    time.sleep(2)
