import pandas as pd
from typing import List, Tuple

def create_bloons_dataset(red_bloon_speed: float) -> pd.DataFrame:
    bloon_type = ['R', 'B', 'G', 'Y', 'W', 'K']
    bloon_name = ['Red', 'Blue', 'Green', 'Yellow', 'White', 'Black']
    bloon_health = [1,2,3,4,5,5]
    bloon_rgb = [(255, 0, 0), (0,0, 255),(0, 255, 0),(255,255,0),(255,255,255),(0,0,0)]
    bloon_relative_speed = [1,1.4,1.8,3.2,2,1.8] # speed relative to Red Bloon speed
    bloons_ice_resits = [0,0,0,0,1,0]
    bloon_bomb_resist = [0,0,0,0,0,1]
    bloons_dataset = pd.DataFrame(
        {
            'type': bloon_type, 
            'name': bloon_name, 
            'health': bloon_health,
            'rgb': bloon_rgb,
            'relative_speed': bloon_relative_speed,
            'ice_resistant': bloons_ice_resits,
            'bomb_resistant': bloon_bomb_resist
            }
        )
    bloons_dataset['speed'] = bloons_dataset['relative_speed']*red_bloon_speed
    bloons_dataset.set_index('type',inplace=True)
    return bloons_dataset

def create_pathline() -> List:
    return [
        (0,400), (170,400), (170, 175), (375,175), (375,615), 
        (95, 615), (95, 760), (755, 760), (755, 525), (540, 525), 
        (540, 330), (755, 330), (755, 95), (465, 95), (465, 0)
        ]
    
    

def create_rounds_dataset() -> pd.DataFrame:
    pass

def create_tower_dataframe() -> pd.DataFrame:
    pass