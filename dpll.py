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
clause_set = load_dimacs("colouring/sw100-16.cnf")
L = [-161, 162, -163, -164, -165, -151, -152, -153, 154, -155, -276, 277, -278, -279, -280, 91, -92, -93, -94, -95, -251, -252, 253, -254, -255, -471, 472, -473, -474, -475, -491, -492, -493, -494, 495, -176, -177, -178, 179, -180, -241, 242, -243, -244, -245, -281, -282, -283, 284, -285, -31, 32, -33, -34, -35, -66, -67, 68, -69, -70, -186, 187, -188, -189, -190, -266, -267, -268, 269, -270, 271, -272, -273, -274, -275, 331, -332, -333, -334, -335, -371, -372, -373, -374, 375, -401, -402, -403, -404, 405, -466, -467, -468, 469, -470, 1, -2, -3, -4, -5, -11, 12, -13, -14, -15, -116, -117, -118, -119, 120, -316, -317, 318, -319, -320, -346, -347, -348, -349, 350, -361, -362, 363, -364, -365, 381, -382, -383, -384, -385, -411, -412, -413, -414, 415, -416, -417, -418, -419, 420, 41, -42, -43, -44, -45, 46, -47, -48, -49, -50, -236, -237, 238, -239, -240, -246, -247, 248, -249, -250, 256, -257, -258, -259, -260, -301, -302, -303, 304, -305, -311, 312, -313, -314, -315, -336, -337, 338, -339, -340, -341, -342, -343, 344, -345, -386, -387, 388, -389, -390, -441, -442, -443, 444, -445, -481, -482, -483, -484, 485, 61, -62, -63, -64, -65, -71, -72, -73, 74, -75, -126, -127, -128, 129, -130, -131, -132, -133, 134, -135, -191, -192, 193, -194, -195, 201, -202, -203, -204, -205, -216, 217, -218, -219, -220, -261, -262, -263, 264, -265, -286, 287, -288, -289, -290, 356, -357, -358, -359, -360, -391, -392, -393, 394, -395, 396, -397, -398, -399, -400, -406, -407, 408, -409, -410, -431, -432, 433, -434, -435, -436, -437, 438, -439, -440, -476, -477, 478, -479, -480, -486, -487, -488, -489, 490, 6, -7, -8, -9, -10, -36, -37, -38, -39, 40, 86, -87, -88, -89, -90, -101, -102, -103, 104, -105, -106, -107, 108, -109, -110, 111, -112, -113, -114, -115, -146, -147, -148, -149, 150, -156, -157, -158, 159, -160, -196, 197, -198, -199, -200, 206, -207, -208, -209, -210, -366, -367, -368, -369, 370, 421, -422, -423, -424, -425, -426, -427, 428, -429, -430, -16, 17, -18, -19, -20, -26, -27, 28, -29, -30, -166, -167, 168, -169, -170, 291, -292, -293, -294, -295, 296, -297, -298, -299, -300, -306, -307, -308, -309, 310, -321, -322, -323, 324, -325, 326, -327, -328, -329, -330, -351, -352, 353, -354, -355, -376, 377, -378, -379, -380, -451, -452, 453, -454, -455, 461, -462, -463, -464, -465, -51, -52, 53, -54, -55, 76, -77, -78, -79, -80, -81, -82, 83, -84, -85, -96, -97, -98, -99, 100, -121, -122, -123, -124, 125, -141, 142, -143, -144, -145, -226, 227, -228, -229, -230, -496, -497, -498, 499, -500, -21, 22, -23, -24, -25, -56, 57, -58, -59, -60, -181, 182, -183, -184, -185, -231, 232, -233, -234, -235, 446, -447, -448, -449, -450, -171, 172, -173, -174, -175, -211, -212, -213, 214, -215, -456, 457, -458, -459, -460, -136, -137, 138, -139, -140, -221, 222, -223, -224, -225]
print(test(clause_set,L))
# print(branching_sat_solve(clause_set,[]))
# print(np.mean(timeit.repeat('dpll_wiki2(clause_set,[])', globals = globals(), number =10, repeat = 1))/10)

    