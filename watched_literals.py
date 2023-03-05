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
    #get all unique variables (first flatten list of lists)
    vars = np.unique(list(itertools.chain.from_iterable(clause_set)))
    literals = list(np.unique(np.abs(vars)))
    partial_assignment = {}
    units = []
    #intialise partial assignments as a dictionary, 0 is unassigned, 1 is set to true, -1, is set to false
    for i in literals:
        partial_assignment[i] = 0
    #initialise dictionary of watched literals, key = literal, value = clauses being watched
    for i in vars:
        watch_literals[i] = []
    for i in range(len(clause_set)):
        #if length of clause is 1, append to units
        if len(clause_set[i]) == 1:
            watch_literals[clause_set[i][0]].append(clause_set[i])
            units.append(clause_set[i][0])
        else:
            watch_literals[clause_set[i][0]].append(clause_set[i])
            watch_literals[clause_set[i][1]].append(clause_set[i])
    #wrapper function needed as only initialise watched literals once
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,literals)
    #obtain list of assignments from dictionary of assignments
    full_assignment = set()
    if partial_assignment == False:
        return False
    for i in range(0,len(literals)):
        if partial_assignment[literals[i]]!=0:
            full_assignment.add(literals[i]*partial_assignment[literals[i]])
    full_assignment = list(full_assignment)
    return full_assignment
    
def dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,literals):
    if units == False:
        return False
    partial_assignment,units,watch_literals = unit_propagate(partial_assignment,units,watch_literals)
    if units == False:
        return False
    for i in literals:
        if partial_assignment[i] == 0:
            var = i
            break
        if i == literals[-1]:
            return partial_assignment
    partial_assignment2 = partial_assignment.copy()   
    units2 = units[:]
    partial_assignment,units,watch_literals = set_var2(partial_assignment, watch_literals,var,units)
    if dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,literals) == False or units == False:
        partial_assignment = partial_assignment2.copy()
        units = units2[:]
    else:
        return partial_assignment
    partial_assignment,units,watch_literals = set_var2(partial_assignment, watch_literals,-1*var,units)
    if dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,literals) == False or units == False:
        partial_assignment = partial_assignment2.copy()
        units = units2[:]
        return False
    return partial_assignment

def unit_propagate(partial_assignment,units,watch_literals):
    #set unit clauses to true until no unit clauses are left
    while units != []:
        if len(np.abs(np.unique(units))) != len(np.unique(units)):
            return partial_assignment,False,watch_literals
        partial_assignment,units,watch_literals = set_var2(partial_assignment,watch_literals,units[-1],units)
        if units == False:
            return partial_assignment,False,watch_literals
        units.pop()
    return partial_assignment,units,watch_literals
def set_var2(partial_assignment,watch_literals,var,units):
    #if variable has already been assigned, return False as it shows it is trying to be assigned to a different value => need to backtrack
    #and partial_assignment[abs(var)]*var != var
    if partial_assignment[abs(var)] != 0 and partial_assignment[abs(var)]*abs(var) != var:
        return partial_assignment,False,watch_literals
    #if var is negative, set var to -1
    if var < 0:
        partial_assignment[abs(var)] = -1
    #else set to 1
    else:
        partial_assignment[abs(var)] = 1
    if -var not in watch_literals:
        return partial_assignment,units,watch_literals
    #go through watched clauses and try to assign to a new watched literal to the clause
    for clause in watch_literals[-var]:
        potential_units = []
        for literal in clause:
            if partial_assignment[abs(literal)]*abs(literal) == literal:
                break
            isIn = clause in watch_literals[literal]
            if isIn:
                potential_units.append(literal)
            if literal != -var and partial_assignment[abs(literal)] == 0 and isIn == False:
                watch_literals[literal].append(clause)
                watch_literals[-var].remove(clause)
                break
            if literal == clause[-1]:
                if partial_assignment[abs(potential_units[0])] == 0 and partial_assignment[abs(potential_units[1])] != 0:
                    partial_assignment[abs(potential_units[0])] = int((potential_units[0])/abs(potential_units[0]))
                    units.append(potential_units[0])
                elif partial_assignment[abs(potential_units[1])] == 0:
                    partial_assignment[abs(potential_units[1])] = int((potential_units[1])/abs(potential_units[1]))
                    units.append(potential_units[1])
                elif partial_assignment[abs(potential_units[1])]*potential_units[1] < 0 and partial_assignment[abs(potential_units[0])]*potential_units[0] < 0:
                    return partial_assignment,False,watch_literals
    return partial_assignment,units,watch_literals

def set_var2(partial_assignment,watch_literals,var,units):
    #if variable has already been assigned, return False as it shows it is trying to be assigned to a different value => need to backtrack
    #and partial_assignment[abs(var)]*var != var
    if partial_assignment[abs(var)] != 0 and partial_assignment[abs(var)]*abs(var) != var:
        return partial_assignment,False,watch_literals
    #if var is negative, set var to -1
    if var < 0:
        partial_assignment[abs(var)] = -1
    #else set to 1
    else:
        partial_assignment[abs(var)] = 1
    if -var not in watch_literals:
        return partial_assignment,units,watch_literals
    #go through watched clauses and try to assign to a new watched literal to the clause
    for clause in watch_literals[-var]:
        potential_unit = 0
        for literal in clause:
            if partial_assignment[abs(literal)]*abs(literal) == literal:
                break
            isIn = clause in watch_literals[literal]
            if isIn and literal != var:
                potential_unit = literal
            if literal != -var and partial_assignment[abs(literal)] == 0 and isIn == False:
                watch_literals[literal].append(clause)
                watch_literals[-var].remove(clause)
                break
            if literal == clause[-1]:
                if partial_assignment[abs(potential_unit)] == 0:
                    partial_assignment[abs(potential_unit)] = int((potential_unit)/abs(potential_unit))
                    units.append(potential_unit)
                elif partial_assignment[abs(potential_unit)]*abs(potential_unit) != potential_unit:
                    return partial_assignment,False,watch_literals
    return partial_assignment,units,watch_literals

clause_set = load_dimacs("sat.txt")
print(dpll_sat_solve(clause_set,[]))
print(timeit.repeat('dpll_sat_solve(clause_set)', globals = globals(), number = 1, repeat = 1))