from Game import Game, prepare_tower_queue
from typing import List, Tuple
from Tower import DartTower, TackTower, BombTower, IceTower, SuperMonkeyTower

actions = [
    # (1, SuperMonkeyTower(100,225)),
    #  (1, (SuperMonkeyTower(100,225),2))
    # (50, SuperMonkeyTower(250,150)), 
    # (50, (SuperMonkeyTower(250,150), 2)), 
    # (50, BombTower(150, 150)), 
    # (50, (BombTower(150, 150), 1)), 
    # (50, IceTower(50,160)), 
    # (50, DartTower(270,300)),
    # (50, TackTower(90,390)),
    # (50, (TackTower(90,390),1)),
    # (50, (TackTower(90,390),2))
    ]

def main(use_graphics: bool, actions: List[Tuple], speed_multiplier: float = 2) -> None:
    queue = prepare_tower_queue(actions)
    game = Game(10000,10000,50, use_graphics, queue, speed_multiplier)
    game.run_game()

if __name__ == "__main__":
    main(True, actions, 10)


