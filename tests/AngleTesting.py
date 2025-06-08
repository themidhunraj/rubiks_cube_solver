import gpiozero
from gpiozero import Servo, AngularServo
from pynput.keyboard import Key, Listener
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
import RPi.GPIO as GPIO

# https://gpiozero.readthedocs.io/en/stable/api_output.html
# https://core-electronics.com.au/guides/control-servo-raspberry-pi/

factory = PiGPIOFactory()   # host='127.0.0.1'    #Make sure you run sudo pigpiod first


def angularServo_x():
    """x"""
    
    #[minPulse, MaxPulse, InitialAngle]  
    set1 = [0.0005, 0.0025, 270]   # Original  0    270
    set2 = [0.0004, 0.0025, 270]   #           15    ?         Use for turns to 0deg
    set3 = [0.0005, 0.0040, 155]   #           ?    155        Use for turns to 270deg (Maxangle is 160)
    set4 = [0.0005, 0.0045, 135]   #           ?    135        Use for turns to 270deg (Maxangle is 140)
    
    
    # [minPulse, MaxPulse, InitialAngle, minAngle, maxAngle]  
    set5 = [0.0004, 0.0045, 0, 0, 144] # (0,77) == (0,270ish)  # IDEAL (-cw:0, 0:4, 90:27:, 180:50:, 270:74, +ccw: 77)
    set6 = [0.0003, 0.0045, 147, 10, 147] # (10,147) == (0,270ish) # NOT IDEAL
    set7 = [0.0002, 0.0065, 102, 10, 102] # (10,102) == ()         # NOT IDEAL
    vals = set5  # Select set
    
    initial_angle = vals[2]
    
    servo = AngularServo(21, pin_factory = factory, initial_angle=initial_angle,
                         min_angle=vals[3], max_angle=vals[4],
                         min_pulse_width=vals[0], max_pulse_width=vals[1])
    # (0.001, 0.002), 180deg: (0.001, -0.0036), 270deg (BEST): (0.0005, 0.0025)
    
    while True:
        x = input("Enter input: ")
        servo.angle = int(x)
        sleep(1)

    
def angularServo_y():
    """x"""
    
    print("Program Starting...")
    
    initial_angle = 25
    neutral_angle_y = 25    # 20 to 25 
    rotate_angle_y = 55
    flip_angle_y = -30   # -25 to -30
    
    servo = AngularServo(19, pin_factory = factory, initial_angle=initial_angle,
                         min_angle=-180, max_angle=180,
                         min_pulse_width=0.0005, max_pulse_width=0.00315)
    
    while True:
        x = input("Enter input: ")
        if x == 'flip':
            servo.angle = flip_angle_y
            sleep(0.5)
            servo.angle = neutral_angle_y
            sleep(1)
        else:
            servo.angle = int(x)
            sleep(1)
    
    
def both():
    """xxx"""
    
    
    vals = [0.0004, 0.0045, 4, 0, 144]
    servo_x = AngularServo(21, pin_factory = factory, initial_angle=vals[2],
                         min_angle=vals[3], max_angle=vals[4],
                         min_pulse_width=vals[0], max_pulse_width=vals[1])
    angle_conv = {
            "-0": 0,   # Min angle
            "0": 4,
            "90": 27,
            "180": 50,
            "270": 74,
            "+170": 77  # Max angle
    }
    
    sleep(1)
    
    initial_angle_y = 20
    neutral_angle_y = initial_angle_y  
    rotate_angle_y = initial_angle_y*(3)      #78
    flip_angle_y = initial_angle_y*(-1)
    flatten_angle_y = initial_angle_y*3   #60
    
    servo_y = AngularServo(19, pin_factory = factory, initial_angle=initial_angle_y,
                         min_angle=-180, max_angle=180,
                         min_pulse_width=0.0005, max_pulse_width=0.00315)
    sleep(1)
    
    
    custom_ang = 90
    x_ang = 90
    while True:
        x = input("Enter command: ")
        
        
        if x == 'flip':  # Current delay times are perfect and result in a perfect flip
            servo_y.angle = flip_angle_y
            sleep(0.3)  # 0.2 (flips 9/10 times) or 0.3 (flips 10/10 but cubes becomes unaligned)
            servo_y.angle = neutral_angle_y
            sleep(0.5)
        elif x == 'turn':
            servo_x.angle = x_ang
            x_ang = 90 if x_ang == 180 else 180
        elif x == 'rotate': 
            print("x_ang: ", x_ang)
            buffer = -3 if x_ang == 90 else 3
            servo_y.angle = rotate_angle_y
            sleep(1)
            servo_x.angle = angle_conv[str(x_ang)] + buffer   # Turn a little extra to correct for discrepency
            sleep(1)
            servo_y.angle = neutral_angle_y
            sleep(1)
            servo_x.angle = angle_conv[str(x_ang)]   # Turn back to angle - buffer 
            x_ang = 90 if x_ang == 180 else 180
        elif x == 'flatten':  # Current delay times are perfect and result in a perfect flatten
            servo_y.angle = flatten_angle_y
            sleep(0.2)
            servo_y.angle = neutral_angle_y
            sleep(0.5)
        elif x[0] in ['x', 'y']:   # Testing
            servo = servo_y if x[0] == 'y' else servo_x
            servo.angle = int(x[1:])
        elif x == 'custom':  # Testing variable delay times after certain degrees of rotations
            # 0.5s for 90deg turns, 1s for 180deg turnss and 
            custom_ang = 90 if custom_ang == 0 else 0
            servo_x.max_angle = 270
            sleep(1.5)
            
            # Flip
            servo_y.angle = flip_angle_y
            sleep(0.3)
            servo_y.angle = neutral_angle_y
            sleep(1)
        
def tests():
    """xxx"""
    
    angle_conv = {
            "-0": 0,   # Min angle
            "0": 4,
            "90": 27,
            "180": 50,
            "270": 74,
            "+170": 77  # Max angle
            }
    
    vals = [0.0004, 0.0045, angle_conv['90'], 0, 144]
    servo_x = AngularServo(21, pin_factory = factory, initial_angle=vals[2],
                         min_angle=vals[3], max_angle=vals[4],
                         min_pulse_width=vals[0], max_pulse_width=vals[1])
    servo_x.angle = 50
    
    
    

            
    
 
    
    
    

    
#angularServo_x()
#angularServo_y()
both()
#tests()
 










