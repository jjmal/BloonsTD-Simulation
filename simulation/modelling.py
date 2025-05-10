import re

from typing import List, Tuple, Dict, Any
from gurobipy import Model, GRB, quicksum
from modelling_sets import generate_vars_1a, generate_coverage_dict, generate_all_footprint_constraint_sets, get_money_constraint_rhs, generate_sets_1a, generate_sets_1b

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
        chosen = extract_pos_from_gurobi(chosen_positions_name_list)

        out = {}
        out['objective_value'] = objective_value
        out['choices'] = chosen

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


class CoverageModel(GameModel):
    """
    Represents a model based on point coverage. It utilises only DartMonkeys (and their upgrades)
    """
    def __init__(self, name, modulo, logging = True):
        super().__init__(name, modulo, logging)


class ConstraintSatisfactionModel(GameModel):
    """
    Represents a model based on Constraint Satisfaction, with no optimization objective needed. 
    """
    def __init__(self, name, modulo, logging = True):
        super().__init__(name, modulo, logging)

class Model1a(CoverageModel):
    """
    Represents Model 1a (Maximum Track Coverage as objective; Dart Tower only; No Upgrades)
    """
    def __init__(self, modulo, logging = True):
        super().__init__('Model 1 (Max Coverage, Dart Only, No Upgrades)', modulo, logging)

    def generate_sets(self):

        self.TOWER_PLACEMENTS = generate_vars_1a(self.modulo)
        if self.logging:
            print('TOWER PLACEMENT SET CREATED')

        self.COVERAGE = generate_coverage_dict()
        if self.logging:
            print('COVERAGE VECTOR CREATED')
        
        self.FOOTPRINTS = generate_all_footprint_constraint_sets("nn", self.modulo)
        if self.logging:
            print('FOOTPRINT SETS CREATED')
    
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
        obj = quicksum(
            self.COVERAGE[pos] * self.varss[pos] 
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
        
        # CONSTRAINT 2 - We want a solution that does not use more Dart Towers than S1 (i.e. uses less than 37 Dart Towers)
        self.model.addConstr(
            quicksum(self.varss[pos] for pos in self.TOWER_PLACEMENTS) <= 37
        )
        self.model.update()
    
    @staticmethod 
    def model_1a_per_round(modulo: int, round_19_correction: bool = True) -> Dict[int, List[Tuple[int,int]]]:
        """
        Runs Model 1a for each round, fixing previous choices.
        :param modulo: number for the divisibility filter
        :param round_19_correction: With an uncorrected model, the game throws an error on round 19 for modulo 10 (not enough money for the build), as it
        by default does not account for lost lives. With correction enabled, the model will take the lives lost into account when calculating
        money from round 19 onwards, enabling the game to last until its properly lost.
        :returns: a Dict of the form (round_nr, choices) with round_nr being the round
        in which we perform Dart Tower Build actions specified in choices
        """
        fixed_points = []
        out = {}
        rounds = 50

        # Define sets:
        sets = generate_sets_1a(modulo)
        TP = sets['TP']
        COV = sets['COV']
        FP = sets['FP']

        print("SETS CREATED")

        for r in range(1, rounds + 1):
            # Get money for round r
            money = get_money_constraint_rhs(r)

            m = Model1a(modulo, False)

            # Set sets
            m.TOWER_PLACEMENTS = TP
            m.COVERAGE = COV
            m.FOOTPRINTS = FP
            
            # Build baseline Model 1a
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

        return out

    @staticmethod
    def model_to_simulation(result_dict: Dict[int, List[Tuple[int,int]]]) -> List[Tuple]:
        out = []
        for key, val in result_dict.items():
            if len(val) > 0:
                for pos in val:
                    out.append((key, ('Dart', pos, 0)))

        return out


class Model1b(Model1a):
    """
    Represents Model 1b (Maximum Track Coverage as objective; Dart Tower only; No Upgrades; Ensuring all points are covered)
    """
    def __init__(self, modulo: int, alpha: int, logging: bool = True):
        super().__init__(modulo, logging)
        self.alpha = alpha

    def generate_sets(self):
        sets = generate_sets_1b(self.modulo, self.alpha)
        self.TOWER_PLACEMENTS = sets['TP']
        self.DISTANCE = sets['DIST']
        self.FOOTPRINTS = sets['FP']

    def set_objective(self):
         # Define the objective function
        obj = quicksum(
            self.DISTANCE[pos] * self.varss[pos] 
            for pos in self.TOWER_PLACEMENTS
            )
        self.objective_function = obj

        # Set the objective function
        self.model.setObjective(
            obj,
            sense=GRB.MINIMIZE
        )
        # Update model
        self.model.update()

    # def set_constraints(self):
    #     super().set_constraints()
    #     # CONSTRAINT 3 - we have to cover all points at least once
    #     self.model.addConstrs(

    #     )
    


def extract_pos_from_gurobi(var_name_list: List[str]) -> List[Tuple]:
    """
    Extracts Tower positions from the Gurobi names given to the model variables
    :param var_name_list: List of variables to perform extraction on
    """
    out = []
    for var_name in var_name_list:
        pos_str = re.search('\[.*\]', var_name).group(0).strip('[]')
        pos_str_sep = pos_str.split(",")
        pos = (int(pos_str_sep[0]), int(pos_str_sep[1]))
        out.append(pos)
    return out



