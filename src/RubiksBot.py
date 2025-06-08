from time import sleep
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory



# Description: This script is for the purpose of controlling the physical bot or hardware that makes real time movements
#              ...to the Rubiks cube. Each of which are executed through commands to the motors.


class RubiksBot:
    """Class represting controls for the phsyical bot. Used for making directional rotations, 
    revolutions and such to the Rubik's cube through use of the two servo motors."""

    def __init__(self) -> None:
        """Contructor class for the RubiksBot class."""

        # * Cube placement: When cube is placed in bot, the bottom side must be face down with the face side direction opposite of the hinge

        # Tracks orientation of the Rubiks cube, relative to the bot     (Positions(indexes): 0=BotFront, 1=BotRight, 2=BotBack, 3=BotLeft, 4=BotTop, 5=BotBottom)
        self.bot_state = ['FACE', 'RIGHT', 'BACK', 'LEFT', 'TOP', 'BOTTOM']

        # Holds steps to get to any of other five positions from position 5
        self.load_instructions = {  # r= CounterClockWise, c=Clockwise
            "0": ['y'],
            "1": ['xr', 'y'],
            "2": ['xc', 'xc', 'y'],
            "3": ['xc', 'y'],
            "4": ['y', 'y'],
            "5": []
        }
        
        # Delay values
        self.post_turn_delay = 1    # Post move delay 
        self.mid_flip_delay = 0.3   # Mid Flip delay  (Much long to wait after servo_y has been moved to flip position)
        self.flatten1_delay = 0.2
        self.flatten2_delay = 0.5
    
        """ Servo x values """
        # Servo x servo angle to common angle value conversion
        self.angle_conv = {
            "-0": 0,   # Min angle
            "0": 4,
            "90": 27,
            "180": 50,
            "270": 74,
            "+270": 77  # Max angle
        }

        # [minPulse, MaxPulse, InitialAngle, minAngle, maxAngle]  
        self.vals = [0.0004, 0.0045, 4, 0, 144]
        initial_angle_x = self.vals[2]
        self.ccw_angle = -90
        self.cw_angle = 90
        self.curr_angle = 0
        
        """ Servo y values """
        initial_angle_y = 20
        self.neutral_angle = initial_angle_y   
        self.rotate_angle = initial_angle_y*(3)
        self.flip_angle = initial_angle_y*(-1)
        self.flatten_angle = initial_angle_y*3 


        # Initialize both servos
        factory = PiGPIOFactory()
        servo_x_pin = 21
        servo_y_pin = 19
        self.servo_x =  AngularServo(servo_x_pin, pin_factory = factory, initial_angle=initial_angle_x,
                    min_angle=self.vals[3], max_angle=self.vals[4],
                    min_pulse_width=self.vals[0], max_pulse_width=self.vals[1])
        sleep(1.5)
    
        self.servo_y = AngularServo(servo_y_pin, pin_factory = factory, initial_angle=initial_angle_y,
                    min_angle=-180, max_angle=180,
                    min_pulse_width=0.0005, max_pulse_width=0.00315)
        

    def update_bot_state(self, specifics):
        """Updates the class variable bot_state after each cube revolution."""

        direction = specifics[0]    # cw, ccw
        plane = specifics[1]        # x, y
        move = specifics[2]         # bot, cube

        # Scenario 1: If rotating bot horizontally (Positions unchanged: 4, 5. Positions changed: 0, 1, 2, 3)
        if plane == 'x' and move == 'bot':
            # Assign variables based on direction value
            points = [0, 4, 1] if direction == 'cw' else [3, -1, -1]
            for i in range(3):
                start = points[0]
                end = points[1]
                step = points[2]

            # Update state
            prev_pos = self.bot_state[3] if direction == 'cw' else self.bot_state[0]
            for i in range(start, end, step): 
                temp = self.bot_state[i]
                self.bot_state[i] = prev_pos
                prev_pos = temp

        # Scenario 2: If rotating bot vertically (Positions unchanged: 1, 3. Positions changed: 0, 4, 2, 5)
        if plane == 'y' and move == 'bot':
            prev_pos = self.bot_state[0]
            for i in [5, 2, 4, 0]:
                temp = self.bot_state[i]
                self.bot_state[i] = prev_pos
                prev_pos = temp


    def flatten_cube(self):
        """Lowers the top cover down close enough to touch the top of the cube, flattening any regions
        that stick out."""

        self.servo_y.angle = self.flatten_angle
        sleep(self.flatten1_delay)
        self.servo_y.angle = self.neutral_angle
        sleep(self.flatten2_delay)


    def load_side(self, side):
        """Revolves cube to place 'side' to position 5, which is the bottom 
        facing position, from where you can call turn_cube to rotate side."""     

        # Initialize variables  
        side_pos = self.bot_state.index(side)  # Get location of target side
        directions = self.load_instructions[str(side_pos)]   # Get direction to load the specified phase
        
        # Execute each move in direction one by one
        for i in range(len(directions)):
            step = directions[i]

            if step[0] == 'y':      # If vertical move
                self.turn_bot_y()
            elif step[0]  == 'x':   # If horizontal move
                direction = 'cw' if step[1] == 'c' else 'ccw'
                self.turn_bot_x(direction)


    def get_buffer_val(self, new_angle):
        """Returns buffer value that are used to overturn the cube
        during rotations. This prevents jams and any irregularities
        when a side is being rotated.
        Returns: int"""
    
        ca = self.curr_angle
        na = new_angle
        
        possible_pos_combs = [[0, 90], [0, 180], [0, 270], [90, 180], [90, 270], [180, 270]]
        
        if [ca, na] in possible_pos_combs:
            return 2
        else:
            return -3
    

    def get_sleep_val(self, angles_moved):
        """Returns a value that represents how long the program will pause
        to allow the motor to execute a turn. This value varys depending on
        the duration of the turn.
        Returns: float"""

        ca = self.curr_angle
        na = angles_moved
        
        diff = abs(ca - na)
        if diff == 90:
            return 0.5
        elif diff == 180:
            return 1.0
        else:
            return 1.5


    def turn_bot_x(self, direction, action='turn_bot'):
        """Rotates servo_x, either revolving or rotating the cube.
        Args: direction= direction of rotation (cw or ccw).
              action= intention behind turn (turn_bot or turn_cube)
        """
        
        sleep_val = None

        # Update class data structure (Only if the cube is being revolved and not rotated)
        self.update_bot_state([direction, "x", 'bot']) if action == 'turn_bot' else None
        
        # Determine target angle
        angle_factor = self.cw_angle if direction == 'cw' else self.ccw_angle
        target_angle = None
        if self.curr_angle + angle_factor < 0:
            target_angle = 270
        elif self.curr_angle + angle_factor > 270:
            target_angle = 0
        else:
            target_angle = self.curr_angle + angle_factor


        # Perform physical turn
        buffer = self.get_buffer_val(target_angle) if action == 'turn_cube' else 0
        
        if self.curr_angle == 0 and target_angle == 270:  # Triggers a 270deg cw turn
            self.servo_x.angle = self.angle_conv['270'] + buffer  # Buffer= +*
            self.curr_angle = 270
            sleep_val = 1.5
        elif self.curr_angle == 270 and target_angle == 0:  # Triggers a 270deg ccw turn
            self.servo_x.angle = self.angle_conv['0'] + buffer  # Buffer= -*
            self.curr_angle = 0
            sleep_val = 1.5
        else:
            sleep_val = self.get_sleep_val(target_angle)
            self.servo_x.angle = self.angle_conv[str(target_angle)] + buffer
            self.curr_angle = target_angle
        sleep(sleep_val)


    def turn_bot_y(self):
        """Turns servo_y for the purpose of flipping the cube."""

        # Update class data structure
        self.update_bot_state([None, "y", 'bot'])

        # Perform physical turn
        self.servo_y.angle = self.flip_angle
        sleep(self.mid_flip_delay)
        self.servo_y.angle = self.neutral_angle
        sleep(0.5)
        
        self.flatten_cube()  # Flatten cube
        

    def turn_cube(self, direction):
        """Rotates the current loaded side in the specified direction.
        Args: direction= direction of rotation (cw or ccw)."""

        # Perform physical turn
        self.servo_y.angle = self.rotate_angle  # Lower hood to clamp cube
        sleep(0.5)
        self.turn_bot_x(direction, "turn_cube")      # Rotate cube side by calling function
        self.servo_y.angle = self.neutral_angle
        sleep(0.5)
        
        # Revert to position minus buffer
        self.servo_x.angle = self.angle_conv[str(self.curr_angle)]
        sleep(0.2)
        
        self.flatten_cube()  # Flatten cube
        
