# Bachelor End Project

This repository contains the source code for my Bachelor End Project: " Deriving Strategies for Bloons Tower Defense with Integer Linear Programming".

The source code for the game simulation are files: 
- Bloon.py
- datasets.py
- Game.py
- main.py
- Tower.py
- utils.py
- BTD1_Map.png, found in the assets folder
  
Simulation is run through main function in main.py . 

The source code for the game analysis (ILP modelling) are files:
- experiments.py
- GameHeuristic.py
- modelling.py
- modelling_sets.py
- modelling_utils.py

The ILP modelling also requires the files for the game simulation. To run the analysis for certain strategies, use dedicated functions in experiments.py . Sometimes, you may first need to generate sets with modelling_sets.py .

Some visualisations present in the thesis were generated using modelling_vis.py .
