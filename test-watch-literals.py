from watched_literals import dpll_sat_solve
from dpll import test
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

# for i in range(1,1001):
#     clause_set = load_dimacs(f'newSatInstances/uf20-0{i}.cnf')
#     result = dpll_sat_solve(clause_set,[])
#     maybe = test(clause_set,result)
#     if maybe == False:
#         print(i)
#         print("False")
#     if i==1000:
#         print("True")
for i in range(1,101):
    clause_set = load_dimacs(f'colouring/sw100-{i}.cnf')
    result = dpll_sat_solve(clause_set,[])
    maybe = test(clause_set,result)
    if maybe == False:
        print(i)
        print("False")
        break
    print(i)
        