import pygame
import sys
import math
import random


class Tower:
    def __init__(self, name, x, y, damage, attacks_per_second):
        self.name = name
        self.x = x
        self.y = y
        self.transformou = False
        self.makeup = 0
        self.damage = damage
        self.pierce = 2
        self.rotation = 0
        self.range = 100  # New attribute
        self.pops = 0
        self.upgrade1 = False
        self.upgrade2 = False
        self.projectiles = []
        # self.spritedart = pygame.image.load("sprites\Monkeys\darts\dart.png").convert_alpha()
        # self.sprite = dart_monkey_sprite
        # self.sprite_original = self.sprite
        self.attacks_per_second = attacks_per_second
        self.attack_timer = 0
        self.rect = self.sprite.get_rect()
    
    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))
        for projectile in self.projectiles:  # New code
            projectile.draw()

    def find_target(self, value):
        min_distance = float("inf")
        target = None
        if len(Bloons) > 0:
            primeiro = Bloons[0]
            for value in Bloons:
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
        
    