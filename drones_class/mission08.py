import time
import logging

from djitellopy import Tello
from dragonflight import Dragon
# import tello_sim

def mission08():
    mission_params = {
        'drone_name': 'dragon',
        'mission_name': 'mission08',
        'ceiling': 150,
        'floor': 50,
        'min_takeoff_power': 30,
        'min_operating_power': 10,
    }
    
    mytello = Tello()
    # mytello = tello_sim.DroneSim()
    drone = Dragon(mytello, mission_params, logging.WARNING)
    
    drone.takeoff()
    drone.rotate_ccw(345)
    # drone.rotate_to_bearing(30 + (180 * 3))
    drone.fly_to_coordinates(313, -157, False)
    # drone.fly_to_coordinates(0, 0, True)
    # drone.fly_home()

    drone.land()

if __name__ == '__main__':
    # try:
    mission08()
    # print("Mission 07 completed successfully")
    # except Exception as e:
    #     print(f"Mission 05 failed: {e}")