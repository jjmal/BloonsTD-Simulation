from utils import Circle, is_circle_overlapping

class Bloon:
    PATH_POINTS = [(0,400), (170,400), (170, 175), (375,175), (375,615), (95, 615), (95, 760), (755, 760), (755, 525), (540, 525), (540, 330), (755, 330), (755, 95), (465, 95), (465, 0)]
    PATH_CIRCLES = [Circle((0,0,0), 2, [point[0], point[1]]) for point in PATH_POINTS]
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
    def __init__(self, type_, life, speed) -> None:
        self.type = type_
        self.life = life
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
        return is_circle_overlapping(self, other)

    def move(self) -> None:
        # Move 
        if self.x < self.target_x:
            self.x += self.speed
        if self.y < self.target_y:
            self.y += self.speed

        if self.x > self.target_x:
            self.x -= self.speed
        if self.y > self.target_y:
            self.y -= self.speed

        # Update circle position
        self.circle.pos[0] = self.x
        self.circle.pos[1] = self.y

        # Set new target if target is reached
        if self.x == self.target_x and self.y == self.target_y:
            self.pathline += 1
            self.target_x = Bloon.PATH_POINTS[self.pathline][0]
            self.target_y = Bloon.PATH_POINTS[self.pathline][1]

    def draw(self, screen) -> None:
        self.circle.draw(screen)