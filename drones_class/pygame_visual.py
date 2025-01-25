# Professor Tallman's Code

import pygame
# from djitellopy import Tello

# You must do this initialization before most pygame things will work
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

################################################################################

# Initialize common colors
COLOR_BLACK = (0, 0, 0) 
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (64, 255, 64)
COLOR_GRAY = (64, 64, 64)

# Initialize font for placing text on the screen
font = pygame.font.Font('freesansbold.ttf', 24)

################################################################################

# Make an all black surface (black is default color: 0,0,0)
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize mouse variables
mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create a surface from an image
logo_surface = pygame.image.load('canva_image.jpg')
logo_rect = logo_surface.get_rect()
logo_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Initialize drone
velocity_x = 0
velocity_y = 0
velocity_z = 0
rotation = 0
#drone = Tello()
#drone.connect()
#drone.takeoff()

# Run the game loop
running = True
while running:

    # Cycle through all of the current events
    for event in pygame.event.get():

        # User clicked the X to close program
        if event.type == pygame.QUIT:
            running = False

        # Special one-time keys: SPACE -> 'boom' and ESC -> Quit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("boom")
            if event.key == pygame.K_ESCAPE:
                running = False            

        # One of the most common mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                print(f"Left button clicked at {mouse_pos}")
            elif event.button == 3:
                print(f"Right button clicked")

    # Capture all of the simultaneously pressed keys
    # Notice that we are no longer in pygame.event.get() loop!
    keys = pygame.key.get_pressed()

    # Full throttle all the time!
    if keys[pygame.K_UP] and keys[pygame.K_DOWN]:
        velocity_x = 0
    elif keys[pygame.K_UP]:
        velocity_x = 100
    elif keys[pygame.K_DOWN]:
        velocity_x = -100
    else:
        velocity_x = 0

    # Send command to drone
    # drone.send_rc_control(velocity_x, velocity_y, velocity_z, rotation)

    # Place surfaces on the screen but don't display them (order matters)
    # Internally this will use depth calculations to create the final image
    screen.blit(background, (0, 0))
    screen.blit(logo_surface, logo_rect)

################################################################################

    # Cannot display text directly, must render it to a pygame surface
    text_message = f"({velocity_x}, {velocity_y}, {velocity_z}) at {rotation}°"
    text_surface = font.render(text_message, True, COLOR_GREEN, COLOR_GRAY)
    text_rect = text_surface.get_rect()
    text_rect.center = mouse_pos
    screen.blit(text_surface, text_rect)

################################################################################

    # Draw the current frame on the screen
    pygame.display.update()

# Close down everything
#drone.land()
#drone.end()
pygame.quit()