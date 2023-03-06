import numpy as np
import copy
import itertools
import collections
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
    vars = list(itertools.chain.from_iterable(clause_set))
    vars = [var[0] for var in collections.Counter(vars).most_common()]
    vars2 = []
    for i in vars:
        if -i not in vars2:
            vars2.append(i)
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
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2)
    #obtain list of assignments from dictionary of assignments
    full_assignment = []
    if partial_assignment == False:
        return False
    for i in range(0,len(literals)):
        full_assignment.append(partial_assignment[literals[i]])
    return full_assignment
    
def dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2):
    partial_assignment,units,watch_literals = unit_propagate(partial_assignment,units,watch_literals)
    if units == False:
        return False
    assigned = [i for i in partial_assignment.values() if i !=0]
    if len(assigned) == len(vars2):
        return partial_assignment
    for i in vars2:
        if partial_assignment[abs(i)] == 0:
            var = i
            break
    partial_assignment2 = partial_assignment.copy()   
    units2 = units[:]
    partial_assignment,units,watch_literals = set_var(partial_assignment, watch_literals,var,units)
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2)
    if partial_assignment == False:
        partial_assignment = partial_assignment2
        units = units2
    else:
        return partial_assignment
    partial_assignment,units,watch_literals = set_var(partial_assignment, watch_literals,-1*var,units)
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2)
    if partial_assignment == False:
        return False
    return partial_assignment

def unit_propagate(partial_assignment,units,watch_literals):
    #set unit clauses to true until no unit clauses are left
    while units != []:
        if len(np.abs(np.unique(units))) != len(np.unique(units)):
            return partial_assignment,False,watch_literals
        partial_assignment,units,watch_literals = set_var(partial_assignment,watch_literals,units[0],units)
        if units == False:
            return partial_assignment,False,watch_literals
        units.pop(0) 
    return partial_assignment,units,watch_literals

def set_var(partial_assignment,watch_literals,var,units):
    #if variable has already been assigned, return False as it shows it is trying to be assigned to a different value => need to backtrack
    #and partial_assignment[abs(var)]*var != var
    if partial_assignment[abs(var)] != 0 and partial_assignment[abs(var)] != var:
        return partial_assignment,False,watch_literals
    #if var is negative, set var to -1
    if var < 0:
        partial_assignment[abs(var)] = var
    #else set to 1
    else:
        partial_assignment[abs(var)] = var
    if -var not in watch_literals:
        return partial_assignment,units,watch_literals
    clause = 0
    #go through watched clauses and try to assign to a new watched literal to the clause
    while clause < len(watch_literals[-var]):
        if not isSat(watch_literals[-var][clause],partial_assignment):
            unassigned_literals = [i for i in watch_literals[-var][clause] if partial_assignment[abs(i)]==0]
            #if full assignment, check if clause is sat, if it is, do nothing, else, return False
            if len(unassigned_literals) == 0:
                return partial_assignment,False,watch_literals
            else:
                not_watches_clause = [i for i in unassigned_literals if watch_literals[-var][clause] not in watch_literals[i]]
                watches_clause = [i for i in watch_literals[-var][clause] if watch_literals[-var][clause] in watch_literals[i] and i != -var][0]
                #if only 1 unassinged literal, 3 cases, either this is not a watch literal, then swap watch literals and add to units and assign to true
                #or, if this a watch literal, do not swap, but still add to units and assign to true
                if len(unassigned_literals) == 1:
                    if unassigned_literals[0] != watches_clause:
                        watch_literals[unassigned_literals[0]].append(watch_literals[-var][clause])
                        watch_literals[-var].remove(watch_literals[-var][clause])
                        clause-=1
                        units.append(unassigned_literals[0])
                        partial_assignment[abs(unassigned_literals[0])] = unassigned_literals[0]
                    # elif partial_assignment[abs(watches_clause[0])]*abs(watches_clause[0]) != watches_clause[0] and partial_assignment[abs(watches_clause[0])] !=0:
                    #     return partial_assignment,False,watch_literals
                    else:
                        units.append(unassigned_literals[0])
                        partial_assignment[abs(unassigned_literals[0])] = unassigned_literals[0]
                #if more than 1 assigned literals, mutliple cases:
                #if both watch literals are false, swap both
                #otherwise, swap with watch literals
                else:
                    if partial_assignment[abs(watches_clause)] != watches_clause and partial_assignment[abs(watches_clause)] !=0:
                        watch_literals[unassigned_literals[0]].append(watch_literals[-var][clause])
                        watch_literals[watches_clause].remove(watch_literals[-var][clause])
                        watch_literals[unassigned_literals[1]].append(watch_literals[-var][clause])
                        watch_literals[-var].remove(watch_literals[-var][clause])
                        clause-=1
                    else:
                        watch_literals[not_watches_clause[0]].append(watch_literals[-var][clause])
                        watch_literals[-var].remove(watch_literals[-var][clause])
                        clause-=1
        clause+=1
    return partial_assignment,units,watch_literals
def isSat(clause,partial_assignment):
    for i in clause:
        if partial_assignment[abs(i)] == i:
            return True
    return False
clause_set = load_dimacs("8queens.txt")
print(dpll_sat_solve(clause_set,[]))
print(np.mean(timeit.repeat('dpll_sat_solve(clause_set)', globals = globals(), number = 1, repeat = 1)))