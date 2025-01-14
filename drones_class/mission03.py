import time
import logging

from djitellopy import Tello
from dragonflight import Dragon

long = 15
med = 10
short = 5

def mission03():
    mytello = Tello()
    drone = Dragon(mytello, {'ceiling':150, 'floor': 50}, logging.WARNING)
    
    # takeoff sequence
    drone.takeoff()
    print(f'battery: {drone.get_battery()}')
    time.sleep(short)

    drone.fly_to_mission_ceiling()
    drone.fly_to_mission_floor()

    drone.fly_to_mission_ceiling()
    drone.fly_to_mission_floor()

    drone.fly_to_mission_ceiling()
    drone.fly_to_mission_floor()

    drone.land()

if __name__ == '__main__':
    try:
        mission03()
        print("Mission 03 completed successfully")
    except Exception as e:
        print(f"Mission 03 failed: {e}")