import numpy as np
import copy
import itertools
import re
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

def check(clause_set, truth_assignment):
    for clause in clause_set:
        for literal in clause:
            if literal in truth_assignment:
                break
            elif literal == clause[-1]:
                return False
    return True
def is_valid(clause_set,partial_assignment, all_variables):
    if check(clause_set, partial_assignment) == True or len(partial_assignment) < len(all_variables):
        return True
    return False
def simple_sat_solve(clause_set):
    all_variables = []
    for i in clause_set:
        for j in i:
            if abs(j) not in all_variables:
                all_variables.append(abs(j))
    L = list(itertools.product([-1,1], repeat= len(all_variables)))
    for num in L:
        truth_assignment = []
        for digit in range(0,len(num)):
            truth_assignment.append(num[digit]*all_variables[digit])
        if check(clause_set, truth_assignment) == True:
            return truth_assignment
    return False

def branching_sat_solve(clause_set, partial_assignment):
    all_variables = []
    for i in clause_set:
        for j in i:
            if abs(j) not in all_variables:
                all_variables.append(abs(j))
    if is_valid(clause_set, partial_assignment, all_variables):
        if check(clause_set,partial_assignment):
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*1)
        if branching_sat_solve(clause_set, partial_assignment) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*-1)
        if branching_sat_solve(clause_set, partial_assignment) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
            
    return False
def unit_propagate(clause_set):
    assignments = []
    i = 0
    while i < len(clause_set):
        if len(clause_set[i]) == 1:
            unit = clause_set[i][0]
            clause_set.remove(clause_set[i])
            assignments.append(unit)
            i-=1

        i +=1 
    i = 0
    while i < len(assignments):
        clause = 0
        
        while clause < len(clause_set):
            if assignments[i] in clause_set[clause]:
                clause_set.remove(clause_set[clause])
                if clause != len(clause_set)-1:
                    clause-=1
            else:
                # if len(clause_set) > 3:
                    while assignments[i]*-1 in clause_set[clause]:
                        clause_set[clause].remove(assignments[i]*-1)
                        if len(clause_set[clause]) == 1:
                            assignments.append(clause_set[clause][0])
                            clause_set.remove(clause_set[clause])
                            if clause != len(clause_set)-1:
                                clause-=1
                        
            clause+=1
        i+=1

    for i in assignments:
        clause_set.append([i])
    assignments = []
    return clause_set
def unit_propagate2(clause_set):
    assignments = []

    i = 0
    while i < len(clause_set):
        if len(clause_set[i]) == 1:
            assignments.append(clause_set[i][0])
            clause_set.remove(clause_set[i])
            i-=1
        i +=1 
    i = 0
    while i < len(assignments):
        clause = 0
        # if assignments[i] and assignments[i]*-1 in assignments:
        #     return [[]]
        while clause < len(clause_set):
            if assignments[i] in clause_set[clause]:
                clause_set.remove(clause_set[clause])
                if clause != len(clause_set)-1:
                    clause-=1
            else:
                while assignments[i]*-1 in clause_set[clause]:
                    clause_set[clause].remove(assignments[i]*-1)
                    if len(clause_set[clause]) == 1:
                        assignments.append(clause_set[clause][0])
                        clause_set.remove(clause_set[clause])
                        if clause == len(clause_set):
                            clause-=1
                    if len(clause_set) == 0:
                        break

                    
            clause+=1
        i+=1
    for i in assignments:
        if i and -i in assignments:

            return [[]]
    return clause_set
def unit_propagate3(clause_set):
    units = set()
    units2 = set()
    clause = 0
    while clause < len(clause_set):
        if len(clause_set[clause]) == 1:
            if not set(clause_set[clause]).isdisjoint(set(units)):
                return False
            units.add(-1*clause_set[clause][0])
            units2.add(clause_set[clause][0])
            clause_set.remove(clause_set[clause])
            clause = -1
        else:
            if len(clause_set[clause]) == 0:
                return False
            if not units2.isdisjoint(set(clause_set[clause])):
                clause_set.remove(clause_set[clause])
                clause-=1
            elif not units.isdisjoint(set(clause_set[clause])):
                for i in list(units.intersection(set(clause_set[clause]))):
                    clause_set[clause].remove(i)
                if len(clause_set[clause]) == 1:
                    if not set(clause_set[clause]).isdisjoint(units):
                        return False
                    units.add(-1*clause_set[clause][0])
                    units2.add(clause_set[clause][0])
                    clause_set.remove(clause_set[clause])
                    clause = -1
                elif len(clause_set[clause]) == 0:
                    return False
        clause+=1
    return clause_set
def find_variables(clause_set):
    clause_set2 = np.concatenate(clause_set).ravel().tolist()
    for i in clause_set2:
        i = abs(i)
    # most_common = np.unique(clause_set2)
    most_common, counts = np.unique(clause_set2,return_counts = True)
    most_common = [x for _,x in sorted(zip(counts,most_common), reverse=True)]
    # all_variables = np.append(all_variables,most_common)
    return most_common
def set_var(clause_set,var):
    clause = 0
    while clause < len(clause_set):
        if var in clause_set[clause]:
            clause_set.remove(clause_set[clause])
            if clause != len(clause_set)-1:
                clause-=1
        else:
            while -1*var in clause_set[clause]:
                clause_set[clause].remove(var*-1)
        clause+=1
    return clause_set
def set_var2(clause_set,var):
    clause_set2 = []
    for clause in clause_set:
        if not set([var]).isdisjoint(set(clause)):
            clause_set2.append(copy.copy(clause))
            if not set([-1*var]).isdisjoint(set(clause_set2[-1])):
                clause_set2[-1].remove(-1*var)
                if clause ==[]:
                    return False
    return clause_set2
def set_var3(clause_set,var):
    clause_set2 = []
    for clause in clause_set:
        if var not in clause:
            clause_set2.append([])
            for literal in clause:
                if literal !=-1*var:
                    clause_set2[-1].append(literal)
            if clause_set2[-1] == []:
                return False
    if clause_set2 == []:
        return True
    return clause_set2


def dpll_sat_solve4(clause_set,partial_assignment):
    all_variables = find_variables(clause_set)
    partial_assignment = dpll_sat_solve4_wrapper(clause_set,partial_assignment,all_variables)
    return partial_assignment
def dpll_sat_solve4_wrapper(clause_set, partial_assignment,all_variables):
    if is_valid(clause_set,partial_assignment,all_variables):
        for clause in clause_set:
            if clause == []:
                return False
        if check(clause_set,partial_assignment):
            return partial_assignment
        unit_propagate(clause_set)
        partial_assignment.append(all_variables[len(partial_assignment)])
        clause_set2 = set_var2(clause_set,partial_assignment[-1])
        if not clause_set2 or dpll_sat_solve4_wrapper(clause_set2, partial_assignment,all_variables) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*-1)
        clause_set2 = set_var2(clause_set,partial_assignment[-1])
        if not clause_set2 or dpll_sat_solve4_wrapper(clause_set2, partial_assignment,all_variables) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
    return False
def dpll_wiki2(clause_set,partial_assignment):
    all_variables = find_variables(clause_set)
    partial_assignment = dpll_wiki_wrapper2(clause_set,partial_assignment,all_variables)
    if partial_assignment == False:
        return False
    return partial_assignment
def dpll_wiki_wrapper2(clause_set,partial_assignment,all_variables):
    clause_set = unit_propagate3(clause_set)
    if clause_set ==[]:
        return partial_assignment
    if not clause_set:
        return False
    # clause_set= pure_literal_elimination(clause_set)
    # partial_assignment += more_assignments
    if clause_set ==[]:
        return partial_assignment
    all_variables = find_variables(clause_set)
    var = 0
    for i in all_variables:
        if i not in partial_assignment:
            var = i
            break
    partial_assignment.append(var)
    clause_set2 = set_var3(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if clause_set2 == False or dpll_wiki_wrapper2(clause_set2, partial_assignment,all_variables) == False:
        partial_assignment.pop()
    else:
        return partial_assignment
    partial_assignment.append(var*-1)
    clause_set2 = set_var3(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if clause_set2 == False or dpll_wiki_wrapper2(clause_set2, partial_assignment,all_variables) == False:
        partial_assignment.pop()
        return False
    else:
        return partial_assignment
def pure_literal_elimination(clause_set):
    flat_clause_set = [item for sublist in clause_set for item in sublist]
    all_literals = list(np.unique(flat_clause_set))
    set_literals = set(all_literals)
    pure_literals = set()
    for i in all_literals:
        if set_literals.isdisjoint(set([-1*i])):
            pure_literals.add(i)
            # partial_asignment2.append(i)
    if pure_literals == set():
        return clause_set
    clause = 0
    while clause < len(clause_set):
        if not set(clause_set[clause]).isdisjoint(pure_literals):
            clause_set.remove(clause_set[clause])
            clause-=1
        clause+=1
    return pure_literal_elimination(clause_set)
def test(clause_set,L):
    for i in L:
        clause_set = set_var3(clause_set,i)
        if clause_set == True or clause_set == False:
            break
    # unit_propagate(clause_set)
    return clause_set
    # assignments = []
    # for i in clause_set:
    #     assignments.append(i[0])
    # for i in clause_set:
    #     if len(i) != 1:
    #         return False
    #     if -i[0] in assignments:
    #         return False
    # return True

def branch(clause_set,partial_assignment,all_variables):
    var = all_variables[len(partial_assignment)]
    clause_set2 = []
    clause_set3 = []
    for clause in clause_set:
        if var not in clause:
            clause_set2.append([])
            for literal in clause:
                if literal !=-1*var:
                    clause_set2[-1].append(literal)
        if -1*var not in clause:
            clause_set3.append([])
            for literal in clause:
                if literal !=var:
                    clause_set3[-1].append(literal)
    if [] in clause_set2 and [] in clause_set3 :
        return False
    partial_assignment.append(var)
    
    if [] in clause_set2 or dpll_wiki_wrapper2(clause_set2,partial_assignment,all_variables) == False:
        partial_assignment.pop()
    else:
        return partial_assignment
    partial_assignment.append(-1*var)
    if [] in clause_set3 or dpll_wiki_wrapper2(clause_set3,partial_assignment,all_variables) == False:
        partial_assignment.pop()
        return False
    else:
        return partial_assignment
# clause_set = load_dimacs("8queens.txt")
# L = [-28, -37, -29, -36, -19, -46, -20, -38, -21, -27, -30, -35, -43, -22, -44, -45, -10, -55, -11, -18, -26, -34, 42, -47, -50, 12, -39, -51, -13, -31, -52, -14, 23, 53, -15, -54, -1, -2, -3, -4, -5, 6, -7, -8, -9, -17, 25, -33, -41, -49, -57, -64, -56, -58, -48, 59, 40, -60, -32, -61, -24, -62, -16, -63]
# print(test(clause_set,L))
# print(branching_sat_solve(clause_set,[]))
# print(np.mean(timeit.repeat('dpll_wiki2(clause_set,[])', globals = globals(), number =10, repeat = 1))/10)

    