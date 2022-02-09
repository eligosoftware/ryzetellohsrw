from murtaza_pid_utils import *
import cv2

# test change
w,h = 360, 240

myDrone=initializeTello()

while True:

	# Step1
	img=telloGetFrame(myDrone,w,h)

	# Step 2

	img, info=findFace(img)
	print(info[0][0])

	cv2.imshow('Image',img)

	if cv2.waitKey(1) & 0xFF==ord('q'):
		myDrone.land()
		break

