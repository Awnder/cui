#!/usr/bin/env python3

import dji_matrix as djim
import logging
import time
import math


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
        self.drone.mission_parameters = mission_parameters
        self.drone.LOGGER.setLevel(debug_level)
        self.x = 0
        self.y = 0
        self._max_movement = 500
        self._min_movement = 20

        try:
            self.drone.connect()
            self.connected = True
        except Exception as excp:
            print(f"ERROR: could not connect to Trello Drone: {excp}")
            print(f" => Did you pass in a valid drone base object?")
            print(f" => Verify that your firewall allows UDP ports 8889 and 8890.")
            print(f"    The Chromebook's firewall reverts to default settings every")
            print(f"    time that you restart the virtual Linux environment.")
            print(f" => You may need to connect to the drone with the Trello App.")
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
        print(f"Drone connection closed gracefully")
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
        print('drone taking off')
        print(f'battery: {self.get_battery()}')
        return self.drone.takeoff()

    def land(self):
        """ Land drone from any height """
        print('drone landing')
        return self.drone.land()
    
    def fly_up(self, up: int):
        ''' 
        fly up to a certain height. 
        if the desired height is above the ceiling, the drone will fly to ceiling 
        if the drone has less than 20 cm to fly, then it will ignore the command
        '''
        ceiling = self.drone.mission_parameters['ceiling']
        desired_height = self.get_height() + up
        print(f'drone is at {self.get_height()}, desired height is at {desired_height}, ceiling is at {ceiling}')
        
        if desired_height > ceiling:
            print('desired height is above ceiling')
            adjusted_height = ceiling - self.get_height()
            print(f'adjusted height is {adjusted_height}')
            if adjusted_height >= 20:
                print(f'drone flying to {self.get_height() + adjusted_height}')
                self.drone.move_up(adjusted_height)
                time.sleep(int(adjusted_height // 10))
            else:
                print(f'adjusted height is less than 20, drone ignoring command')
        else:
            print(f'drone flying to {desired_height}')
            self.drone.move_up(up)
            time.sleep(int(up // 10))

    def fly_down(self, down: int):
        ''' 
        fly down to a certain height. 
        if the desired height is below the floor, the drone will fly to the floor 
        if the drone has less than 20 cm to fly, then it will ignore the command
        '''
        floor = self.drone.mission_parameters['floor']
        desired_height = self.get_height() - down
        print(f'drone is at {self.get_height()}, desired height is at {desired_height}, floor is at {floor}')
        
        if desired_height < floor:
            print('desired height is below floor')
            adjusted_height = self.get_height() - floor
            print(f'adjusted height is {adjusted_height}')
            if adjusted_height >= 20:
                print(f'drone flying to {self.get_height() - adjusted_height}')
                self.drone.move_down(adjusted_height)
                time.sleep(int(adjusted_height // 10))
            else:
                print(f'adjusted height is less than 20, drone ignoring command')
        else:
            print(f'drone flying to {desired_height}')
            self.drone.move_down(down)
            time.sleep(int(down // 10))

    def fly_forward(self, amount):
        """ move drone forward - considered +x direction """
        # drone can't move below 20 cm, chose 480 b/c next number divisible by 20 from 500
        print(f'drone moving from {self.x} to {self.x+amount}')
        self._fly_xy('forward', amount)
    
    def fly_backward(self, amount):
        """ move drone backward - considered -x direction """
        print(f'drone moving from {self.x} to {self.x-amount}')
        self._fly_xy('backward', amount)

    def fly_right(self, amount):
        """ move drone right - considered -y direction """
        print(f'drone moving from {self.y} to {self.y-amount}')
        self._fly_xy('right', amount)

    def fly_left(self, amount):
        """ move drone left - considered +y direction """
        print(f'drone moving from {self.y} to {self.y-amount}')
        self._fly_xy('left', amount)

    def fly_home(self, prioritize_x: bool = True):
        """
        move drone home from any coordinates in two lines instead of diagonal
        prioritize_x (bool): if True, drone will move in x direction first, else y direction
        """
        print(f'drone moving from {self.x}/{self.y} to 0/0')
        print(f'prioritizing x: {prioritize_x}')

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
        internal method to move drone 
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
                match direction:
                    case 'forward':
                        self.drone.move_forward(_max_movement_adjusted)
                        self._update_x(_max_movement_adjusted)
                    case 'backward':
                        self.drone.move_back(_max_movement_adjusted)
                        self._update_x(-_max_movement_adjusted)
                    case 'right':
                        self.drone.move_right(_max_movement_adjusted)
                        self._update_y(-_max_movement_adjusted)
                    case 'left':
                        self.drone.move_left(_max_movement_adjusted)
                        self._update_y(+_max_movement_adjusted)
                self._wait(_max_movement_adjusted)

            # move the remaining distance
            match direction:
                case 'forward':
                    self.drone.move_forward(amount_extra)
                    self._update_x(amount_extra)
                case 'backward':
                    self.drone.move_back(amount_extra)
                    self._update_x(-amount_extra)
                case 'right':
                    self.drone.move_right(amount_extra)
                    self._update_y(-amount_extra)
                case 'left':
                    self.drone.move_left(amount_extra)
                    self._update_y(+amount_extra)
            self._wait(amount_extra)
            
        # if the desired amount is >= 520
        elif amount >= self._max_movement + 20:
            amount_times = amount // self._max_movement
            amount_extra = amount % self._max_movement

            # move forward 500 cm at a time
            for _ in range(amount_times):
                print(f'can only move 500 at a time, moving {self._max_movement}')
                match direction:
                    case 'forward':
                        self.drone.move_forward(self._max_movement)
                        self._update_x(self._max_movement)
                    case 'backward':
                        self.drone.move_back(self._max_movement)
                        self._update_x(-self._max_movement)
                    case 'right':
                        self.drone.move_right(self._max_movement)
                        self._update_y(-self._max_movement)
                    case 'left':
                        self.drone.move_left(self._max_movement)
                        self._update_y(+self._max_movement)
                self._wait(self._max_movement)

            # move the remaining distance
            print(f'moving remaining distance: {amount_extra}')
            match direction:
                case 'forward':
                    self.drone.move_forward(amount_extra)
                    self._update_x(amount_extra)
                case 'backward':
                    self.drone.move_back(amount_extra)
                    self._update_x(-amount_extra)
                case 'right':
                    self.drone.move_right(amount_extra)
                    self._update_y(-amount_extra)
                case 'left':
                    self.drone.move_left(amount_extra)
                    self._update_y(+amount_extra)
            self._wait(amount_extra)
        
        # if desired amount <= 500
        else:
            print(f'moving {amount}')
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
        floor = self.drone.mission_parameters['floor']
        distance = self.get_height() - floor

        print(f'drone is at {self.get_height()} and floor is at {floor}')
        print(f'drone is {distance} away from floor')

        # can only move at distances of 20cm, so need to correct if necessary
        if abs(distance) < 20:
            # drone is above mission floor
            if distance > 0:
                print(f'drone overcorrecting and flying to {self.get_height() + 30}')
                self.drone.move_up(30) # move up to overcorrect with some room for error
                time.sleep(3)
                print(f'drone flying to {floor}')
                self.drone.move_down(self.get_height() - floor) # move back down to mission floor
                time.sleep(int(distance // 10))
            else:
            # drone is below mission floor
                print(f'drone overcorrecting and flying to {abs(distance) + 30}')
                self.drone.move_up(abs(distance) + 30) # move up to overcorrect
                time.sleep(int(abs(distance) // 10))
                print(f'drone flying to {floor}')
                self.drone.move_down(abs(self.get_height() - floor))
                time.sleep(int(self.get_height() // 10))
        else:
            if distance > 0:
                print(f'drone flying to {floor}')
                self.drone.move_down(distance)
                time.sleep(int(distance // 10))
            else:
                print(f'drone flying to {floor}')
                self.drone.move_up(abs(distance))
                time.sleep(int(abs(distance) // 10))

        print(f"drone is at floor: {floor} with actual height at {self.get_height()}")
    
    def fly_to_mission_ceiling(self):
        """ 
        move drone to mission ceiling 
        if drone is < 20cm from ceiling, will overcorrect by 30cm and fly back
        """
        ceiling = self.drone.mission_parameters['ceiling']
        distance = ceiling - self.get_height()

        print(f'drone is at {self.get_height()} and ceiling is at {ceiling}')
        print(f'drone is {distance} away from ceiling')

        # can only move at distances of 20cm, so need to correct if necessary
        if abs(distance) < 20:
            print(f'drone overcorrecting and flying to {self.get_height() - 30}')
            self.drone.move_down(30) # move down to overcorrect with some room for error
            time.sleep(3)
            print(f'drone flying to {ceiling - self.get_height()}')
            self.drone.move_up(ceiling - self.get_height()) # move back up to ceiling
            time.sleep(int(distance // 10))
        else:
            print(f'drone flying to {ceiling}')
            self.drone.move_up(distance)
            time.sleep(int(distance // 10))

        print(f"drone is at ceiling: {ceiling} with actual height at {self.get_height()}")
    
    def _update_x(self, distance: int):
        self.x = self.x + distance
    
    def _update_y(self, distance: int):
        self.y = self.y + distance
    
    def _wait(self, distance: int):
        t = int(math.log(abs(distance), 10))
        print(f'sleeping:{t}')
        if t < 1:
            t = 1
        time.sleep(t)

#------------------------- END OF HeadsUpTello CLASS ---------------------------