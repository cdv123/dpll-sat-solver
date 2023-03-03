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

def dpll_sat_solve(clause_set,partial_assignment=[]):
    watch_literals = {}
    vars = np.unique(list(itertools.chain.from_iterable(clause_set)))
    literals = np.abs(vars)
    partial_assignment = {}
    units = []
    for i in vars:
        watch_literals[i] = []
    for i in literals:
        partial_assignment[i] = 0
    for i in range(len(clause_set)):
        if len(clause_set[i]) == 1:
            watch_literals[clause_set[i][0]].append(clause_set[i])
            units.append(clause_set[i][0])
        else:
            watch_literals[clause_set[i][1]].append(clause_set[i])
    partial_assignment = set()
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals)
    

def dpll_sat_solve_wrapper(partial_assignment,units,watch_literals):
    unit_propagate(partial_assignment,units,watch_literals)
    pass

def unit_propagate(partial_assignment,units,watch_literals):
    while units != []:
        set_var(partial_assignment,units[-1],watch_literals)
        units.pop()
        pass
def set_var(partial_assignment,watch_literals,var):
    if var < 0:
        partial_assignment[var] = -1
    else:
        partial_assignment[var] = 1
    watched_clauses= watch_literals[-var]
    pass

clause_set = load_dimacs("8queens.txt")
print(var)
print(timeit.repeat('dpll_sat_solve(clause_set)', globals = globals(), number = 1, repeat = 1))