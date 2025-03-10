import pygame
from djitellopy import Tello
import tello_sim
import dragonflight
import logging
import cv2
import time
import threading

### GLOBAL VARIABLES FOR VIDEO FEED THREADING ###
current_frame = None
capture_event = threading.Event()
frame_lock = threading.Lock()

def capture_frames(drone):
    """ threading function to capture frames from the drone """
    global current_frame
    global capture_event
    while True:
        if capture_event.is_set():
            frame = drone.get_frame_read().frame
            with frame_lock:
                current_frame = frame
        time.sleep(0.03) # capture every 30ms or about 33fps

def main():
    ### PYGAME SETUP ###
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 720
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Initialize common colors
    COLOR_BLACK = (0, 0, 0) 
    COLOR_WHITE = (255, 255, 255)
    COLOR_GREEN = (64, 255, 64)
    COLOR_GRAY = (64, 64, 64)

    # Initialize font for placing text on the screen
    font = pygame.font.Font('freesansbold.ttf', 24)

    # Make an all black surface (black is default color: 0,0,0)
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create a surface from an image
    logo_surface = pygame.image.load('dragon_drone_logo2.jpg')
    logo_rect = logo_surface.get_rect()
    logo_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


    ### DRONE SETUP ###
    velocity_x = 0
    velocity_y = 0
    velocity_z = 0
    rotation = 0

    mission_params = {
        'drone_name': 'dragon',
        'mission_name': 'mission: pygame',
        'ceiling': 10000,
        'floor': -10000,
        'min_takeoff_power': 0,
        'min_operating_power': 0,
    }
    # mytello = tello_sim.DroneSim()
    mytello = Tello()
    drone = dragonflight.Dragon(mytello, mission_params, logging.WARNING)

    ### THREADING VIDEO SETUP ###
    clock = pygame.time.Clock()
    display_logo = True
    FPS = '30' # set drone camera fps - 5, 15, or 30
    video_thread = threading.Thread(target=capture_frames, args=(drone,), daemon=True)
    video_thread.start()

    ### GAME LOOP ###
    running = True
    while running:

        ### CURRENT EVENTS ###
        for event in pygame.event.get():

            # User clicked the X to close program
            if event.type == pygame.QUIT:
                running = False

            # Special one-time keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t and drone._grounded:
                    drone.takeoff()

                if event.key == pygame.K_l and not drone._grounded:
                    drone.land()

                if event.key == pygame.K_UP:
                    drone.flip_forward()
                
                if event.key == pygame.K_DOWN:
                    drone.flip_backward()
                    
                if event.key == pygame.K_LEFT:
                    drone.flip_left()

                if event.key == pygame.K_RIGHT:
                    drone.flip_right()

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_c:
                    global capture_event
                    if display_logo:
                        drone.streamon()
                        capture_event.set()
                        print(capture_event.is_set())
                        display_logo = not display_logo
                    else:
                        drone.streamoff()
                        capture_event.clear()
                        print(capture_event.is_set())
                        display_logo = not display_logo

        ### SIMULTANEOUSLY PRESSED KEYS ###
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and keys[pygame.K_s]:
            velocity_x = 0
        elif keys[pygame.K_w]:
            velocity_x = 100
        elif keys[pygame.K_s]:
            velocity_x = -100
        else:
            velocity_x = 0

        if keys[pygame.K_a] and keys[pygame.K_d]:
            velocity_y = 0
        elif keys[pygame.K_a]:
            velocity_y = -100
        elif keys[pygame.K_d]:
            velocity_y = 100
        else:
            velocity_y = 0

        if keys[pygame.K_SPACE] and keys[pygame.K_LSHIFT]:
            velocity_z = 0
        elif keys[pygame.K_SPACE]:
            velocity_z = 100
        elif keys[pygame.K_LSHIFT]:
            velocity_z = -100
        else:
            velocity_z = 0

        if keys[pygame.K_q] and keys[pygame.K_e]:
            rotation = 0
        elif keys[pygame.K_q]:
            rotation = -100
        elif keys[pygame.K_e]:
            rotation = 100
        else:
            rotation = 0

        # Send command to drone
        try:
            drone.send_rc_control(velocity_y, velocity_x, velocity_z, rotation)
        except Exception as e:
            print(f"Error on rc control: {e}")

        ### GETTING DRONE STATES ###
        battery = drone.get_battery()
        height = drone.get_height()
        barometer = round(drone.get_barometer(),2)
        temp = drone.get_temperature()
        
        # TOP LEFT OF SCREEN
        battery_surface = font.render(f"Battery: {battery}", True, COLOR_WHITE)
        battery_rect = battery_surface.get_rect()
        battery_rect.center = (80, 20)

        height_surface = font.render(f"Height: {height}", True, COLOR_WHITE)
        height_rect = height_surface.get_rect()
        height_rect.center = (70, 50)

        barometer_surface = font.render(f"Barometer: {barometer}", True, COLOR_WHITE)
        barometer_rect = barometer_surface.get_rect()
        barometer_rect.center = (120, 80)

        temp_surface = font.render(f"Temperature: {temp}", True, COLOR_WHITE)
        temp_rect = temp_surface.get_rect()
        temp_rect.center = (120, 110)

        # BOTTOM MIDDLE OF SCREEN
        controls_surface = font.render(f"WASD: move, QE: rotate, T/L: takeoff/land, C: camera, Arrows: flips", True, COLOR_WHITE)
        controls_rect = controls_surface.get_rect()
        controls_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)

        # TOP RIGHT OF SCREEN
        mparams_ceiling_surface = font.render(f"Mission Ceiling: {mission_params['ceiling']}", True, COLOR_WHITE)
        mparams_ceiling_rect = mparams_ceiling_surface.get_rect()
        mparams_ceiling_rect.center = (SCREEN_WIDTH - 120, 20)

        mparams_floor_surface = font.render(f"Mission Floor: {mission_params['floor']}", True, COLOR_WHITE)
        mparams_floor_rect = mparams_floor_surface.get_rect()
        mparams_floor_rect.center = (SCREEN_WIDTH - 120, 40)

        ### BLIPPING TO SCREEN ###
        screen.blit(background, (0, 0))

        if display_logo:
            screen.blit(logo_surface, logo_rect)
        else:
            with frame_lock:
                if current_frame is not None:
                    cv2_frame = cv2.flip(current_frame, 1)
                    webcam_surface = pygame.surfarray.make_surface(cv2_frame)
                    webcam_surface = pygame.transform.rotate(webcam_surface, -90)
                    webcam_rect = webcam_surface.get_rect()
                    webcam_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    screen.blit(webcam_surface, webcam_rect)
                else:
                    screen.blit(logo_surface, logo_rect)

        # if display_logo:
        #     screen.blit(logo_surface, logo_rect)
        # else:
        #     cv2_frame = drone.get_frame_read().frame

        #     if cv2_frame is not None:
        #         cv2_frame = cv2.flip(cv2_frame, 1)
        #         webcam_surface = pygame.surfarray.make_surface(cv2_frame)
        #         webcam_surface = pygame.transform.rotate(webcam_surface, -90)
        #         webcam_rect = webcam_surface.get_rect()
        #         webcam_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        #         screen.blit(webcam_surface, webcam_rect)

        screen.blit(battery_surface, battery_rect)
        screen.blit(height_surface, height_rect)
        screen.blit(barometer_surface, barometer_rect)
        screen.blit(temp_surface, temp_rect)
        screen.blit(controls_surface, controls_rect)
        screen.blit(mparams_ceiling_surface, mparams_ceiling_rect)
        screen.blit(mparams_floor_surface, mparams_floor_rect)

        if drone._grounded:
            text_message = "Drone is grounded. Takeoff (t) to fly"
        else:
            text_message = f"({velocity_x}, {velocity_y}, {velocity_z}) at {rotation}°"
        text_surface = font.render(text_message, True, COLOR_GREEN)
        text_rect = text_surface.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        screen.blit(text_surface, text_rect)

        ### UPDATING SCREEN ###
        pygame.display.update()
        clock.tick(int(FPS))

    # Close down everything
    drone.streamoff()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == '__main__':
    main()