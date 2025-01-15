import time
import logging

from djitellopy import Tello
from dragonflight import Dragon


def mission05():
    mytello = Tello()
    drone = Dragon(mytello, {'ceiling':150, 'floor': 50}, logging.WARNING)
    
    drone.takeoff()
    time.sleep(1)

    drone.fly_up(50)
    # drone.fly_forward(520)
    drone.fly_forward(60)
    drone.fly_right(50)
    drone.fly_home(False)
    # drone.fly_backward(520)
    # # drone.fly_left(100)
    # # drone.fly_right(150)
    # # drone.fly_left(50)

    drone.land()

if __name__ == '__main__':
    # try:
    mission05()
    print("Mission 05 completed successfully")
    # except Exception as e:
    #     print(f"Mission 05 failed: {e}")