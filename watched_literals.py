import numpy as np
import copy
import itertools
import timeit
def load_dimacs(file_name):
    example = open(file_name, "r")
    lines = example.readlines()
    clause_set = []
    count = 0
    for i in range(0,len(lines)):
        temp = lines[i].split()
        if temp[0] == "p":
            count+=1
        elif temp[0] == "c":
            count+=1
        else:
            clause_set.append([])
            for j in range(0, len(temp)-1):
                clause_set[i-count].append(int(temp[j]))
    return clause_set

def dpll_sat_solve(clause_set,partial_assignment = []):
    watch_literals = {}
    vars = np.unique(list(itertools.chain.from_iterable(clause_set)))
    literals = np.abs(vars)
    for i in vars:
        watch_literals[i] = []
    for i in range(len(clause_set)):
        watch_literals[clause_set[i][0]].append(i)
        watch_literals[clause_set[i][1]].append(i)
    partial_assignment = dpll_sat_solve_wrapper(clause_set,partial_assignment)
    

def dpll_sat_solve_wrapper(clause_set,partial_assignment):
    unit_propagate(clause_set)
    pass

def unit_propagate(clause_set):
    pass

clause_set = load_dimacs("8queens.txt")

print(timeit.repeat('dpll_sat_solve(clause_set)', globals = globals(), number = 1, repeat = 1))