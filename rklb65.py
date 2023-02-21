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
    units = []
    units2 = []
    clause = 0
    while clause < len(clause_set):

        if len(clause_set[clause]) == 1:
            units.append(-1*clause_set[clause][0])
            units2.append(clause_set[clause][0])
            clause_set.remove(clause_set[clause])
            clause = 0
        else:
            if len(clause_set[clause]) == 0:
                return False
            if set(units2).intersection(set(clause_set[clause])) !=set():
                clause_set.remove(clause_set[clause])
                clause-=1
            elif set(units).intersection(set(clause_set[clause])) !=set():
                for i in list(set(units).intersection(set(clause_set[clause]))):
                    clause_set[clause].remove(i)
                if len(clause_set[clause]) == 1:
                    units.append(-1*clause_set[clause][0])
                    clause_set.remove(clause_set[clause])
                    clause = 0
                elif len(clause_set[clause]) == 0:
                    return False
        clause+=1
    return clause_set
# def unit_propogate3(clause_set):
#     clause = 0
#     while clause<len(clause_set):
#         if len(clause_set[clause]) == 1:
#             unit = clause_set.pop(clause_set[clause][0])
            
#     return clause_set
def find_variables(clause_set, all_variables = []):
    clause_set2 = []
    for clause in clause_set:
        for literal in clause:
            clause_set2.append(abs(literal))
    most_common = np.unique(clause_set2)
    # most_common, counts = np.unique(clause_set2,return_counts = True)
    # pairs = [(most_common[i],counts[i]) for i in range(len(most_common))]
    # pairs.sort(key=lambda x:x[0], reverse=True)
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
        if var not in clause:
            clause_set2.append(copy.copy(clause))
            if -1*var in clause_set2[-1]:
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
# dpll ='''


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
def dpll_wiki(clause_set,partial_assignment):
    all_variables = find_variables(clause_set)
    partial_assignment = dpll_wiki_wrapper(clause_set,partial_assignment,all_variables)
    return partial_assignment
def dpll_wiki_wrapper(clause_set,partial_assignment,all_variables):
    if clause_set ==[]:
        return partial_assignment
    if [] in clause_set:
        return False
    unit_propagate(clause_set)
    partial_assignment.append(all_variables[len(partial_assignment)])
    clause_set2 = set_var2(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if dpll_wiki_wrapper(clause_set2, partial_assignment,all_variables) == False:
        partial_assignment.pop()
    else:
        return partial_assignment
    partial_assignment.append(all_variables[len(partial_assignment)]*-1)
    clause_set2 = set_var2(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if dpll_wiki_wrapper(clause_set2, partial_assignment,all_variables) == False:
        partial_assignment.pop()
    else:
        return partial_assignment
    return False
def dpll_wiki2(clause_set,partial_assignment):
    clause_set2 = copy.deepcopy(clause_set)
    all_variables = find_variables(clause_set)
    partial_assignment = list(dpll_wiki_wrapper2(clause_set,partial_assignment,all_variables))
    for i in partial_assignment:
        if i ==0:
            partial_assignment.remove(i)
        clause_set2 = set_var2(clause_set2,i)
    return partial_assignment
def dpll_wiki_wrapper2(clause_set,partial_assignment,all_variables):
    
    if clause_set ==[]:
        return partial_assignment
    if [] in clause_set:
        return False
    clause_set = unit_propagate2(clause_set)
    if [] in clause_set:
        return False
    all_variables = find_variables(clause_set,all_variables)
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
    
    return

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
clause_set = load_DIMACS("1.cnf")
# clause_set = set_var(clause_set,1)
# clause_set = set_var(clause_set,11)
# clause_set = set_var(clause_set,21)

# clause_set = unit_propagate(clause_set)
# L = [1, 2, -3, 4, 5, -6, -7, -8, -9, 14, 15, 20]
# for i in L:
#     clause_set = set_var2(clause_set,i)
# unit_propagate(clause_set)
# print(clause_set)
print(dpll_wiki2(clause_set,[]))
# clause_set2 = copy.deepcopy(clause_set)
# print(timeit.repeat('dpll_wiki2(clause_set,[])', globals = globals(), number =1, repeat = 1))

    