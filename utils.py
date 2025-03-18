import pygame
import math
import random
from typing import Tuple, List



# Adapted from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
class Circle:
    """
    Represents a circle.
    """
    def __init__(self, color: Tuple[int,int,int], radius: int, pos: List[int]=[0, 0], outline: bool = True) -> None:
        self.color = color
        self.radius = radius
        self.pos = pos
    
    def draw(self, screen: pygame.Surface, outline:bool = True) -> None:
        """
        Draws a circle.
        :param screen: A screen to draw on.
        """
        if outline:
            pygame.draw.circle(screen, (0,0,0), self.pos, self.radius)
            pygame.draw.circle(screen, self.color, self.pos, self.radius-2)
        else:
            pygame.draw.circle(screen, self.color, self.pos, self.radius)
      
           


# Adapted from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
def is_circle_overlapping(circle1: Circle, circle2: Circle) -> bool:
    dx = circle1.pos[0] - circle2.pos[0]
    dy = circle1.pos[1] - circle2.pos[1]
    r = circle1.radius + circle2.radius

    return dx ** 2 + dy ** 2 < r ** 2

# Adapted from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
def is_point_in_circle(circle: Circle, px: float, py: float) -> bool:
    dx = circle.pos[0] - px
    dy = circle.pos[1] - py
    r = circle.radius
    
    return dx ** 2 + dy ** 2 < r ** 2