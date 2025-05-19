from datasets import create_towers_dataframe

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

