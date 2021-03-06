'''
Deteksi Pantulan Bola Tenis 'Real-Time'
1. Metode Deteksi :
    - Deteksi Warna Bola (yang telah di-convert ke format HSV)
2. Deteksi arah bola :
    - ke Atas/North
3. Deteksi posisi -y bola :
    - y1 < bola < y2 pixel
4. Menyalakan buzzer
Update Terakhir : 2 Agustus 2020
'''

# import 
from __future__ import print_function
from pyimagesearch.shapedetector import ShapeDetector
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import os
import RPi.GPIO as GPIO
import Adafruit_ADS1x15
import subprocess
from subprocess import Popen, PIPE

# Calling ADC
subprocess.Popen(["python3", "ADC_reading.py"], stdout=PIPE, stderr=PIPE)

# initialize LED and buzzer GPIO
redLed = 13
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(redLed, GPIO.OUT)

#initialize exit button
GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP)

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())

# Start with LED off
GPIO.output(redLed, GPIO.LOW)
ledOn = False

Bola = ("Tidak Ada")

# Use default value if there is a  missing value of ADC_reading
Lower_default = (32, 120, 50)
Upper_default = (64, 255, 255)

# initialize the list of tracked points, the frame counter, and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""

if not args.get("video", False):
    vs = VideoStream(src=0).start()
    
else:
    vs = cv2.VideoCapture(args["video"])

# waktu bagi kamera untuk melakukan "pemanasan"
time.sleep(2.0)

# keep looping
while True:
    with open("variabel_hsv.txt", "r", encoding = "utf-8") as g:
        data_hsv = list(map(int, g.readlines()))

    # warna bola dalam format HSV
    # if real all variable
    if len(data_hsv) == 4:
        greenLower = (data_hsv[0], data_hsv[2], data_hsv[3])
        greenUpper = (data_hsv[1], 255, 255)
    # if only read 3 variable
    if len(data_hsv) == 3:
        greenLower = (data_hsv[0], data_hsv[2], Lower_default[3])
        greenUpper = (data_hsv[1], 255, 255)
    #if only read 2 variable
    if len(data_hsv) == 2:
        greenLower = (data_hsv[0], Lower_default[1], Lower_default[2])
        greenUpper = (data_hsv[1], 255, 255)
    #if only read 1 variable
    if len(data_hsv) == 1:
        greenLower = (data_hsv[0], Lower_default[1], Lower_default[2])
        greenUpper = (Upper_default[0], 255, 255)
    # if ADC didnt read
    if len(data_hsv) == 0:
        greenLower = (Lower_default[0], Lower_default[1], Lower_default[2])
        greenUpper = (Upper_default[0], 255, 255)
        
    # mengambil frame
    frame = vs.read()    
    frame = frame[1] if args.get("video", False) else frame
    
    if frame is None:
        break
    
    # resize frame, blur, dan ubah tangkapan kamera ke HSV
    frame = imutils.resize(frame, width=500)
    ratio = frame.shape[0] / float(frame.shape[0])
    
    #hapus tanda "#" pada line di bawah untuk merotasi kamera
    #frame = imutils.rotate(frame, angle=180)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    #menentukan posisi keadaan bola = on (bola tertangkap kamera).
    #ubah nilai height_low untuk mengubah zona tangkapan sensor (0 < height_low < 180) pixel
    #semakin besar, maka sempit zona deteksi
    height_low = 80
    width_line = 500
    height_high = int((480/640*width_line)-height_low)
    cv2.line(frame, (0, height_low), (width_line, height_low), (0, 255, 0), 2)
    cv2.line(frame, (0, height_high), (width_line, (height_high)), (0, 255, 0), 2)
    cv2.putText(frame, "Zona Deteksi", (0, height_low+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, "Objek = "+ Bola, (0, height_low+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # find contours in the mask and initialize the current
    # (x, y) center of the object
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    sd = ShapeDetector()

    #Mendeteksi bentuk shape objek
    for c in cnts:
    # compute the center of the contour, then detect the name of the
    # shape using only the contour
        M = cv2.moments(c)
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        shape = sd.detect(c)
    # multiply the contour (x, y)-coordinates by the resize ratio,
    # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX, cY), 5, (255, 255, 255), -1)
        #cv2.line

        cv2.putText(frame, "center", (cX - 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
    # only proceed if at least one contour was found
    #if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        
        #Menentukan luasan area tangkapan terbesar
        c = max(cnts, key=cv2.contourArea)
        
        #pakai line ini untuk memilih satu circle terbesar
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        
        #Menentukan titik tengah objek untuk tracking
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        # proses apabila radius objek yang terdeteksi memenuhi syarat
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)
            
            #menampilkan posisi semua object
  #          cv2.putText(frame, "X = {0} and Y =  {1}".format(int(x), int(y)), (cX - 20, cY - 40),
  #              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # loop over the set of tracked points
    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue
        
        # check to see if enough points have been accumulated in
        # the buffer
    
        # menentukan arah bola
        if counter >= 1 and i == 1 and pts[i-1] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # menentukan perpindahan objek dari jarak 1 frame sebelumnya dengan
            # frame sekarang
            dX = pts[i-1][0] - pts[i][0]
            dY = pts[i-1][1] - pts[i][1]
            (dirX, dirY) = ("", "")
            
            if len(cnts)==0:
                dX = 0
                dY = 0
                GPIO.output(redLed, GPIO.LOW)
                lenOn = False
                Bola = ("Tidak Ada")
            if len(cnts)>0:
                Bola = ("Ada")
            # ensure there is significant movement in the
            # x-direction
            #jika perubahan posisi > 20 pixel, maka objek dianggap bergerak
                if np.abs(dX) > 20:
                    dirX = "Kiri" if np.sign(dX) == 1 else "Kanan"
            # ensure there is significant movement in the
            # y-direction
                if np.abs(dY) > 20:
                    dirY = "Bawah" if np.sign(dY) == 1 else "Atas"
                
                #jika bola bergerak ke arah atas
                if (dY) <= -15:
                    #jika bola berada di luar zona deteksi sensor, buzzer mati
                    if (y < height_low):
                        GPIO.output(redLed, GPIO.LOW)
                        ledOn = False
                    if (y > height_low):
                        if (y > height_high):
                                GPIO.output(redLed, GPIO.LOW)
                                ledOn = False
                    #jika bola berada di dalam zona deteksi, buzzer = on
                    #if (y > height_low):
                        if (y < height_high):
                            #jika bola hilang di dalam zona deteksi, buzzer = off
                            if len(cnts)==0:
                                dX = 0
                                dY = 0
                                GPIO.output(redLed, GPIO.LOW)
                                lenOn = False
                            #jika bola muncul di zona deteksi, buzzer = on
                            if len(cnts)>0:
                                if not ledOn:
                                    GPIO.output(redLed, GPIO.HIGH)
                                    ledOn = True
                                #jika bola tidak terdeteksi
                                elif ledOn:
                                    GPIO.output(redLed, GPIO.LOW)
                                    ledOn = False
                #jika bola turun
                if (dY) > -15:
                    GPIO.output(redLed, GPIO.LOW)
                    lenOn = False
         
            # handle when both directions are non-empty
            if dirX != "" and dirY != "":
                direction = "{}-{}".format(dirY, dirX)
            
            # otherwise, only one direction is non-empty
            else:
                direction = dirX if dirX != "" else dirY

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
    
    # show the movement deltas and the direction of movement on
    # the frame
    cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 0, 255), 3)
    cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.35, (0, 0, 255), 1)
    
    #HSV value
    cv2.putText(frame, "Lower : {}".format(greenLower), (1, 15), cv2.FONT_HERSHEY_SIMPLEX,
        0.45, (255, 255, 255), 1)
    cv2.putText(frame, "Upper : {}".format(greenUpper), (1, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.45, (255, 255, 255), 1)
    
    # hapus tanda "#" pada code dibawah ini untuk menampilkan gambar ke layar
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1

    if (GPIO.input(5) == 0):
        key = ord("q")
        print("Program dihentikan")
        
    # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    #mematikan program melalui button GPIO5
    
    if key == ord("q"):
        break


# if not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# hentikan semua window yang berjalan
GPIO.output(redLed, GPIO.LOW)
GPIO.cleanup()
cv2.destroyAllWindows()
