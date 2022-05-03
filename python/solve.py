"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
from pathlib import Path
from typing import Callable, Dict
import random
import math

from sympy import jacobi_normalized
from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper
from point import Point
import gurobipy as gp

 


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

def solve_LP(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=LPSolver(instance),
    )

def solve_LPWithWeights(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=weightsLPSolver(instance),
    )


def greedySetCover(instance: Instance) -> Solution:
    cities = (instance.cities)[:]
    universe = (instance.cities)[:]
    size = instance.grid_side_length - 1
    bigList = []
    for city in cities:
        x = city.x
        y = city.y
        lst_of_points = [Point(x,y)]
        for i in range(-2,3):
            for j in range(-2,3):
                if not(x + i < 0 or x + i > size or y + j < 0 or y + j > size or (x + i == x and y + j == y)):
                    try:
                        lst_of_points.append(Point(x + i,y + j))
                    except:
                        print(x + i, y + j)
        if not(x - 3 < 0):
            lst_of_points.append(Point(x - 3,y))
        if not(x + 3 > size):
            lst_of_points.append(Point(x + 3,y))
        if not(y - 3 < 0):
            lst_of_points.append(Point(x,y - 3))
        if not(y + 3 > size):
            lst_of_points.append(Point(x,y + 3))
        bigList.append(lst_of_points)

    towers = [] 
    while len(universe) > 0:
        max = 0
        maxPoint = Point(0,0) 
        maxPointsCovered = []
        for lst in bigList:
            count = 0
            pointsCovered  = [] 
            for point in lst:
                if point in universe:
                    count = count + 1
                    pointsCovered.append(point)
            if count > max:
                max = count
                maxPoint = lst[0]
                maxPointsCovered = pointsCovered[:]
        for point in maxPointsCovered:
            universe.remove(point)
        towers.append(maxPoint)
    return towers


            
def weightsLPSolver(instance: Instance) -> Solution:
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
        m.addConstr(gp.quicksum(lst_of_points) >= 1)
    
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
            #m.addConstr(weights[x][y] <= 10)
           # m.addConstr(weights[x][y] >= 0)
    
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

            



def LPSolver(instance: Instance) -> Solution:
    m = gp.Model()
    cities = (instance.cities)[:]
    #create the variables
    size = instance.grid_side_length - 1
    variables = [[0 for x in range(size + 1)] for y in range(size + 1)] 
    #weights = [[0 for x in range(size + 1)] for y in range(size + 1)]

    #add the variables to the LP
    for i in range(size + 1):
        for j in range(size + 1):
            variables[i][j] = m.addVar(vtype=gp.GRB.BINARY, name="x_%d_%d" % (i,j))
            #weights[i][j] = m.addVar(vtype=gp.GRB.INTEGER, name="w_%d_%d" % (i,j))
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
    '''
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
            #m.addConstr(weights[x][y] <= 10)
           # m.addConstr(weights[x][y] >= 0)
    '''
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

    

def cityList(instance: Instance):
    cities_initial = (instance.cities)[:]
    finalCities = (instance.cities)[:]
    cities = []
    for city in cities_initial:
        x = city.x
        y = city.y
        x_jitter = random.randint(-2,2)
        y_jitter = random.randint(-2,2)
        x = x + x_jitter
        y = y + y_jitter
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > instance.grid_side_length - 1:
            x = instance.grid_side_length - 1
        if y > instance.grid_side_length - 1:
            y = instance.grid_side_length - 1
        cities.append(Point(x,y))



    random.shuffle(cities)
    random.shuffle(finalCities)
    for originCity in cities:
        if originCity in finalCities:
            for otherCity in cities:
                if otherCity in finalCities:
                    if originCity.distance_obj(otherCity) <= 3 and originCity.distance_obj(otherCity) != 0:
                        finalCities.remove(otherCity)
    return finalCities



SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")


def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")


def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
