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
def unit_propagate2(clause_set,units = set(), units2 = set()):
    extra = False
    for clause in clause_set:
        if len(clause) == 1:
            units.add(-1*clause[0])
            units2.add(clause[0])
            extra = True
    clause = 0
    while clause < len(clause_set):
        if len(clause_set[clause]) == 0:
            return False
        if not units2.isdisjoint(set(clause_set[clause])):
            clause_set.remove(clause_set[clause])
            clause-=1
        elif not units.isdisjoint(set(clause_set[clause])):
            for i in list(units.intersection(set(clause_set[clause]))):
                clause_set[clause].remove(i)
            if len(clause_set[clause]) == 0:
                print("b")
                return False
        clause+=1
    if units != set() and not units.isdisjoint(units2) == False:
        return False
    if extra == False:
        return clause_set
    return unit_propagate2(clause_set,units,units2)
def unit_propagate4(clause_set, units =set(), units2 = set()):
    clause = 0
    extra = False
    while clause< len(clause_set):
        if len(clause_set[clause]) == 1:
            units2.add(clause_set[clause][0])
            units.add(-1*clause_set[clause][0])
            extra = True
        elif len(clause_set[clause]) == 0:
            return False
        elif not units2.isdisjoint(set(clause_set[clause])):
            clause_set.remove(clause_set[clause])
            clause-=1
        elif not units.isdisjoint(set(clause_set[clause])):
            for i in list(units.intersection(set(clause_set[clause]))):
                clause_set[clause].remove(i)
            if len(clause_set[clause]) == 0:
                return False
            if len(clause_set[clause]) == 1:
                units.add(-1*clause_set[clause][0])
                units2.add(clause_set[clause][0])
                extra = True
                clause_set.remove(clause_set[clause])
                clause-= -1
        clause+=1
    if units != set() and not units.isdisjoint(units2) == False:
        return False
    if extra == False:
        return clause_set
    return unit_propagate4(clause_set,units,units2)
def unit_propagate3(clause_set):
    units = set()
    units2 = set()
    clause = 0
    while clause < len(clause_set):
        if len(clause_set[clause]) == 1:
            units.add(-1*clause_set[clause][0])
            units2.add(clause_set[clause][0])
            clause_set.remove(clause_set[clause])
            clause = -1
        else:
            if not clause_set[clause]:
                return False
            if not units2.isdisjoint(clause_set[clause]):
                clause_set.remove(clause_set[clause])
                continue
            elif not units.isdisjoint(clause_set[clause]):
                for i in units.intersection(clause_set[clause]):
                    clause_set[clause].remove(i)
                if len(clause_set[clause]) == 1:
                    if not units.isdisjoint(clause_set[clause]):
                        return False
                    units.add(-1*clause_set[clause][0])
                    units2.add(clause_set[clause][0])
                    clause_set.remove(clause_set[clause])
                    clause = -1
                elif not clause_set[clause]:
                    return False
        clause+=1
    return clause_set
def unit_propagate5(clause_set):
    units = []
    units2 = []
    clause = 0
    while clause < len(clause_set):
        if len(clause_set[clause]) == 1:
            if clause_set[clause][0] in units:
                return False
            units.append(-1*clause_set[clause][0])
            units2.append(clause_set[clause][0])
            clause_set.remove(clause_set[clause])
            clause = -1
        else:
            if len(clause_set[clause]) == 0:
                return False
            for i in units2:
                if i in clause_set[clause]:
                    clause_set.remove(clause_set[clause])
                    continue
            for i in units:
                while -i in clause_set[clause]: 
                    clause_set[clause].remove(-i)
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

def next_var(clause_set):
    clause_set2 = list(itertools.chain.from_iterable(clause_set))
    return collections.Counter(clause_set2).most_common(1)[0][0]
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
            while not set([-1*var]).isdisjoint(clause_set2[-1]):
                clause_set2[-1].remove(-1*var)
                if clause ==[]:
                    return False
    if clause_set2 == []:
        return True
    return clause_set2
def set_var3(clause_set,var):
    clause_set2 = []
    for clause in clause_set:
        if var not in clause:
            clause_set2.append([])
            for literal in clause:
                if literal !=-1*var:
                    clause_set2[-1].append(literal)
            if not clause_set2[-1]:
                return False
    if not clause_set2:
        return True
    return clause_set2
def dpll_wiki2(clause_set,partial_assignment):
    # print(partial_assignment)
    clause_set = unit_propagate3(clause_set)
    if clause_set ==[]:
        return partial_assignment
    if not clause_set:
        return False
    # clause_set= pure_literal_elimination(clause_set)
    # partial_assignment += more_assignments
    var = next_var(clause_set)
    partial_assignment.append(var)
    clause_set2 = set_var3(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if clause_set2 == False or dpll_wiki2(clause_set2, partial_assignment) == False:
        partial_assignment.pop()
    else:
        return partial_assignment
    partial_assignment.append(var*-1)
    clause_set2 = set_var3(clause_set,partial_assignment[-1])
    if clause_set2 == True:
        return partial_assignment
    if clause_set2 == False or dpll_wiki2(clause_set2, partial_assignment) == False:
        partial_assignment.pop()
        return False
    return partial_assignment
def pure_literal_elimination(clause_set):
    flat_clause_set = [item for sublist in clause_set for item in sublist]
    clause_set2 = list(itertools.chain.from_iterable(clause_set))
    counters = collections.Counter(clause_set2)
    print(counters)
    all_literals = list(np.unique(flat_clause_set))
    set_literals = set(all_literals)
    pure_literals = set()
    for i in all_literals:
        if set_literals.isdisjoint([-1*i]):
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
        clause_set = set_var(clause_set,i)
    unit_propagate(clause_set)
    assignments = []
    for i in clause_set:
        assignments.append(i[0])
    for i in clause_set:
        if len(i) != 1:
            return False
        if -i[0] in assignments:
            return False
    return True
clause_set = load_dimacs("gt.txt")
L = [-28, -37, -29, -43, -18, -38, -12, -46, -27, -23, -49, -8, -35, -13, -55, -44, -2, -57, -24, -54, -39, -10, -59, -4, -33, -21, -30, -61, -56, -41, -26, -15, -60, -7, -45, -22, -64, -11, -34, -17, -51, -32, -1, -48, -14, 36, -42]
# print(clause_set)
# print(test(clause_set,L))
# print(dpll_wiki2(clause_set,[]))
print(np.mean(timeit.repeat('dpll_wiki2(clause_set,[])', globals = globals(), number =1, repeat = 1)))

    