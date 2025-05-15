from typing import Tuple
from Game import Game, prepare_tower_queue
from GameHeuristic import GameS1, get_s1_tower_positions
from modelling import Model1

def run_s1(graphics: bool = False, speed_multiplier = 5, dart_monkey_nr: int = 37):
    """
    Runs the experiment for S1.
    :param graphics: whether to run with graphics (True) or not (False)
    """ 
    positions = get_s1_tower_positions()[1:dart_monkey_nr]
    g = GameS1(40,650,1, graphics, positions, speed_multiplier)
    g.run_game()

def run_s2(graphics: bool = False, speed_multiplier = 5):
    """
    Runs the experiment for S2.
    :param graphics: whether to run with graphics (True) or not (False)
    """
    actions = [
        
    ]
    queue = prepare_tower_queue(actions)
    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

def run_1a(modulo: int, graphics: bool = False, speed_multiplier: int = 5, dart_monkey_nr: int = 37,  round_19_correction: bool = False):
    """
    Runs the experiment for model 1a.
    """
    results = Model1.model1_per_round(modulo, 'a', (0,1), dart_monkey_nr, round_19_correction)
    actions = Model1.model1_to_simulation(results)
    queue = prepare_tower_queue(actions)
   
    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

def run_1b(modulo: int, scaling_bracket: Tuple[int,int], graphics: bool = False, speed_multiplier = 5, dart_monkey_nr: int = 37, round_19_correction: bool = False):
    results = Model1.model1_per_round(modulo, 'b', scaling_bracket,  dart_monkey_nr,  round_19_correction)
    actions = Model1.model1_to_simulation(results)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

def run_1c(modulo: int,  scaling_bracket: Tuple[int,int], graphics: bool = False, speed_multiplier: int = 5, dart_monkey_nr: int = 37, round_19_correction: bool = False):
    results = Model1.model1_per_round(modulo, 'c', scaling_bracket, dart_monkey_nr,  round_19_correction)
    actions = Model1.model1_to_simulation(results)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

# run_1a(10, False, 20, 37, True)
run_1c(10, (0,1), False, 20, 37, True)
