import numpy as np
import copy
import itertools
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
