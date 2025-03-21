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
    Bloon("R"),
    Bloon("B"),
    Bloon("G"),
    Bloon("Y"),
    Bloon("K"),
    Bloon("W")
]

# game loop
run = True
FPS = 60
while run:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Background rendering
    screen.blit(background, (0, 0))

    # Bloon movements
    for bloon in bloons:
        bloon.move(bloons)
        bloon.draw(screen)
    
    pygame.display.update()

    # Limit the frame rate
    clock.tick(FPS)


pygame.quit()








