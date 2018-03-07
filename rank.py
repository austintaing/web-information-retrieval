# Austin Taing
# CS 585 Digital Assets
# HW 4 - Rank

import numpy as np
import json

# Iterative rank algorithm
#   f - normalized stochastic matrix
#   v - initial rank vector
#   a - alpha value
def rank(f, v, a):
    l = f.shape[0]
    vi = v
    v = np.matmul(f,vi)
    i = 0
    while(sum(abs(vi-v)) > 0.000001 and i < 100):
        vi = v
        v = np.matmul(f,vi)
        i += 1
        #if i % 5 == 0:
            #v = normalize(v)
        
    return v, i

# JSON file parser
#   fname - name of data file
def parseFile(fname):
    f = open(fname, 'r')
    js = json.load(f)
    f.close()
    
    pageList = []
    for i in js:
        pageList.append(i)

    mat = np.zeros((len(js),len(js)))
    
    for i in js:
        for j in js[i]:
            if j in js:
                mat[pageList.index(j)][pageList.index(i)]=1.
    
    return mat, pageList


# Transformation from adjacency matrix into stochastic matrix
# includes random-surfer adjustment
#   a - adjacency matrix (2-d list)
def normalize(a):
    totals = np.sum(a, axis=0)
    for i in range(len(a)):
        if(totals[i]==0):
            for j in range(len(a)):
                a[j][i]=1/len(a)
        else:
            for j in range(len(a)):
                a[j][i]=a[j][i]/totals[i]
    return np.array(a)

def main():
    fname = input("File: ")
    alpha = input("Alpha: ")
    rFile = input("Output file: ")
    
    mat, pages = parseFile(fname)
    
    mat = normalize(mat)
    mat *= float(alpha)
    
    mat += (1-float(alpha))/mat.shape[0]
    
    vecI = np.ones(mat.shape[0]) / mat.shape[0]
    vecI, iters = rank(mat, vecI, float(alpha))
    
    results = []
    for i in range(len(vecI)):
        results.append((vecI[i],pages[i]))
    results.sort(key=lambda tup: tup[0], reverse=True)
    
    out = open(rFile, 'w')
    for i in range(len(vecI)):
        out.write(str(results[i][0]) + '\t' + str(results[i][1]) + '\n')
    out.write("Iterations:\t" + str(iters))
    
main()