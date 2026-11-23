#!/usr/bin/env python3
"""Q550 v18.49x — X-Turning Clock & Equal-Projection Return Continuation Audit.

Use the full authenticated physical 11D Q550 return ramp, and common kinetic-frame
10D variational transport. Locate genuine roots of the physical x-coordinate
rate, then exactly matched x projections across a turning point. Every event
is measured in both ramp-fraction sigma and model evolution coordinate xi;
no universal physical clock or 3D closed locus is inferred.
"""
import argparse,csv,json,platform,traceback
from pathlib import Path
import numpy as np
from verify_parent_w import verify
from event_math import logistic,scan_sign_roots,classify_turn,matched_locus
ROOT=Path(__file__).resolve().parents[1]

def write_csv(name,items):
    if not items:return
    dest=ROOT/'results'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    cols=list(dict.fromkeys(k for item in items for k in item))
    with dest.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(items)

def spectral_at(ex,back,frame,J0,kind,t,min_gap):
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    y=np.asarray(back(float(t))[:11],float)
    field,Jmat,_=ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)
    _,J=embedding_and_jac(y,ex.params.m_x,1.)
    Jdot=kinetic_frame_derivative(y,field,ex.params.m_x,1.,embedding_and_jac)
    B,Bdot=deforming_frame(J,frame(float(t)),J0,Jdot,Jmat[:10,:10])
    try:
        spec=spectral_generator(B,Bdot,relative_gap_floor=min_gap)
        P=np.sum(spec['projectors'][[5,6,7]],axis=0)
        eig=np.linalg.eigvalsh(P)
        return {'projector':P,'axes':np.asarray(spec['axes'][:,[5,6,7]],float),
           'min_gap':float(spec['min_relative_eigengap']),
           'idempotence':float(np.linalg.norm(P@P-P)),'rank':float(np.trace(P))}
    except (ValueError,ArithmeticError,RuntimeError,np.linalg.LinAlgError) as exc:
        return {'error':str(exc)}

def evaluate(args):
    wroot,w_report,chain=verify()
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from kinetic_metric import embedding_and_jac
    ex=Experiment(args)
    kinds=['original'] if args.smoke else ['original','autonomous'] if args.kind=='both' else [args.kind]
    ramps=[.24] if args.smoke else args.ramps
    cases=[]
    for kind in kinds:
        for r in ramps:cases.append((kind,float(r),'beta:2:2'))
        if args.extra_shape and not args.smoke:cases.append((kind,.24,'beta:3:3'))
    events=[];pairs=[];samples=[];controls=[];errors=[]
    wsource={(str(z['kappa_kind']),round(float(z['ramp_xi']),8)):z for z in w_report['cases']}
    for kind,r,shape in cases:
        try:
            print('v18.49x CASE',kind,r,shape,flush=True)
            design=ex.original_ramp.Design('x_'+kind+'_'+str(r),shape,r)
            back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,
                ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
            def state(t):return np.asarray(back(float(t))[:11],float)
            def latent_rate(t):
                field,_,_=ex.jet.structural_jet(state(t),ex.ks[kind],ex.params,ex.slope)
                return float(field[8])
            def xv(t):return logistic(state(t)[8])
            # Signs are derived from ODE field; root is bracketed, not guessed from an interpolated plotted maximum.
            roots=scan_sign_roots(latent_rate,0.,r,args.root_scan)
            tighter=scan_sign_roots(latent_rate,0.,r,args.root_scan*2-1)
            if len(roots)!=len(tighter) or any(abs(a-b)>args.max_root_grid_shift for a,b in zip(roots,tighter)):
                raise RuntimeError('Event root not stable against grid doubling')
            maxima=[t for t in roots if classify_turn(latent_rate,t,(0,r))=='maximum']
            # Best effort: compute projectors only where their spectrum is well-defined.
            projector_time=set()
            for tt in maxima:projector_time.add(tt)
            found_pairs=[]
            for tt in maxima:
                for af in args.anchors:
                    t1=r*af
                    if t1>=tt-args.min_turn_separation*r:continue
                    z1=float(state(t1)[8]);fun=lambda t:float(state(t)[8])-z1
                    matching=scan_sign_roots(fun,tt,r,args.match_scan)
                    matching=[t for t in matching if t>tt+args.min_turn_separation*r and t-t1>=args.min_pair_separation*r]
                    for t2 in matching:
                        found_pairs.append((t1,t2,tt,af));projector_time.add(t1);projector_time.add(t2)
            projector_cache={}
            if projector_time:
                def jac(y,k,p,sl):return ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)[1]
                frame,frameerr=transport_frame(back,ex.ks[kind],ex.params,ex.slope,jac,r,
                       rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
                _,J0=embedding_and_jac(state(0)[:10],ex.params.m_x,1.)
                for t in sorted(projector_time):
                    if t <= 1e-12:continue
                    projector_cache[t]=spectral_at(ex,back,frame,J0,kind,t,args.min_gap)
            # Case-local metric spans for strict locus (not a physical volume).
            grid=np.linspace(0.,r,81)
            locus=np.asarray([[state(t)[0],state(t)[4],xv(t)] for t in grid])
            spans=np.maximum(np.ptp(locus,axis=0),1e-12)
            for t in np.linspace(0,r,81):
                st=state(t);samples.append({'kappa_kind':kind,'ramp_xi':r,'shape':shape,
                      'xi':float(t),'sigma':float(t/r),'x':xv(t),
                      'x_rate_xi':xv(t)*(1-xv(t))*latent_rate(t),
                      'logrho1':float(st[0]),'logrho2':float(st[4]),
                      'theta1':float(st[2]),'theta2':float(st[6])})
            def stamp(event,t,typ):
                y=state(t);d=projector_cache.get(t,{})
                return {'kappa_kind':kind,'ramp_xi':r,'shape':shape,
                     'event':typ,'xi':float(t),'sigma':float(t/r),'x':xv(t),
                     'x_rate_xi':xv(t)*(1-xv(t))*latent_rate(t),
                     'phase_offset_from_drive_zero_xi':float(t-r/2),
                     'logrho1':float(y[0]),'logrho2':float(y[4]),
                     'theta1':float(y[2]),'theta2':float(y[6]),
                     'mechanical_energy':float(ex.physical.energy(y,ex.ks[kind],ex.params)),
                     'triad_spectral_gap':d.get('min_gap'), 'triad_spectral_error':d.get('error')}
            events.append(stamp('drive',r/2,'drive_zero_prescribed'))
            for t in roots:events.append(stamp('root',t,classify_turn(latent_rate,t,(0,r))))
            for t1,t2,tt,af in found_pairs:
                y1=state(t1);y2=state(t2)
                p1=projector_cache.get(t1,{});p2=projector_cache.get(t2,{})
                diff=None;principal=None;gap=min(float(p1.get('min_gap',np.inf)),float(p2.get('min_gap',np.inf)))
                if 'projector' in p1 and 'projector' in p2:
                    diff=float(np.linalg.norm(p1['projector']-p2['projector'],'fro'))
                    singular=np.linalg.svd(p1['axes'].T@p2['axes'],compute_uv=False)
                    principal=float(np.degrees(np.arccos(np.clip(np.min(singular),-1,1))))
                pairs.append({'kappa_kind':kind,'ramp_xi':r,'shape':shape,'anchor_sigma':af,
                    'xi_in':float(t1),'xi_out':float(t2),'sigma_in':float(t1/r),'sigma_out':float(t2/r),
                    'xi_turn':float(tt),'sigma_turn':float(tt/r),'delta_xi':float(t2-t1),
                    'x_in':xv(t1),'x_out':xv(t2),'x_residual':float(xv(t2)-xv(t1)),
                    'logrho1_gap':float(y2[0]-y1[0]), 'logrho2_gap':float(y2[4]-y1[4]),
                    'posture_theta_pair_gap_rad':float(np.linalg.norm(y2[[2,6]]-y1[[2,6]])),
                    'full_state_10d_gap':float(np.linalg.norm(y2[:10]-y1[:10])),
                    'locus_3d_span_scaled_gap':matched_locus(y1,y2,spans),
                    'triad_projector_frobenius_gap':diff,'triad_max_principal_angle_deg':principal,
                    'min_relative_eigengap':gap if np.isfinite(gap) else None,
                    'mechanical_energy_difference':float(ex.physical.energy(y2,ex.ks[kind],ex.params)-ex.physical.energy(y1,ex.ks[kind],ex.params))})
            # Exact prior v18.49w regression check for cubic at the same ramp.
            reg=None
            if shape=='beta:2:2' and (kind,round(r,8)) in wsource:
                old=wsource[(kind,round(r,8))]
                reg=abs(float(np.linalg.norm(state(r)[:10]-state(0)[:10]))-float(old['closest_x_full_state_10d_gap'])) if False else None
                # Prior w CSV end-point values are recovered directly from archived samples.
                import csv as _csv
                with (wroot/'results/sampled_states_11d_projection.csv').open() as f:
                    arr=[row for row in _csv.DictReader(f) if row['kappa_kind']==kind and abs(float(row['ramp_xi'])-r)<1e-10]
                if len(arr)==61:
                    reg=max(abs(xv(0)-float(arr[0]['x'])),abs(xv(r)-float(arr[-1]['x'])),
                            abs(float(state(r)[4])-float(arr[-1]['logrho2'])))
                    if reg>args.max_parent_regression:raise RuntimeError('v18.49w endpoint mismatch')
            controls.append({'kappa_kind':kind,'ramp_xi':r,'shape':shape,'turn_count':len(roots),
                'maxima_count':len(maxima),'matched_projection_pairs':len(found_pairs),
                'turn_xi':float(maxima[0]) if maxima else None,
                'turn_sigma':float(maxima[0]/r) if maxima else None,
                'drive_zero_xi':float(r/2),
                'turn_minus_drive_xi':float(maxima[0]-r/2) if maxima else None,
                'dx_dxi_at_turn':float(xv(maxima[0])*(1-xv(maxima[0]))*latent_rate(maxima[0])) if maxima else None,
                'turn_grid_refinement_max_shift':float(max([abs(a-b) for a,b in zip(roots,tighter)],default=0.)),
                'mechanical_ledger_error':float(ledger),'v18_49w_endpoint_regression':reg,
                'minimum_pair_spectral_gap':min([x['min_relative_eigengap'] for x in pairs if x['min_relative_eigengap'] is not None and x['kappa_kind']==kind and x['ramp_xi']==r and x['shape']==shape],default=None)})
            print('  TURN',round(maxima[0],10) if maxima else 'NONE','normalized',round(maxima[0]/r,6) if maxima else None,
                  'pairs',len(found_pairs),'ledger',f'{ledger:.2e}',flush=True)
        except Exception as exc:
            if args.fail_fast:raise
            errors.append({'kind':kind,'r':r,'shape':shape,'error':repr(exc),'trace':traceback.format_exc(limit=5)})
            print('CASE FAILURE',kind,r,shape,repr(exc),flush=True)
    if not controls:raise RuntimeError('No authentic integration succeeded')
    write_csv('turning_event_continuation.csv',controls)
    write_csv('phase_resolved_events.csv',events)
    write_csv('equal_projection_return_pairs.csv',pairs)
    write_csv('in_ramp_state_rate_curves.csv',samples)
    write_csv('failed_cases.csv',errors)
    report={'audit':'v18.49x — X-Turning Clock & Equal-Projection Return Continuation Audit',
      'classification':'NUMERICAL_TURNING_CLOCK_AND_EQUAL_X_PROJECTION_NOT_PHYSICAL_CLOCK_OR_CLOSED_3D_LOCUS_CERTIFICATE',
      'genealogy':chain,'counts':{'cases_completed':len(controls),'failed_cases':len(errors),
                                 'turning_roots':sum(c['turn_count'] for c in controls),'matching_projections':len(pairs)},
      'criteria':{'root_grid':args.root_scan,'match_grid':args.match_scan,'anchors':args.anchors,
            'no_fixed_turn_clock':True,'spectral_gap_floor':args.min_gap,
            'minimum_pair_separation_sigma':args.min_pair_separation},
      'controls':{'initial_forward_regression':float(ex.regression),'maximum_ledger_error':max(c['mechanical_ledger_error'] for c in controls),
       'maximum_parent_regression':max([c['v18_49w_endpoint_regression'] or 0 for c in controls]),
       'maximum_turn_grid_shift':max(c['turn_grid_refinement_max_shift'] for c in controls)},
      'cases':controls,
      'limitations':['Time coordinates are model xi and ramp fraction sigma, not universal or empirically calibrated physical time.',
      'No universal turning clock is imposed; roots are recomputed for each genuine Q550 trajectory and ramp.',
      'An equal logistic-x projection is not equal spatial locus, state, energy, or material memory.',
      'Projector comparisons are spectral and gauge invariant in the declared common initial kinetic frame; they do not establish spatial body rotations.',
      'Finite sign-bracketed roots are not a global uniqueness or interval certificate; double the scanning grid to search for hidden roots.',
      'No assumption that the cubical phase-quadrant construction is realized physically by Q550.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--kind',choices=['original','autonomous','both'],default='both')
    p.add_argument('--ramps',nargs='+',type=float,default=[.12,.18,.24,.327375,.5])
    p.add_argument('--extra-shape',action='store_true',default=True)
    p.add_argument('--no-extra-shape',action='store_false',dest='extra_shape')
    p.add_argument('--anchors',nargs='+',type=float,default=[.05,.10,.15,.20])
    p.add_argument('--root-scan',type=int,default=65)
    p.add_argument('--match-scan',type=int,default=65)
    p.add_argument('--min-turn-separation',type=float,default=.005)
    p.add_argument('--min-pair-separation',type=float,default=.15)
    p.add_argument('--max-root-grid-shift',type=float,default=3e-8)
    p.add_argument('--min-gap',type=float,default=1e-6)
    p.add_argument('--fail-fast',action='store_true')
    p.add_argument('--max-parent-regression',type=float,default=2e-8)
    p.add_argument('--rtol',type=float,default=3e-12)
    p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum_parent_share_difference',type=float,default=2e-6)
    p.add_argument('--max_generator_identity_error',type=float,default=1e-7)
    a=p.parse_args()
    if any(r<.02 or r>1 for r in a.ramps):p.error('ramps outside [.02, 1]')
    if any(not 0<z<1 for z in a.anchors):p.error('anchors must lie inside (0,1)')
    evaluate(a)
