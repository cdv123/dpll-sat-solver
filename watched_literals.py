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
        if temp[0] == "%":
            break
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
    last_free_var = [0]
    #get all unique variables (first flatten list of lists)
    vars = list(itertools.chain.from_iterable(clause_set))
    vars = [var[0] for var in collections.Counter(vars).most_common()]
    vars2 = []
    for i in vars:
        if -i not in vars2:
            vars2.append(i)
    literals = list(np.abs(vars))
    partial_assignment = {}
    units = []
    #intialise partial assignments as a dictionary, 0 is unassigned, 1 is set to true, -1, is set to false
    partial_assignment = dict.fromkeys(literals,0)
    #initialise dictionary of watched literals, key = literal, value = clauses being watched
    watch_literals = {key: [] for key in vars}
    clause_set = [list(clause) for clause in set(tuple(clause) for clause in clause_set)]
    units = [i[0] for  i in clause_set if len(i) == 1]
    if units == []:
        for i in range(len(clause_set)):
            watch_literals[clause_set[i][0]].append(clause_set[i])
            watch_literals[clause_set[i][1]].append(clause_set[i])
    else:
        for i in range(len(clause_set)):
            # clause_set[i] = set(clause_set[i])
            if len(clause_set[i]) == 1:
                units.append(clause_set[i][0])
            else:
                watch_literals[clause_set[i][0]].append(clause_set[i])
                watch_literals[clause_set[i][1]].append(clause_set[i])
    # try using dict comprehension
    # watch_literals = {key: [clause_set[i][0],clause_set[i][1]] for key in vars}
    #wrapper function needed as only initialise watched literals once
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var)
    #obtain list of assignments from dictionary of assignments
    if partial_assignment == False:
        return False
    return list(partial_assignment.values())
    
def dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var):
    units = unit_propagate(partial_assignment,units,watch_literals,last_free_var)
    if units == False:
        return False

    if last_free_var[0] != 0 and partial_assignment[abs(last_free_var[0])] == 0:
        var = last_free_var[0]
    else:
        for i in vars2:
            if partial_assignment[abs(i)] == 0:
                var = i
                break
            if i == vars2[-1]:
                return partial_assignment
    partial_assignment2 = partial_assignment.copy()   
    units2 = units[:]
    last_free_var2 = last_free_var[:]
    units = set_var(partial_assignment, watch_literals,var,units,last_free_var)
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var)
    if partial_assignment == False:
        partial_assignment = partial_assignment2
        units = units2
        last_free_var = last_free_var2
    else:
        return partial_assignment
    units = set_var(partial_assignment, watch_literals,-1*var,units,last_free_var)
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var)
    if partial_assignment == False:
        return False
    return partial_assignment

def unit_propagate(partial_assignment,units,watch_literals,last_free_var):
    #set unit clauses to true until no unit clauses are left
    while units != []:
        if units == False:
            return False
        units = set_var(partial_assignment,watch_literals,units[0],units,last_free_var)
        if units == False:
            return False
        units.pop(0) 
    return units

def set_var(partial_assignment,watch_literals,var,units,last_free_var):
    #if variable has already been assigned, return False as it shows it is trying to be assigned to a different value => need to backtrack
    #and partial_assignment[abs(var)]*var != var
    if partial_assignment[abs(var)] != 0 and partial_assignment[abs(var)] != var:
        return False
    partial_assignment[abs(var)] = var
    if -var not in watch_literals:
        return units
    relevantList = watch_literals[-var][:]
    #go through watched clauses and try to assign to a
    # new watched literal to the clause
    for clause in relevantList:
        if not isSat(clause,partial_assignment):
            unassigned_literals = [i for i in clause if partial_assignment[abs(i)]==0]
            #if full assignment, check if clause is sat, if it is, d
            # do nothing, else, return False
            if len(unassigned_literals) == 0:
                return False
            else:
                #if only 1 unassinged literal, 3 cases, either this is not 
                # a watch literal, then swap watch literals and add to units and assign to true
                #or, if this a watch literal, do not swap, 
                # but still add to units and assign to true
                if len(unassigned_literals) == 1:
                    if clause not in watch_literals[unassigned_literals[0]]:
                        watch_literals[unassigned_literals[0]].append(clause)
                        watch_literals[-var].remove(clause)
                    units.append(unassigned_literals[0])
                    partial_assignment[abs(unassigned_literals[0])] = unassigned_literals[0]
                #if more than 1 assigned literals, mutliple cases:
                #if both watch literals are false, swap both
                #otherwise, swap with watch literals
                else:
                    watches_clause = [i for i in clause if clause in watch_literals[i] and i != -var][0]
                    last_free_var[0] = unassigned_literals[0]
                    if partial_assignment[abs(watches_clause)] != watches_clause and partial_assignment[abs(watches_clause)] !=0:
                        watch_literals[unassigned_literals[0]].append(clause)
                        watch_literals[watches_clause].remove(clause)
                        watch_literals[unassigned_literals[1]].append(clause)
                        watch_literals[-var].remove(clause)
                    else:
                        not_watches_clause = [i for i in unassigned_literals if clause not in watch_literals[i]]
                        watch_literals[not_watches_clause[0]].append(clause)
                        watch_literals[-var].remove(clause)
    return units
def isSat(clause,partial_assignment):
    for i in clause:
        if partial_assignment[abs(i)] == i:
            return True
    return False

clause_set = load_dimacs("g250.29.cnf")
# print(dpll_sat_solve(clause_set,[]))
print(np.mean(timeit.repeat('dpll_sat_solve(clause_set)', globals = globals(), number = 1, repeat = 1)))