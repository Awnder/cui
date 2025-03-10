#!/usr/bin/env python3

# Standard python modules
import time
import logging

# Custom modules for the drones
from djitellopy import Tello
from cui.drones.HelloRoboMaster.dragonflight import HeadsUpTello


#-------------------------------------------------------------------------------
# LED Matrix Display Pictures
#-------------------------------------------------------------------------------

# Two ways of storing the same logo... second one is easier to see, right?
huf_logo1 = "000**000000**0000******00******0000**000000**000000**000000**000"
huf_logo2 = "000**000" +\
            "000**000" +\
            "0******0" +\
            "0******0" +\
            "000**000" +\
            "000**000" +\
            "000**000" +\
            "000**000"


#-------------------------------------------------------------------------------
# Mission Programs
#-------------------------------------------------------------------------------

def mission_01():
    """
    Requirements for Mission 01:
      >> Display team logo for 5 seconds
      >> Print out the battery level
    There are a few extra features I've included for fun.
    """

    # Connect to the DJI RoboMaster drone using a HeadsUpTello object
    # Try passing logging.INFO and see how your output changes
    my_robomaster = Tello()
    drone = HeadsUpTello(my_robomaster, logging.WARNING)

    # Turn the top LED bright green
    r = 0
    g = 200
    b = 50
    drone.top_led_color(r, g, b)

    # Show our logo on the matrix display
    drone.matrix_pattern(huf_logo1, 'b')

    # Slowly dim the top LED without changing the LED matrix
    # The loop runs 10 times with a 0.5 second delay => 5 seconds
    # These colors don't exactly match up to true RGB colors
    for i in range(10): 
        g -= 20
        b -= 5
        drone.top_led_color(r, g, b)
        time.sleep(0.5)

    # Turn off the LED matrix and make the top LED red for two seconds  
    drone.matrix_off()
    drone.top_led_color(200, 10, 10)
    time.sleep(2)
    drone.top_led_off()

    # Finish the mission
    print(f"Battery: {drone.get_battery()}%")
    print(f"Temp °F: {drone.get_temperature()}")

    drone.disconnect()
    return


#-------------------------------------------------------------------------------
# Python Entry Point
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        mission_01()
        print(f"Mission completed")
    except Exception as excp:
        print(excp)
        print(f"Mission aborted")
