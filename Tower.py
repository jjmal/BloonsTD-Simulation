import pygame
import sys
import math
import random
from typing import List
from Bloon import Bloon

from utils import Circle, is_circle_overlapping


class Tower:
    def __init__(self, name, x, y, damage, attacks_per_second, footprint_size):
        self.name = name
        self.x = x
        self.y = y
        self.damage = damage
        self.footprint_size = footprint_size

        self.pierce = 1
        self.range = 100  
        self.pops = 0
        self.upgrade1 = False
        self.upgrade2 = False
        self.projectiles = []
        self.attacks_per_second = attacks_per_second
        self.attack_timer = 0
        self.color = (150,75,0)
        self.footprint = Circle(self.color, self.footprint_size, [self.x, self.y])
    
    def draw(self, screen):
        self.circle.draw(screen)
        for projectile in self.projectiles:  
            projectile.draw()

    def find_target(self, bloon_list: List[Bloon]):
        min_distance = float("inf")
        target = None
        if len(bloon_list) > 0:
            primeiro = bloon_list[0]
            for value in bloon_list:
                distance = math.sqrt((value.x - self.x) **
                                    2 + (value.y - self.y) ** 2)
                distancep = math.sqrt((primeiro.x - self.x) **
                                    2 + (primeiro.y - self.y) ** 2)
                if distancep < self.range and value.life > 0 and distance < min_distance:
                    min_distance = distance
                    target = primeiro
                elif distance < self.range and value.life > 0 and distance < min_distance:
                    min_distance = distance
                    target = value
            return target
        
    def attack_target(self):
        pass

class Projectile:
    def __init__(self):
        pass

    def draw(self, screen):
        self.circle.draw(screen)