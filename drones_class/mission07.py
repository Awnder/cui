import time
import logging

from djitellopy import Tello
from dragonflight import Dragon


def mission07():
    mission_params = {
        'drone_name': 'dragon',
        'mission_name': 'mission07',
        'ceiling': 150,
        'floor': 50,
        'min_takeoff_power': 30,
        'min_operating_power': 10,
    }
    
    mytello = Tello()
    drone = Dragon(mytello, mission_params, logging.WARNING)
    
    drone.takeoff()
    drone.fly_forward(100)
    drone.fly_right(70)
    drone.rotate_cw(70)
    drone.fly_home()

    drone.land()

if __name__ == '__main__':
    # try:
    mission07()
    # print("Mission 07 completed successfully")
    # except Exception as e:
    #     print(f"Mission 05 failed: {e}")