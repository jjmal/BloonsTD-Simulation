import pygame

from Game import Game
from Bloon import BloonManager
from Tower import DartTower, BombTower, IceTower, SuperMonkeyTower, TackTower, Tower
from utils import draw_rect_alpha
from typing import List


#  # Set screen parameters
# width = 640
# height = 480
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Bloons TD Simulation")

# # Load background image and surface
# background_graphic = pygame.image.load("assets\\maps\\BTD1_Map.png").convert_alpha()

# # Draw the backgrounds
# screen.blit(background_graphic, (0, 0))
# pygame.display.update()

# # Set up the clock
# clock = pygame.time.Clock()


# # game loop info
# run = True
# FPS = 40*0.5

# # Prepare the right-side rectangle to render
# right_side_rect = pygame.Rect(480, 0, 160, 480)

# # Round preparation
# bloon_manager = BloonManager(45)
# bloon_manager.prepare_queue_for_round()
# bloon_manager.shuffle_queue()
# bloons_spawn_line = 20
# towers: List[Tower] = []
# towers.append(DartTower(150,385))
# towers.append(SuperMonkeyTower(385,385))
# towers.append(IceTower(250,250))
# towers.append(BombTower(250,200))
# towers.append(TackTower(125,150))
# towers[0].get_upgrade_1()
# towers[0].get_upgrade_2()


# # Spawn initial bloon
# if bloon_manager.queue:
#     last_spawned_bloon = bloon_manager.spawn_bloon_from_queue()

# while run:
#     # Event loop
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False

#     ## Background rendering
#     screen.blit(background_graphic, (0, 0))
#     draw_rect_alpha(screen, (220,220,220,175), right_side_rect)

#     ## Spawning

#     # Spawn bloon from queue
#     if last_spawned_bloon.x >= bloons_spawn_line:
#         if bloon_manager.queue:
#             last_spawned_bloon  = bloon_manager.spawn_bloon_from_queue()

#     ## Movement

#     # Move bloons
#     bloon_manager.move_all_bloons()
#     bloon_manager.update_freeze_all_bloons()
    
#     # Test Towers
#     for tower in towers:
#         tower.shoot(bloon_manager.bloon_list)
#         tower.update_attack_counter()
#         tower.move_projectiles()    
#         tower.check_for_projectile_collisions(bloon_manager)
        
#     ## Drawing
#     for tower in towers:
#         tower.draw(screen)
#     bloon_manager.draw_all_bloons(screen)

#     # Update display
#     pygame.display.update()

#     clock.tick(FPS)
    

# pygame.quit()


width = 640
height = 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bloons TD Simulation")

run = True
while run:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.draw.circle(screen, (100,0,0), (225,225), 50, 1) 
    pygame.display.update()
pygame.quit()
