#!/usr/bin/env python3
"""v18.49e: genuinely transported common frame and oriented phase passage markers.

All physical 11D dynamics and input states come from SHA-authenticated historical
Q550 source, with no modifications to the reference RHS. "Passage" means
crossing a DECLARED geometry threshold, not a material cycle or kappa0 period.
"""
from __future__ import annotations
import argparse,csv,json,math,sys,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_parent import verify,dynamic
from frame_math import (transport_frame,physical_to_initial,orthonormal_family,
                        common_decomposition,oriented_crossings,passage_pairs,
                        compare_orientation,gauge_test)
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)
QMIN,QMAX=.20,.80
THRESHOLD=.01

def write_csv(name,records):
    p=ROOT/'results'/name
    if not records:
        p.write_text('status\nno_event\n');return
    keys=list(dict.fromkeys(k for record in records for k in record))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(records)

def run(args):
    d,c,b,a,z,y,j,provenance=verify()
    sys.path.insert(0,str(c/'reference'));sys.path.insert(0,str(c/'scripts'))
    phys=dynamic(c/'reference/physical_math.py','e_original_phys')
    ramp=dynamic(c/'reference/parent_ramp_math.py','e_original_ramp')
    yr=dynamic(c/'reference/y_original_run_audit.py','e_original_y')
    jet=dynamic(c/'reference/structural_jet.py','e_original_jet')
    observer=dynamic(c/'reference/parent_observer_math.py','e_original_observer')
    family=dynamic(c/'scripts/family_math.py','e_original_family')
    support_candidates=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_candidates)!=1:raise RuntimeError('Historical support original source missing or duplicate')
    support=dynamic(support_candidates[0],'e_original_support')
    audit=dynamic(support_candidates[0].parent/'test_support_mobius_monodromy_audit.py','e_original_model')
    h=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    original_report=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(original_report['kappa_original']),
            'autonomous':float(original_report['kappa_autonomous'])}
    omega=float(h['clock_speed']);slope=omega/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(h['y'])):
        groups[(str(h['families'][i]),int(h['seed_branches'][i]),str(h['kappa_kind'][i]))].append(i)
    parent_records={}
    with (d/'results/rank_and_hidden_complement.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            if row['metric']!='euclidean' or int(row['family_size'])!=5 or float(row['rank_tolerance'])!=1e-10:continue
            if abs(float(row['phase_q'])-.50)>1e-10:continue
            parent_records[(row['kappa_kind'],round(float(row['ramp_xi']),8))]=row
    # Every transported frame is relative to the SAME INITIAL TURNING POSTURE of that return.
    physical_runs=0;adjoint_runs=0;frame_runs=0
    max_energy=max_history=max_parent=0.
    max_duality=max_covariance=max_frame_defect=max_balance=0.
    max_clock_mismatch=0.;max_frame_condition=0.
    point_rows=[];events_rows=[];passage_rows=[];scale_rows=[];transport_rows=[]
    n_kappas=1 if args.smoke else 2
    chosen_ramps=(.296333,) if args.smoke else RAMPS
    for kind in tuple(kappas)[:n_kappas]:
        ids=sorted(next(g for (fam,branch,k),g in groups.items()
                  if fam.startswith('phaseblind') and branch==0 and k==kind),key=lambda i:float(h['xi'][i]))
        start=np.asarray(h['y'][ids[0]],float);kap=kappas[kind]
        fwd,err=yr.integrate(phys,ramp,support,audit,kap,params,slope,omega,start,args)
        physical_runs+=1;max_energy=max(max_energy,err)
        max_history=max(max_history,max(float(np.linalg.norm(fwd(t)[:11]-h['y'][i]))
                                    for t,i in zip(np.linspace(0.,1.,41),ids)))
        turn=fwd(1.)[:11].copy();turn[[1,3,5,7,9]]*=-1
        seeds=np.asarray(h['covectors'][ids[-1],:5,:10],float).copy()
        seeds/=np.linalg.norm(seeds,axis=1,keepdims=True)
        U0,sv0,rank0=orthonormal_family(seeds,1e-10)
        for rv in chosen_ramps:
            design=ramp.Design('v18_49e','smoothstep',rv)
            back,err=yr.integrate(phys,ramp,support,audit,kap,params,slope,omega,turn,args,design=design)
            physical_runs+=1;max_energy=max(max_energy,err)
            def jac(state,k,p,sl):return jet.structural_jet(state,k,p,sl)[1]
            time_end=1.+rv
            adjoint,soladj=observer.integrate_dual(back,design,kap,params,slope,omega,jac,seeds,seeds[0],time_end,
                   rtol=args.adjoint_rtol,atol=args.adjoint_atol,max_step=args.adjoint_max_step)
            adjoint_runs+=1
            F,solframe=transport_frame(back,kap,params,slope,jac,time_end,
                      rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            frame_runs+=1
            def states(q):return back(rv+q)[:11],fwd(1.-q)[:11]
            def shape(q):
                yy,xx=states(float(q));return phys.physical_shape_distance(yy,xx)
            qgrid=np.linspace(QMIN,QMAX,args.marker_samples)
            events=oriented_crossings(shape,qgrid,THRESHOLD)
            pairs=passage_pairs(events)
            for i,e in enumerate(events):
                events_rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'event_id':i,'threshold':THRESHOLD,
                       **e,'phase_theta':float(back(rv+e['q'])[10]),'theta_clock_slope':-omega,
                       'event_type':'geometric_threshold_crossing_not_full_11d_recurrence'})
            for i,pair in enumerate(pairs):
                passage_rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'passage_id':i,
                   **pair,'span_over_kappa':pair['span_q']/kap,'span_over_0p2':pair['span_q']/.2,
                   'kappa_closure_if_within_1percent':int(abs(pair['span_q']/kap-1)<.01),
                   '0p2_closure_if_within_1percent':int(abs(pair['span_q']/.2-1)<.01),
                   'interpretation':'connected_subthreshold_interval_only'})
            # Fixed common-frame origins: keep one material frame and 5 original
            # historical covector rows throughout the return.
            qs=sorted(set([round(float(q),12) for q in np.linspace(QMIN,QMAX,19)] +
                 [.35,.50,.55,round(.35+kap,12),round(.55+kap,12),.75]+
                 [round(float(e['q']),12) for e in events]))
            snapshots={}
            for q in qs:
                time=rv+q;yy,xx=states(q)
                delta=family.local_lift(yy,xx)
                gt,vt=adjoint(time)
                ft=F(time)
                pulled,dual_err=physical_to_initial(ft,delta,gt,seeds)
                co=common_decomposition(pulled,U0)
                Ucurrent,svcurrent,rankcurrent=orthonormal_family(gt,1e-10)
                cur=common_decomposition(delta,Ucurrent)
                max_duality=max(max_duality,dual_err)
                frame_defect=np.linalg.norm(gt@ft-seeds)/max(1.,np.linalg.norm(seeds))
                max_frame_defect=max(max_frame_defect,float(frame_defect))
                max_balance=max(max_balance,co['balance_error'],cur['balance_error'])
                cond=np.linalg.cond(ft);max_frame_condition=max(max_frame_condition,float(cond))
                gauge_err=gauge_test(ft,seeds,gt,delta)
                max_covariance=max(max_covariance,gauge_err)
                drive_theta_error=abs(((yy[10]-xx[10]+np.pi)%(2*np.pi))-np.pi)
                max_clock_mismatch=max(max_clock_mismatch,drive_theta_error)
                co_hidden=co.pop('hidden_vector');cur_hidden=cur.pop('hidden_vector')
                snapshots[q]=(pulled,co_hidden,gt,cur_hidden)
                record={'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'phase_q':q,'return_time_xi':time,
                 'shape_distance_3d':shape(q),'full_material_10d_distance':float(np.linalg.norm(delta)),
                 'drive_clock_mismatch_rad':drive_theta_error,'frame_condition_number':cond,
                 'initial_frame_rank':rank0,'instantaneous_frame_rank':rankcurrent,
                 'initial_family_min_relative_singular':float(sv0[-1]/sv0[0]),
                 'frame_observer_duality_residual':dual_err,'frame_pullback_identity_error':frame_defect,
                 'gauge_counterfactual_error':gauge_err,
                 'clock_transport_direction':'q_increases_while_drive_theta_decreases',
                 'energy_difference':float(phys.energy(yy,kap,params)-phys.energy(xx,kap,params))}
                for prefix,obj in [('common',co),('instantaneous',cur)]:
                    record.update({prefix+'_'+key:val for key,val in obj.items()})
                point_rows.append(record)
                if abs(q-.5)<1e-10:
                    row=parent_records.get((kind,round(rv,8)))
                    if row is None:raise RuntimeError('D q=.5 row absent')
                    max_parent=max(max_parent,abs(cur['hidden']-float(row['hidden_complement_norm'])),
                               abs(cur['fraction']-float(row['fraction_explained'])))
            for q0 in (.35,.55):
                for span,lab in ((kap,'kappa0_interval'),(.2,'0p2_interval')):
                    q1=round(q0+span,12)
                    a0,h0,_,_=snapshots[q0];a1,h1,_,_=snapshots[q1]
                    scale_rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'q_entry':q0,'q_exit':q1,
                       'span_kind':lab,'span_xi':span,'span_over_kappa':span/kap,
                       'clock_advance_rad':-omega*span,'hidden_cosine_common_frame':compare_orientation(h0,h1),
                       'finite_difference_cosine_common_frame':compare_orientation(a0,a1),
                       'hidden_norm_entry':float(np.linalg.norm(h0)),'hidden_norm_exit':float(np.linalg.norm(h1)),
                       'hidden_norm_ratio':float(np.linalg.norm(h1)/np.linalg.norm(h0)),
                       'material_difference_norm_ratio':float(np.linalg.norm(a1)/np.linalg.norm(a0)),
                       'hidden_direction_returns_within_1deg':int(compare_orientation(h0,h1)>math.cos(math.pi/180)),
                       'true_physical_cycle_proven':False})
            for q0,q1 in zip(qs[:-1],qs[1:]):
                a0,h0,_,_=snapshots[q0];a1,h1,_,_=snapshots[q1]
                transport_rows.append({'kappa_kind':kind,'ramp_xi':rv,'q0':q0,'q1':q1,
                    'hidden_alignment_common_frame':compare_orientation(h0,h1),
                    'hidden_norm_change_common_frame':float(np.linalg.norm(h1)-np.linalg.norm(h0)),
                    'material_displacement_alignment':compare_orientation(a0,a1)})
            print(f'v18.49e {kind}, ramp={rv:.6f}: {len(events)} oriented roots, {len(pairs)} intervals, '
                  f'frame_cond_max={max_frame_condition:.4g}, duality_max={max_duality:.3g}',flush=True)
    for name,rows in (('common_frame_profiles.csv',point_rows),('oriented_passage_events.csv',events_rows),
         ('subthreshold_passage_pairs.csv',passage_rows),('kappa0_marker_scale_tests.csv',scale_rows),
         ('common_frame_hidden_transport.csv',transport_rows)):
        write_csv(name,rows)
    report={'version':'v18.49e','status':'AUTHENTIC_11D_COMMON_FRAME_DIAGNOSTIC_ONLY',
      'physical_integrations':physical_runs,'adjoint_integrations':adjoint_runs,'frame_integrations':frame_runs,
      'kappas_tested':list(kappas)[:n_kappas],'ramp_values':list(chosen_ramps),
      'count_finite_material_profiles':len(point_rows),'count_oriented_threshold_markers':len(events_rows),
      'count_completed_subthreshold_intervals':len(passage_rows),'count_kappa0_interval_probes':len(scale_rows),
      'max_forward_history_error':max_history,'max_parent_d_regression':max_parent,
      'max_energy_ledger_residual':max_energy,'max_clock_mismatch_rad':max_clock_mismatch,
      'max_cotangent_frame_identity_residual':max_frame_defect,'max_finite_pairing_pullback_error':max_duality,
      'max_metric_decomposition_error':max_balance,'max_chart_covariance_error':max_covariance,
      'max_frame_condition_number':max_frame_condition,
      'historical_source_authenticated_to_J':provenance['history_authenticated_to_J'],
      'passage_threshold_3d':THRESHOLD,'phase_interval':[QMIN,QMAX],
      'kappa_interpretation':'kappa0 used only as a numerical comparison span; NOT an established material period',
      'frame_definition':'material 10x10 fundamental matrix on each NEW counterflow 11D return, based at turning posture',
      'material_metric':'Euclidean in pulled-back turning-point material frame; time-dependent in current coordinates',
      'limitation':'phaseblind branch0 only, both kappas. Threshold events represent sublevel geometry, not physical trajectory return; linear pullback of finite inter-trajectory differences is a diagnostic, not a nonlinear invariant. Norms are metric- and frame-dependent. No unique kappa0 passage is certified.'}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
       'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    for key,cap in (('max_parent_d_regression',1e-6),('max_forward_history_error',1e-7),
       ('max_energy_ledger_residual',1e-8),('max_clock_mismatch_rad',1e-8),
       ('max_cotangent_frame_identity_residual',5e-6),('max_finite_pairing_pullback_error',5e-6),
       ('max_metric_decomposition_error',1e-7),('max_chart_covariance_error',1e-7)):
        if report[key]>cap:raise RuntimeError(f'{key} failed: {report[key]} > {cap}')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--adjoint-rtol',type=float,default=2e-10);p.add_argument('--adjoint-atol',type=float,default=2e-12)
    p.add_argument('--adjoint-max-step',type=float,default=.0125)
    p.add_argument('--frame-rtol',type=float,default=8e-11);p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--marker-samples',type=int,default=901)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    run(p.parse_args())
