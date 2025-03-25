import pygame
import sys
import math
import random
from Bloon import Bloon, BloonManager
from Tower import Tower, DartTower
from utils import Circle, draw_rect_alpha
from typing import List

pygame.init()

 # Set screen parameters
width = 640
height = 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bloons TD Simulation")

# Load background image and surface
background_graphic = pygame.image.load("assets\\maps\\BTD1_Map.png").convert_alpha()

# Draw the backgrounds
screen.blit(background_graphic, (0, 0))
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

# game loop info
run = True
FPS = 40

# Prepare the right-side rectangle to render
right_side_rect = pygame.Rect(480, 0, 160, 480)

# Round preparation
bloon_manager = BloonManager(20)
bloon_manager.prepare_queue_for_round()
bloon_manager.shuffle_queue()
bloons_spawn_line = 20
towers: List[Tower] = []
towers.append(DartTower(150,150))
attacked = 0

# Spawn initial bloon
if bloon_manager.queue:
    last_spawned_bloon = bloon_manager.spawn_bloon_from_queue()

while run:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    ## Background rendering
    screen.blit(background_graphic, (0, 0))
    draw_rect_alpha(screen, (220,220,220,175), right_side_rect)

    ## Spawning

    # Spawn bloon from queue
    if last_spawned_bloon.x >= bloons_spawn_line:
        if bloon_manager.queue:
            last_spawned_bloon  = bloon_manager.spawn_bloon_from_queue()

    ## Movement

    # Move bloons
    bloon_manager.move_all_bloons()

    # Draw all bloons
    

    # Test Towers
    for tower in towers:
        tower.attack(bloon_manager.bloon_list)
        tower.move_projectiles()    
        
    ## Drawing
    for tower in towers:
        tower.draw(screen)
    bloon_manager.draw_all_bloons(screen)

    # Update display
    pygame.display.update()

    clock.tick(FPS)
    

pygame.quit()








