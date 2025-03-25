import pygame
import sys
import math
import random
from typing import List
from Bloon import Bloon, BloonManager

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
        self.projectile_list: List[Projectile] = []
        self.attack_counter = 1
        self.footprint = Circle(self.colors[0], self.footprint_radius, [self.x, self.y])
        self.inner_circle = Circle(self.colors[1], self.footprint_radius - 5, [self.x, self.y])
        self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])
    
    def draw(self, screen) -> None:
        draw_circle_alpha(screen, (220,220,220,150), (self.x, self.y), self.range)
        self.footprint.draw(screen)
        self.inner_circle.draw(screen)
        for projectile in self.projectile_list:  
            projectile.draw(screen)
       
    def find_target(self, bloon_list: List[Bloon]) -> Bloon:
            target = None
            max_progress = 0
            if len(bloon_list) > 0:
                for bloon in bloon_list:
                    if is_point_in_circle(self.range_circle, bloon.x, bloon.y):
                        if max_progress <= bloon.progress:
                            target = bloon
                            max_progress = bloon.progress
            return target
    
    # Idea for movement in any direction taken from https://www.youtube.com/watch?v=3DeW-7vbc50&ab_channel=NealHoltschulte
    def spawn_projectile(self, target: Bloon) -> None:
        if target is not None:
            angle = - (math.atan2(target.x - self.x, target.y - self.y) - math.pi/2)
            dx = math.cos(angle)
            dy = math.sin(angle)
            new_projectile = Projectile(self.x, self.y, self.projectile_speed, dx, dy, self.pierce, self.projectile_lifespan_frames)
            self.projectile_list.append(new_projectile)
    
    def remove_projectile(self, projectile) -> None:
        self.projectile_list.remove(projectile)

    def update_attack_counter(self) -> None:
        if self.attack_counter >= self.attack_cooldown_frames:
            self.attack_counter = 1
        else:
            self.attack_counter += 1

    def shoot(self, bloon_list: List[Bloon]) -> None:
        if self.attack_counter >= self.attack_cooldown_frames:
            target = self.find_target(bloon_list)
            self.spawn_projectile(target)
            
    def move_projectiles(self) -> None:
        for projectile in self.projectile_list: 
            if projectile.lifespan_counter < projectile.lifespan_frames:
                projectile.move()
            else:
                self.remove_projectile(projectile)
    
    def check_for_projectile_collisions(self, bloon_manager: BloonManager) -> None:
        for projectile in self.projectile_list:
            hit_something = projectile.collide(bloon_manager)
            if hit_something:
                self.remove_projectile(projectile)

    
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


class TowerManager:
    """
    Manages spawns and upgrades of towers from a list in the right rounds, and makes updates to towers if necessary.
    """
    def __init__(self, initial_round_nr: int = 1):
        self.round_nr = initial_round_nr

        self.tower_list = []
        self.queue_all_rounds = {}
        self.position_tower_map = {}
        self.currect_queue = self.queue_all_rounds[self.round_nr]
       
    def spawn_tower_from_queue(self) -> None:
        new_tower = self.current_queue.pop(0)
        self.tower_list.append(new_tower)
        self.position_tower_map[(new_tower.x, new_tower.y)] = new_tower

    def upgrade_tower_at_position(self, tower_x: int, tower_y: int, upgrade_type: int) -> None:
        tower = self.position_tower_map[(tower_x, tower_y)]
        if upgrade_type == 1:
            tower.get_upgrade_1()
        else:
            tower.get_upgrade_2()
    
    def update_all_towers(self, bloon_list: List[Bloon]) -> None:
        for tower in self.tower_list:
            target = tower.find_target(bloon_list)
            tower.spawn_projectile(target)
            tower.move_projectiles()
    
    def draw_all_towers(self, screen) -> None:
        for tower in self.tower_list:
            tower.draw(screen)

    def next_round(self):
        self.round_nr += 1
        self.currect_queue = self.queue_all_rounds[self.round_nr]

class Projectile:
    """
    Represents a projectile fired by tower in Bloons TD.
    """
    def __init__(self, x, y, speed, dx, dy, pierce, lifespan_frames):
        self.x = x
        self.y = y
        self.speed = speed
        self.dx = dx
        self.dy = dy
        self.pierce = pierce

        self.vx = self.dx*self.speed
        self.vy = self.dy*self.speed
        self.radius = 3
        self.circle = Circle((139, 0, 139), self.radius, [self.x, self.y])
        self.lifespan_frames = lifespan_frames
        self.lifespan_counter = 1
        
    def draw(self, screen) -> None:
        self.circle.draw(screen, outline=False)

    # Idea for movement in any direction taken from https://www.youtube.com/watch?v=3DeW-7vbc50&ab_channel=NealHoltschulte
    def move(self) -> None:
        self.x += self.vx
        self.y += self.vy

        # Update circle position
        self.circle.pos[0] = int(self.x)
        self.circle.pos[1] = int(self.y)

        # Update lifespan tracker
        self.lifespan_counter += 1
        
    
    def collide(self, bloon_manager: BloonManager) -> bool:
        """
        Checks for collision with bloons. 
        :returns: true if the collision has occured; false otherwise
        """
        hit_set = set()
        bloon_list = bloon_manager.bloon_list
        if len(bloon_list) > 0:
            for bloon in  bloon_list:
                if is_circle_overlapping(bloon.circle, self.circle):
                    hit_set.add(bloon)
            if len(hit_set) > 0:
                hit_bloon = hit_set.pop()
                bloon_manager.resolve_bloon_hit(hit_bloon)
                return True
        return False