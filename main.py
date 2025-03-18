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

# Set up a Bloon
bloon = Bloon("W", 1, 5)


# game loop
run = True
FPS = 60
while run:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Game rendering
    screen.blit(background, (0, 0))
    bloon.draw(screen),
    bloon.move()
    pygame.display.update()

    # Limit the frame rate
    clock.tick(FPS)


pygame.quit()








