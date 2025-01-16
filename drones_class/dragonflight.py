#!/usr/bin/env python3

import dji_matrix as djim
import logging, logging.config
from datetime import datetime
import time
import math

# LOGGING CONFIGURATION
# from Professor Tallman
# Create one log file for each hour of the day to balances the number of files
#   with the size of each file. If we run the drone multiple times within the
#   same hour, each run will be logged in the same file.
logfile = f"dragon.{datetime.now().strftime("%Y%m%d.%H")}.log"

logging.basicConfig(filename=logfile, level=logging.DEBUG, format="%(asctime)s %(message)s")

#------------------------- BEGIN HeadsUpTello CLASS ----------------------------

class Dragon():
    """
    An interface from Team "Heads-Up Flight" to control a DJI Tello RoboMaster 
    Drone. Uses djitellopy.Tello class as the base object.
    """

    def __init__(self, drone_object: object, mission_parameters: dict, debug_level=logging.INFO):
        """
        Constructor that establishes a connection with the drone. Pass in a
        djitellopy Tello object to give your HeadsUpTello object its wings.

        Arguments
            drone_object: A new djitellopy.Tello() object
            mission_parameters: dictionary of mission parameters, includes floor and ceiling in cm
                mission_parameters = {
                    'ceiling': 200,
                    'floor': 0,
                }
            debug_level:  Set the desired logging level.
                          logging.INFO shows every command and response 
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
        self.drone.LOGGER.setLevel(debug_level)
        self.x = 0
        self.y = 0
        self._max_movement = 500
        self._min_movement = 20

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
        """
        Returns the drone's current barometer reading in cm from the  ground.
        The accuracy of this reading fluctates with the weather. 
        """
        return self.drone.get_barometer()
    
    def get_height(self):
        return self.drone.get_height()
    
    def get_temperature(self):
        """ Returns the drone's internal temperature in °F. """
        return self.drone.get_temperature()
    
    def takeoff(self):
        """ Takeoff the drone to around 70 cm """
        logging.info('drone taking off')
        logging.info(f'battery: {self.get_battery()}')
        return self.drone.takeoff()

    def land(self):
        """ Land drone from any height """
        logging.info('drone landing')
        return self.drone.land()
    
    def fly_up(self, up: int):
        ''' 
        fly up to a certain height. 
        if the desired height is above the ceiling, the drone will fly to ceiling 
        if the drone has less than 20 cm to fly, then it will ignore the command
        '''
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
        ''' 
        fly down to a certain height. 
        if the desired height is below the floor, the drone will fly to the floor 
        if the drone has less than 20 cm to fly, then it will ignore the command
        '''
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
        logging.debug(f'drone moving from {self.x} to {self.x+amount}')
        self._fly_xy('forward', amount)
    
    def fly_backward(self, amount):
        """ move drone backward - considered -x direction """
        logging.debug(f'drone moving from {self.x} to {self.x-amount}')
        self._fly_xy('backward', amount)

    def fly_right(self, amount):
        """ move drone right - considered -y direction """
        logging.debug(f'drone moving from {self.y} to {self.y-amount}')
        self._fly_xy('right', amount)

    def fly_left(self, amount):
        """ move drone left - considered +y direction """
        logging.debug(f'drone moving from {self.y} to {self.y-amount}')
        self._fly_xy('left', amount)

    def fly_home(self, prioritize_x: bool = True):
        """
        move drone home from any coordinates in two lines instead of diagonal
        prioritize_x (bool): if True, drone will move in x direction first, else y direction
        """
        logging.debug(f'drone moving from {self.x}/{self.y} to 0/0')
        logging.debug(f'prioritizing x: {prioritize_x}')

        absolute_x = abs(self.x)
        absolute_y = abs(self.y)

        if prioritize_x:
            if self.x > 0:
                self.fly_backward(absolute_x)
            else:
                self.fly_forward(absolute_x)
            if self.y > 0:
                self.fly_right(absolute_y)
            else:
                self.fly_left(absolute_y)
        else:
            if self.y > 0:
                self.fly_right(absolute_y)
            else:
                self.fly_left(absolute_y)
            if self.x > 0:
                self.fly_backward(absolute_x)
            else:
                self.fly_forward(absolute_x)

    def _fly_xy(self, direction: str, amount: int):
        ''' 
        internal method to move drone, handles amount
        direction (str):
            forward: +x
            backward: -x 
            right: -y
            left: +y
        amount (int): cm
        '''
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
            logging.debug(f'moving remaining distance: {amount_extra}')
            self._fly_xy_direction(direction, amount_extra)
        
        # if desired amount <= 500
        else:
            logging.debug(f'moving {amount}')
            self._fly_xy_direction(direction, amount)
            self._wait(amount)

    def _fly_xy_direction(self, direction: str, amount: int):
        ''' 
        internal method to move drone, handles direction choice
        direction (str):
            forward: +x
            backward: -x 
            right: -y
            left: +y
        amount (int): cm
        '''
        match direction:
            case 'forward':
                self.drone.move_forward(amount)
                self._update_x(amount)
            case 'backward':
                self.drone.move_back(amount)
                self._update_x(-amount)
            case 'right':
                self.drone.move_right(amount)
                self._update_y(-amount)
            case 'left':
                self.drone.move_left(amount)
                self._update_y(+amount)
        self._wait(amount)

    def fly_to_mission_floor(self):
        """ move drone to mission floor """
        distance = self.get_height() - self.floor
        magnitude = abs(distance)

        logging.debug(f'drone is at {self.get_height()} and floor is at {self.floor}')
        logging.debug(f'drone is {distance} away from floor')

        # can only move at distances of 20cm, so need to correct if necessary
        if magnitude < 20:
            # drone is above mission floor
            if distance > 0:
                logging.debug(f'drone overcorrecting and flying to {self.get_height() + 30}')
                self.drone.move_up(30) # move up to overcorrect with some room for error
                self._wait(30)
                logging.debug(f'drone flying to {self.floor}')
                self.drone.move_down(self.get_height() - self.floor) # move back down to mission floor
                self._wait(self.get_height()-self.floor)
            else:
            # drone is below mission floor
                logging.debug(f'drone overcorrecting and flying to {magnitude + 30}')
                self.drone.move_up(magnitude + 30) # move up to overcorrect
                self._wait(magnitude + 30)
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
        if drone is < 20cm from ceiling, will overcorrect by 30cm and fly back
        """
        distance = self.ceiling - self.get_height()
        magnitude = abs(distance)

        logging.debug(f'drone is at {self.get_height()} and ceiling is at {self.ceiling}')
        logging.debug(f'drone is {distance} away from ceiling')

        # can only move at distances of 20cm, so need to correct if necessary
        if magnitude < 20:
            logging.debug(f'drone overcorrecting and flying to {self.get_height() - 30}')
            self.drone.move_down(30) # move down to overcorrect with some room for error
            self._wait(30)
            logging.debug(f'drone flying to {self.ceiling - self.get_height()}')
            self.drone.move_up(self.ceiling - self.get_height()) # move back up to self.ceiling
            self._wait(self.ceiling - self.get_height())
        else:
            logging.debug(f'drone flying to {self.ceiling}')
            self.drone.move_up(distance)
            self._wait(distance)

        logging.debug(f"drone is at ceiling: {self.ceiling} with actual height at {self.get_height()}")
    
    def _update_x(self, distance: int):
        self.x = self.x + distance
    
    def _update_y(self, distance: int):
        self.y = self.y + distance
    
    def _wait(self, distance: int):
        t = int(math.log(abs(distance), 10))
        logging.debug(f'sleeping in seconds: {t}')
        if t < 1:
            t = 1
        time.sleep(t)

#------------------------- END OF HeadsUpTello CLASS ---------------------------