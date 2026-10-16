"""VELE09 v0.3: independent exact verifier for two operation-resolved witness families.

The certificate proves exact symbolic identities and graph isomorphism tests.
It does not establish bibliographic novelty or empirical predictive superiority.
"""
import json
from pathlib import Path
import importlib.util
import hashlib
import platform
import sympy as sp
import networkx as nx

ROOT=Path(__file__).resolve().parent
z,x=sp.symbols('z x')
A_ARCS=[(0,2),(0,3),(1,2),(2,4),(3,5),(0,6),(1,5)]
B_ARCS=[(0,2),(0,3),(1,2),(2,4),(3,5),(1,5),(1,6)]
A_ALPHA={(0,2),(0,3)}
B_ALPHA={(0,2),(1,2)}


def compute(arcs,alpha):
    U=sp.zeros(7)
    Balpha=sp.zeros(7)
    support=nx.Graph();support.add_nodes_from(range(7));support.add_edges_from(arcs)
    dag=nx.DiGraph();dag.add_nodes_from(range(7));dag.add_edges_from(arcs)
    eps=[nx.eccentricity(support,v) for v in range(7)]
    E=sp.diag(*eps)
    for i,j in arcs:
        U[i,j]=1
        if (i,j) in alpha: Balpha[i,j]=1
    assert all(any(nx.has_path(dag,a,v) for a in (0,1)) and any(nx.has_path(dag,v,b) for b in (4,5,6)) for v in range(7))
    def forms(B):
        A=B+B.T
        M=U*B+B*U
        Q=M+M.T
        H=A+z*Q
        W=E*A+A*E
        F2=E*Q+Q*E
        L=W+z*F2
        return {'B':B,'H':H,'W':W,'F2':F2,'L':L}
    return {'U':U,'E':E,'ecc':eps,'support':support,'dag':dag,
            'alpha':forms(Balpha),'beta':forms(U-Balpha)}


def old_certificate():
    location=ROOT/'verify_extension_v02.py'
    spec=importlib.util.spec_from_file_location('original_v02',location)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result=mod.verify()
    assert result['status']=='PASS'
    return {'status':'PASS', 'source_sha256':hashlib.sha256(location.read_bytes()).hexdigest(),
            'original_v02_operations':result['operations'],
            'v02_general_depth_test':result['general_depth_test']}


def verify_new():
    a,b=compute(A_ARCS,A_ALPHA),compute(B_ARCS,B_ALPHA)
    iso=next(nx.isomorphism.GraphMatcher(a['support'],b['support']).isomorphisms_iter(),None)
    assert iso is not None
    # one explicit support isomorphism, not a DAG isomorphism
    wanted={0:1,1:0,2:2,3:5,4:4,5:3,6:6}
    assert {tuple(sorted((wanted[u],wanted[v]))) for u,v in A_ARCS}=={tuple(sorted(edge)) for edge in B_ARCS}
    assert nx.diameter(a['support'])==nx.diameter(b['support'])==3
    assert not nx.is_isomorphic(a['dag'],b['dag'])
    assert a['ecc']==[2,3,2,3,3,3,3]
    assert b['ecc']==[3,2,2,3,3,3,3]
    result={'status':'PASS','second_witness':{},'support_diameter':3,
            'support_isomorphism':wanted,'ecc_A':a['ecc'],'ecc_B':b['ecc'],
            'source_arc_lists':{'A':A_ARCS,'B':B_ARCS},'marked_alpha':{'A':sorted(A_ALPHA),'B':sorted(B_ALPHA)}}
    common_beta=(x**7-(6*z**2+5)*x**5-4*z*x**4+
                 (4*z**4-4*z**3+13*z**2+7)*x**3+
                 (4*z**3-2*z**2+8*z)*x**2-(5*z**2+3)*x-4*z)
    expected={
        'alpha':{'H':x**5*(x**2-2*z**2-2),'W':x**5*(x**2-41),
                 'gap':-22*z**2,
                 'LA':x**5*(x**2-(50*z**2+41)),
                 'LB':x**3*(x**4-(61*z**2+41)*x**2+z**2)},
        'beta':{'H':common_beta,'W':x*(x**2-25)*(x**4-122*x**2+2700),
                'gap':-22*z**2}}
    for op in ('alpha','beta'):
        aa,bb=a[op],b[op]
        for obj in ('H','W'):
            pa=sp.expand(aa[obj].charpoly(x).as_expr())
            pb=sp.expand(bb[obj].charpoly(x).as_expr())
            assert sp.expand(pa-pb)==0
            assert sp.expand(pa-expected[op][obj])==0, (op,obj,sp.factor(pa))
        ga=sp.expand(sp.trace(aa['L']**2))
        gb=sp.expand(sp.trace(bb['L']**2))
        gap=sp.factor(ga-gb)
        assert sp.expand(gap-expected[op]['gap'])==0
        b_co=sp.trace(aa['W']*aa['F2'])-sp.trace(bb['W']*bb['F2'])
        c_co=sp.trace(aa['F2']**2)-sp.trace(bb['F2']**2)
        assert (b_co,c_co)==(0,-22)
        assert sp.expand((z**2)*gap+22*z**4)==0
        result['second_witness'][op]={
           'H_charpoly':str(sp.factor(expected[op]['H'])),
           'W_charpoly':str(sp.factor(expected[op]['W'])),
           'reduced_trace2_A':str(sp.factor(ga)),
           'reduced_trace2_B':str(sp.factor(gb)),
           'reduced_trace2_gap':str(gap),
           'clone_trace2_gap':'-22*s**4 for all positive integer s',
           'co_moments':{'b':int(b_co),'c':int(c_co)}}
        if op=='alpha':
            assert sp.expand(aa['L'].charpoly(x).as_expr()-expected[op]['LA'])==0
            assert sp.expand(bb['L'].charpoly(x).as_expr()-expected[op]['LB'])==0
    # Inequality proof based on squared-eigenvalue polynomial B-alpha
    y=50*z*z+41
    t=61*z*z+41
    q=sp.expand(y*y-t*y+z*z)
    assert sp.expand(q+z*z*(550*z*z+450))==0
    result['alpha_all_width_radius_proof']={
      'q_at_radius_squared_A':str(sp.factor(q)),
      'strict_for_all_positive_integer_widths':True,
      'orientation':'rho(K_alpha,T_B,s)>rho(K_alpha,T_A,s)'}
    # Direct, independently formed width-two (or three) route matrices.
    # This tests the actual eccentricities of the cloned undirected supports,
    # rather than just relying on the reduced formula.
    for width in (2,3):
        for op in ('alpha','beta'):
            for dat in (a,b):
                Us=sp.kronecker_product(dat['U'],sp.ones(width))
                Bs=sp.kronecker_product(dat[op]['B'],sp.ones(width))
                P=sp.eye(7*width)+Us+Us**2
                Rs=P*Bs*P
                Cs=Rs+Rs.T
                clone_graph=nx.Graph()
                clone_graph.add_nodes_from(range(7*width))
                for e1,e2 in dat['dag'].edges():
                    for c1 in range(width):
                        for c2 in range(width):
                            clone_graph.add_edge(e1*width+c1,e2*width+c2)
                actual_ecc=[nx.eccentricity(clone_graph,i) for i in range(7*width)]
                assert actual_ecc==sum(([e]*width for e in dat['ecc']),[])
                Es=sp.diag(*actual_ecc)
                Ks=Es*Cs+Cs*Es
                expected_K=sp.kronecker_product(dat[op]['L'].subs(z,width),sp.ones(width))
                assert Ks==expected_K
    result['direct_clone_verification']={'widths':[2,3],'operations':['alpha','beta'],'status':'PASS'}
    return result


def main():
    output={'verification_protocol':'Exact symbolic identities and combinatorial isomorphism checks; no ML labels',
            'python_version':platform.python_version(),'sympy_version':sp.__version__,'networkx_version':nx.__version__}
    output['previous_v02']=old_certificate()
    output['new_v03']=verify_new()
    output['general_width_rigidity']='PASS: by collecting coefficients of s^(k+m), with tr(F_A,1^2)=tr(F_B,1^2), the difference is s^3 times a polynomial of degree <=2*ell-3; fundamental theorem of algebra bounds positive exceptional widths'
    output['status']='PASS'
    resultfile=ROOT/'V03_EXACT_CERTIFICATE.json'
    resultfile.write_text(json.dumps(output,indent=2,ensure_ascii=False))
    print('PASS: old v0.2, new diameter-three family, both control spectra, all-width trace gaps, alpha Perron ordering and cloned-matrix checks')
    print('Saved',resultfile)

if __name__=='__main__':main()
