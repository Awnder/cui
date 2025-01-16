import time
import logging

from djitellopy import Tello
from dragonflight import Dragon


def mission06():
    mytello = Tello()
    drone = Dragon(mytello, {'drone_name':'dragon', 'mission_name':'mission06', 'ceiling':150, 'floor': 50}, logging.WARNING)
    
    # drone.takeoff()

    logging.warning("warning test")
    logging.debug('debug test')
    logging.info('info test')
    logging.error('error test')
    logging.critical('critical test')
    # drone.land()

if __name__ == '__main__':
    # try:
    mission06()
    print("Mission 06 completed successfully")
    # except Exception as e:
    #     print(f"Mission 05 failed: {e}")