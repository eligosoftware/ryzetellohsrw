import sys
from tello import Tello
import cv2
from time import sleep
import jetson.inference
import jetson.utils

global center, me

me =Tello()
me.connect()
print(me.get_battery())
print(me.get_current_state())

me.stream_on()

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

def move_head_to_bottle(bottle_center,image_center):
	global me
	step=10
	#print(bottle_center, image_center)
	threshold=10
	while (abs(bottle_center-image_center) > threshold):
		
		if(bottle_center<image_center):
			me.rotate_counterclockwise(step)
		if(bottle_center>image_center):
			me.rotate_clockwise(step)

def navigate(key):

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

	global me
	distance=20
	angle=10
	if key==104 : me.move_left(distance)
	elif key==106 : me.move_right(distance)

	if key==107: me.move_forward(distance)
	elif key==108: me.move_backward(distance)

	if key==119: me.move_up(distance)
	elif key==115: me.move_down(distance)

	if key==97: me.rotate_counterclockwise(angle)
	elif key==100: me.rotate_clockwise(angle)
	
	if key==114 : me.land()
	#if kp.getKey("l"): me.go_xyz_speed(0,0,10,10)
	if key==101: me.takeoff()
	#if kp.getKey("1"): me.send_command_with_return('downvision 0')
	#if kp.getKey("2"): me.send_command_with_return('downvision 1')

while True:	
	#getKeyboardInput()

	frame=me.read_frame()
	
	#cv2.imshow(sys.argv[1], cv2.imread(sys.argv[1]))
	if (frame is not None):
		image_center=frame.shape[1]/2
		cuda_image=jetson.utils.cudaFromNumpy(frame)
		detections = net.Detect(cuda_image)

		for detection in detections:
			cl_name=net.GetClassDesc(detection.ClassID)
			
			center=detection.Center
			if (cl_name=="bottle"):
				#print("Top: {}, Bottom: {}, Left: {}, Right: {}, Height: {}, Width: {}, Area: {}, Center: {}, ".format(detection.Top,detection.Bottom,detection.Left,detection.Right,				detection.Height,detection.Width, detection.Area,detection.Center))
				move_head_to_bottle(detection.Center[0],image_center)
				
			
			#print(dir(detection))
			#['Area', 'Bottom', 'Center', 'ClassID', 'Confidence', 'Contains', 'Height', 'Instance', 'Left', 'ROI', 'Right', 'Top', 'Width', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']

	#Top: 214.1015625, Bottom: 655.6640625, Left: 672.1875, Right: 841.875, Height: 441.5625, Width: 169.6875, Area: 74927.640625, Center: (757.03125, 434.8828125), 


		nmp_img=jetson.utils.cudaToNumpy(cuda_image)
		cv2.imshow('image', nmp_img)

		res = cv2.waitKey(1)
		# if (res!=-1):
		# 	print('You pressed %d (0x%x), LSB: %d (%s)' % (res, res, res % 256,
		# repr(chr(res%256)) if res%256 < 128 else '?'))

		if(chr(res%256)=='q'):
			me.land()
			break

		navigate(res)
