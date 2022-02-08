import jetson.inference
import jetson.utils
import sys
import _thread
from djitellopy import tello
from time import sleep
import keyPressModule as kp

global center

#print(sys.argv)
args_list=[]
args_list.append(__file__)
args_list.append('--input-codec=h264')
args_list.append('--input-width=480')
args_list.append('--input-height=360')
#print(args_list)

kp.init()
me= tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

sleep(10)

def vision():
	net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
	camera = jetson.utils.videoSource("rtp://0.0.0.0:8822",argv=args_list)
	display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file
	

	while display.IsStreaming():
		img = camera.Capture()
		detections = net.Detect(img)
		for detection in detections:
			cl_name=net.GetClassDesc(detection.ClassID)
			print(cl_name)
			center=detection.Center
			#if (cl_name=="bottle"):
				#print("Top: {}, Bottom: {}, Left: {}, Right: {}, Height: {}, Width: {}, Area: {}, Center: {}, ".format(detection.Top,detection.Bottom,detection.Left,detection.Right,				detection.Height,detection.Width, detection.Area,detection.Center))
				
			
			#print(dir(detection))
			#['Area', 'Bottom', 'Center', 'ClassID', 'Confidence', 'Contains', 'Height', 'Instance', 'Left', 'ROI', 'Right', 'Top', 'Width', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']

	#Top: 214.1015625, Bottom: 655.6640625, Left: 672.1875, Right: 841.875, Height: 441.5625, Width: 169.6875, Area: 74927.640625, Center: (757.03125, 434.8828125), 

		display.Render(img)
		display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))



def getKeyboardInput():
	lr,fb,ud,yv=0,0,0,0
	speed=20
	if kp.getKey("LEFT"): lr=-speed
	elif kp.getKey("RIGHT"): lr=speed

	if kp.getKey("UP"): fb=speed
	elif kp.getKey("DOWN"): fb=-speed

	if kp.getKey("w"): ud=speed
	elif kp.getKey("s"): ud=-speed

	if kp.getKey("a"): yv=speed
	elif kp.getKey("d"): yv=-speed
	
	if kp.getKey("q"): me.land()
	#if kp.getKey("l"): me.go_xyz_speed(0,0,10,10)
	if kp.getKey("e"): me.takeoff()
	#if kp.getKey("1"): me.send_command_with_return('downvision 0')
	#if kp.getKey("2"): me.send_command_with_return('downvision 1')
	return [lr,fb,ud,yv]

_thread.start_new_thread( vision, () )

while True:	
	vals=getKeyboardInput()
	#print(vals)
	me.send_rc_control(vals[0],vals[1],vals[2],vals[3])

