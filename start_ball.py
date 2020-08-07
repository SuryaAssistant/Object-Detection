#!/bin/python
#Simple script for start program of Raspberry Pi

import RPi.GPIO as GPIO
import time
import os
import subprocess
#os.putenv('DISPLAY', ':0')

#Use Broadcome SOC Pin numbers
GPIO.setmode(GPIO.BCM)

GPIO.setup(10, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#When button pressed event happens
while True:
    #start program for preview (ADC reading)
    if GPIO.input(10) == GPIO.LOW:
        print("Program pendeteksian bola sedang berjalan (dengan display)")
        time.sleep(2)
        subprocess.call(["sudo", "python3", "/home/pi/deteksi_bola.py"])
        #os.system("sudo python3 deteksi_bola.py")
        
    #start program
    if GPIO.input(11) == GPIO.LOW:
        print("Program pendeteksian bola sedang berjalan (tanpa display)")
        time.sleep(2)
        subprocess.call(["sudo", "python3", "home/pi/deteksi_bola_no_display.py"])
        #os.system("sudo python3 deteksi_bola.py")
    #shutdown
    if GPIO.input(26) == GPIO.LOW:
        print("Raspberry Pi is Shutting Down")
        time.sleep(5)
        subprocess.call(["sudo", "shutdown", "-h", "now"])
        #os.system("sudo shutdown -h now")
        GPIO.cleanup()
