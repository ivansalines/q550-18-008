#!/usr/bin/env python3
"""Q550 v18.49t: physically integrated return, end-state closure and memory gating.

Forward is a real 11D Q550 IVP; at t=1 its five kinetic velocities are
externally reversed (as in authenticated ancestry). The subsequent 11D IVP
is physically integrated under the inherited finite-duration drive reversal.
There is NO artificial geometric reverse traversal in this experiment.
An energy/configuration/velocity mismatch is not itself material memory.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from verify_t_parent import verify
from return_math import (I_VEL,velocity_flip,config_distance,full_reversed_distance,
                         reversal_velocity_mismatch,best_dynamic_section,principal_angles)
ROOT=Path(__file__).resolve().parents[1]

def write_csv(fn,rows):
    if not rows:return
    dest=ROOT/'results'/fn;dest.parent.mkdir(exist_ok=True,parents=True)
    with dest.open('w',newline='') as fp:
        keys=list(dict.fromkeys(k for row in rows for k in row));w=csv.DictWriter(fp,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    sdir,sreport,ancestry=verify()
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import (kinetic_frame_derivative,deforming_frame,spectral_generator)
    from kinetic_metric import embedding_and_jac
    ex=Experiment(args)
    # Recover the genuine 11D initial states of the authenticated historical forward legs.
    hist_candidates=[p for p in (ROOT/'runtime/parent_s').rglob('physical_paths.npz') if 'verified_sources/j/' in p.as_posix()]
    if len(hist_candidates)!=1:raise RuntimeError(f'Historical 11D source ambiguous: {len(hist_candidates)}')
    hist=np.load(hist_candidates[0],allow_pickle=False)
    grouped=defaultdict(list)
    for i in range(len(hist['y'])):
        grouped[(str(hist['families'][i]),int(hist['seed_branches'][i]),str(hist['kappa_kind'][i]))].append(i)
    cases=[('original',.327375)] if args.smoke else (
        [('original',.327375),('autonomous',.327375)] if args.focus else
        [('original',.32671875),('original',.327375),('original',.33),('autonomous',.327375),('autonomous',.33)])
    initial={}; forward={}; fframe={};fwd_ledger={}
    controls={'historical_forward_regression':float(ex.regression),
      'max_turning_state_residual':0.,'max_turning_energy_jump':0.,
      'max_physical_ledger_error':0.,'min_common_frame_relative_gap':1.,
      'max_constant_chart_projector_error':0.}
    for kind in sorted({k for k,_ in cases}):
        indices=sorted(next(v for (fam,branch,k),v in grouped.items() if fam.startswith('phaseblind') and branch==0 and k==kind),key=lambda idx:float(hist['xi'][idx]))
        y0=np.asarray(hist['y'][indices[0]],float);initial[kind]=y0
        kap=ex.ks[kind]
        fwd,err=ex.original.integrate(ex.physical,ex.original_ramp,ex.support,ex.audit,kap,
             ex.params,ex.slope,ex.omega,y0,args)
        fwd_ledger[kind]=err;forward[kind]=fwd
        controls['max_physical_ledger_error']=max(controls['max_physical_ledger_error'],err)
        end=fwd(1.)[:11];expected=ex.turning[kind]
        dist=float(np.linalg.norm(velocity_flip(end)-expected))
        controls['max_turning_state_residual']=max(controls['max_turning_state_residual'],dist)
        ej=abs(ex.physical.energy(end,kap,ex.params)-ex.physical.energy(expected,kap,ex.params))
        controls['max_turning_energy_jump']=max(controls['max_turning_energy_jump'],ej)
        if dist>args.turning_tolerance or ej>args.energy_jump_tolerance:
            raise RuntimeError('Turnaround mismatch against authenticated physical history')
        def jac(st,kap0,par,sl):return ex.jet.structural_jet(st,kap,ex.params,ex.slope)[1]
        fframe[kind],_=transport_frame(fwd,kap,ex.params,ex.slope,jac,1.,
                    rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
        print('t forward verified',kind,'turnaround mismatch',dist,'energy jump',ej,flush=True)
    rows=[];cases_out=[];failures=[]
    for kind,r in cases:
        kap=ex.ks[kind];fwd=forward[kind];y0=initial[kind];Ff=fframe[kind]
        design=ex.original_ramp.Design('t_dynamic_return_'+kind,'beta:2:2',float(r))
        back,err=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,kap,
          ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
        controls['max_physical_ledger_error']=max(controls['max_physical_ledger_error'],err)
        T=1.+r
        def jac(st,k0,par,sl):return ex.jet.structural_jet(st,kap,ex.params,ex.slope)[1]
        Fr,_=transport_frame(back,kap,ex.params,ex.slope,jac,T,
                     rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
        # Physical return is NOT an inverse matrix transport: its cocycle is
        # composed with the real velocity reversal Jacobian at turnaround.
        R=np.eye(10);R[I_VEL,I_VEL]=-1.
        Fturn=Ff(1.);_,Jinitial=embedding_and_jac(y0[:10],ex.params.m_x,1.)
        def spectral(st,F,clock_sign):
            st=np.asarray(st,float)[:11];field,jacmat,_=ex.jet.structural_jet(st,kap,ex.params,ex.slope)
            # The first 10 physical flow entries do not depend on explicit drive sign.
            # Driver component is external to the material Cauchy-Green tangent frame.
            _,J=embedding_and_jac(st,ex.params.m_x,1.)
            Jdot=kinetic_frame_derivative(st,field,ex.params.m_x,1.,embedding_and_jac)
            B,Bdot=deforming_frame(J,F,Jinitial,Jdot,jacmat[:10,:10])
            out=spectral_generator(B,Bdot)
            S=np.sum(out['projectors'][[5,6,7]],axis=0)
            return S,float(out['min_relative_eigengap'])
        state_initial=y0
        E0=ex.physical.energy(state_initial,kap,ex.params)
        Eturn=ex.physical.energy(fwd(1.)[:11],kap,ex.params)
        Eend=ex.physical.energy(back(T)[:11],kap,ex.params)
        global_config=config_distance(state_initial,back(T)[:11])
        global_velocity=reversal_velocity_mismatch(state_initial,back(T)[:11])
        # Global comparison uses reversed-velocity condition explicitly; this
        # is NOT equivalent to reconstructing the full forward phase orbit.
        print('t dynamic return',kind,'r',r,'global config gap',global_config,
            'reversal velocity gap',global_velocity,flush=True)
        for tA in args.anchor_times:
            a=fwd(tA)[:11]
            tB,d,mincount=best_dynamic_section(a,back,r,T,args.match_samples)
            b=back(tB)[:11]
            evA=ex.physical.energy(a,kap,ex.params);evB=ex.physical.energy(b,kap,ex.params)
            vel=reversal_velocity_mismatch(a,b)
            revfull=full_reversed_distance(a,b)
            # forward and return mechanical ledger terms are measured from
            # their OWN branch starts, not incorrectly subtracted as same path.
            FA=np.asarray(fwd(tA)[11:],float);RB=np.asarray(back(tB)[11:],float)
            eig_gap=None;subgap=None;angles=None
            try:
                SA,gA=spectral(a,Ff(tA),1.)
                SB,gB=spectral(b,Fr(tB)@R@Fturn,-1.)
                angles,subgap=principal_angles(SA,SB)
                eig_gap=min(gA,gB)
                controls['min_common_frame_relative_gap']=min(controls['min_common_frame_relative_gap'],eig_gap)
                if eig_gap<args.min_gap:raise RuntimeError('Spectral gap below declared floor')
                # Use deterministic orthogonal reference rotation; must not
                # change gauge-invariant projector distances.
                rng=np.random.default_rng(4919);X=rng.standard_normal((10,10));Q,_=np.linalg.qr(X)
                ref=float(np.linalg.norm(Q@SA@Q.T-Q@SB@Q.T))
                controls['max_constant_chart_projector_error']=max(controls['max_constant_chart_projector_error'],abs(ref-subgap))
            except (ValueError,np.linalg.LinAlgError) as exc:
                failures.append({'kappa_kind':kind,'ramp_xi':r,'anchor_time':tA,
                    'type':type(exc).__name__,'message':str(exc)})
            is_closed=bool(d<=args.config_tolerance and vel<=args.velocity_tolerance and
                abs(evB-evA)<=args.energy_tolerance and
                subgap is not None and subgap<=args.projector_tolerance)
            row={'kappa_kind':kind,'ramp_xi':r,'forward_anchor_time':tA,'return_match_time':tB,
             'elapsed_time_from_anchor':1.+tB-tA,'configuration_distance':d,
             'reverse_velocity_gap':vel,'full_reversed_state_gap':revfull,
             'energy_forward_anchor':evA,'energy_return_match':evB,'energy_difference':evB-evA,
             'forward_drive_work':float(FA[0]),'forward_radial_damping':float(FA[1]),
             'forward_x_damping':float(FA[2]),'forward_x_source':float(FA[3]),
             'return_drive_work':float(RB[0]),'return_radial_damping':float(RB[1]),
             'return_x_damping':float(RB[2]),'return_x_source':float(RB[3]),
             'spectral_projector_distance_common_frame':subgap,
             'principal_angles_deg':json.dumps(angles) if angles is not None else '',
             'minimum_relative_spectral_gap':eig_gap,
             'section_local_minima_count':mincount,'strict_return_closed':int(is_closed)}
            rows.append(row)
        cases_out.append({'kappa_kind':kind,'ramp_xi':r,'physical_return_duration':T,
          'initial_energy':E0,'turning_energy':Eturn,'final_energy':Eend,
          'total_energy_change':Eend-E0,'global_start_to_final_config_gap':global_config,
          'global_start_to_final_reverse_velocity_gap':global_velocity,
          'forward_11d_ledger_error':fwd_ledger[kind], 'return_11d_ledger_error':err})
    write_csv('dynamic_matched_sections.csv',rows)
    write_csv('physical_return_global_endpoints.csv',cases_out)
    write_csv('spectral_evaluation_failures.csv',failures)
    closure_count=sum(int(x['strict_return_closed']) for x in rows)
    status=('DYNAMIC_RETURN_MATCHED_CANDIDATE_NOT_CERTIFICATE' if closure_count else
           'DYNAMIC_RETURN_NOT_CLOSED_AT_TESTED_SECTIONS')
    if failures:status+='__SPECTRAL_EVALUATIONS_PARTIAL'
    report={'audit':'v18.49t — Dynamical Return Closure & Material-Memory Discrimination Audit',
      'status':status,'parent':ancestry,'genuine_physical_return':True,
      'external_velocity_reversal_at_turning':True,
      'comparisons_without_canonical_endpoint_gluing':True,
      'cases':cases_out,'physical_sections':rows,
      'counts':{'cases':len(cases),'sections':len(rows),'strict_closed_sections':closure_count,
                'spectral_failed_sections':len(failures),'forward_reintegrations':len(forward),
                'return_reintegrations':len(cases),'forward_tangent':len(forward),
                'return_tangent':len(cases)},'controls':controls,
      'tolerances':{'config':args.config_tolerance,'velocity':args.velocity_tolerance,
          'energy':args.energy_tolerance,'projector':args.projector_tolerance,
          'spectral_gap':args.min_gap},'limitations':[
       'Real 11D forward and real 11D return with externally imposed velocity flip and phase-drive reversal; not a closed autonomous orbit.',
       'Closest configuration sections are optimized independently and are not assumed physically identical.',
       'Unmatched state/projector endpoints cannot certify material-memory holonomy; no canonical connector is silently inserted.',
       'Phase/time delays and energy differences measured on unmatched sections do not prove hysteretic constitutive memory.',
       'Spectral projectors are compared using the common INITIAL kinetic material frame, including the reversal Jacobian.',
       'The v18.49s two-path SO3 holonomy remains a different, connector-dependent diagnostic.',
       'Floating point and the stated mechanical model; no interval proof or physical flip theorem.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
             'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    print('v18.49t',status,'cases',len(cases),'sections',len(rows),'matched',closure_count,flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true');p.add_argument('--focus',action='store_true')
    p.add_argument('--anchor-times',type=float,nargs='+',default=[.55,.65,.75])
    p.add_argument('--match-samples',type=int,default=101)
    p.add_argument('--config-tolerance',type=float,default=1e-4)
    p.add_argument('--velocity-tolerance',type=float,default=1e-4)
    p.add_argument('--energy-tolerance',type=float,default=1e-5)
    p.add_argument('--projector-tolerance',type=float,default=1e-3)
    p.add_argument('--min-gap',type=float,default=1e-6)
    p.add_argument('--turning-tolerance',type=float,default=1e-7)
    p.add_argument('--energy-jump-tolerance',type=float,default=1e-7)
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    args=p.parse_args()
    if any(not .1<t<.99 for t in args.anchor_times) or args.match_samples<21:
        p.error('Invalid anchor times / match grid')
    run(args)
