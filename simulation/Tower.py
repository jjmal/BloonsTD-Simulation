import math
import pygame
from typing import List, Dict, Tuple
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
        self.attack_counter = self.attack_cooldown_frames 
        self.footprint = Circle(self.colors[0], self.footprint_radius, [self.x, self.y])
        self.inner_circle = Circle(self.colors[1], self.footprint_radius - 5, [self.x, self.y])
        self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])
        self.target = None
    
    def draw(self, screen) -> None:
        # draw_circle_alpha(screen, (220,220,220,50), (self.x, self.y), self.range)
        pygame.draw.circle(screen, (220,220,220),  (self.x, self.y), self.range, 1)
        self.footprint.draw(screen)
        self.inner_circle.draw(screen)
        for projectile in self.projectile_list:  
            projectile.draw(screen)
       
    def find_target(self, bloon_list: List[Bloon]) -> None:
        """
        Find the bloon to shoot at. The target is defined to be the bloon in range that has reached the 
        furthest in the track and is non-frozen.
        :param bloon_list: A list of active bloons.
        """
        self.target = None
        max_progress = 0
        if len(bloon_list) > 0:
            for bloon in bloon_list:
                if is_point_in_circle(self.range_circle, bloon.x, bloon.y) and not bloon.frozen and not bloon.invulnerable: # don't target frozen bloons
                    if max_progress <= bloon.progress:
                        self.target = bloon
                        max_progress = bloon.progress
    
    # Idea for movement in any direction taken from https://www.youtube.com/watch?v=3DeW-7vbc50&ab_channel=NealHoltschulte
    def spawn_projectile(self) -> None:
        """
        Adds a new projectile to the active projectile list, considering that it should move in a straight
        line to the found target.
        """
        if self.target is not None:
            angle = - (math.atan2(self.target.x - self.x, self.target.y - self.y) - math.pi/2)
            dx = math.cos(angle)
            dy = math.sin(angle)
            new_projectile = Projectile(self.x, self.y, self.projectile_speed, dx, dy, self.pierce, self.projectile_lifespan_frames)
            self.projectile_list.append(new_projectile)
    
    def remove_projectile(self, projectile) -> None:
        """
        Removes a projectile from the active projectile list.
        """
        self.projectile_list.remove(projectile)

    def update_attack_counter(self) -> None:
        """
        Updates the attack counter for the purpose of managing the attack cooldowns.
        """
        if self.attack_counter >= self.attack_cooldown_frames and self.target is not None:
            self.attack_counter = 1
        elif self.attack_counter < self.attack_cooldown_frames:
            self.attack_counter += 1
        else:
            pass

    def shoot(self, bloon_list: List[Bloon]) -> None:
        """
        Shoots a projectile at the suitable target (combines finding the target and spawning the projectile).
        :param bloon_list: list of active bloons.
        """
        if self.attack_counter >= self.attack_cooldown_frames:
            self.find_target(bloon_list)
            self.spawn_projectile()
            
    def move_projectiles(self) -> None:
        """
        Moves all active projectiles shot by the tower. Also manages projectile removal if they reach the end
        of their lifespan.
        """
        for projectile in self.projectile_list: 
            if projectile.lifespan_counter <= projectile.lifespan_frames:
                projectile.move()
            else:
                self.remove_projectile(projectile)
    
    def check_for_projectile_collisions(self, bloon_manager: BloonManager) -> None:
        """
        Checks if an active projectile has collided with anything.
        :param bloon_manager: Bloon Manager object used in the game. 
        """
        for projectile in self.projectile_list:
            hit_something = projectile.collide(bloon_manager)
            if hit_something:
                # Manage how many bloons can be pierced still
                projectile.pierce -= 1
                # Increment pops by the number of pops of the projectile
                self.pops += projectile.pops
                # Remove projectile if cannot pierce more
                if projectile.pierce <= 0:
                    self.remove_projectile(projectile)
    
    def get_upgrade_1(self):
        """
        Template for buying upgrade 1 for the tower.
        """
        self.upgrade1 = True
    
    def get_upgrade_2(self):
        """
        Template for buying upgrade 2 for the tower.
        """
        self.upgrade2 = True

    def __repr__(self) -> str:
        return(f"{self.name}Tower(pos:({self.x}, {self.y}), up1: {self.upgrade1}, up2: {self.upgrade2}, pops: {self.pops})")

    
class DartTower(Tower):
    """
    Represents a Dart Tower in Bloons TD.
    """
    def __init__(self, x, y):
        tower_type = 'Dart'
        super().__init__(
            tower_type, x, y, 
            footprint_radius = Tower.DF_TOWERS.loc[tower_type, "footprint_radius"], 
            attack_cooldown_frames =  Tower.DF_TOWERS.loc[tower_type, "attack_cooldown_frames"],
            cost = Tower.DF_TOWERS.loc[tower_type, "cost"], 
            cost_upgrade_1 = Tower.DF_TOWERS.loc[tower_type, "upgrade_1_cost"], 
            cost_upgrade_2 = Tower.DF_TOWERS.loc[tower_type, "upgrade_2_cost"], 
            range_ = Tower.DF_TOWERS.loc[tower_type, "range"], 
            projectile_speed = Tower.DF_TOWERS.loc[tower_type, "projectile_speed"], 
            projectile_lifetime_frames = Tower.DF_TOWERS.loc[tower_type, "projectile_lifespan_frames"], 
            colors = [Tower.DF_TOWERS.loc[tower_type, "color_outer"], Tower.DF_TOWERS.loc[tower_type, "color_inner"]]
        )
    
    def get_upgrade_1(self):
        """
        Gets upgrade 1 for Dart Tower (increases pierce by 1).
        """
        if not self.upgrade1: 
            super().get_upgrade_1()
            self.pierce = 2
    
    def get_upgrade_2(self):
        """
        Gets upgrade 2 for Dart Tower (increases range).
        """
        if not self.upgrade2:
            super().get_upgrade_2()
            self.range = Tower.DF_TOWERS.loc[self.name, "upgrade_2_range"]
            # Also adjust range circle
            self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])


class SuperMonkeyTower(Tower):
    """
    Represents a Super Monkey Tower in Bloons TD.
    """
    def __init__(self, x, y):
        tower_type = 'Super Monkey'
        super().__init__(
            tower_type, x, y, 
            footprint_radius = Tower.DF_TOWERS.loc[tower_type, "footprint_radius"], 
            attack_cooldown_frames =  Tower.DF_TOWERS.loc[tower_type, "attack_cooldown_frames"],
            cost = Tower.DF_TOWERS.loc[tower_type, "cost"], 
            cost_upgrade_1 = Tower.DF_TOWERS.loc[tower_type, "upgrade_1_cost"], 
            cost_upgrade_2 = Tower.DF_TOWERS.loc[tower_type, "upgrade_2_cost"], 
            range_ = Tower.DF_TOWERS.loc[tower_type, "range"], 
            projectile_speed = Tower.DF_TOWERS.loc[tower_type, "projectile_speed"], 
            projectile_lifetime_frames = Tower.DF_TOWERS.loc[tower_type, "projectile_lifespan_frames"], 
            colors = [Tower.DF_TOWERS.loc[tower_type, "color_outer"], Tower.DF_TOWERS.loc[tower_type, "color_inner"]]
        )

    def get_upgrade_1(self):
        """
        Super Monkey Tower has only one upgrade, so does nothing.
        """
        pass

    def get_upgrade_2(self):
        """
        Gets upgrade 2 for Dart Tower (increases range).
        """
        if not self.upgrade2:
            self.range = Tower.DF_TOWERS.loc[self.name, "upgrade_2_range"]
            # Also adjust range circle
            self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])


class TackTower(Tower):
    """
    Represents a Tack Tower in Bloons TD.
    """
    def __init__(self, x, y):
        tower_type = 'Tack'
        super().__init__(
            tower_type, x, y, 
            footprint_radius = Tower.DF_TOWERS.loc[tower_type, "footprint_radius"], 
            attack_cooldown_frames =  Tower.DF_TOWERS.loc[tower_type, "attack_cooldown_frames"],
            cost = Tower.DF_TOWERS.loc[tower_type, "cost"], 
            cost_upgrade_1 = Tower.DF_TOWERS.loc[tower_type, "upgrade_1_cost"], 
            cost_upgrade_2 = Tower.DF_TOWERS.loc[tower_type, "upgrade_2_cost"], 
            range_ = Tower.DF_TOWERS.loc[tower_type, "range"], 
            projectile_speed = Tower.DF_TOWERS.loc[tower_type, "projectile_speed"], 
            projectile_lifetime_frames = Tower.DF_TOWERS.loc[tower_type, "projectile_lifespan_frames"], 
            colors = [Tower.DF_TOWERS.loc[tower_type, "color_outer"], Tower.DF_TOWERS.loc[tower_type, "color_inner"]]
        )
    
    def find_target(self, bloon_list: List[Bloon]) -> None:
        """
        Checks if there are any non-frozen Bloons in range.
        :param bloon_list: list of active bloons.
        """
        self.target = None
        for bloon in bloon_list:
            if is_point_in_circle(self.range_circle, bloon.x, bloon.y) and not bloon.frozen and not bloon.invulnerable: # don't target frozen bloons
                self.target = True
                return
    
    def spawn_projectile(self) -> None:
        "Spawns 8 projectiles, according to the shooting pattern of the Tack Tower."
        if self.target:
            for angle in (0, math.pi/4, math.pi/2, math.pi*3/4, math.pi, math.pi*5/4, math.pi*6/4, math.pi*7/4):
                dx = math.cos(angle)
                dy = math.sin(angle)
                new_projectile = Projectile(self.x, self.y, self.projectile_speed, dx, dy, self.pierce, self.projectile_lifespan_frames)
                self.projectile_list.append(new_projectile)
    
    def get_upgrade_1(self):
        """
        Gets upgrade 1 for Tack Tower (increases attack speed).
        """
        if not self.upgrade1:
            self.attack_cooldown_frames = 40
            self.attack_counter = self.attack_cooldown_frames
    
    def get_upgrade_2(self):
        """
        Gets upgrade 2 for Tack Tower (increases range).
        """
        if not self.upgrade2:
            self.range = Tower.DF_TOWERS.loc[self.name, "upgrade_2_range"]
            # Also adjust range circle
            self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])
            # Also adjust projectile lifespan
            self.projectile_lifespan_frames = 5
            

class BombTower(Tower):
    """
    Represents a Bomb Tower in Bloons TD.
    """
    def __init__(self, x, y):
        tower_type = 'Bomb'
        super().__init__(
            tower_type, x, y, 
            footprint_radius = Tower.DF_TOWERS.loc[tower_type, "footprint_radius"], 
            attack_cooldown_frames =  Tower.DF_TOWERS.loc[tower_type, "attack_cooldown_frames"],
            cost = Tower.DF_TOWERS.loc[tower_type, "cost"], 
            cost_upgrade_1 = Tower.DF_TOWERS.loc[tower_type, "upgrade_1_cost"], 
            cost_upgrade_2 = Tower.DF_TOWERS.loc[tower_type, "upgrade_2_cost"], 
            range_ = Tower.DF_TOWERS.loc[tower_type, "range"], 
            projectile_speed = Tower.DF_TOWERS.loc[tower_type, "projectile_speed"], 
            projectile_lifetime_frames = Tower.DF_TOWERS.loc[tower_type, "projectile_lifespan_frames"], 
            colors = [Tower.DF_TOWERS.loc[tower_type, "color_outer"], Tower.DF_TOWERS.loc[tower_type, "color_inner"]]
        )
        self.projectile_radius = 10
        self.projectile_explosion_radius = 50
    
    def find_target(self, bloon_list: List[Bloon]) -> None:
        """
        Find the bloon to shoot at. The target is defined to be the bloon in range that has reached the 
        furthest in the track and is non-frozen. Furthermore, Bomb Towers cannot target Black Bloons
        :param bloon_list: A list of active bloons.
        """
        self.target = None
        max_progress = 0
        if len(bloon_list) > 0:
            for bloon in bloon_list:
                if is_point_in_circle(self.range_circle, bloon.x, bloon.y) and bloon.type != "K" and not bloon.invulnerable: # Bomb Towers cannot target black bloons
                    if max_progress <= bloon.progress:
                        self.target = bloon
                        max_progress = bloon.progress

    def spawn_projectile(self) -> None:
        """
        Adds a new Bomb to the active projectile list, considering that it should move in a straight
        line to the found target.
        """
        if self.target is not None:
            angle = - (math.atan2(self.target.x - self.x, self.target.y - self.y) - math.pi/2)
            dx = math.cos(angle)
            dy = math.sin(angle)
            new_projectile = Bomb(self.x, self.y, self.projectile_speed, dx, dy, self.pierce, self.projectile_lifespan_frames, self.projectile_radius, self.projectile_explosion_radius)
            self.projectile_list.append(new_projectile)
    
    def get_upgrade_1(self) -> None:
        """
        Gets upgrade 1 for Bomb Tower (increases projectise size and explosion radius).
        """
        if not self.upgrade1:
            super().get_upgrade_1()
            self.projectile_radius = int(self.projectile_radius*1.5)
            self.projectile_explosion_radius = int(self.projectile_explosion_radius*1.5)
    
    def get_upgrade_2(self) -> None:
        """
        Gets upgrade 1 for Bomb Tower (increases range).
        """
        if not self.upgrade2:
            super().get_upgrade_2()
            self.range = Tower.DF_TOWERS.loc[self.name, "upgrade_2_range"]
            # Also adjust range circle
            self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])


class IceTower(Tower):
    """
    Represents an Ice Tower in Bloons TD.
    """
    def __init__(self, x, y):
        tower_type = 'Ice'
        super().__init__(
            tower_type, x, y, 
            footprint_radius = Tower.DF_TOWERS.loc[tower_type, "footprint_radius"], 
            attack_cooldown_frames =  Tower.DF_TOWERS.loc[tower_type, "attack_cooldown_frames"],
            cost = Tower.DF_TOWERS.loc[tower_type, "cost"], 
            cost_upgrade_1 = Tower.DF_TOWERS.loc[tower_type, "upgrade_1_cost"], 
            cost_upgrade_2 = Tower.DF_TOWERS.loc[tower_type, "upgrade_2_cost"], 
            range_ = Tower.DF_TOWERS.loc[tower_type, "range"], 
            projectile_speed = Tower.DF_TOWERS.loc[tower_type, "projectile_speed"], 
            projectile_lifetime_frames = Tower.DF_TOWERS.loc[tower_type, "projectile_lifespan_frames"], 
            colors = [Tower.DF_TOWERS.loc[tower_type, "color_outer"], Tower.DF_TOWERS.loc[tower_type, "color_inner"]]
        )
        self.freeze_duration_frames = 50
    
    def find_target(self, bloon_list: list[Bloon]):
        """
        Finds up to 20 bloons in range.
        :param bloon_list: List of active bloons
        """
        self.target = []
        bloons_in_freeze = 0
        if len(bloon_list) > 0: 
            for bloon in bloon_list:
                if is_circle_overlapping(self.range_circle, bloon.circle) and bloons_in_freeze < 20 and bloon.type != 'W' and not bloon.invulnerable: # Ice Towers cannot target white bloons
                    self.target.append(bloon)
                    bloons_in_freeze += 1
    
    def spawn_projectile(self):
        """
        Ice Towers don't use projectiles.
        """
        pass

    def move_projectiles(self):
        """
        Ice Towers don't use projectiles.
        """
        pass

    def check_for_projectile_collisions(self, bloon_manager):
        """
        Ice Towers don't use projectiles.
        """
        pass

    def update_attack_counter(self) -> None:
        """
        Updates the attack counter for the purpose of managing the attack cooldowns.
        """
        if self.attack_counter >= self.attack_cooldown_frames and len(self.target) > 0:
            self.attack_counter = 1
        elif self.attack_counter < self.attack_cooldown_frames:
            self.attack_counter += 1
        else:
            pass

    def shoot(self, bloon_list):
        """
        Freezes all bloons in the target list.
        """
        if self.attack_counter >= self.attack_cooldown_frames:
            self.find_target(bloon_list)
            if self.target is not None:
                for bloon in self.target:
                    bloon.freeze(self.freeze_duration_frames)
    
    def get_upgrade_1(self):
        """
        Gets upgrade 1 for Ice Tower (increases freeze duration).
        """
        if not self.upgrade1:
            super().get_upgrade_1()
            self.freeze_duration_frames = 70
    
    def get_upgrade_2(self):
        """
        Gets upgrade 2 for Ice Tower (increases range).
        """
        if not self.upgrade2:
            super().get_upgrade_2()
            self.range = Tower.DF_TOWERS.loc[self.name, "upgrade_2_range"]
            # Also adjust range circle
            self.range_circle = Circle((220, 220, 220), self.range, [self.x, self.y])

        
class TowerManager:
    """
    Manages spawns and upgrades of towers from a list in the right rounds, and makes updates to towers if necessary.
    """
    def __init__(self, queue_all_rounds: Dict, initial_round_nr: int = 1):
        self.round_nr = initial_round_nr
        self.queue_all_rounds = queue_all_rounds

        self.tower_list = []
        self.position_tower_map = {}
        self.current_queue = self.queue_all_rounds[self.round_nr]
        self.pops_sum = 0
    
    def upgrade_tower_at_position(self, tower_x: int, tower_y: int, upgrade_type: int) -> None:
        """
        Upgrades tower positioned at (x, y)
        :param tower_x: x coord of the tower
        :param tower_y: y coord of the tower
        :param upgrade_type: 1 for upgrade 1, 2 for upgrade 2
        """
        tower = self.position_tower_map[(tower_x, tower_y)]
        if upgrade_type == 1:
            tower.get_upgrade_1()
        else:
            tower.get_upgrade_2()
    
    def perform_action_from_queue(self) -> int:
        """
        For the current queue (queue for the current round), pop the first element and resolve its action.
        It can either be a tower (and then the tower will be built), or an upgrade for a tower (in this case
        a tower will be upgraded). Format of action: (tower_name, pos, action_type), with tower_name a string 
        (e.g. 'Dart'), pos a tuple of integers representing the tower position and action_type an integer 
        (0 for build, 1 for upgrade 1, 2 for upgrade 2).
        :returns: cost in money of the action
        """
        out_cost = 0
        action = self.current_queue.pop(0)
        tower_name = action[0]
        pos = action[1]
        action_type = action[2]
        if action_type == 0:
            new_tower = convert_name_to_tower(tower_name, pos)
            self.tower_list.append(new_tower)
            self.position_tower_map[(new_tower.x, new_tower.y)] = new_tower
            out_cost += new_tower.cost
        elif action_type == 1:
            upgraded_tower = self.position_tower_map[pos]
            self.upgrade_tower_at_position(upgraded_tower.x, upgraded_tower.y, action_type)
            if action_type == 1:
                out_cost += upgraded_tower.cost_upgrade_1
            elif action_type == 2:
                out_cost += upgraded_tower.cost_upgrade_2
        return out_cost

    def resolve_queue_in_round(self) -> int:
        """
        Resolve the entire queue for the current round.
        :returns: a total cost of the actions defined for the current round
        """
        out_cost = 0
        for _ in range(len(self.current_queue)):
            out_cost += self.perform_action_from_queue()
        return out_cost

    def update_all_towers(self, bloon_manager: BloonManager) -> None:
        """
        Updates the behaviour of all towers for the given round.
        """
        for tower in self.tower_list:
            tower.shoot(bloon_manager.bloon_list)
            tower.update_attack_counter()
            tower.move_projectiles()    
            tower.check_for_projectile_collisions(bloon_manager)
    
    def update_pops(self) -> None:
        """
        Updates self.pops_sum.
        """
        self.pops_sum = 0
        for tower in self.tower_list:
            self.pops_sum += tower.pops
    
    def draw_all_towers(self, screen) -> None:
        """
        Draws all active towers and their projectiles.
        :param screen: a pygame.Surface object to draw on
        """
        for tower in self.tower_list:
            tower.draw(screen)

    def prepare_current_queue(self):
        """
        Resolves the change of the round without updating pops.
        """
        self.current_queue = self.queue_all_rounds[self.round_nr]

    def next_round(self):
        """
        Resolves the change of the round.
        """
        self.round_nr += 1
        self.current_queue = self.queue_all_rounds[self.round_nr]
        self.update_pops()

def convert_name_to_tower(tower_name: str, pos: Tuple[int, int]) -> Tower:
    """
    Converts a tower name to a Tower object.
    :param tower_name: name of the tower (e.g. 'Dart')
    :param pos: position of the tower, (x,y)
    :returns: the created Tower object
    """
    if tower_name == 'Dart':
        return DartTower(pos[0], pos[1])
    elif tower_name == 'Tack':
        return TackTower(pos[0], pos[1])
    elif tower_name == 'Bomb':
        return BombTower(pos[0], pos[1])
    elif tower_name == 'Ice':
        return IceTower(pos[0], pos[1])
    elif tower_name == 'SuperMonkey':
        return SuperMonkeyTower(pos[0], pos[1])
    else:
        raise ValueError(f"Conversion from name to Tower object impossible (no tower with name {tower_name} exists)")


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
        self.last_bloon_struck = None
        self.pops = 0
        
    def draw(self, screen) -> None:
        self.circle.draw(screen, outline=False)

    # Idea for movement in any direction taken from https://www.youtube.com/watch?v=3DeW-7vbc50&ab_channel=NealHoltschulte
    def move(self) -> None:
        """
        Moves the projectile in the predefined direction.
        """
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
        :param bloon_manager: a BloonManager object used in the game
        :returns: True if the collision has occured; False otherwise
        """
        hit_bloon = None
        bloon_list = bloon_manager.bloon_list
        if len(bloon_list) > 0:
            for bloon in bloon_list:
                if is_circle_overlapping(bloon.circle, self.circle) and not self.last_bloon_struck == bloon and not bloon.invulnerable:
                    hit_bloon = bloon
                    self.last_bloon_struck = bloon
                    break
            if hit_bloon is not None:
                if not hit_bloon.frozen:
                    bloon_manager.resolve_bloon_hit(hit_bloon)
                    self.pops += 1
                    
                return True
        return False


class Bomb(Projectile):
    """
    Represents a Bomb (projectile used by Bomb Tower).
    """
    def __init__(self, x, y, speed, dx, dy, pierce, lifespan_frames, radius, explosion_radius):
        super().__init__(x, y, speed, dx, dy, pierce, lifespan_frames)
        self.radius = radius
        self.explosion_radius = explosion_radius

        self.circle = Circle((255, 102, 0), self.radius, [self.x, self.y])
        
    def find_bloons_in_explosion(self, bloon_list: List[Bloon]) -> List[Bloon]:
        """
        Finds bloons caught in the explosion of the bomb that occurs upon collision.
        :param bloon_list: list of active bloons
        :returns: list of bloons caught in explosion
        """
        hit_bloons = []
        explosion_circle = Circle((255, 102, 0), self.explosion_radius, [self.x, self.y])
        bloons_in_explosion = 0
        for bloon in bloon_list:
            if is_circle_overlapping(bloon.circle, explosion_circle) and bloons_in_explosion < 20 and bloon.type != 'K' and not bloon.invulnerable:
                hit_bloons.append(bloon)
                bloons_in_explosion += 1
        return hit_bloons
    
    def collide(self, bloon_manager: BloonManager) -> bool:
        """
        Checks for collision with bloons; also manages explosion behaviour. 
        :param bloon_manager: BloonManager object used in the game
        :returns: True if the collision has occured; False otherwise
        """
        bloons_in_explosion = []
        bloon_list = bloon_manager.bloon_list
        if len(bloon_list) > 0:
            for bloon in  bloon_list:
                if is_circle_overlapping(bloon.circle, self.circle) and not bloon.invulnerable:
                    bloons_in_explosion = self.find_bloons_in_explosion(bloon_list)
                    break

            if len(bloons_in_explosion) > 0:
                for hit_bloon in bloons_in_explosion:
                    hit_bloon.reset_freeze() # reset bloon freeze upon being damaged by a Bomb.
                    bloon_manager.resolve_bloon_hit(hit_bloon)
                    self.pops += 1
                    
                return True
        return False
    