import pygame
import sys
import math
import random
from Bloon import Bloon
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

# Set up bloons
bloons = [
    Bloon("R", 1, 5),
    Bloon("B", 2, 7),
    Bloon("G", 3, 9),
    Bloon("Y", 4, 16),
    Bloon("K", 5, 9),
    Bloon("W", 5, 10)
]

# game loop
run = True
FPS = 60
while run:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Backdround rendering
    screen.blit(background, (0, 0))

    # Bloon movements
    for bloon in bloons:
        bloon.move()
        bloon.draw(screen),
    
    pygame.display.update()

    # Limit the frame rate
    clock.tick(FPS)


pygame.quit()








