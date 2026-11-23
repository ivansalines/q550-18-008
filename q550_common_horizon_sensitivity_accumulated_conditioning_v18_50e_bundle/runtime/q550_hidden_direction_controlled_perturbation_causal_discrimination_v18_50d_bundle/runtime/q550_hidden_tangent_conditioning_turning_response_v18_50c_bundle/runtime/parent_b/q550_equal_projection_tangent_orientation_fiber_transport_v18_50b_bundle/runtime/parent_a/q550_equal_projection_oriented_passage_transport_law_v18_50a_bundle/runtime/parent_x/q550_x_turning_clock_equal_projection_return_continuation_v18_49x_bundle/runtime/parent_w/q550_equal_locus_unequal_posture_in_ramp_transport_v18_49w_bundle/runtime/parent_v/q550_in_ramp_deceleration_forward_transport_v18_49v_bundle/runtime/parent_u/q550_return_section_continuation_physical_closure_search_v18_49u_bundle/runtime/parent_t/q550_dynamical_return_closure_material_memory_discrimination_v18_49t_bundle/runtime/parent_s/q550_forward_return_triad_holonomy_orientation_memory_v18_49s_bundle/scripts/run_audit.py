#!/usr/bin/env python3
"""Q550 v18.49s — Forward–Return Triad Holonomy & Orientation Memory Audit.

Authenticated Q550 11D physical return histories and 10D variational fields.
Forward = phase advance on physical-return branch A; backward = mathematically
reversed phase traversal of distinct physical-return branch B, with canonical
projector endpoint connectors. This IS NOT a physically reversed return drive.
The resulting SO(3) angle is geometric path sensitivity, NOT by itself material
memory or a physical flip. Identity-reversal must return zero.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
import numpy as np
from verify_s_parent import verify
from holonomy_math import integrate_K_cross,loop,principal_so3
ROOT=Path(__file__).resolve().parents[1]

def save_csv(name,rows):
    if not rows:return
    p=ROOT/'results'/name;p.parent.mkdir(exist_ok=True,parents=True)
    with p.open('w',newline='') as f:
        keys=list(dict.fromkeys(k for r in rows for k in r))
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    rdir,rreport,ancestry=verify()
    with (rdir/'results/phase_resolved_gauge_covariant_triad.csv').open(newline='') as parent_fp:
        parent_rows=list(csv.DictReader(parent_fp))
    parent_phase={(row['kappa_kind'],round(float(row['ramp_xi']),10),round(float(row['q']),9)):row for row in parent_rows}
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    from geometry_math import decompose as gdecompose
    from triad_math import decompose as tdecompose,aligned_relative_rotation
    ex=Experiment(args)
    parent={(c['kappa_kind'],round(c['ramp_xi'],10)):c for c in rreport['cases']}
    primary=('original',.327375)
    rivals=[('original',.33)] if args.smoke else (
        [('original',.32671875),('original',.33),('autonomous',.327375)] if args.focus else
        [('original',.32671875),('original',.33),('autonomous',.327375),('autonomous',.33)])
    keys=[primary]+rivals
    cases={};controls={'max_parent_share_regression':0.,'max_parent_angle_regression_deg':0.,
       'max_roundtrip_same_path_error':0.,'max_projector_transport_error':0.,
       'max_conn_endpoint_error':0.,'min_conn_singular':1.,'min_relative_spectral_gap':1.,
       'max_gauge_orthogonal_angle_difference_deg':0.,'max_orthogonal_chart_angle_difference_deg':0.,
       'max_reverse_loop_reciprocity_deg':0.,'max_parent_11D_ledger_error':0.,'max_holonomy_refinement_delta_deg':0.}
    observation_rows=[];comparison_rows=[];self_rows=[]
    windows=[(args.q_start,args.q_end,'full')]
    if not args.no_subwindows:
        windows +=[(args.q_start+.005,args.q_end,'late'),(args.q_start,args.q_end-.005,'early')]
    for kind,r in keys:
        print('v18.49s re-integrate physical 11D/tangent 10D',kind,r,flush=True)
        k=ex.ks[kind]
        design=ex.original_ramp.Design('s_holonomy_'+kind,'beta:2:2',float(r))
        back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,k,ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
        ex.integrations['physical_return_11D']+=1
        controls['max_parent_11D_ledger_error']=max(controls['max_parent_11D_ledger_error'],float(ledger))
        def jac(st,kap,par,sl):return ex.jet.structural_jet(st,k,ex.params,ex.slope)[1]
        frame,_=transport_frame(back,k,ex.params,ex.slope,jac,1.+r,
                    rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
        ex.integrations['tangent_10D']+=1
        _,J0=embedding_and_jac(back(0.)[:10],ex.params.m_x,1.)
        cache={}
        def obs(q, back=back, frame=frame, k=k, r=r, J0=J0, cache=cache):
            # Explicit capture: each trajectory retains its own physical history.
            q=float(q); key=round(q,14)
            if key not in cache:
                t=r+q;st=back(t)[:11]
                field,jacmat,_=ex.jet.structural_jet(st,k,ex.params,ex.slope)
                _,J=embedding_and_jac(st,ex.params.m_x,1.)
                Jdot=kinetic_frame_derivative(st,field,ex.params.m_x,1.,embedding_and_jac)
                B,Bdot=deforming_frame(J,frame(t),J0,Jdot,jacmat[:10,:10])
                out=spectral_generator(B,Bdot);g=gdecompose(out)
                tri=tdecompose(out['generator'],out['projectors'])
                cache[key]={'S':tri['S'],'Kcross':tri['kc'],'axes':out['axes'][:,[5,6,7]],
                    'gap':float(out['min_relative_eigengap']),'share_67':float(g['share_67']),
                    'share_78':float(g['share_78'])}
            return cache[key]
        for q in np.linspace(args.q_start,args.q_end,args.phase_samples):
            o=obs(q)
            controls['min_relative_spectral_gap']=min(controls['min_relative_spectral_gap'],o['gap'])
            observation_rows.append({'kappa_kind':kind,'ramp_xi':r,'q':float(q),
                    'share_67':o['share_67'],'share_78':o['share_78'],
                    'margin_78_minus_67':o['share_78']-o['share_67'],'min_relative_gap':o['gap']})
        base=parent[(kind,round(r,10))]
        end=obs(args.q_end)
        for qmatch in (args.q_start,args.q_end):
            keyparent=(kind,round(r,10),round(qmatch,9))
            if keyparent in parent_phase:
                old=parent_phase[keyparent]
                now=obs(qmatch)
                delta=max(abs(now['share_67']-float(old['share_67'])),
                          abs(now['share_78']-float(old['share_78'])))
                controls['max_parent_share_regression']=max(controls['max_parent_share_regression'],delta)
                if delta>1e-7:raise RuntimeError('Parent r phase shares not reproduced')
        # The parent r CSV stores phase endpoints precisely; use its parent q report
        # via share regression only when the matching parent record explicitly supplies a share.
        # Separate endpoint angle regression is measured in the same Kato reference.
        fp=lambda q:obs(q)['Kcross']
        u=integrate_K_cross(fp,args.q_start,args.q_end,2*args.transport_steps)
        ucoarse=integrate_K_cross(fp,args.q_start,args.q_end,args.transport_steps)
        A0=obs(args.q_start)['axes'].copy(); Ae=obs(args.q_end)['axes'].copy()
        for i in range(3):
            if np.dot(A0[:,i],Ae[:,i])<0:Ae[:,i]*=-1
        rot=aligned_relative_rotation(A0,u,Ae)[3]
        degree=float(np.degrees(rot))
        regr=abs(degree-float(base['parallel_triads_relative_rotation_deg']))
        controls['max_parent_angle_regression_deg']=max(controls['max_parent_angle_regression_deg'],regr)
        if regr>args.max_parent_angle_error_deg:
            raise RuntimeError(f'v18.49r rotation regression mismatch: {kind}/{r} {regr} deg')
        cases[(kind,r)]={'kind':kind,'r':r,'obs':obs,'U':u,'U_coarse':ucoarse,'parent_angle_deg':degree,
                         'refinement':float(np.linalg.norm(u-ucoarse)),
                         'S0':obs(args.q_start)['S'],'S1':obs(args.q_end)['S'],
                         'A0':A0,'q0':args.q_start,'q1':args.q_end}
        S0=cases[(kind,r)]['S0'];S1=cases[(kind,r)]['S1']
        perr=float(np.linalg.norm(u@S0@u.T-S1))
        controls['max_projector_transport_error']=max(controls['max_projector_transport_error'],perr)
        if perr>args.max_projector_error:raise RuntimeError('Kato transport does not track projector')
        reverse=integrate_K_cross(fp,args.q_end,args.q_start,2*args.transport_steps)
        self_error=float(np.linalg.norm(reverse@u-np.eye(10)))
        controls['max_roundtrip_same_path_error']=max(controls['max_roundtrip_same_path_error'],self_error)
        if self_error>args.max_reversal_error:raise RuntimeError('Exact path reversal is not null')
        self_rows.append({'kappa_kind':kind,'ramp_xi':r,'self_reversed_10D_norm_error':self_error,
                          'Kato_projector_error':perr,'relative_triad_angle_deg':degree,
                          'Kato_step_refinement':cases[(kind,r)]['refinement']})
        print('  r relative triad rotation:',round(degree,8),'deg; roundtrip null:',self_error,
              'Kato projector error:',perr,flush=True)
    rng=np.random.default_rng(4919)
    for (ka,ra),A in [(primary,cases[primary])]:
        for kb,rb in rivals:
            B=cases[(kb,rb)]
            for q0,q1,label in windows:
                def endpoint_and_U(c):
                    o=c['obs'];F=o(q0)['S'];E=o(q1)['S']
                    U=(c['U'] if label=='full' else integrate_K_cross(lambda q:o(q)['Kcross'],q0,q1,2*args.transport_steps))
                    return F,E,U
                A0,A1,UA=endpoint_and_U(A)
                B0,B1,UB=endpoint_and_U(B)
                basis=A['obs'](q0)['axes']
                rloop=loop(A0,A1,UA,B0,B1,UB,basis)
                UAc=(A['U_coarse'] if label=='full' else integrate_K_cross(
                    lambda q:A['obs'](q)['Kcross'],q0,q1,args.transport_steps))
                UBc=(B['U_coarse'] if label=='full' else integrate_K_cross(
                    lambda q:B['obs'](q)['Kcross'],q0,q1,args.transport_steps))
                rloop_coarse=loop(A0,A1,UAc,B0,B1,UBc,basis)
                angle_refinement=abs(rloop['angle_deg']-rloop_coarse['angle_deg'])
                controls['max_holonomy_refinement_delta_deg']=max(controls['max_holonomy_refinement_delta_deg'],angle_refinement)
                controls['min_conn_singular']=min(controls['min_conn_singular'],rloop['connector_min_singular'])
                controls['max_conn_endpoint_error']=max(controls['max_conn_endpoint_error'],rloop['connector_max_error'])
                if rloop['subspace_loop_closure']>args.max_loop_closure_error:
                    raise RuntimeError('Two-path loop fails to close on its starting subspace')
                # Self inverse after reversing the comparison order has same angle.
                rbasis=B['obs'](q0)['axes']
                revloop=loop(B0,B1,UB,A0,A1,UA,rbasis)
                reciprocity=abs(revloop['angle_deg']-rloop['angle_deg'])
                controls['max_reverse_loop_reciprocity_deg']=max(controls['max_reverse_loop_reciprocity_deg'],reciprocity)
                # Sign flips of initial eigenline basis conjugate H by a diagonal ±1 matrix.
                signs=rng.choice([-1.,1.],3);flipped=basis*signs[None,:]
                signedH=flipped.T@rloop['Uloop']@flipped
                angle_flip=np.degrees(principal_so3(signedH)[0])
                controls['max_gauge_orthogonal_angle_difference_deg']=max(controls['max_gauge_orthogonal_angle_difference_deg'],
                                                                    abs(angle_flip-rloop['angle_deg']))
                # Chart conjugation by constant proper orthogonal Q, preserving the same metric.
                Z=rng.normal(size=(10,10));V,_=np.linalg.qr(Z)
                if np.linalg.det(V)<0:V[:,0]*=-1
                mapped=loop(V@A0@V.T,V@A1@V.T,V@UA@V.T,V@B0@V.T,V@B1@V.T,V@UB@V.T,V@basis)
                controls['max_orthogonal_chart_angle_difference_deg']=max(controls['max_orthogonal_chart_angle_difference_deg'],
                                                                    abs(mapped['angle_deg']-rloop['angle_deg']))
                rec={'leg_a':f'{ka}:{ra:.9f}','leg_b':f'{kb}:{rb:.9f}',
                   'pair_type':('same_kappa_duration_shift' if ka==kb else 'cross_kappa'),
                   'window':label,'q_start':q0,'q_end':q1,
                   'loop_holonomy_angle_deg':rloop['angle_deg'],
                   'loop_end_subspace_error':rloop['subspace_loop_closure'],
                   'connector_min_singular':rloop['connector_min_singular'],
                   'connector_max_error':rloop['connector_max_error'],
                   'start_projector_distance':float(np.linalg.norm(A0-B0)),
                   'end_projector_distance':float(np.linalg.norm(A1-B1)),
                   'triad_orthogonality_error':rloop['subspace_restricted_orthogonality_error'],
                   'triad_restricted_det':rloop['subspace_restricted_det'],
                   'holonomy_step_refinement_delta_deg':angle_refinement,
                   'same_path_A_inverse_control':next(x['self_reversed_10D_norm_error'] for x in self_rows if x['kappa_kind']==ka and x['ramp_xi']==ra),
                   'angle_reciprocity_error_deg':reciprocity,
                   'angle_sign_flip_error_deg':abs(angle_flip-rloop['angle_deg']),
                   'angle_constant_chart_error_deg':abs(mapped['angle_deg']-rloop['angle_deg']),
                   'min_path_relative_gap':min(A['obs'](q0)['gap'],A['obs'](q1)['gap'],B['obs'](q0)['gap'],B['obs'](q1)['gap'])}
                comparison_rows.append(rec)
                print('  loop',rec['leg_a'],'vs',rec['leg_b'],label,
                    'SO3 angle',round(rloop['angle_deg'],10),'deg; endpoints mismatch',round(rec['end_projector_distance'],7),flush=True)
    save_csv('phase_resolved_two_path_triads.csv',observation_rows)
    save_csv('forward_reverse_null_controls.csv',self_rows)
    save_csv('two_path_canonical_connector_holonomy.csv',comparison_rows)
    report={'audit':'Q550 v18.49s — Forward–Return Triad Holonomy & Orientation Memory Audit',
      'status':'NUMERICAL_TWO_PATH_DIAGNOSTIC_NOT_MATERIAL_MEMORY_CERTIFICATE',
      'parent_verification':ancestry,
      'replayed_cases':len(keys),'comparisons':len(comparison_rows),'cases':self_rows,
      'two_path_loops':comparison_rows,'controls':controls,'integrations':ex.integrations,
      'definitions':{'triad_modes':'rank-ordered 6,7,8 (0-based indices 5,6,7)',
         'physical_dynamics':'authenticated physical return legs re-integrated with inherited Q550 model and fixed initial kinetic observer',
         'loop':'Advance physically simulated return leg A in q, reverse parametrization of separately simulated return leg B, connect start and end rank-3 projectors by canonical direct rotations',
         'connector':'polar(QP+(I-Q)(I-P)), uniquely specified near coincident projectors',
         'holonomy':'SO(3) conjugacy angle of A0.T C0.T UB.T C1 UA A0 (under explicit initial line reference)',
         'control':'Same trajectory traversed forwards then back gives identity to numerical tolerance',
         'phase_windows':windows,'cross_Kato_steps_fine':2*args.transport_steps},
      'scientific_limits':[
         'Two different post-kick physical return trajectories are sampled; reverse traversal of B is mathematical, NOT integration of a physical time-reversed drive.',
         'The two paths do not have identical endpoint projectors. A specified canonical connector closes them. Holonomy depends on this closure choice.',
         'Nonzero two-path SO(3) holonomy establishes geometric path dependence of the rank-3 eigenspace transport, not material hysteretic memory.',
         'There is no gauge-independent absolute orientation of three unoriented eigenlines; the SO(3) conjugacy angle is reference-sign invariant.',
         'The result is floating-point numerical evidence in the inherited fixed kinetic reference, not a rigorous interval certificate or physical flip theorem.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
        'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true',help='Two authenticated trajectories and one loop')
    p.add_argument('--focus',action='store_true',help='Four trajectories and three loops')
    p.add_argument('--q-start',type=float,default=.63)
    p.add_argument('--q-end',type=float,default=.65)
    p.add_argument('--phase-samples',type=int,default=101)
    p.add_argument('--transport-steps',type=int,default=48)
    p.add_argument('--no-subwindows',action='store_true')
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025);p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13);p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8);p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--max_parent_angle_error_deg',type=float,default=.002)
    p.add_argument('--max_projector_error',type=float,default=1e-4)
    p.add_argument('--max_reversal_error',type=float,default=1e-8)
    p.add_argument('--max_loop_closure_error',type=float,default=2e-4)
    args=p.parse_args()
    if not (.60<=args.q_start<args.q_end<=.65 and args.phase_samples>=15 and args.transport_steps>=16):
        p.error('Invalid requested phase window or resolution')
    out=run(args)
    print(json.dumps({'status':out['status'],'cases':out['replayed_cases'],
        'comparisons':out['comparisons'],'controls':out['controls']},indent=2))
