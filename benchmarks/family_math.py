"""Exact baseline/witness definitions for Phase 7: 3-layer architecture path spectra.
Definitions are repeated locally so this package is independent of Phase 6 paths.
"""
from itertools import combinations
from collections import deque
import numpy as np
import sympy as sp
import networkx as nx

N=7
EDGES_A=((0,2),(0,3),(1,3),(0,6),(1,4),(2,5),(3,4))
EDGES_B=((0,2),(1,3),(0,6),(1,4),(2,4),(2,5),(3,4))
EXPECTED_EA=(2,4,3,3,4,4,3)
EXPECTED_EB=(3,4,2,4,3,3,4)

def graph(edges):
    U=np.zeros((N,N),dtype=np.int64)
    for i,j in edges:
        assert i<j and not U[i,j]
        U[i,j]=1
    assert not np.any(U@U@U)
    G=nx.Graph();G.add_nodes_from(range(N));G.add_edges_from(edges)
    assert nx.is_connected(G)
    e=np.array([nx.eccentricity(G,v) for v in range(N)],dtype=np.int64)
    A=U+U.T
    P=U@U+(U@U).T
    B=A*(e[:,None]+e[None,:])
    return {'U':U,'A':A,'P':P,'B':B,'G':G,'e':e,'edges':edges}

def sym(M):
    return sp.Matrix(np.asarray(M,dtype=np.int64).tolist())

def base_pencil(d,z):
    return sym(d['A'])+z*sym(d['P'])

def weighted_pencil(d,z):
    ee=sp.diag(*map(int,d['e']))
    H=base_pencil(d,z)
    return ee*H+H*ee

def numeric_blown(d,s):
    assert isinstance(s,int) and s>=1
    U=np.kron(d['U'],np.ones((s,s),dtype=np.int64))
    T=U+U@U
    C=T+T.T
    A=U+U.T
    e=np.repeat(d['e'],s)
    K=C*(e[:,None]+e[None,:])
    B=A*(e[:,None]+e[None,:])
    return {'U':U,'T':T,'C':C,'A':A,'e':e,'K':K,'B':B}

def pc(M):
    return [int(v) for v in sym(M).charpoly().all_coeffs()]
