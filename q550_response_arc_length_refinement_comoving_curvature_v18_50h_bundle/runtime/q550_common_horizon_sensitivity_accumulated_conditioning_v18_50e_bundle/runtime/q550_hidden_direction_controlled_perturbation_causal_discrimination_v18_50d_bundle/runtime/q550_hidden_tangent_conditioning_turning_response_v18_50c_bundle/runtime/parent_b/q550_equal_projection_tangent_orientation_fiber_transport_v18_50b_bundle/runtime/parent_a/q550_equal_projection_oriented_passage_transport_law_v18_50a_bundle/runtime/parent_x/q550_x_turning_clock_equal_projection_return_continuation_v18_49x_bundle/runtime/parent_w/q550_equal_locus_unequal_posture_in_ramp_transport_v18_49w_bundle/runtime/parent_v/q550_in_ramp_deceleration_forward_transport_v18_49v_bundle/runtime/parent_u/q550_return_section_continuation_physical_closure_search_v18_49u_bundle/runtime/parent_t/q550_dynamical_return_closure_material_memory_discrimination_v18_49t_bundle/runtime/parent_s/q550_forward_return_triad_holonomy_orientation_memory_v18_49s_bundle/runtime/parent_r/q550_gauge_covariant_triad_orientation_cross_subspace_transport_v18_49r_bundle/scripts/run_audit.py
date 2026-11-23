#!/usr/bin/env python3
"""v18.49r: physical 11D replay and gauge-covariant projector triad audit.

Invariant local operators use the authentic v18.49q kinetic reference.
All calculations are numerical, not formal interval certifications.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from scipy.optimize import brentq
from verify_r_parent import verify
from triad_math import decompose as triad_decompose,parts_from_eigenaxes,chi,gauge_flip,aligned_triad,transport_cross,aligned_relative_rotation,IN,OUT
ROOT=Path(__file__).resolve().parents[1]

def save_csv(name,rows):
    if not rows:return
    dest=ROOT/'results'/name;dest.parent.mkdir(exist_ok=True,parents=True)
    with dest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for v in rows for k in v)));w.writeheader();w.writerows(rows)

def run(args):
    src,qreport,auth=verify()
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    from geometry_math import decompose as parent_decompose,I67,I78,I68
    ex=Experiment(args)
    expected={(c['kappa_kind'],round(c['ramp_xi'],12)):c for c in qreport['cases']}
    cases_req=[('original',.327375)] if args.smoke else ([('original',.327375),('autonomous',.327375)] if args.focus else
        [('original',.32671875),('original',.327375),('original',.33),('autonomous',.327375),('autonomous',.33)])
    report_cases=[];samples=[];events=[];checks={'max_parent_endpoint_regression':0.,'max_gauge_sign_invariance_error':0.,
        'max_constant_orthogonal_chart_error':0.,'max_block_closure':0.,'max_cross_derivative_closure':0.,
        'max_subspace_fd_error':0.,'min_relative_spectral_gap':1.,'min_eigenline_overlap':1.,'max_parallel_rotation_orthogonality':0.,
        'max_parallel_subspace_error':0.,'max_chi_collinearity_error':0.,'max_ledger_error':0.}
    rand=np.random.default_rng(4949)
    for kind,r in cases_req:
        print('v18.49r authentic 11D and 10D replay',kind,r,flush=True)
        k=ex.ks[kind]
        design=ex.original_ramp.Design('r_triad_'+kind,'beta:2:2',float(r))
        back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,k,ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
        ex.integrations['physical_return_11D']+=1
        checks['max_ledger_error']=max(checks['max_ledger_error'],float(ledger))
        def jac(st,kap,par,sl):return ex.jet.structural_jet(st,k,ex.params,ex.slope)[1]
        frame,_=transport_frame(back,k,ex.params,ex.slope,jac,1.+r,rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
        ex.integrations['tangent_10D']+=1
        _,J0=embedding_and_jac(back(0.)[:10],ex.params.m_x,1.)
        cache={}
        def obs(q):
            key=round(float(q),14)
            if key not in cache:
                t=r+float(q);st=back(t)[:11]
                field,jacmat,_=ex.jet.structural_jet(st,k,ex.params,ex.slope)
                _,J=embedding_and_jac(st,ex.params.m_x,1.)
                Jdot=kinetic_frame_derivative(st,field,ex.params.m_x,1.,embedding_and_jac)
                B,Bdot=deforming_frame(J,frame(t),J0,Jdot,jacmat[:10,:10])
                out=spectral_generator(B,Bdot)
                g=parent_decompose(out)
                tblock=triad_decompose(out['generator'],out['projectors'])
                cache[key]=(out,g,tblock)
            return cache[key]
        qs=np.linspace(args.q_start,args.q_end,args.phase_samples)
        Alast=None;Afirst=None;Afr=[]
        for idx,q in enumerate(qs):
            out,g,tri=obs(q); K=out['generator'];P=out['projectors']
            A,signs,over=aligned_triad(out['axes'],Alast)
            if Alast is not None:checks['min_eigenline_overlap']=min(checks['min_eigenline_overlap'],float(np.min(over)))
            if Afirst is None:Afirst=A.copy()
            Alast=A;Afr.append(A)
            p67,p78,p68=(g['parts'][i] for i in (I67,I78,I68))
            cosine,denom=chi(p67,p78,p68)
            if cosine is not None:checks['max_chi_collinearity_error']=max(checks['max_chi_collinearity_error'],abs(abs(cosine)-1.))
            checks['max_block_closure']=max(checks['max_block_closure'],tri['closure'])
            checks['max_cross_derivative_closure']=max(checks['max_cross_derivative_closure'],tri['cross_derivative_closure'])
            checks['min_relative_spectral_gap']=min(checks['min_relative_spectral_gap'],float(out['min_relative_eigengap']))
            if idx%max(1,args.phase_samples//10)==0:
                flip=rand.choice([-1.,1.],size=10)
                newaxes,newomega=gauge_flip(out['axes'],out['Omega'],flip)
                pg=parts_from_eigenaxes(newaxes,newomega)
                checks['max_gauge_sign_invariance_error']=max(checks['max_gauge_sign_invariance_error'],
                    max(float(np.linalg.norm(pg[(5,6)]-p67)),float(np.linalg.norm(pg[(6,7)]-p78)),float(np.linalg.norm(pg[(5,7)]-p68))))
                # Conjugate physical chart by a single fixed orthogonal matrix (not time-varying).
                if idx==0:
                    X=rand.standard_normal((10,10));O,_=np.linalg.qr(X)
                KP=O@K@O.T;PP=np.einsum('ab,ibc,dc->iad',O,P,O)
                tx=triad_decompose(KP,PP)
                checks['max_constant_orthogonal_chart_error']=max(checks['max_constant_orthogonal_chart_error'],
                    max(abs(tx['frac_cross']-tri['frac_cross']),abs(tx['frac_internal']-tri['frac_internal']),
                        abs(tx['frac_external']-tri['frac_external']),abs(float(np.linalg.norm(tx['dS']))-float(np.linalg.norm(tri['dS'])))))
            if 0<idx<len(qs)-1 and idx%max(1,args.phase_samples//12)==0:
                h=min(2e-5, .3*(q-args.q_start),.3*(args.q_end-q))
                pf=triad_decompose(obs(q+h)[0]['generator'],obs(q+h)[0]['projectors'])['S']
                pb=triad_decompose(obs(q-h)[0]['generator'],obs(q-h)[0]['projectors'])['S']
                checks['max_subspace_fd_error']=max(checks['max_subspace_fd_error'],float(np.linalg.norm((pf-pb)/(2*h)-tri['dS'])/max(1,np.linalg.norm(tri['dS']))))
            sv=tri['svals']
            samples.append({'kappa_kind':kind,'ramp_xi':r,'q':float(q),
                'share_67':g['share_67'],'share_78':g['share_78'],'share_68':g['share_68'],
                'chi_comm_K68':cosine,'chi_denominator':denom,
                'internal_fraction':tri['frac_internal'],'cross_fraction':tri['frac_cross'],
                'external_fraction':tri['frac_external'],'cross_generator_norm':float(np.linalg.norm(tri['kc'])),
                'Sdot_norm':float(np.linalg.norm(tri['dS'])),'cross_block_singular_1':float(sv[0]),
                'cross_block_singular_2':float(sv[1]),'cross_block_singular_3':float(sv[2]),
                'cross_block_volume':float(np.prod(sv)),
                'min_relative_gap':float(out['min_relative_eigengap']),
                'aligned_min_overlap':float(np.min(over)) if Alast is not None and idx>0 else 1.})
        # Phase-by-phase Kato transport of the aggregate triad projector.
        # This is not the intrinsic orientation of three unoriented eigenlines;
        # all angles use the explicitly aligned initial eigenframe as reference.
        Uphase=np.eye(10)
        phase_angles=[];phase_parallel_errors=[]
        for i,q in enumerate(qs):
            if i:
                h=float(qs[i]-qs[i-1]);qmid=float((qs[i]+qs[i-1])/2)
                Uphase=expm(h*obs(qmid)[2]['kc'])@Uphase
            raw_i,R_i,_,angle_i=aligned_relative_rotation(Afirst,Uphase,Afr[i])
            err_i=float(np.linalg.norm(Uphase@obs(args.q_start)[2]['S']@Uphase.T-obs(q)[2]['S']))
            phase_angles.append(angle_i*180/np.pi);phase_parallel_errors.append(err_i)
            samples[-len(qs)+i]['relative_triad_rotation_deg']=angle_i*180/np.pi
            samples[-len(qs)+i]['subspace_parallel_error']=err_i
        phase_angle_max_step=max(abs(x-y) for x,y in zip(phase_angles[:-1],phase_angles[1:]))
        parent_case=expected[(kind,round(r,12))]
        for name,q in [('start',args.q_start),('end',args.q_end)]:
            # Parent endpoint shares at q=.65; q=.63 is not its phase window start.
            if name=='end':
                out,g,_=obs(q)
                for pair in ('67','78'):
                    key='share_'+pair+'_at_end'
                    checks['max_parent_endpoint_regression']=max(checks['max_parent_endpoint_regression'],abs(float(g['share_'+pair])-parent_case[key]))
        if checks['max_parent_endpoint_regression']>args.max_parent_error:raise RuntimeError('Parent q regression failed')
        # Compute root on genuine phase evolution; classify global leader via q parent at root.
        diffs=[obs(q)[1]['share_78']-obs(q)[1]['share_67'] for q in qs]
        roots=[]
        for j in range(len(qs)-1):
            if diffs[j]*diffs[j+1]<0:
                root=float(brentq(lambda q:obs(q)[1]['share_78']-obs(q)[1]['share_67'],qs[j],qs[j+1],xtol=3e-13))
                roots.append(root)
                out,g,_=obs(root)
                events.append({'kappa_kind':kind,'ramp_xi':r,'q_root':root,'chi_at_root':chi(g['parts'][I67],g['parts'][I78],g['parts'][I68])[0],
                    'cross_fraction_at_root':triad_decompose(out['generator'],out['projectors'])['frac_cross']})
        parent_roots=parent_case['root_phases']
        if len(roots)!=len(parent_roots) or any(abs(a-b)>args.max_root_error for a,b in zip(roots,parent_roots)):
            raise RuntimeError('The v18.49q root genealogy is not reproduced')
        # Kato-style subspace transport: integrate only the off-diagonal [S, [S, K]].
        for n in (args.transport_steps,2*args.transport_steps):
            h=(args.q_end-args.q_start)/n
            Kc=[obs(args.q_start+(i+.5)*h)[2]['kc'] for i in range(n)]
            U=transport_cross(Kc,h)
            if n==args.transport_steps:Ucoarse=U
        Aend=Afr[-1];start=obs(args.q_start)[2]['S'];end=obs(args.q_end)[2]['S']
        moved=U@start@U.T
        sub_error=float(np.linalg.norm(moved-end));checks['max_parallel_subspace_error']=max(checks['max_parallel_subspace_error'],sub_error)
        raw,R,svals,angle=aligned_relative_rotation(Afirst,U,Aend)
        checks['max_parallel_rotation_orthogonality']=max(checks['max_parallel_rotation_orthogonality'],float(np.linalg.norm(raw.T@raw-np.eye(3))))
        # Direct arbitrary sign-flip stream -> after continuity alignment, same Aend.
        Aprior=Afirst.copy();last=None
        for i,q in enumerate(qs):
            v=obs(q)[0]['axes'].copy()
            signs=rand.choice([-1.,1.],size=10)
            v=v*signs[None,:]
            cand,_,_=aligned_triad(v,Aprior)
            if i==0:
                # Anchor to the original initial reference for a fair comparison.
                cand,_,_=aligned_triad(v,Afirst)
            Aprior=cand;last=cand
        test_alignment=float(np.linalg.norm(last-Aend))
        case={'kappa_kind':kind,'ramp_xi':r,'handover_roots':roots,
           'chi_at_end':samples[-1]['chi_comm_K68'],'chi_defined_fraction':sum(s['chi_comm_K68'] is not None for s in samples[-len(qs):])/len(qs),
           'cross_fraction_at_start':samples[-len(qs)]['cross_fraction'],'cross_fraction_at_end':samples[-1]['cross_fraction'],
           'cross_singular_values_at_end':[float(x) for x in obs(args.q_end)[2]['svals']],
           'parallel_triads_relative_rotation_rad':angle,'parallel_triads_relative_rotation_deg':angle*180/np.pi,
           'parallel_block_determinant':float(np.linalg.det(raw)), 'parallel_block_singular_values':[float(x) for x in svals],
           'parallel_subspace_endpoint_error':sub_error,'parallel_transport_refinement':float(np.linalg.norm(U-Ucoarse)),
           'parallel_gauge_random_sign_stream_endpoint_error':test_alignment,
           'subspace_endpoint_displacement':float(np.linalg.norm(end-start)),
           'phase_resolved_rotation_end_deg':float(phase_angles[-1]),
           'phase_resolved_rotation_max_step_deg':float(phase_angle_max_step),
           'phase_resolved_max_subspace_parallel_error':float(max(phase_parallel_errors)),
           'spectral_gap_min':min(obs(q)[0]['min_relative_eigengap'] for q in qs)}
        if sub_error>args.max_subspace_transport_error:raise RuntimeError('Cross-only transport failed to follow the triad subspace')
        if test_alignment>1e-8:raise RuntimeError('Continuous line-sign gauge was not robust to random sign flips')
        report_cases.append(case)
        print('  chi endpoint',case['chi_at_end'],'triad rotation [deg]',round(case['parallel_triads_relative_rotation_deg'],6),
              'cross-only S error',round(sub_error,10),'handover roots',roots,flush=True)
    save_csv('phase_resolved_gauge_covariant_triad.csv',samples)
    save_csv('handover_orientation_events.csv',events)
    report={'audit':'Q550 v18.49r — Gauge-Covariant Triad Orientation & Cross-Subspace Transport Audit',
      'status':'SMOKE_NUMERICAL_DIAGNOSTIC' if args.smoke else 'PHASE_RESOLVED_NUMERICAL_AUDIT',
      'cases':report_cases,'handover_events':events,'controls':checks,'parent_verification':auth,'integrations':ex.integrations,
      'method':{'phase_window':[args.q_start,args.q_end],'phase_samples':args.phase_samples,
           'cross_parallel_steps':2*args.transport_steps,
           'metric':'authenticated fixed initial kinetic metric',
           'definition':'K=SKS+(SKT+TKS)+TKT; Kato-style transport of S via Kcross',
           'orientation':'relative SO(3) holonomy with continuously aligned eigenlines and explicit initial sign reference'},
      'limitations':['An unordered or unoriented set of eigenlines does not have a gauge-independent intrinsic orientation.',
          'The scalar commutator alignment chi has |chi|=1 by a three-index Lie algebra identity wherever defined; it is not by itself independent evidence of physical torsion.',
          'The relative SO(3) rotation depends on the initial oriented eigenframe and chosen path; only conjugacy-invariant summaries such as angle are sign-gauge robust.',
          'Results are in the authenticated kinetic metric with a fixed external observer reference; no arbitrary time-dependent observer covariance or material flip theorem.',
          'These are high-precision floating-point replay diagnostics; no rigorous interval certificate.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true');p.add_argument('--focus',action='store_true')
    p.add_argument('--q-start',type=float,default=.63);p.add_argument('--q-end',type=float,default=.65)
    p.add_argument('--phase-samples',type=int,default=151);p.add_argument('--transport-steps',type=int,default=100)
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025);p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13);p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8);p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--max_parent_error',type=float,default=5e-8);p.add_argument('--max_root_error',type=float,default=5e-7)
    p.add_argument('--max_subspace_transport_error',type=float,default=5e-4)
    args=p.parse_args()
    if not (.60<=args.q_start<args.q_end<=.65 and args.phase_samples>=11 and args.transport_steps>=20):raise ValueError('Invalid sample window')
    result=run(args)
    print(json.dumps({'status':result['status'],'cases':len(result['cases']),
        'events':len(result['handover_events']),'controls':result['controls']},indent=2))
