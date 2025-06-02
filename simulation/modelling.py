import re
import random
import numpy as np
import pandas as pd

from datetime import datetime
from typing import List, Tuple, Dict, Any
from datetime import datetime
from gurobipy import Model, GRB, quicksum
from datasets import create_towers_dataframe, create_rounds_dataframe
from modelling_sets import  get_money_constraint_rhs, generate_sets_1a, generate_sets_1b, generate_sets_1c, \
      generate_sets_2a, generate_sets_2b, generate_sets_2c, generate_sets_3
from modelling_utils import read_pickle, write_pickle, filter_point_set_modulo
from Game import Game, prepare_tower_queue
 
class GameModel:
    """
    Template class for models that will derive the solutions for the game.
    """
    def __init__(self, name: str, modulo: int, logging: bool = True):
        self.name = name
        self.modulo = modulo
        self.model = Model(name=name)
        self.logging = logging

        self.objective_function = None

    def generate_sets(self):
        pass

    def set_variables(self):
        pass

    def set_objective(self):
        pass

    def set_constraints(self):
        pass

    def build(self):
        self.generate_sets()
        self.set_variables()
        self.set_objective()
        self.set_constraints()

    def solve(self):
        self.model.optimize()
    
    def get_results(self) -> Dict[str, Any]:
        objective_value = self.model.ObjVal
        chosen_positions_name_list = []
        for var in self.model.getVars():
            if int(var.X) == 1:
                chosen_positions_name_list.append(var.VarName)
        chosen = self.extract_vars_from_gurobi(chosen_positions_name_list)

        out = {}
        out['objective_value'] = objective_value
        out['choices'] = chosen
        out['parameters'] = self.get_parameters()
        out['mipgap'] = self.model.MIPGap

        # Save result as pickle, if Model is not Model 1 (as for Model 1 we care about the final result after 50 models are run)
        if self.name != 'Model1':
            name = f"{self.name}{self.type}_mod{self.modulo}_m{self.human_strategy_cost}_a{self.scaling_bracket[0]}"
            if self.money_correction > 0:
                name = name + f"_mc{self.money_correction}_{datetime.now().strftime("%Y%m%d-%H%M%S")}"
            write_pickle(out, name , True)
            

        return out 
    
    def run(self) -> Dict[str, Any]:
        self.build()
        if self.logging:
            print('BEGIN SOLVING')

        self.solve()
        if self.logging:
            print('MODEL DONE')
        
        return self.get_results()
    
    def get_parameters(self):
        pass

    def save_model(self):
        self.model.write(f"{self.name}.lp")

    @staticmethod
    def extract_vars_from_gurobi(var_name_list: List[str]) -> List[Tuple]:
        pass
    

class Model1(GameModel):
    """
    Represents a model that maximises some kind of coverage as an objective function, and only places Dart Towers. 
    (Maximize Coverage, Dart Tower Only, No Upgrades)
    """
    def __init__(self, modulo: int, type_: str, scaling_bracket: Tuple[float, float] = (0,1), dart_monkey_nr: int = 37, logging = True):
        super().__init__('Model1', modulo, logging)
        self.type = type_
        self.dart_monkey_nr = dart_monkey_nr
        self.scaling_bracket = scaling_bracket

    def generate_sets(self):
        if self.type == 'a':
            sets = generate_sets_1a(self.modulo)
            self.COVERAGE = sets['COV']
        
        elif self.type == 'b':
            sets = generate_sets_1b(self.modulo, self.scaling_bracket)
            self.DISTANCE = sets['DIST']

        elif self.type == 'c':
            sets = generate_sets_1c(self.modulo, self.scaling_bracket)
            self.ANGLE_COVERAGE = sets['ANG_COV']
                
        self.TOWER_PLACEMENTS = sets['TP']
        self.FOOTPRINTS = sets['FP']

    def set_variables(self):
        # Define variables
        self.varss = self.model.addVars(
            self.TOWER_PLACEMENTS, 
            name='tower-placement',
            vtype=GRB.BINARY
            )
        self.model.update()

    def set_objective(self):
        # Define the objective function
        if self.type == 'a':
            obj = quicksum(
                self.COVERAGE[pos, 'Dart', 0] * self.varss[pos] 
                for pos in self.TOWER_PLACEMENTS
                )

        elif self.type == 'b':
            obj = quicksum(
                self.DISTANCE[pos, 'Dart', 0]* self.varss[pos] 
                for pos in self.TOWER_PLACEMENTS
            )
        
        elif self.type == 'c':
            obj = quicksum(
                self.ANGLE_COVERAGE[pos, 'Dart', 0]* self.varss[pos] 
                for pos in self.TOWER_PLACEMENTS
            )

        self.objective_function = obj

        # Set the objective function
        self.model.setObjective(
            obj,
            sense=GRB.MAXIMIZE
        )

        # Update model
        self.model.update()
    
    def set_constraints(self):
        # CONSTRAINT 1 - towers cannot be placed inside other towers' footprints
        self.model.addConstrs(
            (self.varss[unavailable_point] + self.varss[pos] <= 1
            for pos in self.TOWER_PLACEMENTS for unavailable_point in self.FOOTPRINTS[pos] if pos != unavailable_point),
            name='footprints'
        )
        
        # CONSTRAINT 2 - We want a solution that does not use more Dart Towers than S1. Customizable, build 37 monkeys normally
        self.model.addConstr(
            quicksum(self.varss[pos] for pos in self.TOWER_PLACEMENTS) <= self.dart_monkey_nr
        )
        self.model.update()

    def get_parameters(self) -> Dict[str, Any]:
        out = {}
        out['name'] = self.name
        out['modulo'] = self.modulo
        out['type'] = self.type
        out['dart_monkey_nr'] = self.dart_monkey_nr
        out['scaling_bracket'] = self.scaling_bracket

        return out
        

    @staticmethod
    def extract_vars_from_gurobi(var_name_list: List[str]) -> List[Tuple]:
        """
        Extracts Tower positions from the Gurobi names given to the model variables.
        :param var_name_list: List of variables to perform extraction on
        """
        out = []
        for var_name in var_name_list:
            pos_str = re.search('\[.*\]', var_name).group(0).strip('[]')
            pos_str_sep = pos_str.split(",")
            pos = (int(pos_str_sep[0]), int(pos_str_sep[1]))
            out.append(pos)
        return out

    @staticmethod 
    def model1_per_round(modulo: int, type_: str, scaling_bracket: Tuple[int,int] = (0,1), dart_monkey_nr: int = 37, money_correction: Tuple[int, int] = (0,0)) -> Dict[int, List[Tuple[int,int]]]:
        """
        Runs Model 1 for each round, fixing previous choices.
        :param modulo: number for the divisibility filter
        :param type_: type of Model ('a', 'b', or 'c'), which determines the objective function
        :param money_correction: With an uncorrected model, the game can throws an error (not 
        enough money for the build) for some experiments as it by default does not account for lost lives. 
        This parameter set to (round_nr, money_amount) will subtract money_amount from available money,
        starting at roung round_nr.
        :returns: a Dict of the form (round_nr, choices) with round_nr being the round
        in which we perform Dart Tower Build actions specified in choices
        """
        fixed_points = []
        out = {}
        rounds = 50

        # Define sets:
        if type_ == 'a':
            sets = generate_sets_1a(modulo) 
            TP = sets['TP']
            COV = sets['COV']
            FP = sets['FP']
        elif type_ == 'b':
            sets = generate_sets_1b(modulo, scaling_bracket)
            TP = sets['TP']
            DIST = sets['DIST']
            FP = sets['FP']
        elif type_ == 'c':
            sets = generate_sets_1c(modulo, scaling_bracket)
            TP = sets['TP']
            ANG_COV = sets['ANG_COV']
            FP = sets['FP']
        else:
            raise ValueError('type_ must be one of: "a", "b", "c" ')

        for r in range(1, rounds + 1):
            # Get money for round r
            money = get_money_constraint_rhs(r)

            m = Model1(modulo, type_, (0,1), dart_monkey_nr, False)

            # Set sets
            if type_ == 'a':
                m.COVERAGE = COV
            elif type_ == 'b':
                m.DISTANCE = DIST
            elif type_ == 'c':
                m.ANGLE_COVERAGE = ANG_COV
            m.TOWER_PLACEMENTS = TP
            m.FOOTPRINTS = FP
            
            # Build baseline model
            m.set_variables()
            m.set_objective()
            m.set_constraints()

            # CONSTRAINT 3 - Money constraints per round
            if money_correction == (0,0):
                m.model.addConstr(quicksum(250*m.varss[pos] for pos in m.TOWER_PLACEMENTS) <= money)
            else:
                if r < money_correction[0]:
                    m.model.addConstr(quicksum(250*m.varss[pos] for pos in m.TOWER_PLACEMENTS) <= money)
                else:
                    print(f"printing money corrections: {money_correction[1]}")
                    m.model.addConstr(quicksum(250*m.varss[pos] for pos in m.TOWER_PLACEMENTS) <= money - money_correction[1])
                    
            # CONSTRAINT 4 - Points fixed in previous rounds must stay fixed
            if len(fixed_points) > 0:
                m.model.addConstrs(m.varss[fixed] == 1 for fixed in fixed_points)
            
            # Update model
            m.model.update()

            # Run model
            m.solve()

            # Get results
            d = m.get_results()
            choices = d['choices']

            # Update out
            out[r] = list(set(choices) - set(fixed_points))

            # Update fixed choices
            fixed_points = choices

            # Print progress
            print(f"Model progress: {r}/{rounds}")
        
        # Save result as pickle
        m = Model1(modulo, type_, scaling_bracket, dart_monkey_nr, False) # dummy model just to get the parameters
        params = m.get_parameters()
        params['money_correction'] = money_correction
        out['parameters'] = params
        # write_pickle(out, f"Model1{type_}_mod{modulo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", True)
        write_pickle(out, f"Model1{type_}_mod{modulo}_m{250*dart_monkey_nr}_a{scaling_bracket[0]}_d{money_correction[0]}-{money_correction[1]}", True)

        return out

    @staticmethod
    def model1_to_simulation(result_dict: Dict[int, List[Tuple[int,int]]]) -> List[Tuple]:
        out = []
        for key, val in result_dict.items():
            if len(val) > 0 and key != 'parameters':
                for pos in val:
                    out.append((key, ('Dart', pos, 0)))

        return out


class Model2(GameModel):
    """
    (Maximize coverage all rounds, Dart Monkey with upgrades)
    """
    def __init__(self, modulo, type_: str, money_correction: int = 0, chosen_lists: List = [], scaling_bracket: Tuple[int,int] = (0,1), human_strategy_cost: int = 9250, round_weights: List[float] = [0.02 for i in range(50)],  logging = True):
        super().__init__('Model2', modulo, logging)
        self.type = type_
        self.scaling_bracket = scaling_bracket
        self.human_strategy_cost = human_strategy_cost
        self.round_weights = round_weights
        self.money_correction = money_correction
        self.chosen_lists = chosen_lists
        
    def generate_sets(self):
        if self.type == 'a':
            sets = generate_sets_2a(self.modulo)
            self.COVERAGE = sets['COV']
        
        elif self.type == 'b':
            sets = generate_sets_2b(self.modulo, self.scaling_bracket)
            self.DISTANCE = sets['DIST']

        elif self.type == 'c':
            sets = generate_sets_2c(self.modulo, self.scaling_bracket)
            self.ANGLE_COVERAGE = sets['ANG_COV']
                
        VARIABLE_LIST = sets['VAR']
        self.ROUNDS = VARIABLE_LIST[0]
        self.TOWER_PLACEMENTS = VARIABLE_LIST[1]
        self.UPGRADES = VARIABLE_LIST[2]

        self.FOOTPRINTS = sets['FP']
        self.COST = sets['COST']
        self.MONEY = sets['MONEY']

    def set_variables(self):
        # Define variables
        self.varss = self.model.addVars(
            self.ROUNDS, self.TOWER_PLACEMENTS, self.UPGRADES,
            name='round-towerplacement-upgrade',
            vtype=GRB.BINARY
            )
        self.model.update()

    def set_objective(self):
        # Define the objective function
        if self.type == 'a':
            obj = quicksum(
                self.round_weights[r-1]*self.COVERAGE[(i,j), 'Dart', u]*self.varss[r, i,j, u] 
                for r in self.ROUNDS for i,j in self.TOWER_PLACEMENTS for u in self.UPGRADES
                )

        elif self.type == 'b':
            obj = quicksum(
                self.round_weights[r-1]*self.DISTANCE[(i,j), 'Dart', u] * self.varss[(r, i,j, u)] 
                for r in self.ROUNDS for i,j in self.TOWER_PLACEMENTS for u in self.UPGRADES
            )
        
        elif self.type == 'c':
            obj = quicksum(
                self.round_weights[r-1]*self.ANGLE_COVERAGE[(i,j), 'Dart', u] * self.varss[(r, i,j, u)] 
                for r in self.ROUNDS for i,j in self.TOWER_PLACEMENTS for u in self.UPGRADES
            )

        self.objective_function = obj

        # Set the objective function
        self.model.setObjective(
            obj,
            sense=GRB.MAXIMIZE
        )

        # Update model
        self.model.update()

    def set_constraints(self):
        # CONSTRAINT 1 - towers cannot be placed inside other towers' footprints
        self.model.addConstrs(
            (self.varss[r, i,j, u] + self.varss[r, k,l, u_prim] <= 1
            for r in range(1,51) for u in range(4) for u_prim in range(4) for i,j in self.TOWER_PLACEMENTS for k,l in self.FOOTPRINTS[(i,j)] if (i,j) != (k,l)),
            name = 'footprints'
        )

        if len(self.chosen_lists) > 0:
            # CONSTRAINT 13 - "Advanced" money correction with indicators
            for chosen in self.chosen_lists:
                M = len(chosen)
                delta = self.model.addVar(vtype=GRB.BINARY, name='indicator')
                self.model.addConstr(quicksum(self.varss[var] for var in chosen) <= (1+delta)*(M - 1))
                self.model.addConstr(quicksum(self.varss[var] for var in chosen) >= M*delta)
                self.model.addConstrs((quicksum(self.COST['Dart', u]*self.varss[r, i,j, u] for i,j in self.TOWER_PLACEMENTS for u in range(4)) <= self.MONEY[r] - delta*self.money_correction
                                        for r in range(1,51)), name='advanced-money-corr')
        else:
            # CONSTRAINT 2 - We must afford the build each round
            self.model.addConstrs(
                ((quicksum(self.COST['Dart', u]*self.varss[r, i,j, u] for i,j in self.TOWER_PLACEMENTS for u in range(4)) <= self.MONEY[r])
                for r in range(1,51)),
                name='money'
            )
        
        # CONSTRAINT 3 - We want to beat the human strategy cost
        self.model.addConstrs(
            ((quicksum(self.COST['Dart', u]*self.varss[r, i,j, u] for i,j in self.TOWER_PLACEMENTS for u in range(4)) <= self.human_strategy_cost)
            for r in range(1,51)),
            name='beathuman'
        )

        # CONSTRAINT 4 - We treat each upgrade as a separate tower - only one (tower, upgrade) pair can be active at each position
        self.model.addConstrs(
            ((quicksum(self.varss[r, i,j, u] for u in range(4)) <= 1)
            for r in range(1,51) for i,j in self.TOWER_PLACEMENTS),
            name = 'upgradecoding'
        )

        # CONSTRAINT 8 - Fix previous placement choices
        self.model.addConstrs(
            (quicksum(self.varss[r_prim, i, j, u] for u in range(4)) <= quicksum(self.varss[r, i, j, u] for u in range(4))
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'fixpreviouschoices'
        )

        # CONSTRAINT 9 - No downgrades from upgrade 1, 2, 3 to upgrade 0
        self.model.addConstrs(
            (self.varss[r_prim, i, j, 1] + self.varss[r_prim, i, j, 2] + self.varss[r_prim, i, j, 3] + self.varss[r,i,j,0] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'nodowngrades1230'
        )

        # CONSTRAINT 10 - No downgrades from upgrade 3 to upgrade 1 or 2
        self.model.addConstrs(
            (self.varss[r_prim, i, j, 3] + self.varss[r,i,j,1] + self.varss[r,i,j,2] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'nodowngrades312'
        )

        # CONSTRAINT 11 - Separate upgrade paths 1 and 2 - part 1
        self.model.addConstrs(
            (self.varss[r_prim, i, j, 1] + self.varss[r,i,j,2] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'separate12'
        )

        # CONSTRAINT 12 - Separate upgrade paths 1 and 2 - part 2
        self.model.addConstrs(
            (self.varss[r_prim, i, j, 2] + self.varss[r,i,j,1] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'separate21'
        )

    def get_parameters(self) -> Dict[str, Any]:
        out = {}
        out['name'] = self.name
        out['modulo'] = self.modulo
        out['type'] = self.type
        out['human_strategy_cost'] = self.human_strategy_cost
        out['scaling_bracket'] = self.scaling_bracket
        out['round_weights'] = self.round_weights

        return out


    @staticmethod
    def extract_vars_from_gurobi(var_name_list: List[str]) -> List[Tuple]:
        """
        Extracts Tower positions from the Gurobi names given to the model variables.
        :param var_name_list: List of variables to perform extraction on
        """
        out = []
        for var_name in var_name_list:
            var_str = re.search('\[.*\]', var_name).group(0).strip('[]')
            var_str_sep = var_str.split(",")
            var = (int(var_str_sep[0]), int(var_str_sep[1]), int(var_str_sep[2]), int(var_str_sep[3]))
            out.append(var)
        return out
    
    @staticmethod
    def enrich_build_order(sorted_round_action: List[Tuple]) -> List[Tuple]:
        # Go through the sorted list in order; for each upgrade operation we need to see if a build needs to be added right before it
        exists_set = set()
        for round_action in sorted_round_action:
            round_ = round_action[0]
            action = (round_action[1], round_action[2], round_action[3])
            if action[2] == 0:
                exists_set.add(action) 
            if action[2] > 0:
                if action[2] == 3:
                    if (action[0], action[1], 1) in exists_set:
                        sorted_round_action.insert(0, (round_, action[0], action[1], 2))
                    elif (action[0], action[1], 2) in exists_set:
                        sorted_round_action.insert(0, (round_, action[0], action[1], 1))
                    else:
                        sorted_round_action.insert(0, (round_, action[0], action[1], 1))
                        sorted_round_action.insert(0, (round_, action[0], action[1], 2))
                    sorted_round_action.remove(round_action)
                else:
                    exists_set.add(action)

                if (action[0], action[1], 0) not in exists_set:
                    sorted_round_action.insert(0, (round_, action[0], action[1], 0))
                    exists_set.add((action[0], action[1], 0)) 

                
        
        return sorted_round_action
    

    @staticmethod
    def model2_to_simulation(result_tuple_list: List[Tuple[int,int,int,int]]) -> List[Tuple]:
        out = []

        # For each position, upgrade keep only the occurence in the earliest round
        keep_earliest_filter = {}
        for round_, position_x, position_y, upgrade in result_tuple_list:
            keep_earliest_filter[(position_x, position_y, upgrade)] = []
        for (round_, position_x, position_y, upgrade) in result_tuple_list:
            keep_earliest_filter[(position_x, position_y, upgrade)].append(round_)
        only_first_occurence = {key: min(val) for key, val in keep_earliest_filter.items()}

        # transform and sort
        round_action = []
        for key, val in only_first_occurence.items():
            round_action.append((val, key[0], key[1], key[2]))
        sorted_round_action = sorted(round_action, key= lambda x: x[0])

        # Enrich to make into a valid build order
        valid = Model2.enrich_build_order(sorted_round_action)
        # Change syntax and sort
    
        for round_, position_x, position_y, upgrade in valid:
            out.append((round_, ('Dart', (position_x,position_y), upgrade)))
        
        out.sort()


        return out
        

class Model3(GameModel):
    def __init__(self, modulo, type_: str, scaling_bracket: Tuple[int,int] = (0,1), human_strategy_cost: int = 9250, round_weights: List[float] = [0.02 for i in range(50)], logging = True):
        super().__init__('Model3', modulo, logging)
        self.type = type_
        self.scaling_bracket = scaling_bracket
        self.human_strategy_cost = human_strategy_cost
        self.round_weights = round_weights

    def generate_sets(self):
        sets = generate_sets_3(self.modulo, self.scaling_bracket)
        if self.type == 'a':
            self.COVERAGE = sets['COV']   
        elif self.type == 'b':
            self.COVERAGE = sets['DIST']

        elif self.type == 'c':
            self.COVERAGE = sets['ANG_COV']
                
        
        var_d = sets['VAR_D']
        var_s = sets['VAR_S']

        self.ROUNDS = var_d[0]

        self.TOWER_PLACEMENTS = var_d[1]
        self.UPGRADES_D = var_d[2]

        self.TOWER_PLACEMENTS_S = var_s[1]
        self.UPGRADES_S = var_s[2]

        self.FOOTPRINTS = sets['FP']
        self.FOOTPRINTS_NS = sets['FPNS']
        self.FOOTPRINTS_SS = sets['FPSS']
        self.COST = sets['COST']
        self.MONEY = sets['MONEY']
    
    def set_variables(self):
        # Define variables for Dart
        self.vars_d = self.model.addVars(
            self.ROUNDS, self.TOWER_PLACEMENTS, 'D', self.UPGRADES_D,
            name='round-towerplacement-upgrade-dart',
            vtype=GRB.BINARY
            )
        # Define variables for Super Monkey
        self.vars_s = self.model.addVars(
            self.ROUNDS, self.TOWER_PLACEMENTS_S, 'S', self.UPGRADES_S,
            name='round-towerplacement-upgrade-super',
            vtype=GRB.BINARY
            )
        self.model.update()

    def set_objective(self):
        # Define the objective function
        
        obj = quicksum(
            self.round_weights[r-1]*self.COVERAGE[(i,j), 'Dart', u]*self.vars_d[r, i,j, 'D',u] 
            for r in self.ROUNDS for i,j in self.TOWER_PLACEMENTS for u in self.UPGRADES_D
            ) + \
            quicksum(
                self.round_weights[r-1]*self.COVERAGE[(i,j), 'Super Monkey', u]*self.vars_s[r, i,j, 'S', u] 
                for r in self.ROUNDS for i,j in self.TOWER_PLACEMENTS_S for u in self.UPGRADES_S
                )
        
        self.objective_function = obj

        # Set the objective function
        self.model.setObjective(
            obj,
            sense=GRB.MAXIMIZE
        )

        # Update model
        self.model.update()
    
    def set_constraints(self):
        # CONSTRAINT 1.1 - towers cannot be placed inside other towers' footprints - NN
        self.model.addConstrs(
            (self.vars_d[r, i,j, 'D',u] + self.vars_d[r, k,l, 'D', u_prim] <= 1
            for r in range(1,51) for u in range(4) for u_prim in range(4) for i,j in self.TOWER_PLACEMENTS for k,l in self.FOOTPRINTS[(i,j)] if (i,j) != (k,l)),
            name = 'footprints-nn'
        )

        # CONSTRAINT 1.2 - towers cannot be placed inside other towers' footprints - NS
        self.model.addConstrs(
            (self.vars_s[r, i,j, 'S', u] + self.vars_d[r, k,l,'D', u_prim] <= 1
            for r in range(1,51) for u in [0,2] for u_prim in range(4) for i,j in self.TOWER_PLACEMENTS_S for k,l in self.FOOTPRINTS_NS[(i,j)] if (i,j) != (k,l)),
            name = 'footprints-ns'
        )

        # CONSTRAINT 1.3 - towers cannot be placed inside other towers' footprints - SS
        self.model.addConstrs(
            (self.vars_s[r, i,j, 'S',u] + self.vars_s[r, k,l,'S', u_prim] <= 1
            for r in range(1,51) for u in [0,2] for u_prim in [0,2] for i,j in self.TOWER_PLACEMENTS_S for k,l in self.FOOTPRINTS_SS[(i,j)] if (i,j) != (k,l)),
            name = 'footprints-ss'
        )

        # CONSTRAINT 2 - We must afford the build each round
        self.model.addConstrs(
            ((quicksum(self.COST['Dart', u]*self.vars_d[r, i,j, 'D',u] for i,j in self.TOWER_PLACEMENTS for u in range(4)) + \
              quicksum(self.COST['Super Monkey', u]*self.vars_s[r, i,j, 'S',u] for i,j in self.TOWER_PLACEMENTS_S for u in [0,2]) <= self.MONEY[r])
            for r in range(1,51)),
            name='money'
        )
        
        # CONSTRAINT 3 - We want to beat the human strategy cost
        self.model.addConstrs(
            ((quicksum(self.COST['Dart', u]*self.vars_d[r, i,j, 'D',u] for i,j in self.TOWER_PLACEMENTS for u in range(4)) + \
              quicksum(self.COST['Super Monkey', u]*self.vars_s[r, i,j,'S',u] for i,j in self.TOWER_PLACEMENTS_S for u in [0,2]) <= self.human_strategy_cost)
            for r in range(1,51)),
            name='beathuman'
        )

        # CONSTRAINT 4.1 - only one (Dart, upgrade) pair can be active at each position
        self.model.addConstrs(
            ((quicksum(self.vars_d[r, i,j, 'D', u] for u in range(4)) <= 1)
            for r in range(1,51) for i,j in self.TOWER_PLACEMENTS),
            name = 'upgradecoding-d'
        )

        # CONSTRAINT 4.2 - only one (Super Monkey, upgrade) pair can be active at each position
        self.model.addConstrs(
            ((quicksum(self.vars_s[r, i,j,'S', u] for u in [0,2]) <= 1)
            for r in range(1,51) for i,j in self.TOWER_PLACEMENTS_S),
            name = 'upgradecoding-s'
        )

        # CONSTRAINT 5.1 - Fix previous placement choices D
        self.model.addConstrs(
            (quicksum(self.vars_d[r_prim, i, j,  'D', u] for u in range(4)) <= quicksum(self.vars_d[r, i, j, 'D', u] for u in range(4))
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'fixpreviouschoices-d'
        )

        # CONSTRAINT 5.2 - Fix previous placement choices S
        self.model.addConstrs(
            (quicksum(self.vars_s[r_prim, i, j, 'S',u] for u in [0,2]) <= quicksum(self.vars_s[r, i, j,'S', u] for u in [0,2])
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS_S),
            name = 'fixpreviouschoices-s'
        )

        # CONSTRAINT 6.1 - No downgrades from upgrade 1, 2, 3 to upgrade 0
        self.model.addConstrs(
            (self.vars_d[r_prim, i, j,'D',1] + self.vars_d[r_prim, i, j,'D', 2] + self.vars_d[r_prim, i, j, 'D', 3] + self.vars_d[r,i,j,'D',0] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'nodowngrades1230'
        )

        # CONSTRAINT 6.2 - No downgrades from upgrade 3 to upgrade 1 or 2
        self.model.addConstrs(
            (self.vars_d[r_prim, i, j, 'D',3] + self.vars_d[r,i,j,'D',1] + self.vars_d[r,i,j,'D',2] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'nodowngrades312'
        )

        # CONSTRAINT 6.3 - Separate upgrade paths 1 and 2 - part 1
        self.model.addConstrs(
            (self.vars_d[r_prim, i, j, 'D',1] + self.vars_d[r,i,j,'D',2] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'separate12'
        )

        # CONSTRAINT 6.4 - Separate upgrade paths 1 and 2 - part 2
        self.model.addConstrs(
            (self.vars_d[r_prim, i, j, 'D',2] + self.vars_d[r,i,j,'D', 1] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'separate21'
        )

        # CONSTRAINT 6.5 - No downgrades from upgrade 2 to upgrade 0 S
        self.model.addConstrs(
            (self.vars_s[r_prim, i, j,'S', 2] + self.vars_s[r,i,j, 'S', 0] <= 1
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS_S),
            name = 'nodowngrades20-s'
        )

    def get_parameters(self) -> Dict[str, Any]:
        out = {}
        out['name'] = self.name
        out['modulo'] = self.modulo
        out['type'] = self.type
        out['human_strategy_cost'] = self.human_strategy_cost
        out['scaling_bracket'] = self.scaling_bracket
        out['round_weights'] = self.round_weights

        return out
    

    @staticmethod
    def extract_vars_from_gurobi(var_name_list: List[str]) -> List[Tuple]:
        """
        Extracts Tower positions from the Gurobi names given to the model variables.
        :param var_name_list: List of variables to perform extraction on
        """
        out = []
        for var_name in var_name_list:
            var_str = re.search('\[.*\]', var_name).group(0).strip('[]')
            var_str_sep = var_str.split(",")
            var = (int(var_str_sep[0]), int(var_str_sep[1]), int(var_str_sep[2]), str(var_str_sep[3]), int(var_str_sep[4]))
            out.append(var)
        return out
    
    @staticmethod
    def enrich_build_order(sorted_round_action: List[Tuple]) -> List[Tuple]:
        # Go through the sorted list in order; for each upgrade operation we need to see if a build needs to be added right before it
        exists_set = set()
        for round_action in sorted_round_action:
            round_ = round_action[0]
            action = (round_action[1], round_action[2], round_action[3], round_action[4])
            if action[3] == 0:
                exists_set.add(action) 
            if action[3] > 0:
                if action[3] == 3:
                    sorted_round_action.insert(0, (round_, action[0], action[1], action[2], 1))
                    sorted_round_action.insert(0, (round_, action[0], action[1], action[2], 2))
                    sorted_round_action.remove(round_action)

                if (action[0], action[1], 0) not in exists_set:
                    sorted_round_action.insert(0, (round_, action[0], action[1], action[2], 0))
                    exists_set.add((action[0], action[1], action[2], 0)) 

                exists_set.add(action)
        
        return sorted_round_action
    
    @staticmethod
    def model3_to_simulation(result_tuple_list: List[Tuple[int,int,int,str,int]]) -> List[Tuple]:
        out = []
        keep_earliest_filter = {}
        for round_, position_x, position_y, tower, upgrade in result_tuple_list:
            keep_earliest_filter[(position_x, position_y, tower, upgrade)] = []
        for (round_, position_x, position_y, tower, upgrade) in result_tuple_list:
            keep_earliest_filter[(position_x, position_y, tower, upgrade)].append(round_)
        only_first_occurence = {key: min(val) for key, val in keep_earliest_filter.items()}

        # transform and sort
        round_action = []
        for key, val in only_first_occurence.items():
            round_action.append((val, key[0], key[1], key[2], key[3]))
        sorted_round_action = sorted(round_action, key= lambda x: x[0])

        # Enrich to make into a valid build order
        valid = Model3.enrich_build_order(sorted_round_action) 
        # Change syntax and sort
        for round_, position_x, position_y, tower, upgrade in valid:
            if tower == 'D':
                out.append((round_, ('Dart', (position_x,position_y), upgrade)))
            elif tower == 'S':
                 out.append((round_, ('Super Monkey', (position_x,position_y), upgrade)))
        
        out.sort()

        return out
    

class ProxyEvaluator:
    """
    Used for evaluating the quality of proxies.
    """
    def __init__(self, model_nr: int, type_: str, times_per_round: int = 20, modulo: int = 1, money_offset: int = 0,logging: bool = True):
        random.seed(40) # set seed for reproducibility
        self.model_nr = model_nr
        self.type = type_
        self.times_per_round = times_per_round
        self.modulo = modulo
        self.money_offset = money_offset
        self.logging = logging

        self.pos_D = read_pickle('PLACEMENTS')
        self.pos_S = read_pickle('PLACEMENTS_S')
        
        if self.type == 'a':
            self.cov = read_pickle('COV')
        elif self.type == 'b':
            self.cov = read_pickle('DIST_0_1')
        elif self.type == 'c':
            self.cov = read_pickle('ANG_0_1')
        if self.modulo > 1:
            self.pos_D = filter_point_set_modulo(self.pos_D, self.modulo)
            self.pos_S = filter_point_set_modulo(self.pos_S, self.modulo)

        self.results = {}

    def get_random_build_for_round(self, round_nr : int) -> List[Tuple]:
        out = []
        pos_D = self.pos_D.copy()
        pos_S = self.pos_S.copy()
        money = get_money_constraint_rhs(round_nr)

        if self.model_nr == 1:
            while money >= 250 + self.money_offset: # Money offset for finding a setting in which we could get the most varied and reliable results
                pos = random.choice(pos_D)
                out.append((round_nr, ('Dart', (pos[0], pos[1]), 0)))
                money = money - 250
                pos_D.remove(pos)
        
        else:
            while money >= 250:
                if money >= 4000 and round_nr > 30 and self.model_nr == 3:
                    pos = random.choice(pos_S)
                    out.append((round_nr, ('Super Monkey', (pos[0], pos[1]), 0)))
                    money = money - 4000
                    pos_S.remove(pos)
                    if money >= 2400:
                        out.append((round_nr, ('Super Monkey', (pos[0], pos[1]), 2)))
                        money = money - 2400
                else:
                    pos = random.choice(pos_D)
                    out.append((round_nr, ('Dart', (pos[0], pos[1]), 0)))
                    money = money - 250
                    pos_D.remove(pos)
                    if money >= 210:
                        out.append((round_nr, ('Dart', (pos[0], pos[1]), 1)))
                        money = money - 210
                    if money >= 100:
                        out.append((round_nr, ('Dart', (pos[0], pos[1]), 2)))
                        money = money - 100
        return out

    def compute_cov_for_build(self, build: List[Tuple]) -> int:
        total = 0
        for action in build:
            tow, pos, upg = action[1]
            total += self.cov[pos, tow, upg]
        
        return total

    def run_round_for_proxy_evaluation(self, round_nr: int) -> None:
        self.results[round_nr] = [[],[]]
        for _ in range(self.times_per_round):
            build = self.get_random_build_for_round(round_nr)
            cov = self.compute_cov_for_build(build)
            queue = prepare_tower_queue(build)
            g = Game(1792, 30000, round_nr, False, queue, 5)
            results = g.run_round()
            lives = results['lives']
            self.results[round_nr][0].append(cov)
            self.results[round_nr][1].append(lives)

    def run_evaluation(self) -> Dict[int, List]:
        for round_nr in range(1,51):
            self.run_round_for_proxy_evaluation(round_nr)
            if self.logging:
                print(f"Evaluation progress: {round_nr}/50")

        self.write_results_to_pickle()
        return self.results

    def write_results_to_pickle(self):
        name = f'proxy_evaluation_{self.model_nr}{self.type}'
        if self.modulo > 1:
            name = name + f'_{self.modulo}'
        if self.money_offset > 0:
            name = name + f'_{self.money_offset}'
        write_pickle(self.results, name, True)

    @staticmethod
    def get_correlation_per_round(evaluation_results: Dict[int, List]) -> Dict[int, float]:
        out_dct = {}
        for round_nr in range(1,51):
            cov = evaluation_results[round_nr][0]
            lives = evaluation_results[round_nr][1]
            out_dct[round_nr] = np.corrcoef(cov, lives)[0,1]
        return out_dct
    
    @staticmethod
    def filter_our_extremes(evaluation_results: Dict[int, List]) -> Dict[int,List]:
        zero_lives_count = 0
        forty_lives_count = 0
        for round_nr in range(1,51):
            df = pd.DataFrame({'cov':evaluation_results[round_nr][0], 'lives':evaluation_results[round_nr][1]})
            zero_lives = (df['lives'] == 0)
            forty_lives = (df['lives'] == 40)
            df_new = df[~(zero_lives | forty_lives)]
            zero_lives_count += len(df[zero_lives])
            forty_lives_count += len(df[forty_lives])
            evaluation_results[round_nr][0] = list(df_new['cov'])
            evaluation_results[round_nr][1] = list(df_new['lives'])
        
        print(f"Zero lives cases removed: {zero_lives_count}\nFull lives cases removed: {forty_lives_count}")
        return evaluation_results

    @staticmethod
    def get_correlation(evaluation_results: Dict[int, List], extremes_correction: bool = False) -> float:
        x = []
        y = []
        if extremes_correction:
            evaluation_results = ProxyEvaluator.filter_our_extremes(evaluation_results)

        for round_nr in range(1,51):
            cov_ls = evaluation_results[round_nr][0]
            lives_ls = evaluation_results[round_nr][1]
            x.extend(cov_ls)
            y.extend(lives_ls)
        return  np.corrcoef(x,y)[0,1]
    

class ProxyEvaluatorOneRound:
    """
    Used for evaluating the quality of proxies.
    """
    def __init__(self, model_nr: int, type_: str, round_nr: int, dart_monkey_number: int,  reps: int = 5000, modulo: int = 1, logging: bool = True):
        random.seed(40) # set seed for reproducibility
        self.model_nr = model_nr
        self.type = type_
        self.round_nr = round_nr
        self.reps = reps
        self.dart_monkey_nr = dart_monkey_number
        self.modulo = modulo
        self.logging = logging

        self.money = get_money_constraint_rhs(self.round_nr)
        self.max_lives = create_rounds_dataframe().loc[self.round_nr, "RBE_Cash"]

        self.pos_D = read_pickle('PLACEMENTS')
        
        if self.type == 'a':
            self.cov = read_pickle('COV')
        elif self.type == 'b':
            self.cov = read_pickle('DIST_0_1')
        elif self.type == 'c':
            self.cov = read_pickle('ANG_0_1')
        if self.modulo > 1:
            self.pos_D = filter_point_set_modulo(self.pos_D, self.modulo)
            self.pos_S = filter_point_set_modulo(self.pos_S, self.modulo)

        self.results = [[],[]]

    def compute_cov_for_build(self, build: List[Tuple]) -> int:
        total = 0
        for action in build:
            tow, pos, upg = action[1]
            total += self.cov[pos, tow, upg]
        
        return total
    
    def get_random_build(self) -> List[Tuple]:
        out = []

        if self.money < 250*self.dart_monkey_nr:
            raise ValueError('Cannot built as many Dart Monkeys in the evaluation due to budget constraints!')

        if self.model_nr == 1:
            pos_ls = random.sample(self.pos_D, self.dart_monkey_nr)
            for pos in pos_ls:
                out.append((self.round_nr, ('Dart', (pos[0], pos[1]), 0)))
            
        return out


    def run_one_setting(self) -> bool:
        """
        Returns: Whether all round in the given setting were won with a perfect score (True) or not (False)
        """
        for i in range(self.reps):
            build = self.get_random_build()
            cov = self.compute_cov_for_build(build)
            queue = prepare_tower_queue(build)
            g = Game(self.max_lives, 30000, self.round_nr, False, queue, 5)
            results = g.run_round()
            lives = results['lives']
            self.results[0].append(cov)
            self.results[1].append(lives)
            if self.logging:
                print(f'Progress: {i+1}/{self.reps}')

    def run_evaluation(self, save: bool = True) -> List:
        
        self.run_one_setting()

        if save:
            self.write_results_to_pickle()
        return self.results

    def write_results_to_pickle(self):
        name = f'proxy_evaluation_oneround_{self.model_nr}{self.type}{self.round_nr}_monkeys{self.dart_monkey_nr}_reps{self.reps}'
        if self.modulo > 1:
            name = name + f'_{self.modulo}'
        write_pickle(self.results, name, True)

    @staticmethod
    def print_lives_var(round_nr: int):
        dart_monkey_max_nr = int(np.floor(get_money_constraint_rhs(round_nr)/250))
        for i in range(dart_monkey_max_nr):
            if i > 37:
                break
            p = ProxyEvaluatorOneRound(1, 'a', 50, i+1, 100, 1, False)
            r = p.run_evaluation(False)
            print(f"Life variance for M1a, i = {i+1}: {np.var(r[1])}")


# ev = ProxyEvaluatorOneRound(1, 'c', 50, 37, 1000)
# ev.run_evaluation()

# r = read_pickle('proxy_evaluation_oneround_1a50_monkeys34', True)
# print(np.corrcoef(r[0], r[1])[0][1])



# for typ in ['a', 'b', 'c']:
#     p = ProxyEvaluatorOneRound(1, typ, 50, 23, 1000, 1, False)
#     r = p.run_evaluation(True)
#     print(f'1{typ} corr: {np.corrcoef(r[0], r[1])[0][1]}')
# print(get_money_constraint_rhs(5))

# ProxyEvaluatorOneRound.print_lives_var(50)
