import pandas as pd
from typing import List, Tuple, Dict, Any

def create_bloons_dataframe(red_bloon_speed: float) -> pd.DataFrame:
    bloon_type = ['R', 'B', 'G', 'Y', 'W', 'K']
    bloon_name = ['Red', 'Blue', 'Green', 'Yellow', 'White', 'Black']
    bloon_health = [1,2,3,4,5,5]
    bloon_rgb = [(255, 0, 0), (0,0, 255),(0, 255, 0),(255,255,0),(255,255,255),(0,0,0)]
    bloon_relative_speed = [1,1.4,1.8,3.2,2,1.8] # speed relative to Red Bloon speed
    bloons_ice_resist = [0,0,0,0,1,0]
    bloon_bomb_resist = [0,0,0,0,0,1]
    bloons_dataset = pd.DataFrame(
        {
            'type': bloon_type, 
            'name': bloon_name, 
            'health': bloon_health,
            'rgb': bloon_rgb,
            'relative_speed': bloon_relative_speed,
            'ice_resistant': bloons_ice_resist,
            'bomb_resistant': bloon_bomb_resist
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
        (-20,400), (170,400), (170, 175), (375,175), (375,615), 
        (95, 615), (95, 760), (755, 760), (755, 525), (540, 525), 
        (540, 330), (755, 330), (755, 95), (465, 95), (465, 20)
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

def create_tower_dataframe() -> pd.DataFrame:
    pass
