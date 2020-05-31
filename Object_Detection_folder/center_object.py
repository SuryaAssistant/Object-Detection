'''
Center of Object Detection
Contours detection included
https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/

'''
'''
Alat Deteksi Pantulan Bola Tenis
1. Metode Deteksi :
    - Deteksi Warna Bola (yang telah di-convert ke format HSV)
2. Deteksi arah bola :
    - ke Atas/North
3. Deteksi posisi -y bola :
    - 125 <= bola <= 250 pixel, dengan imutils=500
4. Menyalakan buzzer

Update Terakhir : 15 Mei 2020
Kekurangan :
    - Posisi pencahayaan berpengaruh
    - background warna berpengaruh
    - Kecepatan bola berpengaruh terhadap tangkapan kamera    

Referensi:
1. Adrian Rosebrock
    - https://www.pyimagesearch.com/2015/09/21/opencv-track-object-movement/
    -
2. Marcelo Rovai
    - 
'''

# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())

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
    
    # loop over the contours
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # draw the contour and center of the shape on the image
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(frame, "center", (cX - 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


    # only proceed if at least one contour was found
#    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
#        c = max(cnts, key=cv2.contourArea)
#        ((x, y), radius) = cv2.minEnclosingCircle(c)
#        M = cv2.moments(c)
#        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        # only proceed if the radius meets a minimum size
#        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
#            cv2.circle(frame, (int(x), int(y)), int(radius),
#                (0, 255, 255), 2)
#            cv2.circle(frame, center, 5, (0, 0, 255), -1)
#            pts.appendleft(center)
            
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
