from utils import Circle, is_circle_overlapping, is_point_in_circle
from typing import Tuple, List, Any

class Bloon:
    PATH_POINTS = [
        (-20,400), (170,400), (170, 175), (375,175), (375,615), 
        (95, 615), (95, 760), (755, 760), (755, 525), (540, 525), 
        (540, 330), (755, 330), (755, 95), (465, 95), (465, -20)
        ]
    HEALTH_TYPE_DICT = {
        1: "R",
        2: "B",
        3: "G",
        4: "Y"
    }
    TYPE_COLOR_DICT = {
        "R":(255, 0, 0),
        "B":(0,0, 255),
        "G":(0, 255, 0),
        "Y":(255,255,0),
        "W":(255,255,255),
        "K": (0,0,0)
    }
    RADIUS = 20
    RED_BLOON_SPEED = 5
    """
    Represents a Bloon (creep) in Bloons TD
    """
    def __init__(self, type_, health, speed) -> None:
        self.type = type_
        self.health = health
        self.speed = speed

        self.color = Bloon.TYPE_COLOR_DICT[self.type]
        self.x = Bloon.PATH_POINTS[0][0]
        self.y = Bloon.PATH_POINTS[0][1]
        self.circle = Circle(color=self.color, radius=Bloon.RADIUS, pos=[self.x, self.y])
        self.pathline = 1
        self.target_x = Bloon.PATH_POINTS[self.pathline][0]
        self.target_y = Bloon.PATH_POINTS[self.pathline][1]
        
        # self.anteriorx = self.x
        # self.anteriory = self.y
    
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
    
    def die(self, bloons_list: List[Any]) -> None:
        bloons_list.remove(self)

    def move(self, bloons_list: List[Any]) -> None:
        """
        Performs movement by the numbertaking into account speed. Also resolves  
        :param bloons_list: list of active Bloons.
        """
        for _ in range(self.speed):
            self.move_once()
            endpoint_reached = self.reach_target()
            if endpoint_reached:
                self.die(bloons_list)
                print(bloons_list)
                break

    def draw(self, screen) -> None:
        self.circle.draw(screen)
    
    def hit(self, damage = int) -> None: # TODO - Finish
        """
        Transforms the Bloon into bloon of another type (upod takign damage).
        """
        pass
        # self.health -= damage
        # new_type = Bloon.HEALTH_TYPE_DICT[self.health]
        # self.type = new_type
        # self.color = Bloon.TYPE_COLOR_DICT[self.type]

