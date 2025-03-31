import pandas as pd
from typing import List, Tuple, Dict, Any

def create_bloons_dataframe(red_bloon_speed: float) -> pd.DataFrame:
    bloon_type = ['R', 'B', 'G', 'Y', 'W', 'K']
    bloon_name = ['Red', 'Blue', 'Green', 'Yellow', 'White', 'Black']
    bloon_health = [1,2,3,4,5,5]
    bloon_rgb = [(255, 0, 0), (0,0, 255),(0, 255, 0),(255,255,0),(255,255,255),(0,0,0)]
    bloon_relative_speed = [1,1.4,1.8,3.2,2,1.8] # speed relative to Red Bloon speed
    bloon_damage = [1,2,3,4,9,9]
    bloons_dataset = pd.DataFrame(
        {
            'type': bloon_type, 
            'name': bloon_name, 
            'health': bloon_health,
            'rgb': bloon_rgb,
            'relative_speed': bloon_relative_speed,
            'damage': bloon_damage
            }
        )
    # Get the real speed by using the relative speed; round to get integer speeds
    bloons_dataset['speed'] = round(bloons_dataset['relative_speed']*red_bloon_speed)
    bloons_dataset['speed'] = bloons_dataset['speed'].astype(int)

    # Set index to be Bloon type
    bloons_dataset.set_index('type',inplace=True)

    return bloons_dataset

def create_pathline() -> List:
    return [
        (-10,230), (95,230), (95, 100), (210,100), (210,350), 
        (55,350), (55,430), (425,430), (425,300), (305,300), 
        (305,185), (430,185), (430,55), (265,55), (265,-10)
        ]
     
def create_rounds_dataframe() -> pd.DataFrame:
    rounds_raw = pd.read_csv("data\\rounds.csv",  encoding='unicode_escape')
    # Clean the data
    rounds_raw['description'] = rounds_raw['description'].replace(",", "", regex=True)
    rounds_raw['description'] = rounds_raw['description'].replace("\xa0", " ", regex=True)
    # Transform description to list with numbers and types
    rounds_raw['bloons_info'] = rounds_raw['description'].str.split(" ")
    
    def process_bloons_info(bloons_info_line: pd.Series, bloon_type: str) -> int:
        for i in range(0, len(bloons_info_line), 2):
            bloon_nr = bloons_info_line[i]
            bloon_type_in_list = bloons_info_line[i+1]
            if bloon_type_in_list == bloon_type:
                return bloon_nr
        return 0

    for color in ['Red', 'Blue', 'Green', 'Yellow', 'White', 'Black']:
        rounds_raw[color] = rounds_raw['bloons_info'].apply(process_bloons_info, args=(color,))

    
    # Rename Columns
    rename_mapper = {'Red':'R', 'Blue':'B', 'Green':'G', 'Yellow':'Y', 'White':'W', 'Black':'K'}
    rounds = rounds_raw.rename(columns=rename_mapper).copy()
    # Keep only relevant columns
    rounds = rounds.drop(['description', 'bloons_info'], axis = 1).copy()
    # Add data on money gained at the end of each round
    rounds['money_round_end'] = rounds['money_total'] - rounds['money_popping_max'] 
    rounds.loc[6,'money_round_end'] = 94 # manual correction needed
    # Set index to be round nr
    rounds.set_index('round', inplace=True)

    return rounds

def create_towers_dataframe() -> pd.DataFrame:
    tower_name = ['Dart', 'Tack', 'Ice', 'Bomb', 'Super Monkey']
    tower_cost = [250, 320, 850, 720, 4000]
    tower_upgrade_1_cost = [210, 250, 450, 650, 0]
    tower_upgrade_2_cost = [100, 150, 300, 250, 2400]
    tower_range = [100, 70, 60, 120, 140]
    tower_upgrade_2_range = [125, 80, 70, 140, 240]
    tower_attack_cooldown_frames = [29, 55, 100, 55, 2]
    tower_footprint_radius = [10,10,10,10, 15] 
    projectile_speed = [20, 15, pd.NA, 11, 20]
    projectile_lifespan_frames = [7, 4, pd.NA, 18, 20] # For Tack set to 4 instead of 5 to better reflect its in-game range without the range upgrade (set to 5 after upgrade)
    color_outer = [(123, 63, 0), (255, 182, 193), (255, 255, 255),(211, 211, 211), (100, 149, 237)]
    color_inner = [(234, 221, 202), (211, 211, 211), (240, 255, 255),(0,0,0), (220, 20, 60)]
    
    
    towers_dataset = pd.DataFrame(
        {
            "name" : tower_name,
            "cost": tower_cost,
            "upgrade_1_cost": tower_upgrade_1_cost,
            "upgrade_2_cost": tower_upgrade_2_cost,
            "range": tower_range,
            "upgrade_2_range": tower_upgrade_2_range,
            "attack_cooldown_frames" : tower_attack_cooldown_frames,
            "footprint_radius" : tower_footprint_radius,
            "projectile_speed" : projectile_speed,
            "projectile_lifespan_frames" : projectile_lifespan_frames,
            "color_outer": color_outer,
            "color_inner" : color_inner
        }
    )

    # Add cumulative cost information
    # towers_dataset['cumulative_cost_upgrade_1'] = towers_dataset['cost'] + towers_dataset['upgrade_1_cost']
    # towers_dataset['cumulative_cost_upgrade_2'] = towers_dataset['cost'] + towers_dataset['upgrade_2_cost']
    # towers_dataset['cumulative_cost'] = towers_dataset['cost'] + towers_dataset['upgrade_1_cost'] + towers_dataset['upgrade_2_cost']

    # Set index to be Bloon type
    towers_dataset.set_index('name', inplace=True)

    return towers_dataset
