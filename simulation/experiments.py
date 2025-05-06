from Game import Game, prepare_tower_queue
from GameHeuristic import GameS1, get_s1_tower_positions

def run_s1(graphics: bool = False):
    """
    Runs the experiment for S1.
    :param graphics: whether to run with graphics (True) or not (False)
    """ 
    positions = get_s1_tower_positions()
    g = GameS1(40,650,1, graphics, positions, 2)
    g.run_game()

def run_s2(graphics: bool = False):
    """
    Runs the experiment for S2.
    :param graphics: whether to run with graphics (True) or not (False)
    """
    actions = [
        
    ]
    queue = prepare_tower_queue(actions)
    g = Game(40, 650, 1, graphics, queue, 2)
    g.run_game()
    
