import pygame
import sys
import math
import random
from typing import List
from Bloon import Bloon

from datasets import create_towers_dataframe
from utils import Circle, is_circle_overlapping, is_point_in_circle, draw_circle_alpha


class Tower:
    """
    Represents a Tower in Bloons TD.
    """
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
        
        self.pierce = 1
        self.pops = 0
        self.upgrade1 = False
        self.upgrade2 = False
        self.projectile_list = []
        self.attack_timer = 0
        self.footprint = Circle(self.colors[0], self.footprint_radius, [self.x, self.y])
        self.inner_circle = Circle(self.colors[1], self.footprint_radius - 5, [self.x, self.y])
        self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])
    
    def draw(self, screen) -> None:
        draw_circle_alpha(screen, (220,220,220,150), (self.x, self.y), self.range)
        self.footprint.draw(screen)
        self.inner_circle.draw(screen)
        for projectile in self.projectile_list:  
            projectile.draw()
       
    def move_projectiles(self) -> None:
        for projectile in self.projectile_list: 
            for _ in projectile.speed:
                projectile.move_once()

    def find_target(self, bloon_list: List[Bloon]) -> Bloon:
            target = None
            if bloon_list:
                for bloon in bloon_list:
                    if is_point_in_circle(self.range_circle, bloon.x, bloon.y):
                        return target
                    
    def spawn_projectile(self, target: Bloon) -> None:
        if target is not None:
            new_projectile = Projectile(self.x, self.y, self.projectile_speed, target.x, target.y, self.pierce)
            self.projectile_list.append(new_projectile)



class DartTower(Tower):
    """
    Represents a Tower in Bloons TD.
    """
    def __init__(self, x, y):
        super().__init__(
            'Dart', x, y, 
            footprint_radius = Tower.DF_TOWERS.loc['Dart', "footprint_radius"], 
            attack_cooldown_frames =  Tower.DF_TOWERS.loc['Dart', "attack_cooldown_frames"],
            cost = Tower.DF_TOWERS.loc['Dart', "cost"], 
            cost_upgrade_1 = Tower.DF_TOWERS.loc['Dart', "upgrade_1_cost"], 
            cost_upgrade_2 = Tower.DF_TOWERS.loc['Dart', "upgrade_2_cost"], 
            range_ = Tower.DF_TOWERS.loc['Dart', "range"], 
            projectile_speed = Tower.DF_TOWERS.loc['Dart', "projectile_speed"], 
            projectile_lifetime_frames = Tower.DF_TOWERS.loc['Dart', "projectile_lifespan_frames"], 
            colors = [Tower.DF_TOWERS.loc['Dart', "color_outer"], Tower.DF_TOWERS.loc['Dart', "color_inner"]]
        )
    
    def get_upgrade_1(self):
        self.pierce = 2
    
    def get_upgrade_2(self):
        self.range = Tower.DF_TOWERS.loc['Dart', "upgrade_2_range"]

class TowerManager():
    """
    Manages spawns of towers from a list in the right rounds, and makes updates to towers if necessary.
    """

class Projectile:
    """
    Represents a projectile fired by tower in Bloons TD.
    """
    def __init__(self, x, y, speed, target_x, target_y, pierce):
        self.x = x
        self.y = y
        self.speed = speed
        self.target_x = target_x
        self.target_y = target_y
        self.pierce = pierce

        self.damage = 1
        self.radius = 2
        self.circle = Circle((139, 0, 139), self.radius, [self.x, self.y])
        
    def draw(self, screen) -> None:
        self.circle.draw(screen)

    def move_once(self) -> None:
        if self.x < self.target_x:
            self.x += 1
        if self.y < self.target_y:
            self.y += 1

        if self.x > self.target_x:
            self.x -= 1
        if self.y > self.target_y:
            self.y -= 1

        # Update circle position
        self.circle.pos[0] = self.x
        self.circle.pos[1] = self.y
    
    def collide(self, bloons_in_range: List[Bloon]) -> bool:
        damage_set = {}
        if bloons_in_range:
            for bloon in bloons_in_range:
                if is_circle_overlapping(bloon.circle, self.circle):
                    damage_set.add(bloon)
            hit_bloon = damage_set.pop()
            hit_bloon.hit()
            return True
        return False