import logging
import random
import time


def _approximate(value):
    rand_10pct = value // 10
    return value + random.randint(-rand_10pct, +rand_10pct)


class DroneSim:

    def __init__(self):
        self._height = 0
        self._grounded = True
        self._connected = False
        self._start_time = 0
        self._stop_time = 0
        self._battery_level = 90

        # Set up logger, straight from DJI
        HANDLER = logging.StreamHandler()
        FORMATTER = logging.Formatter('[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
        HANDLER.setFormatter(FORMATTER)

        self.LOGGER = logging.getLogger('djitellopy')
        self.LOGGER.addHandler(HANDLER)
        self.LOGGER.setLevel(logging.INFO)
        

    def connect(self):
        print(">> CONNECTION ESTABLISHED <<")
        self._connected = True


    def end(self):
        print(f">> CONNECTION TERMINATED <<")
        self._connected = False

    def turn_motor_on(self):
        print(f">> MOTORS SPINNING <<")
        return

    def turn_motor_off(self):
        print(f">> MOTORS HAVE STOPPED <<")
        return

    def takeoff(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot takeoff b/c drone is not connected")
        if self._grounded == False:
            raise RuntimeError(f"Cannot takeoff b/c drone is already flying")

        # Start new mission flight time
        self._start_time = int(time.time())
        self._stop_time = self._start_time  # stop_time set by land() function

        # Simulate time delay
        delay = 2 * random.random()
        # time.sleep(delay)

        # Perform requested operation
        self._height = _approximate(60)
        self._grounded = False
        self._battery_level -= 1

        # Log message
        print(f">> DRONE AIRBORN <<")


    def land(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot land b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot land b/c drone is already grounded")

        # Simulate time delay
        delay = 2 * random.random()
        # time.sleep(delay)

        # Perform requested operation
        self._stop_time = int(time.time())
        self._height = 0
        self._grounded = True
        self._battery_level -= 1

        # Log message        
        print(f">> DRONE LANDED <<")

    
    def get_flight_time(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get flight time b/c drone is not connected")
        if self._grounded == True:
            return self._stop_time - self._start_time

        # Perform requested operation
        return int(time.time()) - self._start_time

    def send_rc_control(self, left_right_velocity: int, forward_backward_velocity: int, up_down_velocity: int, yaw_velocity: int):
        print(f"left_right_velocity: {left_right_velocity}, forward_backward_velocity: {forward_backward_velocity}, up_down_velocity: {up_down_velocity}, yaw_velocity: {yaw_velocity}")

    def move_up(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move UP b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move UP b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        # time.sleep(delay)

        # Perform requested operation
        self._height += _approximate(value_cm)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED UP {value_cm}cm <<")
        return self._height


    def move_down(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move DOWN b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move DOWN b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        # time.sleep(delay)

        # Perform requested operation
        self._height -= _approximate(value_cm)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED DOWN {value_cm}cm <<")
        return self._height
    

    def move_forward(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move FWD b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move FWD b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED FORWARD {value_cm}cm <<")
        return


    def move_back(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move BACK b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move BACK b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        # time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED BACK {value_cm}cm <<")
        return


    def move_left(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move LEFT b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move LEFT b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        # time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED LEFT {value_cm}cm <<")
        return


    def move_right(self, value_cm):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot move RIGHT b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot move RIGHT b/c drone is grounded")

        # Simulate time delay
        delay = (value_cm // 100) + 2 * random.random()
        # time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> MOVED RIGHT {value_cm}cm <<")
        return


    def rotate_counter_clockwise(self, degrees):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot ROT CCW b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot ROT CCW b/c drone is grounded")

        # Simulate time delay
        delay = 1.5 * random.random()
        # time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> ROTATED CCW {degrees}° <<")
        return


    def rotate_clockwise(self, degrees):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot ROT CW b/c drone is not connected")
        if self._grounded == True:
            raise RuntimeError(f"Cannot ROT CW b/c drone is grounded")

        # Simulate time delay
        delay = 1.5 + 2 * random.random()
        # time.sleep(delay)
        self._battery_level -= 1

        # Log message
        print(f">> ROTATED CW {degrees}° <<")
        return


    def get_height(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get height b/c drone is not connected")        

        # Perform requested operation
        return self._height


    def get_temperature(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get battery level b/c drone is not connected")
        
        # Perform requested operation
        return 95.5


    def get_battery(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get battery level b/c drone is not connected")
        
        # Perform requested operation
        return self._battery_level


    def get_barometer(self):
        # Verify drone state
        if self._connected == False:
            raise RuntimeError(f"Cannot get battery level b/c drone is not connected")
        
        # Perform requested operation... assumes that ground level is 10 meters
        return self._height + 10000
