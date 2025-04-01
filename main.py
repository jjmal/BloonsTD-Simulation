from Game import Game, prepare_tower_queue
from typing import List, Tuple
from Tower import DartTower, TackTower, BombTower, IceTower, SuperMonkeyTower

actions = [(1, BombTower(250,150))]

def main(use_graphics: bool, actions: List[Tuple], speed_multiplier: float = 2) -> None:
    queue = prepare_tower_queue(actions)
    game = Game(40,800,1, use_graphics, queue, speed_multiplier)
    game.run_game()

if __name__ == "__main__":
    main(True, actions)


