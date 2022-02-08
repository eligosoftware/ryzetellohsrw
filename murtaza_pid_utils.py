from djitellopy import Tello
import cv2

def initializeTello():
	myDrone=Tello()
	myDrone.connect()
	myDrone.for_back_velocity = 0
	myDrone.left_right_velocity=0
	myDrone.up_down_velocity=0
	myDrone.yaw_velocity=0
	myDrone.speed=0
	print(myDrone.get_battery())
	myDrone.streamoff()
	myDrone.streamon()
	
	return myDrone

def telloGetFrame(myDrone,w=360, h=240):
	myFrame = myDrone.get_frame_read()
	myFrame = myFrame.frame
	img = cv2.resize(myFrame,(w,h))
	return img
