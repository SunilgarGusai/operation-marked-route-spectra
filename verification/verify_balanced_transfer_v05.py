"""VELE09 v0.5 exact balanced-edge transfer and non-similarity verification.
All operations are symbolic, independent of NAS datasets. Python + SymPy only.
"""
from pathlib import Path
import json, hashlib, platform, time
import sympy as S
import importlib.util

HERE=Path(__file__).resolve().parent
x,a,b,q,u,z,t=S.symbols('x a b q u z t')

def weighted_template(a,b,q):
    M=S.zeros(7)
    data={(0,2):1,(3,4):1,(0,4):a,(0,5):a,(0,6):q,(1,3):q,(2,5):q,(1,4):b}
    for (i,j),v in data.items():M[i,j]=M[j,i]=v
    return M

def edge(i,j):
    E=S.zeros(7);E[i,j]=E[j,i]=1
    return E

def cofactor(A,i,j):
    return (-1)**(i+j)*A.minor_submatrix(i,j).det(method='berkowitz')

def principal2(A,i,j):
    keep=[k for k in range(7) if k not in (i,j)]
    return A.extract(keep,keep).det(method='berkowitz')

start=time.perf_counter()
M=weighted_template(a,b,q)
N=x*S.eye(7)-M
co=S.factor(cofactor(N,0,3)-cofactor(N,2,4))
pm=S.factor(principal2(N,0,3)-principal2(N,2,4))
assert S.factor(co-a*q*x*(b-a)*(x*x-q*q))==0
assert S.factor(pm-x*(x*x-q*q)*(q*q+a*a-b*b))==0
formula=S.factor(-2*u*co-u*u*pm)
expected=-u*x*(x*x-q*q)*(2*a*q*(b-a)+u*(q*q+a*a-b*b))
assert S.factor(formula-expected)==0
matched=S.factor(formula.subs(u,q))
assert S.factor(matched-q*q*x*(x*x-q*q)*((b-a)**2-q*q))==0
assert S.factor(matched.subs(b,a+q))==0
assert S.factor(matched.subs(b,a-q))==0

# Independently expand determinants at several non-balanced rational points to
# reject a mistaken sign or a purely formal invalid rank-two identity.
checks=[]
for i,settings in enumerate(((2,5,1,1),(S.Rational(3,2),S.Rational(-2,3),2,3),(-1,0,4,S.Rational(1,2)),(0,1,2,2),(7,8,1,1),(7,6,1,1))):
    av,bv,qv,uv=settings
    sample=M.subs({a:av,b:bv,q:qv})
    HA=sample+uv*edge(0,3);HB=sample+uv*edge(2,4)
    observed=S.factor(HA.charpoly(x).as_expr()-HB.charpoly(x).as_expr())
    wanted=S.factor(expected.subs({a:av,b:bv,q:qv,u:uv}))
    assert S.expand(observed-wanted)==0,(settings,observed,wanted)
    checks.append({'a':str(av),'b':str(bv),'q':str(qv),'u':str(uv),'difference':str(observed)})

# Original first family with operation-marked route matrices, reconstructed
# strictly from listed arcs and exact three-layer path formula.
ARCS={
 'A':[(0,2),(0,3),(1,3),(0,6),(1,4),(2,5),(3,4)],
 'B':[(0,2),(1,3),(0,6),(1,4),(2,4),(2,5),(3,4)]}
ALPHA={(0,2),(3,4)}
def marked(side,operation):
    U=S.zeros(7);B=S.zeros(7)
    for i,j in ARCS[side]:
        U[i,j]=1
        if ((i,j) in ALPHA)==(operation=='alpha'):B[i,j]=1
    D=U*B+B*U
    return B+B.T+z*(D+D.T)
alphaA=marked('A','alpha');alphaB=marked('B','alpha')
betaA=marked('A','beta');betaB=marked('B','beta')
assert alphaA==alphaB
HA=alphaA+t*betaA;HB=alphaB+t*betaB
route_template=weighted_template(z*(1+t),z*(1+t)+t,t)
assert (HA-route_template-t*edge(0,3)).applyfunc(S.expand)==S.zeros(7)
assert (HB-route_template-t*edge(2,4)).applyfunc(S.expand)==S.zeros(7)
route_difference=S.factor(formula.subs({a:z*(1+t),b:z*(1+t)+t,q:t,u:t}))
assert route_difference==0
# Direct polynomial reconstruction is a separate check, no transfer formula used.
assert S.Poly(HA.charpoly(x).as_expr()-HB.charpoly(x).as_expr(),x,z,t).is_zero

# Reconfirm width-one absence of any nonzero common intertwiner and derive a
# generic-width theorem from the existence of a polynomial nonzero maximal minor.
L=[]
for op in ('alpha','beta'):
    AA=marked('A',op).subs(z,1);BB=marked('B',op).subs(z,1)
    for i in range(7):
        for j in range(7):
            row=[0]*49
            for k in range(7):
                row[7*k+j]+=int(AA[i,k]);row[7*i+k]-=int(BB[k,j])
            L.append(row)
r1=S.Matrix(L).rank()
assert r1==49
# Each entry of stacked intertwiner map is degree <=1 in z, so at least one
# maximal minor is a nonzero polynomial of degree <=49.

certificate={
 'status':'PASS', 'method':'exact cofactor / principal-minor balance and direct characteristic polynomials',
 'sympy':S.__version__,'python':platform.python_version(),
 'template_edges':'(0,2)=1, (3,4)=1, (0,4)=(0,5)=a, (0,6)=(1,3)=(2,5)=q, (1,4)=b',
 'transferred_edges':['(0,3)','(2,4)'],
 'cofactor_difference':str(co), 'two_principal_minor_difference':str(pm),
 'general_determinant_difference':str(S.factor(expected)),
 'equal_transfer_difference':str(matched),
 'balanced_branches':['b-a=q','b-a=-q'],
 'direct_matrix_characteristic_checks':checks,
 'original_route_reconstruction':{'a':'z*(1+t)','b':'z*(1+t)+t','q':'t','transfer_weight':'t','difference':'0', 'polynomial_in':'x,z,t'},
 'simultaneous_intertwiner_rank_at_z1':r1,
 'generic_intertwiner_statement':'rank 49 for all but at most 49 real z values, by a nonzero degree <=49 maximal minor',
 'execution_seconds':round(time.perf_counter()-start,3)
}
(HERE/'V05_BALANCED_TRANSFER_CERTIFICATE.json').write_text(json.dumps(certificate,indent=2),encoding='utf-8')
print('PASS: general transfer formula, exact balanced branches, original route embedding, independent determinant checks, generic non-intertwining')
print(json.dumps({'status':'PASS','direct_checks':len(checks),'rank_at_one':r1,'seconds':certificate['execution_seconds']}))
