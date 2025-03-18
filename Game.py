import pygame
import sys
import math
import random

class Game:
    # Set up the screen
    SCREEN_WIDTH = 830
    SCREEN_HEIGHT = 842
    
    """
    Object for running the simulation.
    """

    def load_screen(self) -> None:
        """
        Loads screen and background.
        """
        # Set screen parameters
        screen = pygame.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
        pygame.display.set_caption("Bloons TD Simulation")

        # Load background image
        background = pygame.image.load("assets\\maps\\BTD1Map.png").convert()

        # Draw the background
        screen.blit(background, (0, 0))
        pygame.display.update()

    def run_game(self) -> None:
        # Initialize Pygame
        pygame.init()

        # Load screen
        self.load_screen()

        # Set up the clock
        clock = pygame.time.Clock()
       
        # game loop
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
        pygame.quit()