'''
In this Document:
- Collect contour of object
- Collect Center of object
- Determine object (triangle, square, circle)
- Read the radius of shape in circle
- Create a circle boundary (yellow)


Referensi:
1. Adrian Rosebrock
    - https://www.pyimagesearch.com/2015/09/21/opencv-track-object-movement/
    - https://www.pyimagesearch.com/2016/02/15/determining-object-color-with-opencv/
2. Marcelo Rovai
    - 
'''

# import the necessary packages
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

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())

def mapObjectPosition (x, y):
    print ("[INFO] Object Center coordenates at X0 = {0} and Y0 =  {1}".format(x, y))
    
# Ubah bagian ini untuk mendapatkan tangkapan warna
# warna bola dalam format HSV
greenLower = (32, 120, 50) #29 90 40 (default) -- 32 150 50 (room -clean)
greenUpper = (64, 255, 255) #64 255 255

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""

# if a video path was not supplied, grab the reference
# to the webcam/raspi camera
if not args.get("video", False):
    vs = VideoStream(src=0).start()
    
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# waktu bagi kamera untuk melakukan "pemanasan"
time.sleep(2.0)

# keep looping
while True:
    # mengambil frame
    frame = vs.read()
    
    # memilih frame antara video dengan raspi camera
    frame = frame[1] if args.get("video", False) else frame
    
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break
    
    # resize frame, blur, dan ubah tangkapan kamera ke HSV
    # color space
    frame = imutils.resize(frame, width=500)
    ratio = frame.shape[0] / float(frame.shape[0])
    #hapus tanda "#" pada line dibawah untuk merotasi kamera
    #frame = imutils.rotate(frame, angle=180)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # construct a mask for the color "choose", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    sd = ShapeDetector()

    #Mendeteksi bentuk shape objek
    # loop over the contours
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
        cv2.putText(frame, shape, (cX + 20, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)
        cv2.putText(frame, "center", (cX - 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        #pakai line di bawah untuk mendapat lebih dari satu circle
        #((x, y), radius) = cv2.minEnclosingCircle(c)

    # only proceed if at least one contour was found
#    if len(cnts) > 0:
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
        
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)

            # Menampilkan posisi object
            mapObjectPosition(int(x), int(y))
            
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

#Code asli dari Adrian memiliki bug
#yaitu ketika objek tidak muncul di layar ketika pertama dibuka,
#program stuck
#        if counter >= 10 and i == 1 and pts[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
#            dX = pts[-10][0] - pts[i][0]
#            dY = pts[-10][1] - pts[i][1]
#            (dirX, dirY) = ("", "")
#solusi kode di atas berdasarkan komen di artikel Adrian
            
        
        if counter >= 10 and i == 10 and pts[i-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
            dX = pts[i-10][0] - pts[i][0]
            dY = pts[i-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
            
            # ensure there is significant movement in the
            # x-direction
            if np.abs(dX) > 20:
                dirX = "East" if np.sign(dX) == 1 else "West"
            
            # ensure there is significant movement in the
            # y-direction
            if np.abs(dY) > 20:
                dirY = "North" if np.sign(dY) == 1 else "South"
            
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
    
    # show the frame to our screen and increment the frame counter
    # hapus tanda "#" pada code dibawah ini untuk menampilkan gambar ke layar
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1
    
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
