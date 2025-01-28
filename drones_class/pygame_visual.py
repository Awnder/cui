# Professor Tallman's Code

import pygame
from djitellopy import Tello
import tello_sim
import dragonflight
import logging
import cv2

### WEBCAM SETUP ###

# print("\nInitializing webcam (this may take a few seconds)")

# webcam = cv2.VideoCapture(0)
# if not webcam.isOpened():
#     print("Error: Could not open webcam.")
#     exit()
# width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
# FPS = int(webcam.get(cv2.CAP_PROP_FPS))
# print(f"Webcam is {width}x{height} at {FPS} FPS")

clock = pygame.time.Clock()


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

# Initialize mouse variables
mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create a surface from an image
logo_surface = pygame.image.load('canva_image.jpg')
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
    'ceiling': 500,
    'floor': 20,
    'min_takeoff_power': 30,
    'min_operating_power': 10,
}
# mytello = tello_sim.DroneSim()
mytello = Tello()
drone = dragonflight.Dragon(mytello, mission_params, logging.WARNING)


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

            if event.key == pygame.K_ESCAPE:
                running = False

        # One of the most common mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                print(f"Left button clicked at {mouse_pos}")
            elif event.button == 3:
                print(f"Right button clicked")

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

    if keys[pygame.K_UP]:
        drone.flip_forward()
    
    if keys[pygame.K_DOWN]:
        drone.flip_backward()

    if keys[pygame.K_LEFT]:
        drone.flip_left()

    if keys[pygame.K_RIGHT]:
        drone.flip_right()

    if keys[pygame.K_c]:
        if show_logo:
            show_logo = not show_logo
            drone.streamon()
        else:
            show_logo = not show_logo
            drone.streamoff()

    # Send command to drone
    drone.send_rc_control(velocity_y, velocity_x, velocity_z, rotation)


    ### GETTING DRONE STATES ###
    battery = drone.get_battery()
    height = drone.get_height()
    barometer = drone.get_barometer()
    temp = drone.get_temperature()
    
    battery_surface = font.render(f"Battery: {battery}", True, COLOR_GREEN, COLOR_GRAY)
    battery_rect = battery_surface.get_rect()
    battery_rect.center = (80, 20)

    height_surface = font.render(f"Height: {height}", True, COLOR_GREEN, COLOR_GRAY)
    height_rect = height_surface.get_rect()
    height_rect.center = (70, 50)

    barometer_surface = font.render(f"Barometer: {barometer}", True, COLOR_GREEN, COLOR_GRAY)
    barometer_rect = barometer_surface.get_rect()
    barometer_rect.center = (120, 80)

    temp_surface = font.render(f"Temperature: {temp}", True, COLOR_GREEN, COLOR_GRAY)
    temp_rect = temp_surface.get_rect()
    temp_rect.center = (120, 110)

    coords_surface = font.render(f"Coordinates: ({drone.x},{drone.y})", True, COLOR_GREEN, COLOR_GRAY)
    coords_rect = coords_surface.get_rect()
    coords_rect.center = (120, 140)

    ### BLIPPING TO SCREEN ###
    # Place surfaces on the screen but don't display them (order matters)
    # Internally this will use depth calculations to create the final image
    screen.blit(background, (0, 0))

    # if show_logo:
    if show_logo:
        screen.blit(logo_surface, logo_rect)
    else:
        # Read a frame from the webcam
        drone.set_video_direction() # forward camera
        tello_frame = drone.get_frame_read()

        if tello_frame is not None:
            cv2_frame = tello_frame.frame

            # Convert the frame from BGR (OpenCV format) to RGB (Pygame format)
            cv2_frame = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)

            # Create a surface from the current picture and rotate it to match display
            webcam_surface = pygame.surfarray.make_surface(cv2_frame)
            webcam_surface = pygame.transform.rotate(webcam_surface, -90)
            webcam_rect = webcam_surface.get_rect()
            webcam_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            screen.blit(webcam_surface, webcam_rect)


    screen.blit(battery_surface, battery_rect)
    screen.blit(height_surface, height_rect)
    screen.blit(barometer_surface, barometer_rect)
    screen.blit(temp_surface, temp_rect)
    screen.blit(coords_surface, coords_rect)

    # Cannot display text directly, must render it to a pygame surface
    if drone._grounded:
        text_message = "Drone is grounded. Takeoff (t) to fly"
    else:
        text_message = f"({velocity_x}, {velocity_y}, {velocity_z}) at {rotation}°"
    text_surface = font.render(text_message, True, COLOR_GREEN, COLOR_GRAY)
    text_rect = text_surface.get_rect()
    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    screen.blit(text_surface, text_rect)

    ### UPDATING SCREEN ###

    # Draw the current frame on the screen
    pygame.display.update()
    
    # ensure refresh speed matches camera
    clock.tick(FPS)


# Close down everything
webcam.release()
#drone.land()
drone.end()
pygame.quit()