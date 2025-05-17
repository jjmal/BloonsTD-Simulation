from typing import Tuple, List
from Game import Game, prepare_tower_queue
from GameHeuristic import GameS1, get_s1_tower_positions
from modelling import Model1, Model2
from modelling_utils import read_pickle

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

# def run_1a(modulo: int, graphics: bool = False, speed_multiplier: int = 5, dart_monkey_nr: int = 37,  round_19_correction: bool = False, from_file = None):
#     """
#     Runs the experiment for model 1a.
#     """
#     results = Model1.model1_per_round(modulo, 'a', (0,1), dart_monkey_nr, round_19_correction)
#     actions = Model1.model1_to_simulation(results)
#     queue = prepare_tower_queue(actions)
   
#     g = Game(40, 650, 1, graphics, queue, speed_multiplier)
#     g.run_game()

# def run_1b(modulo: int, scaling_bracket: Tuple[int,int], graphics: bool = False, speed_multiplier = 5, dart_monkey_nr: int = 37, round_19_correction: bool = False, from_file = None):
#     results = Model1.model1_per_round(modulo, 'b', scaling_bracket,  dart_monkey_nr,  round_19_correction)
#     actions = Model1.model1_to_simulation(results)
#     queue = prepare_tower_queue(actions)

#     g = Game(40, 650, 1, graphics, queue, speed_multiplier)
#     g.run_game()

# def run_1c(modulo: int,  scaling_bracket: Tuple[int,int], graphics: bool = False, speed_multiplier: int = 5, dart_monkey_nr: int = 37, round_19_correction: bool = False, from_file = None):
#     results = Model1.model1_per_round(modulo, 'c', scaling_bracket, dart_monkey_nr,  round_19_correction)
#     actions = Model1.model1_to_simulation(results)
#     queue = prepare_tower_queue(actions)

#     g = Game(40, 650, 1, graphics, queue, speed_multiplier)
#     g.run_game()

def run_1(modulo: int, type_: str,  graphics: bool = False, speed_multiplier: int = 5, dart_monkey_nr: int = 37, scaling_bracket: Tuple[int,int] = (0,1), round_19_correction: bool = False, from_file = None):
    if from_file is None:
        results = Model1.model1_per_round(modulo, type_, scaling_bracket, dart_monkey_nr, round_19_correction)
    else:
        path = from_file
        results = read_pickle(path, True)
        results.pop('parameters')
    actions = Model1.model1_to_simulation(results)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()



def run_2a(modulo: int, graphics: bool = False, speed_multiplier: int = 5, human_strategy_cost: int = 9250, round_weights: List[float] = [0.02 for i in range(50)]):
    model = Model2(modulo, 'a', (0,1), human_strategy_cost, round_weights, False)
    results = model.run()
    extracted = Model2.extract_vars_from_gurobi(results['choices'])
    actions = Model2.model2_to_simulation(extracted)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

