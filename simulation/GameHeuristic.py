from modelling_sets import create_towers_dataframe
from modelling_utils import sort_positions_by_middle_dist, get_empty_tower_queue
from typing import List ,Tuple

from Game import Game


class GameS1(Game):
    """
    Represents a game played using strategy 1.
    """
    TOWERS_DF = create_towers_dataframe()

    def __init__(self, starting_lives, starting_money, starting_round, graphics, positions_list, speed_multiplier = 1, round_break_frames = 60):
        super().__init__(starting_lives, starting_money, starting_round, graphics, get_empty_tower_queue(), speed_multiplier, round_break_frames)
        self.good_position_list = positions_list

    def get_next_good_positions(self) -> Tuple[int,int]:
        """
        Gets the next good position (according to Strategy 1).
        :returns: the next good position, in the format (x-coord, y-coord)
        """
        return self.good_position_list.pop(0)

    def strategy_1(self) -> None:
        """
        Adds actions to the queue according to Strategy 1.
        """
        can_buy = True
        money_value = self.money
        while can_buy:
            if money_value >= 250 and len(self.good_position_list) > 0:
                pos = self.get_next_good_positions()
                self.tower_manager.current_queue.append(('Dart', (pos[0],pos[1]), 0))
                money_value += -250
            else:
                can_buy = False
    
    def next_round(self) -> None:
        """
        Changes round to next.
        """
        # Get previous round (pre-update) pops sum
        previous_round_pops_sum = self.tower_manager.pops_sum
        self.bloon_manager.next_round()

        # Update pops for the money computation (we need the difference in pops!)
        self.tower_manager.round_nr += 1 
        self.tower_manager.update_pops() 

        # Make money
        self.make_money(previous_round_pops_sum)
        self.round += 1

        # Declare strategy
        self.strategy_1()
    
    def run_game(self):
        # Initialise strategy for the first round
        self.strategy_1()
        # Run game
        super().run_game()


def get_s1_tower_positions() -> List[Tuple[int,int]]:
        """
        Returns a good position for the Dart Tower. Some rules of thumb for good positions are:
        close to the middle of the map, close to a turn (i.e. in a corner), covering a lot of track area.
        :returns: a List of good positions in the form (x-coord, y-coord).
        """
        corners = [(55,190), (105, 260), (130,235), (55,105), (80,80), 
                   (130,140), (175,140), (210,60), (230,80), (250, 100), 
                   (175, 315), (240, 360), (215, 385), (40, 320), (20, 345),
                   (90,388), (20, 435), (40, 460), (435, 460), (455, 435),
                   (388,388), (388, 335), (460, 290), (430, 265), (340, 265),
                   (290, 330), (270, 315), (340, 230), (270, 190), (280, 160),
                   (440, 215), (460, 195), (390, 150), (390, 90), (460, 50),
                   (415, 20), (300, 25)]
        
        return sort_positions_by_middle_dist(corners)

# positions = [(350, 120), (370, 230), (370, 260), (170, 170), (360, 350), (120, 390), (360, 380), (380, 120), (130, 150), (270, 240), (180, 390), (160, 140), (140, 270), (400, 230), (400, 260), (270, 270), (340, 260), (390, 350), (390, 380), (340, 230), (270, 210), (360, 150), (350, 90), (330, 350), (330, 380), (90, 390), (210, 390), (250, 360), (390, 150), (380, 90), (140, 300), (290, 120), (170, 260), (280, 340), (290, 150), (260, 300), (260, 120), (260, 180), (260, 150), (140, 210), (240, 390), (170, 200), (300, 370), (250, 90), (170, 290), (60, 160), (30, 160), (140, 240), (320, 120), (80, 300), (170, 230), (280, 90), (50, 280), (80, 270), (270, 390), (60, 190), (250, 330), (200, 60), (360, 20), (110, 280), (50, 310), (230, 60), (110, 310), (30, 190), (320, 90), (330, 150), (430, 230), (430, 260), (20, 300), (170, 60), (330, 20), (460, 370), (200, 30), (230, 30), (470, 130), (20, 270), (140, 60), (460, 340), (20, 390), (300, 20), (130, 470), (470, 100), (170, 30), (370, 470), (390, 20), (340, 470), (100, 470), (60, 130), (460, 400), (20, 360), (20, 420), (160, 470), (190, 470), (220, 470), (250, 470), (310, 470), (280, 470), (470, 160), (400, 470), (460, 250), (460, 310), (420, 20), (110, 60), (470, 70), (70, 470), (460, 220), (460, 430), (60, 100), (470, 190), (430, 470), (460, 280), (140, 30), (30, 130), (20, 330), (20, 450), (450, 20), (80, 60), (470, 40), (40, 470), (460, 460), (110, 30), (50, 70), (30, 100), (80, 30), (50, 40), (20, 70), (20, 40)]
# game = GameHeuristic(40, 650, 1, True, {1: [('Dart', (150, 390), 0), ('Dart',(140, 180), 0)]}, 1, 5)
# game.set_position_list(positions)
# game.run_game()
