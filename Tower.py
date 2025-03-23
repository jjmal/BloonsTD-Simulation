import pygame
import sys
import math
import random
from typing import List
from Bloon import Bloon

from datasets import create_towers_dataframe
from utils import Circle, is_circle_overlapping, is_point_in_circle


class Tower:
    DF_TOWERS = create_towers_dataframe()
    def __init__(self, name, x, y, footprint_radius, attack_cooldown_frames, cost, cost_upgrade_1, cost_upgrade_2, range_, projectile_speed, projectile_lifetime_frames, colors):
        self.name = name
        self.x = x
        self.y = y
        self.footprint_radius = footprint_radius
        self.attack_cooldown_frames = attack_cooldown_frames
        self.cost = cost
        self.cost_upgrade_1 = cost_upgrade_1
        self.cost_upgrade_2 = cost_upgrade_2
        self.cumulative_cost_upgrade_1 = cost + cost_upgrade_1 
        self.cumulative_cost_upgrade_2 = cost + cost_upgrade_2
        self.cumulative_cost_all = cost + cost_upgrade_1 + cost_upgrade_2
        self.range = range_
        self.projectile_speed = projectile_speed
        self.projectile_lifespan_frames = projectile_lifetime_frames
        self.colors = colors
        
        self.damage = 1
        self.pierce = 1
        self.pops = 0
        self.upgrade1 = False
        self.upgrade2 = False
        self.projectiles = []
        self.attack_timer = 0
        self.footprint = Circle(self.colors[0], self.footprint_size, [self.x, self.y])
        self.inner_circle = Circle(self.colors[1], self.footprint_size - 5, [self.x, self.y])
        self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])
    
    def draw(self, screen) -> None:
        self.range_circle.draw(screen)
        self.footprint.draw(screen)
        self.inner_circle.draw(screen)
        for projectile in self.projectiles:  
            projectile.draw()

    def find_target(self, bloon_list: List[Bloon]) -> Bloon:
        target = None
        if bloon_list:
            for bloon in bloon_list:
                if is_point_in_circle(self.range_circle, bloon.x, bloon.y):
                    return target
                    
       
        
    def attack_target(self):
        pass

class Projectile:
    def __init__(self):
        pass

    def draw(self, screen):
        self.circle.draw(screen)