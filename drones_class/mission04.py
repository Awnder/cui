import time
import logging

from djitellopy import Tello
from dragonflight import Dragon


def mission04():
    mytello = Tello()
    drone = Dragon(mytello, {'ceiling':150, 'floor': 50}, logging.WARNING)
    
    drone.takeoff()
    time.sleep(4)

    drone.fly_up(60)
    time.sleep(2)
    drone.fly_down(20)

    time.sleep(2)
    drone.land()

if __name__ == '__main__':
    try:
        mission04()
        print("Mission 04 completed successfully")
    except Exception as e:
        print(f"Mission 04 failed: {e}")