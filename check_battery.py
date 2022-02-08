from djitellopy import tello
from time import sleep

me =tello.Tello()
me.connect()
print(me.get_battery())
print(me.get_current_state())
while True:
	print(me.get_speed_z())
