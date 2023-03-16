import numpy as np
import itertools
import collections
import timeit
# Q4 imports text file and makes clause set a list of lists
def load_dimacs(file_name):
    example = open(file_name, "r")
    lines = example.readlines()
    clause_set = []
    count = 0
    for i in range(0,len(lines)):
        temp = lines[i].split()
        # if line begins with p or c, skip
        if temp[0] == "p":
            count+=1
        elif temp[0] == "c":
            count+=1
        #else, make a new list and append the numbers on that line except 0
        else:
            clause_set.append([])
            for j in range(0, len(temp)-1):
                clause_set[i-count].append(int(temp[j]))
    return clause_set
# Verifies that every clause is sat, and hence that the clause set is sat as a result
def check(clause_set, truth_assignment):
    for clause in clause_set:
        for literal in clause:
            if literal in truth_assignment:
                break
            elif literal == clause[-1]:
                return False
    return True
# Q5 - simple sat solve
def simple_sat_solve(clause_set):
    all_variables = []
    for i in clause_set:
        for j in i:
            if abs(j) not in all_variables:
                all_variables.append(abs(j))
    # find all combinations of true and false (1,-1) for the variables
    L = list(itertools.product([-1,1], repeat= len(all_variables)))
    # iterate through it and check that it works, if none found, return false, else return the assignment that worked
    for num in L:
        truth_assignment = []
        for digit in range(0,len(num)):
            truth_assignment.append(num[digit]*all_variables[digit])
        if check(clause_set, truth_assignment) == True:
            return truth_assignment
    return False

# Using the most common variable heuristic, counts how much each each literal appears and returns the most common one
def next_var(clause_set):
    clause_set2 = list(itertools.chain.from_iterable(clause_set))
    return collections.Counter(clause_set2).most_common(1)[0][0]

# Q6 - branching_sat_solve, checks if clause is sat or unsat, if not yet sat or unsat, branches on variable
def branching_sat_solve(clause_set,partial_assignment):
    clause_set = unit_propagate(clause_set)
    #since each time a clause is sat, it is removed, an empty list means the clause is sat
    if clause_set ==[]:
        return partial_assignment
    if clause_set == False:
        return False
    # calls next var function to branch on the most common variable
    var = next_var(clause_set)
    partial_assignment.append(var)
    # set var to true
    clause_set2 = set_var2(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if clause_set2 == False or branching_sat_solve(clause_set2, partial_assignment) == False:
        # backtrack by removing latest assignment
        partial_assignment.pop()
    else:
        return partial_assignment
    partial_assignment.append(var*-1)
    # set -1 * var to true 
    clause_set2 = set_var2(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if clause_set2 == False or branching_sat_solve(clause_set2, partial_assignment) == False:
        # backtrack by removing latest assignment
        partial_assignment.pop()
        return False
    return partial_assignment
def set_var2(clause_set,var):
    # creates new clause set which has no clauses with the variable, and no literals with -1 times the variable
    clause_set2 = []
    for clause in clause_set:
        if var not in clause:
            clause_set2.append([])
            for literal in clause:
                if literal !=-1*var:
                    clause_set2[-1].append(literal)
            if not clause_set2[-1]:
                return False
    return clause_set2

# Q7 - unit propagate, without watch literal implementation, wrapper used to initialise the dictionary of watch literals
def unit_propagate(clause_set):
    # first make a set of all units by using a list comprehension and then turning that into a set
    units = set([clause[0] for clause in clause_set if len(clause)==1])
    # if there are no units, then return the clause_set as nothing needs to be done
    if units == set():
        return clause_set
    # then make set of -1*units for use later
    units2 = set([-clause[0] for clause in clause_set if len(clause)==1])
    # initialise clause for while loop
    clause = 0
    while clause < len(clause_set):
        if len(clause_set[clause]) == 1:
            if clause_set[clause][0] not in units:
                # if new unit is found, add to set of units and units2, then reset counter to -1 in case any clauses had that literal before
                units.add(clause_set[clause][0])
                units2.add(-clause_set[clause][0])
                clause_set.remove(clause_set[clause])
                clause = -1
            else:
                #if unit found that was already found in the set of units before hand, remove it and continue to next clause
                clause_set.remove(clause_set[clause])
                continue
        else:
            # else, if any elements in the clause have an element in common with the set of units, remove it and continue to next clause
            if not units.isdisjoint(clause_set[clause]):
                clause_set.remove(clause_set[clause])
                continue
            else:
                # else if any elements in the clause have an element in common with the set of -1*units, remove those elements
                if not units2.isdisjoint(clause_set[clause]):
                    intersection = units2.intersection(clause_set[clause])
                    clause_set[clause] = [i for i in clause_set[clause] if i not in intersection]
                    # check if unit was just created, if so, add to set of units and units2, remove it and reset clause to -1 in case any clauses had that literal before
                    if len(clause_set[clause]) == 1:
                        units.add(clause_set[clause][0])
                        units2.add(-clause_set[clause][0])
                        clause_set.remove(clause_set[clause])
                        clause = -1
        clause+=1   
    return clause_set
                
# Q8 - dpll_sat_solve, implemented using watch literals, with the heuristic of last free variable being used
# Papers / sources used for learning about watched literals and LEFV:
# https://school.a4cp.org/summer2011/slides/Gent/SATCP3.pdf
# https://dspace.mit.edu/bitstream/handle/1721.1/37691/129947026-MIT.pdf?sequence=2
# https://www.researchgate.net/figure/The-2-watching-literal-method-The-watched-literals-are-are-x-6-and-x-8-Variable-x-6_fig3_220565739
# https://baldur.iti.kit.edu/sat/files/2018/l05.pdf
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
    clause_set = (list(map(list,set(map(tuple,clause_set)))))
    #intialise partial assignments as a dictionary, 0 is unassigned, 1 is set to true, -1, is set to false
    partial_assignment = dict.fromkeys(literals,0)
    #initialise dictionary of watched literals, key = literal, value = clauses being watched
    watch_literals = {key: [] for key in vars}
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
    #wrapper function needed as only initialise watched literals once
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var)
    #obtain list of assignments from dictionary of assignments
    if partial_assignment == False:
        return False
    return list(partial_assignment.values())
    
def dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var):
    #generic dpll structure, first, units propagate
    units = unit_propagate2(partial_assignment,units,watch_literals,last_free_var)
    if units == False:
        return False
    #if last free variable found, use it as the next variable, as according to LEFV 
    if last_free_var[0] != 0 and partial_assignment[abs(last_free_var[0])] == 0:
        var = last_free_var[0]
    #else, go back to most common variable heusitic
    else:
        for i in vars2:
            if partial_assignment[abs(i)] == 0:
                var = i
                break
            if i== vars2[-1]:
                return partial_assignment
    #shallow copy partial_assignment, units and last free var for backtracking
    partial_assignment2 = partial_assignment.copy()   
    units2 = units[:]
    last_free_var2 = last_free_var[:]
    #set var to true 
    units = set_var(partial_assignment, watch_literals,var,units,last_free_var)
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var)
    if partial_assignment == False:
        #if false, then backtrack, hence restore previous partial_assignmnet, units, and last_free_var
        partial_assignment = partial_assignment2
        units = units2
        last_free_var = last_free_var2
    else:
        return partial_assignment
    #set -var to true
    units = set_var(partial_assignment, watch_literals,-1*var,units,last_free_var)
    partial_assignment = dpll_sat_solve_wrapper(partial_assignment,units,watch_literals,vars2,last_free_var)
    if partial_assignment == False:
        #if still false, return false as both false for var and -var
        return False
    return partial_assignment

def unit_propagate2(partial_assignment,units,watch_literals,last_free_var):
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
        #if clause is sat, skip and go to next clause
        if not isSat(clause,partial_assignment):
            unassigned_literals = [i for i in clause if partial_assignment[abs(i)]==0]
            #if full assignment, check if clause is sat, if it is, d
            # do nothing, else, return False
            if len(unassigned_literals) == 0:
                return False
            else:
                #for loop to find which literal is being watched other that -var
                for i in clause:
                    if clause in watch_literals[i] and i!= -var:
                        watches_clause = i
                        break
                #if only 1 unassinged literal, 3 cases, either this is not 
                # a watch literal, then swap watch literals and add to units and assign to true
                #or, if this a watch literal, do not swap, 
                # but still add to units and assign to true
                if len(unassigned_literals) == 1:
                    if unassigned_literals[0] != watches_clause:
                        watch_literals[unassigned_literals[0]].append(clause)
                        watch_literals[-var].remove(clause)
                    units.append(unassigned_literals[0])
                    partial_assignment[abs(unassigned_literals[0])] = unassigned_literals[0]
                #if more than 1 assigned literals, mutliple cases:
                #if both watch literals are false, swap both
                #otherwise, swap with watch literals
                else:
                    #make last seen variable the last free variable for the heuristic
                    last_free_var[0] = unassigned_literals[0]
                    if partial_assignment[abs(watches_clause)] != watches_clause and partial_assignment[abs(watches_clause)] !=0:
                        watch_literals[unassigned_literals[0]].append(clause)
                        watch_literals[watches_clause].remove(clause)
                        watch_literals[unassigned_literals[1]].append(clause)
                        watch_literals[-var].remove(clause)
                    else:
                        #for loop to find which of the unassigned literals is not a watched literal
                        for i in unassigned_literals:
                            if clause not in watch_literals[i]:
                                not_watches_clause = i
                                break
                        watch_literals[not_watches_clause].append(clause)
                        watch_literals[-var].remove(clause)
    return units
def isSat(clause,partial_assignment):
    # go through the clause, if a literal is assigned to true, then return True as it is sat, else if none is found, return false.
    for i in clause:
        if partial_assignment[abs(i)] == i:
            return True
    return False