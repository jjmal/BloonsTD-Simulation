import pygame
import math
import random
from typing import Tuple, List



# Taken from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
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
      

# Taken from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
def is_circle_overlapping(circle1: Circle, circle2: Circle) -> bool:
    dx = circle1.pos[0] - circle2.pos[0]
    dy = circle1.pos[1] - circle2.pos[1]
    r = circle1.radius + circle2.radius

    return dx ** 2 + dy ** 2 < r ** 2

# Taken from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
def is_point_in_circle(circle: Circle, px: float, py: float) -> bool:
    dx = circle.pos[0] - px
    dy = circle.pos[1] - py
    r = circle.radius
    
    return dx ** 2 + dy ** 2 < r ** 2

# Taken from https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

# Taken from https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
def draw_circle_alpha(surface, color, center, radius):
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)

# Taken from https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)

def draw_text(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img,(x, y))