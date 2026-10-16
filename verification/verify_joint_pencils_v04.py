"""Independent exact matrix-pencil verification, VELE09 version 0.4.

Does not access NAS data or change v0.3 results.
"""
from pathlib import Path
import hashlib, json, platform, sympy as sp, networkx as nx
import verify_v03 as new
import verify_extension_v02 as old
ROOT = Path(__file__).resolve().parent
x,z,t,s=sp.symbols('x z t s')

def family_matrices(which, side):
    if which=='I':
        return {op:{key:old.matrices(side,op)[nm] for key,nm in (('H','C'),('W','W'),('L','L'))} for op in ('alpha','beta')}
    d=new.compute(new.A_ARCS if side=='A' else new.B_ARCS, new.A_ALPHA if side=='A' else new.B_ALPHA)
    return {op:{key:d[op][key] for key in ('H','W','L')} for op in ('alpha','beta')}

def graph_isomorphic_weighted_pair(M,N):
    def build(X):
        G=nx.Graph();G.add_nodes_from(range(7))
        for i in range(7):
            for j in range(i+1,7):
                weight=(str(sp.expand(X['alpha'][i,j])),str(sp.expand(X['beta'][i,j])))
                if weight!=('0','0'):G.add_edge(i,j,combo=weight)
        return G
    gm=nx.isomorphism.GraphMatcher(build(M),build(N), edge_match=lambda e,f:e['combo']==f['combo'])
    return gm.is_isomorphic(), next(gm.isomorphisms_iter(),None)

result={'protocol':'Exact SymPy polynomial determinant and trace verification; no ML/holdout access',
        'python':platform.python_version(),'sympy':sp.__version__, 'networkx':nx.__version__, 'comparisons':{}}
for which in ('I','II'):
    a=family_matrices(which,'A');b=family_matrices(which,'B')
    output={}
    for key in ('H','W'):
        ma=a['alpha'][key]+t*a['beta'][key]
        mb=b['alpha'][key]+t*b['beta'][key]
        pA=sp.Poly(ma.charpoly(x).as_expr(),x,z,t)
        pB=sp.Poly(mb.charpoly(x).as_expr(),x,z,t)
        diff=sp.factor(pA.as_expr()-pB.as_expr())
        output[key]={'joint_cospectral_as_polynomial': diff==0, 'difference':str(diff),
                     'coefficient_count_A':len(pA.terms()),'coefficient_count_B':len(pB.terms())}
        if which=='I':assert diff==0,(which,key,diff)
        if which=='II' and key=='H':
            expected=-2*t**2*z*(x-t)*(x+t)*(t**2+2*t*x*z+t*x+t-x)
            assert sp.expand(diff-expected)==0
            assert sp.expand(diff.subs(t,1)+4*z*(x**2-1)*(x*z+1))==0
        if which=='II' and key=='W':assert diff==0
        similar,mp=graph_isomorphic_weighted_pair({c:a[c][key] for c in ('alpha','beta')}, {c:b[c][key] for c in ('alpha','beta')})
        output[key].update({'simultaneous_permutation_equivalence':similar,'permutation_map':mp})
        if which=='I' and key=='H':assert not similar
        if key=='W':assert similar
    al=a['alpha']['L'];bl=b['alpha']['L'];be=a['beta']['L'];bb=b['beta']['L']
    cross=sp.factor(sp.trace(al*be)-sp.trace(bl*bb))
    red=sp.factor(sp.trace((al+t*be)**2)-sp.trace((bl+t*bb)**2))
    output['weighted']={'mixed_trace_gap':str(cross),'reduced_trace_gap':str(red),'cloned_trace_gap':str(sp.factor(s**2*red.subs(z,s)))}
    if which=='I':
        assert cross==30*z*(z+1)
        expected=30*s**3*(s+2*t*(s+1)+t**2*(s+2))
        assert sp.expand(s**2*red.subs(z,s)-expected)==0
        # Positivity is immediate for s>0 and t>=0 from all-positive coefficient representation.
        output['weighted']['positivity_domain']='s positive integer, t real nonnegative; every summand positive or nonnegative'
    if which=='II':
        assert cross==-22*z**2
    result['comparisons'][which]=output
# At width one, even one fixed orthogonal/similarity switch cannot intertwine
# both route-operation matrices: exact stacked linear map has trivial kernel.
A=family_matrices('I','A');B=family_matrices('I','B')
rows=[]
for op in ('alpha','beta'):
    u=A[op]['H'].subs(z,1); w=B[op]['H'].subs(z,1)
    for i in range(7):
        for j in range(7):
            row=[0]*49
            for k in range(7):
                row[7*k+j]+=int(u[i,k])
                row[7*i+k]-=int(w[k,j])
            rows.append(row)
intertwiner_rank=sp.Matrix(rows).rank()
assert intertwiner_rank==49
result['comparisons']['I']['joint_route_intertwiner_at_z1']={
    'matrix_size':'98 by 49','exact_rational_rank':49,
    'conclusion':'only zero X satisfies H_alpha,A(1) X = X H_alpha,B(1) and H_beta,A(1) X = X H_beta,B(1)'}
result['status']='PASS'
result['source_v03_sha256']=hashlib.sha256((ROOT/'verify_v03.py').read_bytes()).hexdigest()
(ROOT/'V04_EXACT_PENCIL_CERTIFICATE.json').write_text(json.dumps(result,indent=2))
print('PASS: family I full H/W multivariate pencil controls + strictly positive weighted gap; family II joint H obstruction')
print('Saved V04_EXACT_PENCIL_CERTIFICATE.json')
