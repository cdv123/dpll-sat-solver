import numpy as np
import copy
import itertools
import re
import timeit
def load_DIMACS(file_name):
    example = open(file_name, "r")
    lines = example.readlines()
    clause_size=int(lines[0].split()[-1])
    maximum = int(lines[0].split()[-2])
    clause_set = []
    for i in range(0,clause_size):
        clause_set.append([])
    count = 1
    for i in range(1,len(lines)):
        temp = lines[i].split()
        if temp[0] == "c":
            count+=1
        else:
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
def unit_propogate(clause_set):
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
                if len(clause_set) > 3:
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
def unit_propogate2(clause_set):
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
                        if clause != len(clause_set)-1:
                            clause-=1
                        
            clause+=1
        i+=1
    return clause_set
# def unit_propogate3(clause_set):
#     clause = 0
#     while clause<len(clause_set):
#         if len(clause_set[clause]) == 1:
#             unit = clause_set.pop(clause_set[clause][0])
            
#     return clause_set
def find_variables(clause_set):
    all_variables =[]
    for i in clause_set:
        for j in i:
            if abs(j) not in all_variables:
                all_variables.append(abs(j))
    return all_variables
def mostCommonVariables(clause_set, all_variables):
    commonVariables = []
    for i in all_variables:
        commonVariables.append([i,0])
        for clause in clause_set:
            if i in clause or -1*i in clause:
                commonVariables[-1][1]+=1
    commonVariables = sorted(commonVariables, key = lambda x:x[1], reverse=True)
    all_variables = []
    for i in commonVariables:
        all_variables.append(i[0])
    return all_variables
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
        if var not in clause:
            clause_set2.append(copy.copy(clause))
    for clause in clause_set2:
        while -1*var in clause:
            clause.remove(-1*var)
    return clause_set2
# dpll ='''
def dpll_sat_solve(clause_set, partial_assignment):
    all_variables = find_variables(clause_set)
    all_variables = mostCommonVariables(clause_set,all_variables)
    dpll_sat_solve_wrapper(clause_set,partial_assignment,all_variables)
    print(partial_assignment)
# '''
def dpll_sat_solve_wrapper(clause_set,partial_assignment,all_variables):
    print(partial_assignment)
    if is_valid(clause_set,partial_assignment,all_variables):
        for clause in clause_set:
            if clause == []:
                return False
        if check(clause_set,partial_assignment):
            return partial_assignment
        # unit_propogate(clause_set)
        partial_assignment.append(all_variables[len(partial_assignment)])
        clause_set2 = set_var2(clause_set,partial_assignment[-1])
        if dpll_sat_solve_wrapper(clause_set2, partial_assignment) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*-1)
        clause_set2 = set_var2(clause_set,partial_assignment[-1])
        if dpll_sat_solve_wrapper(clause_set, partial_assignment) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
    return False
def dpll_sat_solve2(clause_set, partial_assignment):
    all_variables = find_variables(clause_set)
    all_variables = mostCommonVariables(clause_set,all_variables)
    dpll_sat_solve_wrapper2(clause_set,partial_assignment,all_variables)
    print(partial_assignment)
# '''
def dpll_sat_solve_wrapper2(clause_set,partial_assignment,all_variables):
    if is_valid(clause_set,partial_assignment,all_variables):
        for clause in clause_set:
            if clause == []:
                return False
        if check(clause_set,partial_assignment):
            return partial_assignment
        # unit_propogate(clause_set)
        clause_set2 = copy.deepcopy(clause_set)
        partial_assignment.append(all_variables[len(partial_assignment)])
        clause_set = set_var(clause_set,partial_assignment[-1])
        if dpll_sat_solve_wrapper2(clause_set2, partial_assignment,all_variables) == False:
            partial_assignment.pop()
            clause_set = clause_set2
        else:
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*-1)
        clause_set = set_var(clause_set,partial_assignment[-1])
        if dpll_sat_solve_wrapper2(clause_set, partial_assignment,all_variables) == False:
            partial_assignment.pop()
            clause_set = clause_set2
        else:
            return partial_assignment
    return False
def dpll_sat_solve3(clause_set, partial_assignment):
    if is_valid(clause_set,partial_assignment,all_variables):
        for clause in clause_set:
            if clause == []:
                return False
        if check(clause_set,partial_assignment):
            return partial_assignment
        unit_propogate(clause_set)
        clause_set2 = copy.deepcopy(clause_set)
        partial_assignment.append(all_variables[len(partial_assignment)])
        clause_set = set_var(clause_set,partial_assignment[-1])
        if dpll_sat_solve3(clause_set, partial_assignment) == False:
            partial_assignment.pop()
            clause_set = clause_set2
        else:
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*-1)
        clause_set = set_var(clause_set,partial_assignment[-1])
        if dpll_sat_solve3(clause_set, partial_assignment) == False:
            partial_assignment.pop()
            clause_set = clause_set2
        else:
            return partial_assignment
    return False

def dpll_sat_solve4(clause_set, partial_assignment):
    if is_valid(clause_set,partial_assignment,all_variables):
        for clause in clause_set:
            if clause == []:
                return False
        if check(clause_set,partial_assignment):
            return partial_assignment
        unit_propogate(clause_set)
        partial_assignment.append(all_variables[len(partial_assignment)])
        clause_set2 = set_var2(clause_set,partial_assignment[-1])
        if dpll_sat_solve4(clause_set2, partial_assignment) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
        partial_assignment.append(all_variables[len(partial_assignment)]*-1)
        clause_set2 = set_var2(clause_set,partial_assignment[-1])
        if dpll_sat_solve4(clause_set2, partial_assignment) == False:
            partial_assignment.pop()
        else:
            return partial_assignment
    return False

clause_set = load_DIMACS("8queens.txt")

# L = [28, 29, 36, 37, 19, 20, 21, 22, 27, 30, 35, 38, 43, 44, 45, 46]
# for i in L:
#     clause_set = set_var2(clause_set,i)
# unit_propogate3(clause_set)
# print(clause_set)
all_variables = find_variables(clause_set)
all_variables = mostCommonVariables(clause_set,all_variables)
# print(set_var2(clause_set,1))
# print(dpll_sat_solve4(clause_set,[]))
# print(check(dpll_sat_solve4))
# clause_set = set_var2(clause_set,2)
# print(clause_set)
print(timeit.repeat('dpll_sat_solve4(clause_set,[])', globals=globals(), number = 1 , repeat = 1))
clause_set = load_DIMACS("8queens.txt")
all_variables = find_variables(clause_set)
all_variables = mostCommonVariables(clause_set,all_variables)
print(timeit.repeat('dpll_sat_solve3(clause_set,[])', globals=globals(), number = 1 , repeat = 1))



    