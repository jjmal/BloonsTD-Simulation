import pygame

from typing import Dict, Tuple, List
from Tower import TowerManager, DartTower
from Bloon import BloonManager
from utils import draw_rect_alpha, draw_text
from datasets import create_rounds_dataframe, create_towers_dataframe

class Game:
    """
    Object for running the simulation.
    """
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    FPS = 40
    DF_ROUNDS = create_rounds_dataframe()
    BLOONS_SPAWN_LINE = -10
    
    def __init__(self, 
                 starting_lives: int, 
                 starting_money: int, 
                 starting_round: int, 
                 graphics: bool, 
                 tower_queue: Dict, 
                 speed_multiplier: float = 1, 
                 round_break_frames: int = 60) -> None:
        self.lives = starting_lives
        self.money = starting_money
        self.round = starting_round
        self.graphics = graphics
        self.speed_multiplier = speed_multiplier
        self.tower_manager = TowerManager(tower_queue, self.round)
        self.round_brake_frames = round_break_frames

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
        draw_text(self.screen, f"Round: {self.round}", self.text_font, (0,0,0), 485, 5)
        draw_text(self.screen, f"Lives: {self.lives}", self.text_font, (0,0,0), 485, 20)
        draw_text(self.screen, f"Money: {self.money}", self.text_font, (0,0,0), 550 , 20)

    def spawn_bloon(self) -> None:
        """
        Spawns all bloons from queue.
        """
        if self.last_spawned_bloon.x >= Game.BLOONS_SPAWN_LINE:
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

    def check_round_end(self) -> bool:
        """
        Checks for the end of the round.
        :returns: True if round has ended; False otherwise.
        """
        if len(self.bloon_manager.bloon_list) <= 0:
            return True
        return False
    
    def make_money(self, previous_round_pops_sum: int) -> None:
        """
        Increments the money at the end of the round.
        :param previous_round_pops: sum of pops at the end of the previous round of all active towers
        """
        end_round_money = int(Game.DF_ROUNDS.loc[self.round,'money_round_end'])
        pops_sum = self.tower_manager.pops_sum
        pop_money = pops_sum - previous_round_pops_sum
        self.money += end_round_money
        self.money += pop_money
    
    def next_round(self) -> None:
        """
        Changes round to next.
        """
        # Get previous round (pre-update) pops sum
        previous_round_pops_sum = self.tower_manager.pops_sum
        self.bloon_manager.next_round()
        self.tower_manager.next_round() # This also updates pops!
        # Make money
        self.make_money(previous_round_pops_sum)
        self.round += 1

    def check_game_end(self) -> int:
        """
        Checks for the end of the game and its type.
        :returns: 0 if the game has not ended; 1 if the game has ended and is won by the player; 2 if the game has ended and is lost by the player.
        """
        if self.lives <= 0:
            return 2
        if self.round >= 50 and self.check_round_end():
            return 1
        return 0


    def get_endgame_info(self) -> Dict:
        """
        Gets information at the end of the game.
        """
        info_dict = {}
        info_dict['round'] = self.round
        info_dict['lives'] = int(self.lives)
        info_dict['money'] = int(self.money)
        info_dict['towers'] = self.tower_manager.tower_list
        return info_dict

    def run_game(self) -> None:
        """
        Runs the entire game with graphics.
        """

        if self.graphics:
            # Initialise pygame
            pygame.init()
            # Set up the screen
            self.setup_screen()
            # Set up the clock
            clock = pygame.time.Clock()

        # Set up the round break counter
        round_break_counter = 1
        
        # Prepare round 1
        self.bloon_manager.prepare_queue_for_round()

        # Spawn initial bloon
        if len(self.bloon_manager.queue) > 0:
            self.last_spawned_bloon = self.bloon_manager.spawn_bloon_from_queue()
    
        # Game loop
        run = True
        while run:
            if self.graphics:
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
            
            if self.graphics:
                # Rendering
                self.render_towers()
                self.render_bloons()
                self.render_ui()

            # Resolve game end:
            if self.check_game_end() == 1:
                run = False
                print("Game won!")
                print(f"Some end game information:\n{self.get_endgame_info()}")
            elif self.check_game_end() == 2:
                run = False
                print(f"Game lost on round {self.round}!")
                print(f"Some end game information:\n{self.get_endgame_info()}")

            # Manage round changes
            if self.check_round_end():
                if round_break_counter >= self.round_brake_frames:
                    # Change round
                    self.next_round()
                    round_break_counter = 1

                else:
                    round_break_counter += 1

            if self.graphics:
                # Update display
                pygame.display.update()

                # Control game speed
                clock.tick(self.fps)
        if self.graphics:
            pygame.quit()

def prepare_tower_queue(tower_actions_tuple: List[Tuple[int, List]]) -> Dict:
    """
    Transforms list of tuples into a queue that can be put in a Game object.
    :param tower_actions_tuples: A list of tuples, with the tuples in the 
    form (round_nr, (tower_name, pos, action_type)). 
    :returns: A dictionary that is readable by the Game object as a valid queue.
    """
    builds = [[] for i in range(50)]
    keys = [(i+1) for i in range(50)]
    queue = dict(zip(keys,builds))
    for action in tower_actions_tuple:
        queue[action[0]].append(action[1])

    return queue


