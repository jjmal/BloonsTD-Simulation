from Game import Game, prepare_tower_queue
from typing import List, Tuple

actions = [
    (1, ('Dart', (150,225), 0)),
    (2, ('Dart', (150,225), 1)),
    (3, ('Tack', (250,150), 0)),
]


def main(use_graphics: bool, actions: List[Tuple], speed_multiplier: int = 2) -> None:
    queue = prepare_tower_queue(actions)
    # DEMO 1 - 40, 650, 1
    # DEMO 2 - 40, 10000, 50
    game = Game(40, 10000, 1, use_graphics, queue, speed_multiplier)
    game.run_game()

if __name__ == "__main__":
    main(True, actions, 5)
    


