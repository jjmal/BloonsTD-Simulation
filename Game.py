import pygame
import sys
import math
import random

from typing import Dict
from Tower import TowerManager
from Bloon import BloonManager
from utils import draw_rect_alpha, draw_text

class Game:
    """
    Object for running the simulation.
    """
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    FPS = 40
    
    def __init__(self, starting_lives: int, starting_money: int, starting_round: int, graphics: bool, tower_queue: Dict, speed_multiplier: float = 1, bloons_spawn_line: int = 20) -> None:
        self.lives = starting_lives
        self.money = starting_money
        self.round = starting_round
        self.graphics = graphics
        self.speed_multiplier = speed_multiplier
        self.bloons_spawn_line = bloons_spawn_line
        self.tower_manager = TowerManager(tower_queue, self.round)

        self.bloon_manager = BloonManager(self.round)
        self.fps = self.FPS*self.speed_multiplier
        self.last_spawned_bloon = None

    def setup_screen(self) -> None:
        """
        Prepare screen and background settings.
        """
        # Set screen parameters
        self.screen = pygame.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
        pygame.display.set_caption("Bloons TD Simulation")

        # Load background image
        self.background = pygame.image.load("assets\\maps\\BTD1_Map.png").convert()

        # Set up the UI rectangle
        self.right_side_rect = pygame.Rect(480, 0, 160, 480)

        # Set up font
        self.text_font = pygame.font.SysFont("Times New Roman", 14)

    def render_screen(self) -> None:
        """
        Renders the background which fills the screen.
        """
        # Draw the background
        self.screen.blit(self.background, (0, 0))

    def render_bloons(self) -> None:
        """
        Renders Bloons.
        """
        self.bloon_manager.draw_all_bloons(self.screen)

    def render_towers(self) -> None:
        """
        Renders Towers.
        """
        self.tower_manager.draw_all_towers(self.screen)

    def render_ui(self) -> None:
        """
        Renders the UI elements and information displayed on it.
        """
        draw_rect_alpha(self.screen, (220,220,220,175), self.right_side_rect)
        draw_text(self.screen, f"Lives: {self.lives}", self.text_font, (0,0,0), 485, 5)
        draw_text(self.screen, f"Money: {self.money}", self.text_font, (0,0,0), 560, 5)

    def spawn_bloon(self) -> None:
        """
        Spawns all bloons from queue.
        """
        if self.last_spawned_bloon.x >= self.bloons_spawn_line:
            if self.bloon_manager.queue:
                self.last_spawned_bloon  = self.bloon_manager.spawn_bloon_from_queue()

    def build_and_upgrade_towers(self) -> None:
        """
        Builds and upgrades towers for the given round.
        """
        cost = self.tower_manager.resolve_queue_in_round()
        if cost <= self.money:
            self.money += -cost
        else:
            raise ValueError(f"Not enough money for the declared build in round {self.round}!")

    def move_bloons(self) -> None:
        """
        Moves all active bloons.
        """
        for bloon in self.bloon_manager.bloon_list:
            damage = self.bloon_manager.move_bloon(bloon)
            if damage is not None: # damage if endpoint is reached
                self.lives += -damage
        self.bloon_manager.update_freeze_all_bloons() # manage freeze

    def update_towers(self) -> None: 
        """
        Updates all tower behaiour
        """
        self.tower_manager.update_all_towers(self.bloon_manager)
        

    def run_game_with_graphics(self) -> None:
        """
        Runs the entire game with graphics.
        """
        # Initialise pygame
        pygame.init()
        # Set up the screen
        self.setup_screen()
        # Set up the clock
        clock = pygame.time.Clock()
        
        
        # Prepare round
        self.bloon_manager.prepare_queue_for_round()

        # Spawn initial bloon
        if len(self.bloon_manager.queue) > 0:
            self.last_spawned_bloon = self.bloon_manager.spawn_bloon_from_queue()
    
        # Game loop
        run = True
        while run:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            # Background rendering
            self.render_screen()

            # Building towers
            self.build_and_upgrade_towers()

            # Spawning
            self.spawn_bloon()
            
            # Movement
            self.move_bloons()
            self.update_towers()

            # Rendering
            self.render_towers()
            self.render_bloons()
            self.render_ui()

            # Update display
            pygame.display.update()

            # Control game speed
            clock.tick(self.fps)

        pygame.quit()

    def run_game_without_graphics(self):
        """
        Runs the entire game without graphics. This also ignores the FPS cap, as there is nothing to display.
        """
        pass

    def run_game(self):
        """
        Runs the game with or without graphics, depending on the game settings.
        """
        if self.graphics:
            self.run_game_with_graphics()
        else:
            self.run_game_without_graphics()