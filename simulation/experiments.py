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
        (1, ('Dart', (232, 364), 0)),
        (1, ('Dart', (277, 327), 0)),
        (2,  ('Dart', (230, 77), 0)),
        (4,  ('Dart', (255, 207), 0)),
        (6, ('Dart', (365,365), 0)),
        (7, ('Dart', (232, 364), 1)),
        (8, ('Dart', (277, 327), 1)),
        (9, ('Dart', (255, 207), 1)),
        (10, ('Dart', (230, 77), 1)),
        (11, ('Dart', (365,365), 1)),
        (11, ('Dart', (277, 327), 2)),
        (12, ('Dart', (232, 364), 2)),
        (12, ('Dart', (255, 207), 2)),
        (13, ('Dart',  (230, 77), 2)),
        (13, ('Dart', (365,365), 2)),
        (14, ('Dart', (246,96), 0)),
        (15, ('Dart', (246,96), 1)),
        (15, ('Dart', (246,96), 2)),
        (16, ('Dart', (254,236), 0)),
        (17, ('Dart', (254,236), 1)),
        (17, ('Dart', (254,236), 2)),
        (17, ('Dart', (212,383), 0)),
        (18, ('Dart', (212,383), 1)),
        (18, ('Dart', (212,383), 2)),
        (19, ('Dart', (173,223), 0)),
        (19, ('Dart', (173,223), 1)),
        (20, ('Dart', (173,223), 2)),
        (20, ('Dart', (235,390), 0)),
        (21, ('Dart', (235,390), 1)),
        (21, ('Dart', (235,390), 2)),
        (22, ('Tack', (128,135), 0)),
        (23, ('Tack', (173,137), 0)),
        (24, ('Tack', (89,388), 0)),
        (25, ('Tack', (390,397), 0)),
        (26, ('Tack', (390,330), 0)), # money falls to zero - may need to move sth to be built later!
        (26, ('Tack', (128,135), 1)),
        (27, ('Tack', (173,137), 1)),
        (28, ('Tack', (89,388), 1)),
        (29, ('Tack', (390,397), 1)),
        (29, ('Tack', (390,330), 1)),
        (30, ('Tack', (128,135), 2)),
        (30, ('Tack', (173,137),2)),
        (30, ('Tack', (89,388), 2)),
        (30, ('Tack', (390,397), 2)),
        (30, ('Tack', (390,330), 2)),
        (31, ('Tack', (181, 316), 0)),
        (31, ('Tack', (181, 316), 1)),
        (31, ('Tack', (181, 316), 2)),
        (32, ('Tack', (335, 266), 0)),
        (33, ('Tack', (335, 266), 1)),
        (33, ('Tack', (335, 266), 2)),
        (34, ('Tack', (335,219), 0)),
        (34, ('Tack', (335,219), 1)),
        (34, ('Tack', (335,219), 2)),
        (35, ('Tack', (392,149), 0)),
        (36, ('Tack', (392,149), 1)),
        (36, ('Tack', (392,149), 2)),
        (36, ('Tack', (393,87), 0)),
        (37, ('Tack', (393,87), 1)),
        (37, ('Tack', (393,87), 2)),
        (37, ('Tack', (58,193), 0)),
        (38, ('Tack', (58,193), 1)),
        (38, ('Tack', (58,193), 2)),
        (38, ('Tack', (293,25), 0)),
        (39, ('Tack', (293,25), 1)),
        (39, ('Tack', (293,25), 2)),
        (39, ('Tack', (127,158), 0)),
        (40, ('Tack', (127,158), 1)),
        (40, ('Tack', (127,158), 2)),
        (40, ('Tack', (173,157), 0)),
        (40, ('Tack', (173,157), 1)),
        (40, ('Tack', (173,157), 2)),
        (45, ('Super Monkey', (257,115), 0)),
        (47, ('Super Monkey', (257,115), 2)),
        (49, ('Super Monkey', (275,363), 0))
    ]
    queue = prepare_tower_queue(actions)
    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()


def run_1(modulo: int, type_: str,  graphics: bool = False, speed_multiplier: int = 5, dart_monkey_nr: int = 37, scaling_bracket: Tuple[int,int] = (0,1), round_19_correction: bool = False):
    results = Model1.model1_per_round(modulo, type_, scaling_bracket, dart_monkey_nr, round_19_correction)
    actions = Model1.model1_to_simulation(results)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

def run_1_from_file(filename: str, graphics: bool = False, speed_multiplier: int = 5):
    results = read_pickle(filename, True)
    results.pop('parameters')

    actions = Model1.model1_to_simulation(results)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

def run_2(modulo: int, type_: str, graphics: bool = False, speed_multiplier: int = 5, human_strategy_cost: int = 9250, round_weights: List[float] = [0.02 for i in range(50)]):
    model = Model2(modulo, type_, (0,1), human_strategy_cost, round_weights, False)
    results = model.run()
    extracted = Model2.extract_vars_from_gurobi(results['choices'])
    actions = Model2.model2_to_simulation(extracted)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()

def run_2_from_file(filename: str, graphics: bool = False, speed_multiplier: int = 5):
    results = read_pickle(filename, True)
    results.pop('parameters')

    actions = Model2.model2_to_simulation(results)
    queue = prepare_tower_queue(actions)

    g = Game(40, 650, 1, graphics, queue, speed_multiplier)
    g.run_game()


# run_1(3, 'c', False, 10, 37, (0,1), False)



# run_1_from_file('Model1bmod10_20250517_171701', True, 10)
run_s2(True, 10)
