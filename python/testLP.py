import argparse
from pathlib import Path
from typing import Callable, Dict
import random
from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper
from point import Point
import gurobipy as gp

'''
def LPSolver(instance: Instance) -> Solution:
    m = gp.Model()
    cities = (instance.cities)[:]
    #create the variables
    size = instance.grid_side_length - 1
    variables = [[0 for x in range(size + 1)] for y in range(size + 1)] 

    #add the variables to the LP
    for i in range(size + 1):
        for j in range(size + 1):
            variables[i][j] = m.addVar(vtype=gp.GRB.BINARY, name="x_%d_%d" % (i,j))
    #add constraints
    for city in cities:
        x = city.x
        y = city.y
        lst_of_points = []
        for i in range(-2,3):
            for j in range(-2,3):
                if not(x + i < 0 or x + i > size or y + j < 0 or y + j > size):
                    try:
                        lst_of_points.append(variables[x + i][y + j])
                    except:
                        print(x + i, y + j)
        if not(x - 3 < 0):
            lst_of_points.append(variables[x - 3][y])
        if not(x + 3 > size):
            lst_of_points.append(variables[x + 3][y])
        if not(y - 3 < 0):
            lst_of_points.append(variables[x][y - 3])
        if not(y + 3 > size):
            lst_of_points.append(variables[x][y + 3])
        m.addConstr(gp.quicksum(lst_of_points) >= 1)
    #set the objective
    m.setObjective(gp.quicksum(variables[i][j] for i in range(size + 1) for j in range(size + 1)), gp.GRB.MINIMIZE)

    #solve the LP
    m.optimize()
    #get the solution
    solution = []
    for i in range(size + 1):
        for j in range(size + 1):
            if variables[i][j].X == 1:
                solution.append(Point(i,j))
    
    return solution
'''

def LPSolver(instance: Instance) -> Solution:
    m = gp.Model()
    cities = (instance.cities)[:]
    #create the variables
    size = instance.grid_side_length - 1
    variables = [[0 for x in range(size + 1)] for y in range(size + 1)] 
    weights = [[0 for x in range(size + 1)] for y in range(size + 1)]

    #add the variables to the LP
    for i in range(size + 1):
        for j in range(size + 1):
            variables[i][j] = m.addVar(vtype=gp.GRB.BINARY, name="x_%d_%d" % (i,j))
            weights[i][j] = m.addVar(vtype=gp.GRB.INTEGER, name="w_%d_%d" % (i,j))
    #add constraints
    for city in cities:
        x = city.x
        y = city.y
        lst_of_points = []
        for i in range(-2,3):
            for j in range(-2,3):
                if not(x + i < 0 or x + i > size or y + j < 0 or y + j > size):
                    try:
                        lst_of_points.append(variables[x + i][y + j])
                    except:
                        print(x + i, y + j)
        if not(x - 3 < 0):
            lst_of_points.append(variables[x - 3][y])
        if not(x + 3 > size):
            lst_of_points.append(variables[x + 3][y])
        if not(y - 3 < 0):
            lst_of_points.append(variables[x][y - 3])
        if not(y + 3 > size):
            lst_of_points.append(variables[x][y + 3])
        m.addConstr(gp.quicksum(lst_of_points) == 1)

    for x in range(size + 1):
        for y in range(size + 1):

            lst_of_points = []
            pR = instance.penalty_radius
            for i in range(-pR + 1, pR):
                for j in range(-pR + 1, pR):
                    if not(x + i < 0 or x + i > size or y + j < 0 or y + j > size):
                        try:
                            lst_of_points.append(variables[x + i][y + j])
                        except:
                            print(x + i, y + j)          
            m.addConstr(weights[x][y] == gp.quicksum(lst_of_points))

    #set the objective
    m.setObjective(gp.quicksum(variables[i][j]*weights[i][j] for i in range(size + 1) for j in range(size + 1)), gp.GRB.MINIMIZE)

    #solve the LP
    m.optimize()
    #get the solution
    solution = []
    for i in range(size + 1):
        for j in range(size + 1):
            if variables[i][j].X == 1:
                solution.append(Point(i,j))
    
    return solution

with open('inputs/small/054.in') as f:
    instance = Instance.parse(f.readlines())
    LPSolver(instance)

