import re

from typing import List, Tuple, Dict, Any
from datetime import datetime
from gurobipy import Model, GRB, quicksum
from datasets import create_towers_dataframe
from modelling_sets import  get_money_constraint_rhs, generate_sets_1a, generate_sets_1b, generate_sets_1c, \
      generate_sets_2a, generate_sets_2b, generate_sets_2c
from modelling_utils import write_pickle
 
class GameModel:
    """
    Template class for models that will derive the solutions for the game.
    """
    def __init__(self, name: str, modulo: int, logging: bool = True):
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
        out['parameters'] = vars(self)

        # Save result as pickle, if Model is not Model 1 (as for Model 1 we care about the final result after 50 models are run)
        if self.name != 'Model1':
            write_pickle(out, f"{self.name}{self.type}mod{self.modulo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        return out 
    
    def run(self) -> Dict[str, Any]:
        self.build()
        if self.logging:
            print('BEGIN SOLVING')

        self.solve()
        if self.logging:
            print('MODEL DONE')
        
        return self.get_results()
    
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
    def model1_per_round(modulo: int, type_: str, scaling_bracket: Tuple[int,int] = (0,1), dart_monkey_nr: int = 37, round_19_correction: bool = True) -> Dict[int, List[Tuple[int,int]]]:
        """
        Runs Model 1 for each round, fixing previous choices.
        :param modulo: number for the divisibility filter
        :param type_: type of Model ('a', 'b', or 'c'), which determines the objective function
        :param round_19_correction: With an uncorrected model, the game throws an error on round 19 for modulo 10 (not enough money for the build) for 
        types 'a' and 'b', as it by default does not account for lost lives. With correction enabled, the model will take the lives lost into account 
        when calculating money from round 19 onwards, enabling the game to last until its properly lost.
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
            if not round_19_correction:
                m.model.addConstr(quicksum(250*m.varss[pos] for pos in m.TOWER_PLACEMENTS) <= money)
            else:
                if r < 19:
                    m.model.addConstr(quicksum(250*m.varss[pos] for pos in m.TOWER_PLACEMENTS) <= money)
                else:
                    m.model.addConstr(quicksum(250*m.varss[pos] for pos in m.TOWER_PLACEMENTS) <= money - 32)

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
        write_pickle(out, f"Model1{type_}mod{modulo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        return out

    @staticmethod
    def model1_to_simulation(result_dict: Dict[int, List[Tuple[int,int]]]) -> List[Tuple]:
        out = []
        for key, val in result_dict.items():
            if len(val) > 0:
                for pos in val:
                    out.append((key, ('Dart', pos, 0)))

        return out


class Model2(GameModel):
    """
    (Maximize coverage all rounds, Dart Monkey with upgrades)
    """
    def __init__(self, modulo, type_: str, scaling_bracket: Tuple[int,int] = (0,1), human_strategy_cost: int = 9250, round_weights: List[float] = [0.02 for i in range(50)], logging = True):
        super().__init__('Model2', modulo, logging)
        self.type = type_
        self.scaling_bracket = scaling_bracket
        self.human_strategy_cost = human_strategy_cost
        self.round_weights = round_weights
        
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
                self.round_weights[r]*self.DISTANCE[(i,j), 'Dart', u] * self.varss[(r, i,j, u)] 
                for r in self.ROUNDS for i,j in self.TOWER_PLACEMENTS for u in self.UPGRADES
            )
        
        elif self.type == 'c':
            obj = quicksum(
                self.round_weights[r]*self.ANGLE_COVERAGE[(i,j), 'Dart', u] * self.varss[(r, i,j, u)] 
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
            (self.varss[r, i,j, u] + self.varss[r, k,l, u] <= 1
            for r in range(1,51) for u in range(4) for i,j in self.TOWER_PLACEMENTS for k,l in self.FOOTPRINTS[(i,j)] if (i,j) != (k,l)),
            name = 'footprints'
        )

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

        # CONSTRAINT 5 - To have upgrade 1 at round r, you must have had either upgrade 0 or upgrade 1 at one of the previous rounds
        self.model.addConstrs(
            (self.varss[r_prim, i,j, 0] + self.varss[r_prim, i,j, 1] >= self.varss[r, i,j, 1]
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'upgradeflow01'
        )

        # CONSTRAINT 6 - To have upgrade 2 at round r, you must have had either upgrade 0 or upgrade 2 at one of the previous rounds
        self.model.addConstrs(
            (self.varss[r_prim, i,j, 0] + self.varss[r_prim, i,j, 2] >= self.varss[r, i,j, 2]
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'upgradeflow02'
        )

        # CONSTRAINT 7 - To have upgrade 1+2 (coded as 3) at round r, you must have had either upgrade 1 or upgrade 2 or upgrade 3 at one of the previous rounds
        self.model.addConstrs(
            (self.varss[r_prim, i,j, 1] + self.varss[r_prim, i,j, 2] + self.varss[r_prim, i,j, 3] >= self.varss[r, i,j, 3]
            for r in range(2,51) for r_prim in range(1,r) for i,j in self.TOWER_PLACEMENTS),
            name = 'upgradeflow123'
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
            name = 'nodowngrades20'
        )

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
    def model2_to_simulation(result_tuple_list: List[Tuple[int,int,int,int]]) -> List[Tuple]:
        out = []
        for round_, position_x, position_y, upgrade in result_tuple_list:
            out.append((round_, ('Dart', (position_x, position_y), upgrade)))

        return out
        

class Model3(GameModel):
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
            var = (int(var_str_sep[0]), int(var_str_sep[1]), int(var_str_sep[2]), int(var_str_sep[3]), int(var_str_sep[4]))
            out.append(var)
        return out
        
    @staticmethod
    def model3_to_simulation(result_tuple_list: List[Tuple[int,int,int,str,int]]) -> List[Tuple]:
        out = []
        for round_, position_x, position_y, tower, upgrade in result_tuple_list:
            out.append((round_, (tower, (position_x, position_y), upgrade)))

        return out

# m2 = Model2(10, "a")
# m2.run()
