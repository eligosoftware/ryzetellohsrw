from murtaza_pid_utils import *
import cv2

# test change
w,h = 360, 240

#kp ,kd ,ki
pid=[0.5,0.5,0]
pError=0
myDrone=initializeTello()
startCounter=0 # for no flight put 1, for flight 0
while True:

	# flight

	if startCounter==0:
		myDrone.takeoff()
		startCounter=1


	# Step1
	img=telloGetFrame(myDrone,w,h)

	# Step 2

	img, info=findFace(img)

	# Step 3
	pError=trackFace(myDrone,info,w,pid, pError)
	#print(info[0][0])

	cv2.imshow('Image',img)

	if cv2.waitKey(1) & 0xFF==ord('q'):
		myDrone.land()
		break

