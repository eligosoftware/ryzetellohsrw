from murtaza_pid_utils import *
import cv2

w,h = 360, 240

myDrone=initializeTello()

while True:

	#Step1
	img=telloGetFrame(myDrone,w,h)
	cv2.imshow('Image',img)

	if cv2.waitKey(1) & 0xFF==ord('q'):
		myDrone.land()
		break

