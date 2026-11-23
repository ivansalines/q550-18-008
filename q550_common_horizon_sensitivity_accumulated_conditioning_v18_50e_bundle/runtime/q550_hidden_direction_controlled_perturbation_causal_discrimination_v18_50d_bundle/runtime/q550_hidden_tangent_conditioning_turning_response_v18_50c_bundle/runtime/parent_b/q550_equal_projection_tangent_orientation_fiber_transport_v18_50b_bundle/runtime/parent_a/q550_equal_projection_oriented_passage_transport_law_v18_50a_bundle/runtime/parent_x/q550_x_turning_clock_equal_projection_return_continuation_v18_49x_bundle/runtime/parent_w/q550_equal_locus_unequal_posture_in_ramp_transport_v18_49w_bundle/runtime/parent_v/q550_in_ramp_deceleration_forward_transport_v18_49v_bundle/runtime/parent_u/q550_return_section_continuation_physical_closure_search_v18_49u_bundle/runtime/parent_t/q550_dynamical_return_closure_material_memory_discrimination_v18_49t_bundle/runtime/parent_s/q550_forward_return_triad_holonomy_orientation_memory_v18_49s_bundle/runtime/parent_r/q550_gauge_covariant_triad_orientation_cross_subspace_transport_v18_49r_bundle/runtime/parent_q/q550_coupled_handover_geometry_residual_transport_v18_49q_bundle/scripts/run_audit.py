#!/usr/bin/env python3
"""v18.49q: coupled handover geometry and finite non-Abelian residual transport.

Uses authenticated v18.49p 11D dynamics / 10D tangent operator, re-integrated
for each case. Observes phase-registered projector generators in the SAME fixed
initial kinetic reference. Numerical (not interval) audit; no material or
observer-universal torsional flip is claimed.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from geometry_math import decompose,transports,projector_transport_error,aggregated_subspace_change,angle_projector,PAIRS,I67,I78,I68
from verify_q_parent import verify
ROOT=Path(__file__).resolve().parents[1]

def save_csv(n,rows):
    if not rows:return
    p=ROOT/'results'/n;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));w.writeheader();w.writerows(rows)

def run(args):
    source,old,auth=verify()
    # Parent scripts are now on sys.path after verification, with no altered source.
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    from pairwise_math import pair_spectrum
    e=Experiment(args)
    cases=[];phase_rows=[];events=[];max_exact=0;max_pdot=0;max_fd=0;max_parent=0
    min_gap=1.;max_ledger=0;max_transport_refine=0
    parent_rows={(c['kappa_kind'],round(c['ramp_xi'],10)):c for c in old['cases']}
    requested=[('original',.327375)] if args.smoke else ([('original',.327375),('autonomous',.327375)] if args.focus else
       [('original',.32671875),('original',.327375),('original',.33),('autonomous',.327375),('autonomous',.33)])
    for kind,r in requested:
        print('v18.49q authentic replay:',kind,r,flush=True)
        k=e.ks[kind];design=e.original_ramp.Design('q_geometry_'+kind,'beta:2:2',float(r))
        back,ledger=e.original.integrate(e.physical,e.clock,e.support,e.audit,k,e.params,e.slope,e.omega,e.turning[kind],args,design=design)
        e.integrations['physical_return_11D']+=1;max_ledger=max(max_ledger,ledger)
        def jac(st,kap,par,sl):return e.jet.structural_jet(st,k,e.params,e.slope)[1]
        frame,_=transport_frame(back,k,e.params,e.slope,jac,1.+r,rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
        e.integrations['tangent_10D']+=1
        _,J0=embedding_and_jac(back(0.)[:10],e.params.m_x,1.)
        cache={}
        def obs(q):
            key=round(float(q),14)
            if key not in cache:
                t=float(r+q);st=back(t)[:11]
                field,jacmat,_=e.jet.structural_jet(st,k,e.params,e.slope)
                _,J=embedding_and_jac(st,e.params.m_x,1.)
                Jdot=kinetic_frame_derivative(st,field,e.params.m_x,1.,embedding_and_jac)
                B,Bdot=deforming_frame(J,frame(t),J0,Jdot,jacmat[:10,:10])
                out=spectral_generator(B,Bdot)
                g=decompose(out)
                spec=pair_spectrum(out)
                cache[key]=(out,g,spec)
            return cache[key]
        qs=np.linspace(args.q_start,args.q_end,args.phase_samples)
        for q in qs:
            out,g,s=obs(q)
            min_gap=min(min_gap,out['min_relative_eigengap'])
            max_exact=max(max_exact,g['generator_closure_relative'],g['orthogonality_relative'])
            max_pdot=max(max_pdot,g['projector_derivative_closure'])
            ratio=float(g['share_78']-g['share_67'])
            winner=int(np.argmax(s['pair_K_frob_sq']))
            phase_rows.append({'kappa_kind':kind,'ramp_xi':r,'q':float(q),
                'share_67':g['share_67'],'share_78':g['share_78'],'share_68':g['share_68'],
                'share_43_other_pairs':g['share_other'],'share_67_78_sum':g['share_two'],
                'leading_pair':f'{PAIRS[winner][0]+1}-{PAIRS[winner][1]+1}',
                'raw_margin_78_minus_67':ratio,
                'comm_norm_67_78':g['norm_comm'], 'comm_68_coefficient':g['bracket_68_coefficient'],
                'observed_K68_norm':float(np.linalg.norm(g['parts'][I68])),
                'other_generator_norm':g['norm_other'],'subspace_678_leakage_norm':g['norm_leak_S678'],
                'min_relative_gap':float(out['min_relative_eigengap']),
                'algebraic_closure_relative':g['generator_closure_relative'],
                'orthogonality_relative':g['orthogonality_relative'],
                'comm_outside_68':g['comm_outside_68'],
                'projector_derivative_closure':g['projector_derivative_closure'],
                'two_internal_commutator':g['internal_subspace_commutator'],
                'commutator_theory_residual':g['comm_theory_residual']})
        # Reproduce independent v18.49p parent measurements, without fitting to them.
        pcase=parent_rows[(kind,round(r,10))]
        for q,label in [(args.q_start,'start'),(args.q_end,'end')]:
            out,g,sp=obs(q);expected=pcase['relative_share_78_minus_67_at_'+label]
            max_parent=max(max_parent,abs((g['share_78']-g['share_67'])-expected))
        if max_parent>args.max_parent_error:raise RuntimeError('Authentic v18.49p share regression differs')
        roots=[]
        diffs=np.array([obs(q)[1]['share_78']-obs(q)[1]['share_67'] for q in qs])
        for i in range(len(qs)-1):
            if diffs[i]*diffs[i+1]<0:
                root=brentq(lambda q:obs(q)[1]['share_78']-obs(q)[1]['share_67'],qs[i],qs[i+1],xtol=2e-13)
                out,g,s=obs(root);win=np.argsort(-s['pair_K_frob_sq'])[:2]
                if set(win)!={I67,I78}:raise RuntimeError('Crossing is NOT a global leadership handover')
                roots.append(float(root))
                events.append({'kappa_kind':kind,'ramp_xi':r,'q_root':float(root),
                   'share_at_root':g['share_67'],'share_68_at_root':g['share_68'],
                   'comm_norm':g['norm_comm'], 'bracket_68_coefficient':g['bracket_68_coefficient'],
                   'K68_norm':float(np.linalg.norm(g['parts'][I68])),
                   'other_share':g['share_other'],'subspace_leakage':g['norm_leak_S678'],
                   'relative_gap':float(out['min_relative_eigengap']),
                   'residual_crossing':g['share_78']-g['share_67']})
        parent_roots=pcase['root_phases']
        if len(roots)!=len(parent_roots):raise RuntimeError('Parent root count mismatch')
        if roots and max(abs(x-y) for x,y in zip(roots,parent_roots))>args.max_root_error:raise RuntimeError('Parent root phase mismatch')
        # Direct projector derivative check, not tautological use of stored Pdot.
        phase_probes=roots or [args.q_end-.001]
        for q0 in phase_probes:
            h=min(2e-5,(q0-args.q_start)/4,(args.q_end-q0)/4) if args.q_start<q0<args.q_end else 1e-5
            if h<2e-7:h=2e-7
            P0=obs(q0)[0]['projectors']; K0=obs(q0)[1]['K']
            Pplus=obs(q0+h)[0]['projectors'];Pminus=obs(q0-h)[0]['projectors']
            for i in (5,6,7):
                fd=(Pplus[i]-Pminus[i])/(2*h)
                analytic=K0@P0[i]-P0[i]@K0
                max_fd=max(max_fd,float(np.linalg.norm(fd-analytic)/max(1,np.linalg.norm(analytic))))
        # Re-integrate the non-Abelian projector transport with step refinement.
        window0=max(args.q_start,args.transport_q_start);window1=args.q_end
        runs=[]
        for N in (args.transport_steps,args.transport_steps*2):
            h=(window1-window0)/N
            mids=[obs(window0+(i+.5)*h)[1] for i in range(N)]
            runs.append(transports(mids,h))
        U,U2,Uo,U268=runs[-1]
        max_transport_refine=max(max_transport_refine,float(np.linalg.norm(runs[0][0]-U)))
        Pstart=obs(window0)[0]['projectors'];Pend=obs(window1)[0]['projectors']
        Sstart=np.sum(Pstart[[5,6,7]],axis=0); Send=np.sum(Pend[[5,6,7]],axis=0)
        true_movement=aggregated_subspace_change(Sstart,Send)
        full_err=projector_transport_error(U,Pstart,Pend)
        two_err=projector_transport_error(U2,Pstart,Pend)
        with68_err=projector_transport_error(U268,Pstart,Pend)
        other_err=projector_transport_error(Uo,Pstart,Pend)
        product_err=float(np.linalg.norm(U-U2@Uo))
        if full_err>args.max_full_transport_error:raise RuntimeError('Full generator transport failed projector test: '+str(full_err))
        case={'kappa_kind':kind,'ramp_xi':r,'root_phases':roots,'relative_gap_min':min(obs(q)[0]['min_relative_eigengap'] for q in qs),
            'share_67_at_end':obs(args.q_end)[1]['share_67'],'share_78_at_end':obs(args.q_end)[1]['share_78'],
            'share_other_at_end':obs(args.q_end)[1]['share_other'],
            'comm_norm_at_end':obs(args.q_end)[1]['norm_comm'],
            'bracket_68_at_end':obs(args.q_end)[1]['bracket_68_coefficient'],
            'observed_K68_at_end':float(np.linalg.norm(obs(args.q_end)[1]['parts'][I68])),
            'measured_S678_change':true_movement,
            'full_projector_transport_max_error':full_err,
            'pair_only_projector_transport_max_error':two_err,
            'pair_plus_68_projector_transport_max_error':with68_err,
            'other_43_projector_transport_max_error':other_err,
            'full_vs_pair_then_rest_noncommutativity':product_err,
            'full_transport_step_refinement':float(np.linalg.norm(runs[0][0]-U)),
            'orthogonal_full_error':float(np.linalg.norm(U.T@U-np.eye(10))),
            'subspace_motion_predicted_by_pair_only':float(np.linalg.norm(U2@Sstart@U2.T-Sstart)),
            'subspace_motion_predicted_by_full':float(np.linalg.norm(U@Sstart@U.T-Sstart)),
            'subspace_final_mismatch_pair_only':float(np.linalg.norm(U2@Sstart@U2.T-Send)),
            'subspace_final_mismatch_full':float(np.linalg.norm(U@Sstart@U.T-Send)),
            'phase_window':[args.q_start,args.q_end], 'transport_window':[window0,window1],
            'verified_parent_max_abs_share_difference':max_parent,'physical_ledger_error':float(ledger)}
        cases.append(case)
        print('v18.49q',kind,r,'events',roots,'at end 6-7 / 7-8 / other',round(case['share_67_at_end'],5),round(case['share_78_at_end'],5),round(case['share_other_at_end'],5),'full projector err',full_err,'pair only err',two_err,flush=True)
    save_csv('phase_resolved_geometric_ledger.csv',phase_rows)
    save_csv('numerical_handover_geometry_events.csv',events)
    report={'audit':'Q550 v18.49q — Coupled Handover Geometry & Residual Transport Audit',
      'status':'SMOKE_NUMERICAL_DIAGNOSTIC' if args.smoke else ('FOCUSED_NUMERICAL_DIAGNOSTIC' if args.focus else 'PHASE_RESOLVED_NUMERICAL_AUDIT'),
      'cases':cases,'handover_events':events,'parent_verification':auth,'integrations':e.integrations,
      'controls':{'max_instantaneous_generator_closure_relative':max_exact,'max_projector_identity_error':max_pdot,
       'max_finite_difference_projector_derivative_relative_error':max_fd,
       'max_parent_p_share_endpoint_regression':max_parent,'min_relative_spectral_gap':min_gap,
       'max_mechanical_ledger_error':max_ledger,'max_U_step_refinement':max_transport_refine},
      'method':{'phase_samples':args.phase_samples,'transport_steps_fine':2*args.transport_steps,
        'observer':'inherited fixed initial kinetic frame','spectral_ordering':'descending eigenspace rank',
        'phase_register':'q=t-r, same for all cases','relative_crossing':'D78-D67'},
      'limitations':['Pair 6-7 and 7-8 are rank-ordered eigenspace couplings, not distinct material objects.',
        'Commutator opening the 6-8 plane is an algebraic Lie-bracket identity; it is not by itself an independent observed 6-8 transport.',
        'The remaining 43-pair generator is measured, not a closure failure. Instantaneous decomposition is exact by definition.',
        'The difference between full and ordered-factor finite transports depends on the chosen splitting and interval; not a uniquely defined material memory.',
        'Results are in the inherited kinetic metric and fixed observer gauge. Only constant orthogonal chart covariance is automatic.',
        'Root event is numerical, not a verified interval enclosure. No universal torsional flip has been demonstrated.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--smoke',action='store_true');ap.add_argument('--focus',action='store_true')
    ap.add_argument('--phase-samples',type=int,default=151);ap.add_argument('--q-start',type=float,default=.60);ap.add_argument('--q-end',type=float,default=.65)
    ap.add_argument('--transport-q-start',type=float,default=.63);ap.add_argument('--transport-steps',type=int,default=100)
    ap.add_argument('--rtol',type=float,default=3e-12);ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025);ap.add_argument('--frame-rtol',type=float,default=8e-11)
    ap.add_argument('--frame-atol',type=float,default=8e-13);ap.add_argument('--frame-max-step',type=float,default=.008)
    ap.add_argument('--maximum-ledger-error',type=float,default=1e-8);ap.add_argument('--maximum-regression',type=float,default=1e-7)
    ap.add_argument('--max_parent_error',type=float,default=2e-7);ap.add_argument('--max_root_error',type=float,default=5e-7)
    ap.add_argument('--max_full_transport_error',type=float,default=1e-3)
    a=ap.parse_args()
    if not (a.phase_samples>=3 and .35<=a.q_start<a.q_end<=.65 and a.transport_steps>=20 and a.transport_q_start>=a.q_start and a.transport_q_start<a.q_end):raise ValueError('Invalid window')
    res=run(a)
    print(json.dumps({'status':res['status'],'cases':len(res['cases']),'events':len(res['handover_events']),'controls':res['controls']},indent=2),flush=True)
