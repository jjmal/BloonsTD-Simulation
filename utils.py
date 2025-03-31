import pygame
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
        :param screen: A pygame Surface to draw on.
        """
        if outline:
            pygame.draw.circle(screen, (0,0,0), self.pos, self.radius)
            pygame.draw.circle(screen, self.color, self.pos, self.radius-2)
        else:
            pygame.draw.circle(screen, self.color, self.pos, self.radius)
      

# Taken from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
def is_circle_overlapping(circle1: Circle, circle2: Circle) -> bool:
    """
    Checks if two Circle objects overlap.
    :param circle1: one Circle
    :param circle2: the other circle
    :returns: True if the two circles overlap; false otherwise.
    """
    dx = circle1.pos[0] - circle2.pos[0]
    dy = circle1.pos[1] - circle2.pos[1]
    r = circle1.radius + circle2.radius

    return dx ** 2 + dy ** 2 < r ** 2

# Taken from https://github.com/ViniciusPiresLopes/PygameCirclesCollision/blob/master/main.py
def is_point_in_circle(circle: Circle, px: float, py: float) -> bool:
    """
    Checks if a Circle object contains a point.
    :param circle: the Circle object.
    :param px: x coord of the point
    :param py: y coord of the point.
    :returns: True if the circle contains a point; false otherwise.
    """
    dx = circle.pos[0] - px
    dy = circle.pos[1] - py
    r = circle.radius
    
    return dx ** 2 + dy ** 2 < r ** 2

# Taken from https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
def draw_rect_alpha(surface, color, rect) -> None:
    """
    Draws a rectangle with transparency enabled.
    :param surface: A pygame Surface to draw on.
    :param color: a tuple (R,G,B,A), with A representing the transparency (0-255)
    :param rect: a rectangle defined as neede by pygame.Rect
    """
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

# Taken from https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
def draw_circle_alpha(surface, color, center, radius) -> None:
    """
    Draws a circle with transparency enabled.
    :param surface: A pygame Surface to draw on.
    :param color: a tuple (R,G,B,A), with A representing the transparency (0-255)
    :param center: centre of the circle (x, y)
    :param radius: radius of the circle
    """
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.SysFont, color, x, y):
    """
    Draws String on surface.
    :param surface: A pygame Surface to draw on.
    :param text: the string to draw
    :param font: A pygame font object
    :param color:  a tuple (R,G,B)
    :param x: top-left x coord of where to draw
    :param y: top-left y coord of where to draw
    """
    img = font.render(text, True, color)
    surface.blit(img,(x, y))