# 电机和传感器联动，用于视频中Broll的演示
from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

# Create your objects here.
hub = MSHub()

# Write your program here.
hub.speaker.beep()

paper_scanner = ColorSensor('E')
motor_a = Motor('A')

while True:
    print('testing...')
    color = paper_scanner.get_color()
    if not_equal_to(color, None):
        hub.status_light.on(color)
        motor_a.start(60)
        print(color)
    else :
        motor_a.stop()
        print('stop')