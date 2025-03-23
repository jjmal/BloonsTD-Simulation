import pygame
import sys
import math
import random
from Bloon import Bloon, BloonManager
from utils import Circle

pygame.init()

 # Set screen parameters
width = 830
height = 842
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bloons TD Simulation")

# Load background image
background = pygame.image.load("assets\\maps\\BTD1Map.png").convert()

# Draw the background
screen.blit(background, (0, 0))
pygame.display.update()

# Set up the clock
clock = pygame.time.Clock()

# # Set up bloons
# bloons = [
#     Bloon("R"),
#     Bloon("B"),
#     Bloon("G"),
#     Bloon("Y"),
#     Bloon("K"),
#     Bloon("W")
# ]

# game loop
run = True
FPS = 60
bloon_manager = BloonManager(1)
# Round preparation
bloon_manager.prepare_queue_for_round()
bloon_manager.shuffle_queue()
bloons_per_sec = 2
bloons_spawn_frame_threshold = 60/bloons_per_sec
bloon_spawn_frame_counter = bloons_spawn_frame_threshold

while run:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Background rendering
    screen.blit(background, (0, 0))
    
    # Spawn bloon from queue
    if bloon_spawn_frame_counter >= bloons_spawn_frame_threshold:
        if bloon_manager.queue:
            bloon_manager.spawn_bloon_from_queue()
            bloon_spawn_frame_counter = 1
    else:
        bloon_spawn_frame_counter += 1

    # Move bloons
    bloon_manager.move_all_bloons(screen)
    
    # Update display
    pygame.display.update()

    # Limit the frame rate
    clock.tick(FPS)
    

pygame.quit()








