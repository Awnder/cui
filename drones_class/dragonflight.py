#!/usr/bin/env python3

import dji_matrix as djim
import logging, logging.config
from datetime import datetime
import math
import asyncio

# LOGGING CONFIGURATION
# from Professor Tallman
# Create one log file for each hour of the day to balances the number of files
#   with the size of each file. If we run the drone multiple times within the
#   same hour, each run will be logged in the same file.
now = datetime.now().strftime('%Y%m%d%H')
logfile = f"dragon.{now}.log"

logging.basicConfig(filename=logfile, level=logging.DEBUG, format="%(asctime)s %(message)s")

#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class Dragon():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Uses djitellopy.Tello class as the base object.
    """

    def __init__(self, drone_object: object, mission_parameters: dict, debug_level=logging.info):
        """
        Constructor that establishes a connection with the drone. Pass in a
        djitellopy Tello object to give your HeadsUpTello object its wings.

        Arguments
            drone_object: A new djitellopy.Tello() object
            mission_parameters: dictionary of mission parameters, includes floor and ceiling in cm
                mission_parameters = {
                    'ceiling': 200,
                    'floor': 0, 
                    ...
                }
            debug_level:  Set the desired logging level.
                          logging.info shows every command and response 
                          logging.WARN will only show problems
                          There are other possibilities, see logging module
        """

        # HeadsUpTello class uses the design principal of composition (has-a)
        # instead of inheritance (is-a) so that we can choose between the real
        # drone and a simulator. If we had used inheritance, we would be forced
        # to choose one or the other.
        self.drone = drone_object
        self.drone_name = mission_parameters['drone_name']
        self.mission_name = mission_parameters['mission_name']
        self.ceiling = mission_parameters['ceiling']
        self.floor = mission_parameters['floor']
        self.min_takeoff_power = mission_parameters['min_takeoff_power']
        self.min_operating_power = mission_parameters['min_operating_power']
        self.drone.LOGGER.setLevel(debug_level)
        self.x = 0
        self.y = 0
        self.current_heading = 0
        self._max_movement = 500
        self._min_movement = 20
        self._grounded = True

        try:
            self.drone.connect()
            self.connected = True
        except Exception as excp:
            logging.fatal(f"ERROR: could not connect to Trello Drone: {excp}")
            logging.debug(f" => Did you pass in a valid drone base object?")
            logging.debug(f" => Verify that your firewall allows UDP ports 8889 and 8890.")
            logging.debug(f"    The Chromebook's firewall reverts to default settings every")
            logging.debug(f"    time that you restart the virtual Linux environment.")
            logging.debug(f" => You may need to connect to the drone with the Trello App.")
            self.connected = False
            self.disconnect()
            raise
        return

    def __del__(self):
        """ Destructor that gracefully closes the connection to the drone. """
        if self.connected:
            self.disconnect()
        return

    def disconnect(self):
        """ Gracefully close the connection with the drone. """
        self.drone.end()
        self.connected = False
        logging.info(f"Drone connection closed gracefully")
        logging.info('------------------------------------')
        return

    def top_led_color(self, red:int, green:int, blue:int):
        """
        Change the top LED to the specified color. The colors don't match the
        normal RGB palette very well.

        Arguments
            red:   0-255
            green: 0-255
            blue:  0-255
        """
        self._check_operating_power()

        r = djim.capped_color(red)
        g = djim.capped_color(green)
        b = djim.capped_color(blue)
        cmd = f"EXT led {r} {g} {b}"
        self.drone.send_control_command(cmd)
        return
            
    def top_led_off(self):
        """ Turn off the top LED. """

        self.top_led_color(0, 0, 0)
        return

    def matrix_pattern(self, flattened_pattern:str, color:str='b'):
        """
        Show the flattened pattern on the LED matrix. The pattern should be 
        64 letters in a row with values either (r)ed, (b)lue, (p)urple, or (0)
        off. The first 8 characters are the top row, the next 8 are the second
        row, and so on. If only one color is desired, the '*' and '0' chars
        can be used as a binary coding system.  
        
        Arguments
            flattened_pattern: see examples in dji_matrix.py
            color:             'r', 'b', or 'p'
        """
        self._check_operating_power()

        if color.lower() not in "rpb":
            color = 'b'
        cmd = f"EXT mled g {flattened_pattern.replace('*', color.lower())}"
        self.drone.send_control_command(cmd)
        return

    def matrix_off(self):
        """ Turn off the 64 LED matrix. """
        off_pattern = "0" * 64
        self.matrix_pattern(off_pattern)
        return

    def get_battery(self):
        """ Returns the drone's battery level as a percent. """
        return self.drone.get_battery()

    def get_barometer(self):
        """ Returns the drone's current barometer reading in cm from the ground. The accuracy of this reading fluctates with the weather. """
        return self.drone.get_barometer()
    
    def get_height(self):
        """ Returns the drone's current height in cm from the ground. """
        return self.drone.get_height()
    
    def get_temperature(self):
        """ Returns the drone's internal temperature in °F. """
        return self.drone.get_temperature()
    
    def takeoff(self):
        """ Takeoff the drone to around 40-60 cm """
        logging.info('drone taking off')
        self._check_takeoff_power()
        logging.info(f'battery: {self.get_battery()}')
        self._wait(1)
        self._grounded = False
        return self.drone.takeoff()

    def land(self):
        """ Land drone from any height """
        logging.info('drone landing')
        self._grounded = True
        return self.drone.land()

    def streamon(self):
        """ turns on video streaming, use get_frame_read after """
        self.drone.streamon()

    def streamoff(self):
        """ turns off video streaming """
        self.drone.streamoff()
    
    def set_video_fps(self, fps: str='30'):
        """ set video fps either 5, 15, or 30"""
        self.drone.set_video_fps(fps)

    def get_frame_read(self):
        """ returns a videoframe from camera """
        return self.drone.get_frame_read()

    def send_rc_control(self, left_right_velocity: int, forward_backward_velocity: int, up_down_velocity: int, yaw_velocity: int):
        """
        Send RC control commands to the drone.

        Arguments:
            left_right_velocity: Velocity in the left/right direction (-100 to 100)
            forward_backward_velocity: Velocity in the forward/backward direction (-100 to 100)
            up_down_velocity: Velocity in the up/down direction (-100 to 100)
            yaw_velocity: Yaw velocity (-100 to 100)
        """
        self._check_operating_power()
        logging.debug(f'Sending RC control: lr={left_right_velocity}, fb={forward_backward_velocity}, ud={up_down_velocity}, yaw={yaw_velocity}')
        self.drone.send_rc_control(left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity)
        
    def fly_up(self, up: int):
        """ 
        fly up to a certain height. 
        if the desired height is above the ceiling, the drone will fly to ceiling 
        if the drone has less than 20 cm to fly, then it will ignore the command
        """
        self._check_operating_power()

        desired_height = self.get_height() + up
        logging.debug(f'drone is at {self.get_height()}, desired height is at {desired_height}, ceiling is at {self.ceiling}')
        
        if desired_height > self.ceiling:
            logging.warning('desired height is above ceiling')
            adjusted_height = self.ceiling - self.get_height()
            logging.debug(f'adjusted height is {adjusted_height}')
            if adjusted_height >= self._min_movement:
                logging.debug(f'drone flying to {self.get_height() + adjusted_height}')
                self.drone.move_up(adjusted_height)
                self._wait(adjusted_height)
            else:
                logging.warning(f'adjusted height is less than 20, drone ignoring command')
        else:
            logging.debug(f'drone flying to {desired_height}')
            self.drone.move_up(up)
            self._wait(up)

    def fly_down(self, down: int):
        """
        fly down to a certain height. 
        if the desired height is below the floor, the drone will fly to the floor 
        if the drone has less than 20 cm to fly, then it will ignore the command
        """
        self._check_operating_power()
        
        desired_height = self.get_height() - down
        logging.debug(f'drone is at {self.get_height()}, desired height is at {desired_height}, floor is at {self.floor}')
        
        if desired_height < self.floor:
            logging.warning('desired height is below floor')
            adjusted_height = self.get_height() - self.floor
            logging.debug(f'adjusted height is {adjusted_height}')
            if adjusted_height >= self._min_movement:
                logging.debug(f'drone flying to {self.get_height() - adjusted_height}')
                self.drone.move_down(adjusted_height)
                self._wait(adjusted_height)
            else:
                logging.warning(f'adjusted height is less than 20, drone ignoring command')
        else:
            logging.debug(f'drone flying to {desired_height}')
            self.drone.move_down(down)
            self._wait(down)

    def fly_forward(self, amount):
        """ move drone forward - considered +x direction """
        # drone can't move below 20 cm, chose 480 b/c next number divisible by 20 from 500
        self._fly_xy_amount('forward', amount)
        self._update_absolute_coordinates(self._calculate_vector_from_magnitude('forward', amount))

    def fly_backward(self, amount):
        """ move drone backward - considered -x direction """
        self._fly_xy_amount('backward', amount)
        self._update_absolute_coordinates(self._calculate_vector_from_magnitude('backward', amount))

    def fly_right(self, amount):
        """ move drone right - considered -y direction """
        self._fly_xy_amount('right', amount)
        self._update_absolute_coordinates(self._calculate_vector_from_magnitude('right', amount))

    def fly_left(self, amount):
        """ move drone left - considered +y direction """
        self._fly_xy_amount('left', amount)
        self._update_absolute_coordinates(self._calculate_vector_from_magnitude('left', amount))

    def fly_to_coordinates(self, desired_x: int, desired_y: int, direct: bool=False):
        """ 
        given coordinates, calculate vector to the new position
        Parameters:
            desired_x (int): x coordinate
            desired_y (int): y coordinate
            direct (bool): determines if drone rotates and flies straight to destination
        """
        self._check_operating_power()

        logging.debug(f'drone given coordinates to fly to ({desired_x},{desired_y})')

        if direct:
            distance_x = desired_x - self.x
            distance_y = desired_y - self.y

            angle = int(round(math.degrees(math.atan2(distance_y, distance_x)),0))
            magnitude = int(round(math.sqrt((distance_x)**2 + distance_y**2),0))

            logging.debug(f'drone flying direct: calculated direct angle {angle}, magnitude {magnitude}')

            if angle < 0: # normalize a negative angle
                angle += 360
            
            self.rotate_to_bearing(angle)
            self.fly_forward(magnitude)
        else:
            # need to figure out given coordinates but not direct
            diff_x = desired_x - self.x
            diff_y = desired_y - self.y

            delta_x = int(round(diff_x * math.cos(math.radians(self.current_heading)) + diff_y * math.sin(math.radians(self.current_heading)),0))
            delta_y = int(round(-diff_x * math.sin(math.radians(self.current_heading)) + diff_y * math.cos(math.radians(self.current_heading)),0))

            logging.debug(f'drone flying in rectangle: calculated delta x: {delta_x}, delta y: {delta_y}')

            if delta_x > 0:
                self.fly_backward(delta_x)
            else:
                self.fly_forward(abs(delta_x))

            if delta_y > 0:
                self.fly_right(delta_y)
            else:
                self.fly_left(abs(delta_y))

    def fly_home(self, direct_flight: bool=True):
        """
        move drone home from any coordinates
        Arguments:
            direct_flight (bool): if True, drone will orient to origin and fly directly, else drone will rotate to 0 deg and fly in two lines
        """
        self._check_operating_power()
        
        logging.debug(f'drone moving from ({self.x},{self.y}) to (0,0)')
        distance_to_home = int(round(math.sqrt(self.x**2 + self.y**2)),0)
        logging.debug(f'distance to home: {distance_to_home}')
        
        angle_to_origin = math.atan2(self.y, self.x) # in radians
        angle_to_origin_deg = math.degrees(angle_to_origin)
        turn_angle = int(round(angle_to_origin_deg - self.current_heading),0)

        # help from chatgpt to determine which direction to turn - it still doesn't really work
        # it only turns ccw to the origin right now
        if direct_flight:
            if turn_angle > 0:
                self.rotate_ccw(turn_angle + 180)
            elif turn_angle < 0:
                self.rotate_cw(abs(turn_angle - 180))
            self.fly_forward(distance_to_home)
            self._wait(distance_to_home)
        else:
            absolute_x = abs(self.x)
            absolute_y = abs(self.y)

            if self.x > 0:
                self.fly_backward(absolute_x)
            else:
                self.fly_forward(absolute_x)
            self._wait(absolute_x)
            if self.y > 0:
                self.fly_right(absolute_y)
            else:
                self.fly_left(absolute_y)
            self._wait(absolute_y)
        
    def fly_to_mission_floor(self):
        """ 
        move drone to mission floor 
        if drone is above mission floor and < 20cm, will overcorrect by flying up 30cm and fly back down
        if drone is below mission floor and < 20cm, will overcorrect by flying up 30cm + that extra amount and fly back down
        """
        self._check_operating_power()
        
        distance = self.get_height() - self.floor
        magnitude = abs(distance)
        overcorrect = 30

        logging.debug(f'drone is at {self.get_height()} and floor is at {self.floor}')
        logging.debug(f'drone is {distance} away from floor')

        # can only move at distances of 20cm, so need to correct if necessary
        if magnitude < self._min_movement:
            # drone is above mission floor
            if distance > 0:
                logging.debug(f'drone overcorrecting and flying to {self.get_height() + overcorrect}')
                self.drone.move_up(overcorrect) # move up to overcorrect with some room for error
                self._wait(overcorrect)
                logging.debug(f'drone flying to {self.floor}')
                self.drone.move_down(self.get_height() - self.floor) # move back down to mission floor
                self._wait(self.get_height()-self.floor)
            else:
            # drone is below mission floor
                logging.debug(f'drone overcorrecting and flying to {magnitude + 30}')
                self.drone.move_up(magnitude + overcorrect) # move up to overcorrect
                self._wait(magnitude + overcorrect)
                logging.debug(f'drone flying to {self.floor}')
                self.drone.move_down(abs(self.get_height() - self.floor))
                self._wait(abs(self.get_height() - self.floor))
        else:
            if distance > 0:
                logging.debug(f'drone flying to {self.floor}')
                self.drone.move_down(distance)
                self._wait(distance)
            else:
                logging.debug(f'drone flying to {self.floor}')
                self.drone.move_up(magnitude)
                self._wait(magnitude)

        logging.debug(f"drone is at floor: {self.floor} with actual height at {self.get_height()}")
    
    def fly_to_mission_ceiling(self):
        """ 
        move drone to mission ceiling 
        if drone is < 20cm from ceiling, will overcorrect by flying down 30cm and fly back
        """
        self._check_operating_power()
        
        distance = self.ceiling - self.get_height()
        magnitude = abs(distance)
        overcorrect = 30

        logging.debug(f'drone is at {self.get_height()} and ceiling is at {self.ceiling}')
        logging.debug(f'drone is {distance} away from ceiling')

        # can only move at distances of 20cm, so need to correct if necessary
        if magnitude < self._min_movement:
            logging.debug(f'drone overcorrecting and flying to {self.get_height() - overcorrect}')
            self.drone.move_down(overcorrect) # move down to overcorrect with some room for error
            self._wait(overcorrect)
            logging.debug(f'drone flying to {self.ceiling - self.get_height()}')
            self.drone.move_up(self.ceiling - self.get_height()) # move back up to self.ceiling
            self._wait(self.ceiling - self.get_height())
        else:
            logging.debug(f'drone flying to {self.ceiling}')
            self.drone.move_up(distance)
            self._wait(distance)

        logging.debug(f"drone is at ceiling: {self.ceiling} with actual height at {self.get_height()}")
 
    def flip_forward(self):
        """ do a flip forward """
        self.drone.flip_forward()

    def flip_backward(self):
        """ do a flip backward """
        self.drone.flip_back()

    def flip_right(self):
        """ do a flip right """
        self.drone.flip_right()

    def flip_left(self):
        """ do a flip left """
        self.drone.flip_left()

    def rotate_to_bearing(self, degrees: int):
        """ rotate drone to absolute bearing taking into account current heading """
        self._check_operating_power()

        if self.current_heading == degrees:
            logging.debug(f'drone is already facing {degrees} degrees')
            return

        logging.debug(f'drone rotating to bearing from {self.current_heading} to {degrees} degrees')

        degrees = degrees % 360

        ccw_degrees = degrees - self.current_heading
        cw_degrees = 360 - ccw_degrees

        if ccw_degrees <= cw_degrees:
            self.rotate_ccw(ccw_degrees)
        else:
            self.rotate_cw(cw_degrees)

    def rotate_cw(self, degrees: int):
        """ rotate drone clockwise """
        self._check_operating_power()
        
        logging.debug(f'drone rotating cw {degrees} degrees')
        self.drone.rotate_clockwise(degrees)
        self._update_heading(degrees)
        self._wait(degrees)

    def rotate_ccw(self, degrees: int):
        """ rotate drone counter clockwise """
        self._check_operating_power()
        
        logging.debug(f'drone rotating ccw {degrees} degrees')
        self.drone.rotate_counter_clockwise(degrees)
        self._update_heading(degrees)
        self._wait(degrees)

    def _fly_xy_amount(self, direction: str, amount: int):
        """ 
        internal method to move drone, handles amount. moves 480 cm at a time if 500 < amount < 520
        direction (str):
            forward: +x
            backward: -x 
            right: -y
            left: +y
        amount (int): cm
        """
        self._check_operating_power()
        if amount < 20:
            logging.warning('drone ignoring command, amount is less than 20')
            return

        # if 500 < amount < 520
        if amount > self._max_movement and amount < self._max_movement+20:
            _max_movement_adjusted = 480
            amount_times = amount // _max_movement_adjusted
            amount_extra = amount % _max_movement_adjusted

            # move 480 cm at a time
            for _ in range(amount_times):
                self._fly_xy_direction(direction, _max_movement_adjusted)

            # move the remaining distance
            self._fly_xy_direction(direction, amount_extra)
            
        # if the desired amount is >= 520
        elif amount >= self._max_movement + 20:
            amount_times = amount // self._max_movement
            amount_extra = amount % self._max_movement

            # move forward 500 cm at a time
            for _ in range(amount_times):
                logging.debug(f'can only move 500 at a time, moving {self._max_movement}')
                self._fly_xy_direction(direction, self._max_movement)
            
            # move the remaining distance
            self._fly_xy_direction(direction, amount_extra)
        
        # if desired amount <= 500
        else:
            self._fly_xy_direction(direction, amount)
            self._wait(amount)

    def _fly_xy_direction(self, direction: str, amount: int):
        """
        internal method to move drone, handles direction choice
        direction (str):
            forward: +x
            backward: -x 
            right: -y
            left: +y
        amount (int): cm
        """
        match direction:
            case 'forward':
                logging.debug(f'moving forward {amount}')
                self.drone.move_forward(amount)
            case 'backward':
                logging.debug(f'moving back {amount}')
                self.drone.move_back(amount)
            case 'right':
                logging.debug(f'moving right {amount}')
                self.drone.move_right(amount)
            case 'left':
                logging.debug(f'moving left {amount}')
                self.drone.move_left(amount)
        self._wait(amount)
   
    def _calculate_vector_from_magnitude(self, direction: str, magnitude: int) -> list:
        """ given the magnitude, calculate the vector to the new position """
        angle = self.current_heading

        if direction == 'left':
            angle += 90
        elif direction == 'backward':
            angle += 180
        elif direction == 'right':
            angle += 270

        angle = angle % 360

        x_component = int(round(magnitude * math.cos(math.radians(angle)),0))
        y_component = int(round(magnitude * math.sin(math.radians(angle)),0))

        return [x_component, y_component, magnitude]

    def _update_absolute_coordinates(self, new_position_vector: list):
        """ 
        calculate new absolute coordinates from origin after drone flies to new position 
        Parameters:
            new_position_vector (list): [x_component, y_component, magnitude]
        """
        logging.debug(f'drone moving from ({self.x},{self.y}) to ({self.x + new_position_vector[0]},{self.y + new_position_vector[1]})')
        self.x += new_position_vector[0]
        self.y += new_position_vector[1]

    def _update_heading(self, degrees: int):
        """ update current heading """
        degrees = degrees % 360

        # if degrees is negative, convert to positive
        if degrees < 0:
            degrees = 360 - degrees
            
        self.current_heading += degrees
        self.current_heading = self.current_heading % 360
    
    def _check_takeoff_power(self):
        """ check if the drone battery is over the low power takeoff threshold """
        if self.get_battery() < self.min_takeoff_power:
            logging.critical(f'battery is too low to fly: {self.get_battery()}')
            return self.land()
    
    def _check_operating_power(self):
        """ check if the drone battery is over the low power operating threshold"""
        if self.get_battery() < self.min_operating_power:
            logging.critical(f'battery is too low to fly: {self.get_battery()}')
            return self.land()

    def _wait(self, distance: int):
        """ call time.sleep() using logarithmic scale since linear scales too fast """
        try:
            t = int(round(math.log(abs(distance),10),0))
        except:
            t = 1
        finally:
            if t < 1:
                t = 1
            # time.sleep(t)
            # logging.debug(f'sleeping in seconds: {t}')

#------------------------- END OF HeadsUpTello CLASS ---------------------------