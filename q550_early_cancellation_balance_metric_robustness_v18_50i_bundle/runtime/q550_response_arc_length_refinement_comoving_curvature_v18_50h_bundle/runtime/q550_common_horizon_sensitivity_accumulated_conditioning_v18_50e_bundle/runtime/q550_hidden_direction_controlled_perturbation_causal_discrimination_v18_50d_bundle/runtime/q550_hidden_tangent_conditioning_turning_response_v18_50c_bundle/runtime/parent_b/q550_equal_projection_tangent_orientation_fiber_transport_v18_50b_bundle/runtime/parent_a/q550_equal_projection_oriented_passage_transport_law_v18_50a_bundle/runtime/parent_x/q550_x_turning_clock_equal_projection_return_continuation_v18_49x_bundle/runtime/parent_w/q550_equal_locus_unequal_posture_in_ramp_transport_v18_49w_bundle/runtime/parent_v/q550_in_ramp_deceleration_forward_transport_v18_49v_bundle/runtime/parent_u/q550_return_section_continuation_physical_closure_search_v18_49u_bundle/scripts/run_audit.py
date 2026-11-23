#!/usr/bin/env python3
"""v18.49u genuine Q550 return-section continuation without artificial closure.

Original 11D forward + externally flipped velocities + original signed/ramped
11D physical return; 10D tangent projectors only evaluated at selected
joint-state minima. Full-state match is phase-wrapped and requires reversed
velocities; *lifted* phase difference is separately reported.
"""
import argparse,csv,json,platform,sys,traceback
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_u_parent import verify
from section_math import best_candidates,metrics,strict_gate,wrap
ROOT=Path(__file__).resolve().parents[1]

def write_csv(filename,rows):
    if not rows:return
    p=ROOT/'results'/filename;p.parent.mkdir(exist_ok=True,parents=True)
    keys=list(dict.fromkeys(k for r in rows for k in r.keys()))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    tdir,parent_report,ancestry=verify()
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    # Use the exact, authenticated original Q550 implementation and initial states.
    ex=Experiment(args)
    hist_candidates=[p for p in (ROOT/'runtime/parent_t').rglob('physical_paths.npz') if 'verified_sources/j/' in p.as_posix()]
    if len(hist_candidates)!=1:raise RuntimeError('Nonunique historical 11D forward provenance')
    hist=np.load(hist_candidates[0],allow_pickle=False)
    grouped=defaultdict(list)
    for i in range(len(hist['y'])):
        grouped[(str(hist['families'][i]),int(hist['seed_branches'][i]),str(hist['kappa_kind'][i]))].append(i)
    requested=['original'] if args.smoke else ['original','autonomous']
    if args.kind!='both':requested=[args.kind]
    start={};fwd={};fwd_ledger={}
    for kind in requested:
        indices=sorted(next(v for (fam,br,k),v in grouped.items() if fam.startswith('phaseblind') and br==0 and k==kind),
            key=lambda idx:float(hist['xi'][idx]))
        start[kind]=np.asarray(hist['y'][indices[0]],float)
        fwd[kind],err=ex.original.integrate(ex.physical,ex.original_ramp,ex.support,ex.audit,
                ex.ks[kind],ex.params,ex.slope,ex.omega,start[kind],args)
        fwd_ledger[kind]=float(err)
        turn=fwd[kind](1.)[:11].copy();turn[[1,3,5,7,9]]*=-1.
        if np.linalg.norm(turn-ex.turning[kind])>1e-7:raise RuntimeError('Turning mismatch vs original verified Q550')
        print('v18.49u verified original forward',kind,'ledger',err,flush=True)
    if args.ramp_values:
        ramp_values=sorted(set(float(x) for x in args.ramp_values))
    elif args.smoke:
        ramp_values=[.327375]
    elif args.focus:
        ramp_values=[.24,.327375,.42]
    else:
        ramp_values=[.12,.18,.24,.285,.327375,.36,.42,.50,.70,.90]
    if any(x<.07 or x>1.0 for x in ramp_values):raise ValueError('Ramp values outside 0.07..1.0')
    cases={};ramp_rows=[];candidates=[];failure_rows=[];frames={};step_log=[]
    for kind in requested:
        def integrate_case(r):
            key=(kind,round(r,12))
            if key in cases:return cases[key]
            k0=ex.ks[kind];design=ex.original_ramp.Design('u_dynamic_return_'+kind,'beta:2:2',r)
            back,err=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,k0,
                ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
            if err>args.maximum_ledger_error:raise RuntimeError('Physical mechanical ledger exceeds tolerance')
            local=best_candidates(fwd[kind],back,r,tuple(args.anchor_bounds),tuple(args.return_phase_bounds),
                args.grid_anchor,args.grid_phase,args.optim_seeds)
            E0=ex.physical.energy(start[kind],k0,ex.params)
            Eend=ex.physical.energy(back(1.+r)[:11],k0,ex.params)
            for entry in local:
                sa=entry['anchor_time'];tb=entry['return_time']
                A=fwd[kind](sa)[:11];B=back(tb)[:11]
                EA=ex.physical.energy(A,k0,ex.params);EB=ex.physical.energy(B,k0,ex.params)
                entry.update({'kappa_kind':kind,'ramp_xi':r,
                    'energy_forward_anchor':float(EA),'energy_return_match':float(EB),
                    'energy_difference':float(EB-EA),
                    'elapsed_time_from_anchor':float(1.+tb-sa),
                    'minimum_tolerance_ratio_preprojector':float(max(entry['config']/args.config_tolerance,
                        entry['velocity']/args.velocity_tolerance,abs(EB-EA)/args.energy_tolerance)),
                    'spectral_projector_distance':None,'minimum_relative_gap':None,
                    'strict_return_closed':False})
                candidates.append(entry)
            summary={'kappa_kind':kind,'ramp_xi':r,'return_duration':1.+r,
               'min_config':min(x['config'] for x in local),
               'min_velocity':min(x['velocity'] for x in local),
               'min_joint_full_state':min(x['full'] for x in local),
               'min_energy_difference_abs_at_joint_candidate':abs(next(x for x in local if x['objective']=='joint_full_state')['energy_difference']),
               'return_ledger_error':float(err),'initial_energy':float(E0),'final_energy':float(Eend),
               'max_forward_ledger_error':fwd_ledger[kind],
               'candidate_at_bounds':int(any(x['boundary_hit'] for x in local))}
            ramp_rows.append(summary);cases[key]=(back,err,summary)
            print('v18.49u',kind,'r=',r,'min config=',round(summary['min_config'],8),
                  'min full=',round(summary['min_joint_full_state'],8),flush=True)
            return cases[key]
        for r in ramp_values:
            try:integrate_case(r)
            except Exception as e:
                failure_rows.append({'kappa_kind':kind,'ramp_xi':r,'stage':'scan',
                  'error_type':type(e).__name__,'message':str(e)})
                print('v18.49u scan fail',kind,r,repr(e),flush=True)
        # One-dimensional continuation by bracketing neighboring sampled durations
        # about the current lowest joint mismatch; no global optimizer claims.
        for iteration in range(args.refine_rounds):
            rr=sorted((z['ramp_xi'],z['min_joint_full_state']) for z in ramp_rows if z['kappa_kind']==kind)
            if len(rr)<2:break
            j=min(range(len(rr)),key=lambda i:rr[i][1])
            mids=set()
            if j>0:mids.add(.5*(rr[j-1][0]+rr[j][0]))
            if j+1<len(rr):mids.add(.5*(rr[j][0]+rr[j+1][0]))
            for r in sorted(mids):
                try:integrate_case(r)
                except Exception as e:
                    failure_rows.append({'kappa_kind':kind,'ramp_xi':r,'stage':'refine',
                      'error_type':type(e).__name__,'message':str(e)})
        # Select best joint candidates, plus baseline for common-frame spectral checks.
        pool=sorted([c for c in candidates if c['kappa_kind']==kind and c['objective']=='joint_full_state'],
            key=lambda x:x['full'])
        chosen=pool[:args.spectral_top]
        baseline=next((c for c in pool if abs(c['ramp_xi']-.327375)<1e-12),None)
        if baseline and baseline not in chosen:chosen.append(baseline)
        if not chosen:continue
        k0=ex.ks[kind]
        def jac(st,k,params,sl):return ex.jet.structural_jet(st,k0,ex.params,ex.slope)[1]
        Ff,_=transport_frame(fwd[kind],k0,ex.params,ex.slope,jac,1.,
                rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
        _,J0=embedding_and_jac(start[kind][:10],ex.params.m_x,1.)
        R=np.eye(10);R[[1,3,5,7,9],[1,3,5,7,9]]=-1.
        def projector(y,F):
            field,jacmat,_=ex.jet.structural_jet(y,k0,ex.params,ex.slope)
            _,J=embedding_and_jac(y[:10],ex.params.m_x,1.)
            Jdot=kinetic_frame_derivative(y,field,ex.params.m_x,1.,embedding_and_jac)
            B,Bdot=deforming_frame(J,F,J0,Jdot,jacmat[:10,:10])
            spec=spectral_generator(B,Bdot)
            return np.sum(spec['projectors'][[5,6,7]],axis=0),float(spec['min_relative_eigengap'])
        for entry in chosen:
            r=entry['ramp_xi'];back=cases[(kind,round(r,12))][0]
            if (kind,round(r,12)) not in frames:
                frames[(kind,round(r,12))],_=transport_frame(back,k0,ex.params,ex.slope,jac,1.+r,
                    rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            try:
                Fback=frames[(kind,round(r,12))]
                SA,ga=projector(fwd[kind](entry['anchor_time'])[:11],Ff(entry['anchor_time']))
                SB,gb=projector(back(entry['return_time'])[:11],
                    Fback(entry['return_time'])@R@Ff(1.))
                entry['spectral_projector_distance']=float(np.linalg.norm(SA-SB))
                entry['minimum_relative_gap']=min(ga,gb)
                tol=dict(config=args.config_tolerance,velocity=args.velocity_tolerance,
                    energy=args.energy_tolerance,projector=args.projector_tolerance,
                    spectral_gap=args.min_gap,phase_lift_turns=args.phase_lift_tolerance_turns)
                entry['strict_return_closed']=strict_gate(entry,tol,args.require_phase_lift_closure)
                if min(ga,gb)<args.min_gap:entry['strict_return_closed']=False
            except Exception as e:
                failure_rows.append({'kappa_kind':kind,'ramp_xi':r,'stage':'projector',
                  'error_type':type(e).__name__,'message':str(e)})
    if not ramp_rows:raise RuntimeError('No successful physical return computations')
    write_csv('duration_continuation.csv',ramp_rows)
    write_csv('matched_section_candidates.csv',candidates)
    write_csv('evaluation_failures.csv',failure_rows)
    best_config=min(candidates,key=lambda c:c['config'])
    best_full=min((c for c in candidates if c['objective']=='joint_full_state'),key=lambda c:c['full'])
    matched=[c for c in candidates if c['strict_return_closed']]
    status=('NUMERICAL_DYNAMIC_CLOSURE_CANDIDATE_NOT_MEMORY_CERTIFICATE' if matched else
         'NO_PHYSICAL_CLOSURE_IN_EXPLORED_RETURN_SECTION_DOMAIN')
    if failure_rows:status+='__PARTIAL_EVALUATIONS'
    report={'audit':'v18.49u — Return-Section Continuation & Physical Closure Search',
      'status':status,'parent':ancestry,
      'counts':{'physical_forward_reintegrations':len(fwd),'physical_return_reintegrations':len(ramp_rows),
          'optimized_candidate_sections':len(candidates),'strict_closure_candidates':len(matched),
          'tangent_forward':len(requested),'tangent_return':len(frames),
          'evaluation_failures':len(failure_rows)},
      'domain':{'ramp_values_initial':ramp_values,'adaptive_refine_rounds':args.refine_rounds,
          'forward_anchor_bounds':args.anchor_bounds,'return_phase_bounds_relative_to_ramp_end':args.return_phase_bounds,
          'all_returns_exclude_turnaround':True,
          'relative_velocity_matching_condition':'v_return + v_forward = 0',
          'configuration_coordinates':'0,2,4,6,8,10 with indices 2,6,10 wrapped mod 2pi'},
      'best_config_candidate':best_config,'best_joint_candidate':best_full,
      'tolerances':{'config':args.config_tolerance,'velocity':args.velocity_tolerance,
        'energy':args.energy_tolerance,'projector':args.projector_tolerance,
        'spectral_gap':args.min_gap,'optional_lift_turns':args.phase_lift_tolerance_turns},
      'require_phase_lift_closure':args.require_phase_lift_closure,
      'limitations':[
        'A finite coarse-to-adaptive duration search; not proof that a return section cannot exist elsewhere.',
        'Forward/return both genuine Q550 11D integrations under an externally imposed velocity reversal; not spontaneous time reversal.',
        'The search optimizes two section times at each duration; closure may lie outside their declared windows.',
        'Nearest configuration, nearest velocity and nearest full reversed state are separate minima and do not imply closure.',
        'Mechanical-energy matching is checked as an independent gate with full original work/damping/source ledger.',
        'Common-frame spectral projectors are computed only for selected best joint candidates; missing projectors never count as matched.',
        'Wrapped phase is a modulo-2pi matching convention; unwrapped lifted phase difference is reported separately.',
        'A numerical closed candidate alone would NOT certify physical material memory or physical torsion.',
        'No interval enclosure or global continuation theorem is established.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
      'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    print('v18.49u STATUS:',status,'cases',len(ramp_rows),'best joint',best_full['full'],
          'strict closures',len(matched),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--focus',action='store_true')
    p.add_argument('--kind',choices=['original','autonomous','both'],default='both')
    p.add_argument('--ramp-values',type=float,nargs='+')
    p.add_argument('--refine-rounds',type=int,default=1)
    p.add_argument('--anchor-bounds',type=float,nargs=2,default=[.30,.85])
    p.add_argument('--return-phase-bounds',type=float,nargs=2,default=[.10,.96])
    p.add_argument('--grid-anchor',type=int,default=31)
    p.add_argument('--grid-phase',type=int,default=61)
    p.add_argument('--optim-seeds',type=int,default=4)
    p.add_argument('--spectral-top',type=int,default=2)
    p.add_argument('--config-tolerance',type=float,default=1e-4)
    p.add_argument('--velocity-tolerance',type=float,default=1e-4)
    p.add_argument('--energy-tolerance',type=float,default=1e-5)
    p.add_argument('--projector-tolerance',type=float,default=1e-3)
    p.add_argument('--min-gap',type=float,default=1e-6)
    p.add_argument('--require-phase-lift-closure',action='store_true')
    p.add_argument('--phase-lift-tolerance-turns',type=float,default=1e-3)
    p.add_argument('--rtol',type=float,default=3e-12)
    p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    args=p.parse_args()
    if not (.1<args.anchor_bounds[0]<args.anchor_bounds[1]<.99):p.error('Invalid nontrivial forward section bounds')
    if not (0<args.return_phase_bounds[0]<args.return_phase_bounds[1]<=1.):p.error('Invalid return phase bounds')
    if args.grid_anchor<7 or args.grid_phase<7 or args.optim_seeds<1:p.error('Invalid grid/seeds')
    run(args)
