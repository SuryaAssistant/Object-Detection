#!/bin/python
#Simple script for shutting down Raspberry Pi

import RPi.GPIO as GPIO
import time
import os

#Use Broadcome SOC Pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#when button is pressed
def Shutdown(channel):
    print("Raspberry Pi is Shutting Down")
    time.sleep(5)
    os.system("sudo shutdown -h.now")

#When button pressed event happens
GPIO.add_event_detect(26, GPIO.FALLING, callback=Shutdown, bouncetime=2000)

#Wait until shutdown safely
while 1:
    time.sleep(1)
