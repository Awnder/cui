import pygame
from djitellopy import Tello
import tello_sim
import dragonflight
import logging
import cv2
import numpy as np
import threading

# https://pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
# https://www.reddit.com/r/computervision/comments/g9ikr6/help_with_latency_in_video/?rdt=52617


### GLOBAL VARIABLES FOR VIDEO FEED ###
webcam_surface = None
webcam_rect = None

# def video_feed(drone, stop_thread_event, display_video_live=False, SCREEN_WIDTH=960, SCREEN_HEIGHT=720):
#     drone.streamon()

#     while not stop_thread_event.isSet():
#         frame = drone.get_frame_read().frame
#         if display_video_live and frame is not None:
#             cv2_frame = cv2.flip(frame, 1)
#             webcam_surface = pygame.surfarray.make_surface(cv2_frame)
#             webcam_surface = pygame.transform.rotate(webcam_surface, -90)
#             webcam_rect = webcam_surface.get_rect()
#             webcam_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

### YOLO DEEP NEURAL NETWORK SETUP ###
def _load_yolo_deep_neural_network():
    """
    Professor Tallman
    Loads the YOLOv3 object detection algorithm that has been trained with the
    Microsoft Common Objects in Context Dataset (COCO) to identify 80 objects.
    The three YOLOv3-COCO data files must be located in the same directory as
    this python script. See https://arxiv.org/abs/1405.0312.

    Returns a tuple containing 3 objects:
      0. Fully trained YOLO Deep Neurel Network Object classifier
      1. List of the DNN classifier's output layers by name
      2. List of the classification labels for the 80 known COCO objects
    """

    # Download weights: wget https://pjreddie.com/media/files/yolov3.weights
    # Download coco.names: wget https://raw.githubusercontent.com/pjreddie/darknet/refs/heads/master/data/coco.names
    # Download yolov3.cfg: wget https://raw.githubusercontent.com/pjreddie/darknet/refs/heads/master/cfg/yolov3.cfg
    labels_path = f'coco.names'
    config_path = f'yolov3.cfg'
    weights_path = f'yolov3.weights'

    with open(labels_path, 'r') as f:
        dnn_labels = [line.strip('\n') for line in f]

    dnn_object = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    dnn_layers = dnn_object.getUnconnectedOutLayersNames()

    return (dnn_object, dnn_layers, dnn_labels)

def _detect_persons(img, dnn_object, obj_confidence, nms_threshold):
    """
    Professor Tallman
    Detects COCO objects in an image with an OpenCV Deep Neural Network using
    Non-Maxima Supression to reduce the number of duplicate objects.

    Returns a list of detected objects, each defined as a tuple:
      0. COCO label, as an index number
      1. DNN confidence score
      2. Bounding box for the object
    """

    # Process raw image through the neural network to obtain potential objects
    #  => 1/255 is the scaling factor --> RGB value to a percentage
    #  => (224, 224) is the size of the output blob with smaller sizees being
    #     faster but potentially less accurate. The number came from this
    #     article by Adrian Rosebrock on PyImageSearch and produced fairly
    #     accurate results during some limited testing.

    blob = cv2.dnn.blobFromImage(img, 1/255.0, (224, 224), swapRB=True, crop=False)
    
    # Run the DNN object detection algorithm

    dnn_classifier, dnn_outputlayers = dnn_object
    dnn_classifier.setInput(blob)
    outputs = dnn_classifier.forward(dnn_outputlayers)
    flattened_outputs = [result for layer in outputs for result in layer]

    # We will identify objects by their location (the bounding box), the
    #   confidence score, and then the COCO label assigned by the DNN.
    # We need the image width x height to create the bounding boxes

    boxes = []
    scores = []
    labels = []
    img_h, img_w = img.shape[:2]

    # Each result is a nested list of all the detected objects. At the top
    #   level, we have a list of objects. Within each object, we are given a
    #   list containing the 4 coordinates of a bounding box followed by 80
    #   classification scores. There are 80 scores because our DNN was trained
    #   with 80 objects from the COCO dataset. We need to extract the bounding
    #   box and then identify the highest scoring object.
    # DNN bounding boxes identified by center, width, and height. We'll convert
    #   these to the upper-left coordinates of the box and the width & height.
    # Filter down to only the highest scoring people objects (label #0)

    for result in flattened_outputs:
        bbox = result[:4]
        all_scores = result[5:]
        best_label = np.argmax(all_scores)
        best_score = all_scores[best_label]
        
        if best_score > obj_confidence and best_label == 0:
            cx, cy, w, h = bbox * np.array([img_w, img_h, img_w, img_h])
            x = cx - w / 2
            y = cy - h / 2
            labels.append(best_label)
            scores.append(float(best_score))
            boxes.append([int(x), int(y), int(w), int(h)])

    # The DNN is likely to have identfied the same object multiple times, with
    #   each repeat found in a slightly different, overlapped, region of the
    #   image. We use the Non-Maxima Supression algorithm to detect redundant
    #   objects and return the best fitting bounding box from amongst all of
    #   the candidates.  

    best_idx = cv2.dnn.NMSBoxes(boxes, scores, obj_confidence, nms_threshold)
    if len(best_idx) > 0:
        objects = [(labels[i], scores[i], boxes[i]) for i in best_idx.flatten()]
    else:
        objects = []
    
    return objects

def _process_image(img, SCREEN_WIDTH, SCREEN_HEIGHT, dnn_object, confidence: float=0.90, threshold: float=0.3):
    """
    Professor Tallman
    Detect persons in an image file using Deep Neural Network object detection
    algorithm. The image file will be downsized to fit within 640x480 before
    it is run through the DNN.

    Returns a new version of the image that has been overlayed with recangular
    bounding boxes and also a list of tuples identifying each object. The tuple
    contains the following three fields:
      0. COCO label, as an index number
      1. DNN confidence score
      2. Bounding box for the object 
    """

    # Resize the image to fit within 640x480 for easier viewing
    height, width = img.shape[:2]
    if width > SCREEN_WIDTH or height > SCREEN_HEIGHT:
        largest_dimension = max(height, width)
        scale_factor = 1 + largest_dimension // SCREEN_WIDTH
        dimensions = (width // scale_factor, height // scale_factor)
        img = cv2.resize(img, dimensions, interpolation = cv2.INTER_AREA)
        height, width = img.shape[:2]

    # Detect all of the objects in this image
    objects = _detect_persons(img, dnn_object, confidence, threshold)

    # Place a visual bounding box around each object detected in the image
    bgr_red = (0, 0, 255)
    for label, score, (x, y, w, h) in objects:
        cv2.rectangle(img, (x, y), (x+w, y+h), bgr_red, 2)
        #text = f"{label_names[label]}: {100*score:.1f}%"
        #cv2.putText(image, text, (x, y-5), cv2.FONT_HERSHEY_PLAIN, 1, bgr_red, 2)

    return img, objects

def yolo(frame, dnn_object, confidence: float=0.90, threshold: float=0.3):
    if frame is None or not isinstance(frame, np.ndarray):
        return None
    img, objs = _process_image(img, dnn_object, confidence, threshold)        
    
    return img


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

    # Initialize mouse variables
    mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Create a surface from an image
    logo_surface = pygame.image.load('dragon_drone_logo2.jpg')
    logo_rect = logo_surface.get_rect()
    logo_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


    ### DRONE SETUP ###
    velocity_x = 0
    velocity_y = 0
    velocity_z = 0
    rotation = 0

    absolute_x = 0
    absolute_y = 0
    absolute_z = 0
    absolute_rotation = 0

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

    ### THREADING VIDEO SETUP ###
    clock = pygame.time.Clock()
    display_logo = True
    FPS = '30' # set drone camera fps - 5, 15, or 30
    # stop_thread_event = threading.Event()
    # video_thread = threading.Thread(target=video_feed, args=(drone, stop_thread_event, False, SCREEN_WIDTH, SCREEN_HEIGHT), daemon=True)
    # video_thread.start()

    ### YOLO SETUP ###
    dnn_classifier, dnn_layers, label_names = _load_yolo_deep_neural_network()
    dnn_object = (dnn_classifier, dnn_layers)

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

        ### SIMULTANEOUSLY PRESSED KEYS ###
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and keys[pygame.K_s]:
            velocity_x = 0
        elif keys[pygame.K_w]:
            velocity_x = 100
            absolute_x += 100
        elif keys[pygame.K_s]:
            velocity_x = -100
            absolute_x -= 100
        else:
            velocity_x = 0

        if keys[pygame.K_a] and keys[pygame.K_d]:
            velocity_y = 0
        elif keys[pygame.K_a]:
            velocity_y = -100
            absolute_y -= 100
        elif keys[pygame.K_d]:
            velocity_y = 100
            absolute_y += 100
        else:
            velocity_y = 0

        if keys[pygame.K_SPACE] and keys[pygame.K_LSHIFT]:
            velocity_z = 0
        elif keys[pygame.K_SPACE]:
            velocity_z = 100
            absolute_z += 100
        elif keys[pygame.K_LSHIFT]:
            velocity_z = -100
            absolute_z -= 100
        else:
            velocity_z = 0

        if keys[pygame.K_q] and keys[pygame.K_e]:
            rotation = 0
        elif keys[pygame.K_q]:
            rotation = -100
            absolute_rotation -= 100
        elif keys[pygame.K_e]:
            rotation = 100
            absolute_rotation += 100
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
            if display_logo:
                drone.streamon()
                display_logo = not display_logo
            else:
                drone.streamoff()
                display_logo = not display_logo

        # Send command to drone
        drone.send_rc_control(velocity_y, velocity_x, velocity_z, rotation)


        ### GETTING DRONE STATES ###
        battery = drone.get_battery()
        height = drone.get_height()
        barometer = drone.get_barometer()
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

        absolute_coord_surface = font.render(f"Absolute Position: ({absolute_x // 10}, {absolute_y // 10}, {absolute_z // 10}) at {(absolute_rotation // 10) % 360}°", True, COLOR_WHITE)
        absolute_coord_rect = absolute_coord_surface.get_rect()
        absolute_coord_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40) 

        # TOP RIGHT OF SCREEN
        mparams_ceiling_surface = font.render(f"Mission Ceiling: {mission_params['ceiling']}", True, COLOR_WHITE)
        mparams_ceiling_rect = mparams_ceiling_surface.get_rect()
        mparams_ceiling_rect.center = (SCREEN_WIDTH - 120, 20)

        mparams_floor_surface = font.render(f"Mission Floor: {mission_params['floor']}", True, COLOR_WHITE)
        mparams_floor_rect = mparams_floor_surface.get_rect()
        mparams_floor_rect.center = (SCREEN_WIDTH - 120, 40)

        ### BLIPPING TO SCREEN ###
        screen.blit(background, (0, 0))

        # if display_logo:
        #     screen.blit(logo_surface, logo_rect)
        # else:
        #     screen.blit(webcam_surface, webcam_rect)

        if display_logo:
            screen.blit(logo_surface, logo_rect)
        else:
            cv2_frame = drone.get_frame_read().frame

            if cv2_frame is not None:
                cv2_frame = cv2.flip(cv2_frame, 1)
                cv2_frame = yolo(cv2_frame, dnn_object)
                webcam_surface = pygame.surfarray.make_surface(cv2_frame)
                webcam_surface = pygame.transform.rotate(webcam_surface, -90)
                webcam_rect = webcam_surface.get_rect()
                webcam_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                screen.blit(webcam_surface, webcam_rect)

        screen.blit(battery_surface, battery_rect)
        screen.blit(height_surface, height_rect)
        screen.blit(barometer_surface, barometer_rect)
        screen.blit(temp_surface, temp_rect)
        screen.blit(controls_surface, controls_rect)
        screen.blit(absolute_coord_surface, absolute_coord_rect)
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
    # stop_thread_event.set()
    # video_thread.join()
    drone.streamoff()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == '__main__':
    main()