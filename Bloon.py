import random
import pygame

from utils import Circle, is_circle_overlapping, is_point_in_circle
from datasets import create_pathline, create_bloons_dataframe, create_rounds_dataframe
from typing import Tuple, List, Any

class Bloon:
    """
    Represents a Bloon (creep) in Bloons TD.
    """
    RED_BLOON_SPEED = 2
    RADIUS = 10
    DF_BLOONS = create_bloons_dataframe(RED_BLOON_SPEED)
    PATH_POINTS = create_pathline()
    def __init__(self, type_) -> None:
        self.type = type_

        self.health = Bloon.DF_BLOONS.loc[type_, 'health']
        self.speed = Bloon.DF_BLOONS.loc[type_, 'speed']
        self.color = Bloon.DF_BLOONS.loc[type_, 'rgb']
        self.x = Bloon.PATH_POINTS[0][0]
        self.y = Bloon.PATH_POINTS[0][1]
        self.circle = Circle(color=self.color, radius=Bloon.RADIUS, pos=[self.x, self.y])
        self.pathline = 1
        self.target_x = Bloon.PATH_POINTS[self.pathline][0]
        self.target_y = Bloon.PATH_POINTS[self.pathline][1]
        self.progress = 0
    
    def overlaps(self, other: Circle) -> bool:
        return is_circle_overlapping(self.circle, other)
    
    def contains(self, point: Tuple[int, int]) -> bool:
        return is_point_in_circle(self.circle, point[0], point[1])

    def move_once(self):
        """
        Moves the bloon by one pixel in the given direction.
        """
        # Move (by one pixel)
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

        # Update progress
        self.progress += 1
        
    def reach_target(self) -> bool:
        """
        Checks if a target point (turning point of Bloons on the track) or the endpoint has been reached, 
        and resolves the target changes.
        :returns: whether the endpoint was reached with this movement (True) or not (False)
        """
        # When the target (turn on the road or endpoint) is reached
        if self.x == self.target_x and self.y == self.target_y:
            # Send signal that bloon should dissapear when it reached endpoint
            if self.x == Bloon.PATH_POINTS[-1][0] and self.y == Bloon.PATH_POINTS[-1][1]: 
                return True
                
            # In other cases set a new target 
            else:    
                self.pathline += 1
                self.target_x = Bloon.PATH_POINTS[self.pathline][0]
                self.target_y = Bloon.PATH_POINTS[self.pathline][1]
        # If endpoint was not reached, send a signal with that info
        return False

    def draw(self, screen) -> None:
        self.circle.draw(screen)


class BloonManager:
    """
    Manages Bloon spawns and movement each round and keeps track of existing of Bloons.
    """
    SPAWN_RATE = 5 # nr of bloons spawned per second (on 60 FPS)
    DF_ROUNDS = create_rounds_dataframe()

    def __init__(self, round_nr: int = 1):
        self.bloon_list = []
        self.queue = []
        self.round_nr = round_nr

    def enqueue_bloon(self, bloon_type: str) -> None:
        self.queue.append(Bloon(bloon_type))

    def spawn_bloon_from_queue(self) -> Bloon:
        spawned_bloon = self.queue.pop(0)
        self.bloon_list.append(spawned_bloon )
        return spawned_bloon 

    def spawn_bloon_outside_queue(self, bloon_type: str) -> Bloon:
        new_bloon = Bloon(bloon_type)
        self.bloon_list.append(new_bloon)
        return new_bloon
    
    def remove_bloon(self, bloon: Bloon) -> None:
        self.bloon_list.remove(bloon)

    def prepare_queue_for_round(self):
        for bloon_type in ['R', 'B', 'G', 'K', 'W', 'Y']:
            for _ in range(int(BloonManager.DF_ROUNDS.loc[self.round_nr, bloon_type])):
                self.enqueue_bloon(bloon_type)

    def shuffle_queue(self):
        random.shuffle(self.queue)
    
    def move_bloon(self, bloon: Bloon) -> None:
        speed = bloon.speed
        for _ in range(speed):
            bloon.move_once()
            endpoint_reached = bloon.reach_target()
            if endpoint_reached:
                self.remove_bloon(bloon)
                break
    
    def resolve_bloon_hit(self, bloon: Bloon) -> None:
        """
        Resolves Bloon being hit by a projectile.
        :param bloon: Bloon that gets hit.
        """
        # Get damaged
        bloon.health += -1

        # Check for death
        if bloon.health <= 0:
            self.remove_bloon(bloon)
        else:
            # Transform Bloon 
            if bloon.type == 'B':
                into = 'R'
            if bloon.type == 'G':
                into = 'B'
            if bloon.type == 'Y':
                into = 'G'
            if bloon.type == 'W' or bloon.type == 'K':
                into == 'Y'
            bloon.type = into
            bloon.speed = Bloon.DF_BLOONS.loc[into, 'speed']
            bloon.color = Bloon.DF_BLOONS.loc[into, 'rgb']
            bloon.circle = Circle(color=bloon.color, radius=Bloon.RADIUS, pos=[bloon.x, bloon.y])



    def move_all_bloons(self) -> None:
        for bloon in self.bloon_list:
            self.move_bloon(bloon)
    
    def draw_all_bloons(self,screen) -> None:
        for bloon in self.bloon_list:
            bloon.draw(screen)