from Game import Game, prepare_tower_queue
from typing import List, Tuple

actions = [
    [(1, ('Dart', (150, 180), 0)), 
     (1, ('Dart', (140, 390), 0)), 
     (2, ('Dart', (380, 240), 0)), 
     (4, ('Dart', (360, 120), 0)), 
     (6, ('Dart', (350, 360), 0)), (8, ('Dart', (370, 260), 0)), (9, ('Dart', (170, 170), 0)), (9, ('Dart', (140, 160), 0)), (10, ('Dart', (370, 220), 0)), (12, ('Dart', (120, 390), 0)), (13, ('Dart', (360, 380), 0)), (14, ('Dart', (130, 180), 0)), (15, ('Dart', (360, 240), 0)), (16, ('Dart', (370, 360), 0)), (17, ('Dart', (170, 190), 0)), (17, ('Dart', (390, 260), 0)), (18, ('Dart', (360, 140), 0)), (18, ('Dart', (380, 130), 0)), (19, ('Dart', (380, 110), 0)), (19, ('Dart', (340, 380), 0)), (20, ('Dart', (350, 100), 0)), (21, ('Dart', (340, 120), 0)), (22, ('Dart', (160, 150), 0)), (22, ('Dart', (390, 220), 0)), (23, ('Dart', (350, 260), 0)), (24, ('Dart', (160, 390), 0)), (24, ('Dart', (350, 220), 0)), (25, ('Dart', (370, 340), 0)), (25, ('Dart', (270, 240), 0)), (26, ('Dart', (380, 380), 0)), (26, ('Dart', (340, 140), 0)), (27, ('Dart', (140, 280), 0)), (27, ('Dart', (350, 340), 0)), (28, ('Dart', (270, 260), 0)), (29, ('Dart', (180, 390), 0)), (30, ('Dart', (270, 220), 0)), (30, ('Dart', (400, 240), 0))]
]


def main(use_graphics: bool, actions: List[Tuple], speed_multiplier: int = 2) -> None:
    queue = prepare_tower_queue(actions)
    # DEMO 1 - 40, 650, 1
    # DEMO 2 - 40, 10000, 50
    game = Game(40, 10000, 1, use_graphics, queue, speed_multiplier)
    game.run_game()

if __name__ == "__main__":
    main(False, actions, 2)
    


