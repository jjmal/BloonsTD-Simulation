from gurobipy import Model, GRB, quicksum
import numpy as np
# pos_d = [(0,3), (0,2), (1,1), (0,0)]
# pos_s = [(0,3), (0,2), (1,1,)]

# u_d = [0,1,2,3]
# u_s = [0,2]

# r = [i+1 for i in range(50)]

# m = Model('test')
# m.addVars(r, pos_d, 'D', u_d, name = 'dart')
# m.addVars(r, pos_s, 'S', u_s, name = 'super')
# m.update()

x = [993, 342, 145]
y = [40,40,40]

print(np.corrcoef(x,y))
