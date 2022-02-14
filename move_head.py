import sys
from tello import Tello
import cv2
import numpy as np
import jetson.utils

# screen width and height
w,h = 960, 720

# PID controller parameters
#kp ,kd ,ki
pid=[0.2,0.2,0]
pError=0

# create Tello drone instance
me =Tello()

# set yaw_velocity default value to 0
me.yaw_velocity=0

# connect to drone
me.connect()
# print drone state and battery information
# state information contains battery information
print(me.get_battery())
print(me.get_current_state())

# start stream for getting video
me.stream_on()

# create network instance of SSD-mobilenet-v2 network with precision threshold equal to 0.5
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

# this function stops the drone's yaw movement
# when no person is detected
def stop_tracking(myDrone):

# set yaw_velocity to 0
	myDrone.yaw_velocity = 0

# send the set value to drone via Tello's joystick_control command
	myDrone.joystick_control(0,0,myDrone.yaw_velocity,0)

# this function receives drone instance, information about center coordinates (x,y) of person, pid k values
# and the last error value, calculas yaw speed and new error, sends this yaw speed to drone (or stop movement
# signal, in case of missing detection), and returns new error value back to calling thread
def trackPerson(myDrone, info, w, pid, pError):

	# calculate new PID error and speed based on the center x value of detected Person and the center of image
	error=info[0] -w//2
	speed=pid[0]*error+pid[1]*(error-pError)
	speed=int(np.clip(speed,-100,100))

	print(speed)

	# if there is a detection, value of center is different from 0
	if info[0]!=0:
		myDrone.yaw_velocity= speed
	else:
	# in case of missing detection stop moving in yaw space
		myDrone.yaw_velocity = 0
		error=0
	print("sending yaw velocity, ", myDrone.yaw_velocity)
	# chack for possibility of sending joystick_control command and send the calculated speed
	if myDrone.joystick_control:
		myDrone.joystick_control(0,0,myDrone.yaw_velocity,0)
	# return error for the next iteration
	return error


# this function uses keyboard press information from OpenCV to send basic movement commands to Tello
def navigate(key):
# the codes of keys from opencv
# 119 w
# 101 e
# 100 d
# 97 a
# 115 s
# 104 h
# 106 j
# 107 k
# 108 l
# 113 q
# 114 r
# 101 e

# using global drone value
	global me
# setting distance (in cm) and angle (in degrees) values for movements
	distance=30
	angle=20

	# checking for code and sending the command
	if key==104 : me.move_left(distance)
	elif key==106 : me.move_right(distance)

	if key==107: me.move_forward(distance)
	elif key==108: me.move_backward(distance)

	if key==119: me.move_up(distance)
	elif key==115: me.move_down(distance)

	if key==97: me.rotate_counterclockwise(angle)
	elif key==100: me.rotate_clockwise(angle)
	
	if key==114: me.land()
	# some commands were deactivated and being tested right now
	#if kp.getKey("l"): me.go_xyz_speed(0,0,10,10)
	if key==101: me.takeoff()
	#if kp.getKey("1"): me.send_command_with_return('downvision 0')
	#if kp.getKey("2"): me.send_command_with_return('downvision 1')

# main thread of running
while True:

	# read frame from Tello
	frame=me.read_frame()


	if (frame is not None):
		# resize frame image to width and height, given above
		img = cv2.resize(frame, (w, h))
		# change the image format from Numpy array to CUDA (used for jetson detection)
		cuda_image=jetson.utils.cudaFromNumpy(img)
		# detect objects from CUDA image
		detections = net.Detect(cuda_image)

		# flag for checking if object was found
		object_found = False
		# list for center coordinates of object
		objectsListC = []
		# list for area values of detections
		objectsArea = []
		# iterate over detections
		for detection in detections:
			# get class name from ID
			cl_name=net.GetClassDesc(detection.ClassID)
			# get detection center coordinates
			center=detection.Center
			# check for class name, only person is required in this implementation
			if (cl_name=="person"):
				# set the flag to true
				object_found=True
				# print detection values
				#print("Top: {}, Bottom: {}, Left: {}, Right: {}, Height: {}, Width: {}, Area: {}, Center: {}, ".format(detection.Top,detection.Bottom,detection.Left,detection.Right,				detection.Height,detection.Width, detection.Area,detection.Center))
				# append found detection center and area to responding lists
				objectsListC.append(detection.Center)
				objectsArea.append(detection.Area)
		# if there were detections found
		if len(objectsArea) != 0:
			# get the center value with maximum area
			i = objectsArea.index(max(objectsArea))
			# send tracking command and update PID error value
			pError = trackPerson(me, objectsListC[i], w, pid, pError)
		# if object was not found
		if object_found == False:
		# stop drone movement
			stop_tracking(me)

			# test code for understanding detection objects inside structure
			#print(dir(detection))
			#['Area', 'Bottom', 'Center', 'ClassID', 'Confidence', 'Contains', 'Height', 'Instance', 'Left', 'ROI', 'Right', 'Top', 'Width', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']

	#Top: 214.1015625, Bottom: 655.6640625, Left: 672.1875, Right: 841.875, Height: 441.5625, Width: 169.6875, Area: 74927.640625, Center: (757.03125, 434.8828125), 

		# convert the cuda image with detections on it back to numpy image
		nmp_img=jetson.utils.cudaToNumpy(cuda_image)
		# show that numpy image on desktop
		cv2.imshow('image', nmp_img)

		# opencv wait for keyboard press
		res = cv2.waitKey(1)
		# if (res!=-1):
		# 	print('You pressed %d (0x%x), LSB: %d (%s)' % (res, res, res % 256,
		# repr(chr(res%256)) if res%256 < 128 else '?'))
		# if q was pressed land drone and stop loop execution
		if(chr(res%256)=='q'):
			me.land()
			break
		# else use the given command to move the drone
		navigate(res)

