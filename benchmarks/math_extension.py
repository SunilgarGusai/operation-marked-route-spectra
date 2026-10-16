"""Architecture-specific identities. Both are elementary matrix calculus;
not represented as invented universal theorems. Verify with exact integers.
"""
import itertools,json
from pathlib import Path
import numpy as np
import sympy as sp
import networkx as nx

def verify(run_count=60):
 rng=np.random.default_rng(20261015)
 direct=[];tested=0
 for t in range(run_count):
  n=int(rng.integers(4,8)); U=np.zeros((n,n),dtype=np.int64)
  for i in range(n-1):U[i,i+1]=1
  for i in range(n):
   for j in range(i+2,n):
    if rng.random()<.4:U[i,j]=1
  B=np.zeros_like(U);arcs=list(zip(*np.nonzero(U)))
  for a,b in arcs:
   if rng.random()<.45:B[a,b]=1
  # exact resolvent derivative / marked-route count: P B P
  P=sum((np.linalg.matrix_power(U,k) for k in range(n)),np.zeros_like(U))
  marked=P@B@P
  # independently count marked edges per directed simple path
  G=nx.DiGraph();G.add_nodes_from(range(n));G.add_edges_from(arcs)
  mark2=np.zeros((n,n),dtype=np.int64)
  for u in range(n):
   for v in range(u+1,n):
    for route in nx.all_simple_paths(G,u,v):
     mark2[u,v]+=sum(B[a,b] for a,b in zip(route[:-1],route[1:]))
  assert np.array_equal(marked,mark2)
  # test exact polynomial derivative for a few small matrices using sympy
  if t<8:
   z=sp.symbols('z');Ut=sp.Matrix(U.tolist());Bt=sp.Matrix(B.tolist())
   polynomial=sum(((Ut+z*Bt)**k for k in range(1,n)),sp.zeros(n))
   assert sp.diff(polynomial,z).subs(z,0)==sp.Matrix(marked.tolist())
  V=U.copy();nonedges=[(i,j) for i in range(n) for j in range(i+1,n) if not V[i,j]]
  if nonedges:
   a,b=nonedges[int(rng.integers(len(nonedges)))];V[a,b]=1
  def graphops(M):
   S=M+M.T;G=nx.from_numpy_array(S);assert nx.is_connected(G)
   e=np.array([nx.eccentricity(G,i) for i in range(n)])
   PP=sum((np.linalg.matrix_power(M,k) for k in range(n)),np.zeros_like(M))
   C=PP+PP.T-2*np.eye(n,dtype=np.int64)
   K=(e[:,None]+e[None,:])*C
   return PP,C,K,e
  PU,CU,KU,eu=graphops(U);PV,CV,KV,ev=graphops(V)
  norm=lambda A:np.linalg.norm(A,2)
  bound=4*norm(np.diag(eu))*norm(PU)*norm(U-V)*norm(PV)+2*norm(np.diag(eu-ev))*norm(CV)
  assert norm(KU-KV)<bound+1e-8
  assert abs(np.linalg.eigvalsh(KU)[-1]-np.linalg.eigvalsh(KV)[-1])<=bound+1e-8
  tested+=1
 return {'status':'PASS','random_exact_path_checks':tested,
   'exact_symbolic_resolvent_derivative_checks':min(8,run_count),
   'perturbation_norm_bound_checks':tested,
   'identity':'d/dt (I-U-tB)^(-1)|0 = (I-U)^(-1) B (I-U)^(-1)',
   'novelty':'Standard resolvent calculus applied to DAG operation-marked routes; not asserted as a new general identity.'}

if __name__=='__main__':
 print(json.dumps(verify(),indent=2))
