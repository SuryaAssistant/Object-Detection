'''
Deteksi objek dan tracking dengan OpenCV
Berdasarkan program OpenCV tracking objek oleh Adrian Rosebrock
Original post: https://www.pyimagesearch.com/2016/05/09/opencv-rpi-gpio-and-gpio-zero-on-the-raspberry-pi/
Dikebangkan berikutnya oleh Marcelo Rovai - MJRoBot.org @ 9Feqb2018 
Diubah terakhir 11 Mei 2020 oleh Fandi Adinata
'''

# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
import imutils
import time
import cv2
import os
import RPi.GPIO as GPIO

# initialize LED GPIO
redLed = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(redLed, GPIO.OUT)

# print object coordinates
def mapObjectPosition (x, y):
    print ("[INFO] Object Center coordenates at X0 = {0} and Y0 =  {1}".format(x, y))

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] waiting for camera to warmup...")
vs = VideoStream(0).start()
time.sleep(2.0)

# define the lower and upper boundaries of the object
# to be tracked in the HSV color space
colorLower = (29, 90, 40)
colorUpper = (64, 255, 255)

# Start with LED off
GPIO.output(redLed, GPIO.LOW)
ledOn = False

# loop over the frames from the video stream
while True:
    # grab the next frame from the video stream, Invert 180o, resize the
    # frame, and convert it to the HSV color space
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    #frame = imutils.rotate(frame, angle=180)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the object color, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the object
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            # position Servo at center of circle
            mapObjectPosition(int(x), int(y))
            
            # if the led is not already on, turn the LED on
            if (y <125):
                GPIO.output(redLed, GPIO.LOW)
                ledOn = False
            if (y > 125):
                if (y > 250):
                        GPIO.output(redLed, GPIO.LOW)
                        ledOn = False
            if (y > 125):
                if (y < 250):
                    if not ledOn:
                        GPIO.output(redLed, GPIO.HIGH)
                        ledOn = True

    # if the ball is not detected, turn the LED off
                    elif ledOn:
                        GPIO.output(redLed, GPIO.LOW)
                        ledOn = False
        

    # menampilkan hasil tangkapan kamera ke layar
    # hapus tanda "#" pada kode di bawah untuk melihat hasil
    cv2.imshow("Frame", frame)
    
    # if [ESC] key is pressed, stop the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
            break

# do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff \n")
GPIO.output(redLed, GPIO.LOW)
GPIO.cleanup()
cv2.destroyAllWindows()
vs.stop()
