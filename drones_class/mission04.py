import time
import logging
from djitellopy import Tello
from dragonflight import Dragon

def mission04():
    mytello = Tello()
    mission_params = {
        'drone_name': 'dragon',
        'mission_name': 'mission06',
        'ceiling': 150,
        'floor': 50,
        'min_takeoff_power': 25,
        'min_operating_power': 10,
    }
    drone = Dragon(mytello, mission_params, logging.WARNING)
    
    drone.takeoff()

    drone.fly_up(80)
    drone.fly_down(40)
    drone.fly_up(40)

    drone.land()

if __name__ == '__main__':
    try:
        mission04()
        print("Mission 04 completed successfully")
    except Exception as e:
        print(f"Mission 04 failed {e}")