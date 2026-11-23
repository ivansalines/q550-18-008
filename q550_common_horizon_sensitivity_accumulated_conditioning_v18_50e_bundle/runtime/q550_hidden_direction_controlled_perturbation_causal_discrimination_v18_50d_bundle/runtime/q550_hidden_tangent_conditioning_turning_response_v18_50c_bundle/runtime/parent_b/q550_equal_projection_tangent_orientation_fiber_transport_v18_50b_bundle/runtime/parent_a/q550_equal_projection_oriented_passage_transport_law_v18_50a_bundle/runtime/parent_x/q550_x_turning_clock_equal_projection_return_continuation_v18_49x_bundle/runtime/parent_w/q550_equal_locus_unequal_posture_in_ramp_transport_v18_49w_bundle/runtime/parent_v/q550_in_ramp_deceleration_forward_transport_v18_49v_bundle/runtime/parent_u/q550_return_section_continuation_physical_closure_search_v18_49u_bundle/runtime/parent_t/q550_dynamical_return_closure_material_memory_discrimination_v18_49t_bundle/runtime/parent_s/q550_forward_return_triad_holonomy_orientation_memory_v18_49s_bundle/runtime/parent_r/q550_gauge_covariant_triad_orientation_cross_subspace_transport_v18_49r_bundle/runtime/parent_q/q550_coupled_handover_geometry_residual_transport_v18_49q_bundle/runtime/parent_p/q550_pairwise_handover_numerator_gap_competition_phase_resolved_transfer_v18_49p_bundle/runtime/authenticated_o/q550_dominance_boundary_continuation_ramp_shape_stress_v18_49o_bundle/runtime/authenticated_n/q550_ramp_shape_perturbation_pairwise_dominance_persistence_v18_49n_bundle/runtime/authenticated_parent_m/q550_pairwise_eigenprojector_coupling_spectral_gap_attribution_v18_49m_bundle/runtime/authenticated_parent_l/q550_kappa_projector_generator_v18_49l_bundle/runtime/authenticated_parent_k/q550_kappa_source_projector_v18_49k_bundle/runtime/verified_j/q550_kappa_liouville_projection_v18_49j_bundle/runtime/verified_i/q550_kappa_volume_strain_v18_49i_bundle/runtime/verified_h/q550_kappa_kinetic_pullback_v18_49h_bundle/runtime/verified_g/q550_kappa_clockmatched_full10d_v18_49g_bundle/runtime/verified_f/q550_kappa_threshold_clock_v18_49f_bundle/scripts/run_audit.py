#!/usr/bin/env python3
"""v18.49f -- threshold robust oriented passages in a transported common frame.

Only the SHA-verified parent E and its ancestors provide physical 11D equations.
Threshold event connectivity and orientation of a pulled-back finite difference
are numerical diagnostics, not proofs of a material period, chirality, or cycle.
"""
from __future__ import annotations
import argparse,csv,json,math,platform,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_parent import verify,dynamic
from frame_math import transport_frame,orthonormal_family,common_decomposition
from passage_math import critical_points,crossings_from_extrema,paired_passages,orientation_trace,relative_orientation,covariance_in_common_frame
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)
THRESHOLDS=(.006,.008,.009,.010,.011,.012,.014)
QMIN,QMAX=.2,.8

def output(name,rows):
    path=ROOT/'results'/name
    if not rows:path.write_text('status\nno_events\n');return
    keys=list(dict.fromkeys(k for r in rows for k in r.keys()))
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def run(args):
    e,d,c,b,a,z,y,j,provenance=verify()
    sys.path.insert(0,str(c/'reference'));sys.path.insert(0,str(c/'scripts'))
    physical=dynamic(c/'reference/physical_math.py','f_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','f_original_ramp')
    yr=dynamic(c/'reference/y_original_run_audit.py','f_original_y')
    jet=dynamic(c/'reference/structural_jet.py','f_original_jet')
    support_paths=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_paths)!=1:raise RuntimeError('Historical support file not unique')
    support=dynamic(support_paths[0],'f_original_support')
    audit=dynamic(support_paths[0].parent/'test_support_mobius_monodromy_audit.py','f_original_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hreport=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(hreport['kappa_original']),'autonomous':float(hreport['kappa_autonomous'])}
    omega=float(history['clock_speed']);slope=omega/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(history['y'])):
        groups[(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))].append(i)
    ref_profiles={}
    with (e/'results/common_frame_profiles.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            if abs(float(row['phase_q'])-.50)<1e-10:
                ref_profiles[(row['kappa_kind'],round(float(row['ramp_xi']),7))]=row
    events=[];intervals=[];extrema=[];trace=[];fixed=[];summary=[];clock_profiles=[]
    cnt_physical=0;cnt_frame=0;max_history=max_energy=max_parent=max_frame=0.0
    max_clock=max_event=max_grid_refinement=max_turn_refinement=0.0
    kinds=('original',) if args.smoke else ('original','autonomous')
    ramps=(.300,) if args.smoke else RAMPS
    for kind in kinds:
        idx=sorted(next(rows for (fam,branch,k),rows in groups.items() if fam.startswith('phaseblind') and branch==0 and k==kind),
                   key=lambda i:float(history['xi'][i]))
        kap=kappas[kind];start=history['y'][idx[0]].astype(float)
        forward,err=yr.integrate(physical,ramp,support,audit,kap,params,slope,omega,start,args)
        cnt_physical+=1;max_energy=max(max_energy,float(err))
        max_history=max(max_history,max(float(np.linalg.norm(forward(t)[:11]-history['y'][i])) for t,i in zip(np.linspace(0,1,41),idx)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1.
        seeds=history['covectors'][idx[-1],:5,:10].astype(float)
        seeds/=np.linalg.norm(seeds,axis=1,keepdims=True)
        basis,sv,rank=orthonormal_family(seeds,1e-10)
        for rv in ramps:
            design=ramp.Design('v18_49f','smoothstep',rv)
            back,err=yr.integrate(physical,ramp,support,audit,kap,params,slope,omega,turning,args,design=design)
            cnt_physical+=1;max_energy=max(max_energy,float(err))
            def jac(y,k,p,sl):return jet.structural_jet(y,k,p,sl)[1]
            F,frame_sol=transport_frame(back,kap,params,slope,jac,1.+rv,
                         rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            cnt_frame+=1
            def both(q):return back(rv+float(q))[:11],forward(1.-float(q))[:11]
            def shape(q):
                yy,xx=both(q);return float(physical.physical_shape_distance(yy,xx))
            def hidden(q,detail=False):
                yy,xx=both(q);delta=np.asarray(yy[:10]-xx[:10],float)
                # Same material finite-difference lift as original E; no unjustified coordinate subtraction.
                original_family=dynamic_family
                delta=original_family.local_lift(yy,xx)
                pull=np.linalg.solve(F(rv+float(q)),delta)
                h=pull-basis@(basis.T@pull)
                return (h,pull,yy,xx) if detail else h
            # Need the real source's coordinate-aware local lift (angular wrap correct).
            if 'dynamic_family' not in locals():
                dynamic_family=dynamic(c/'scripts/family_math.py','f_original_family')
            qs=np.linspace(QMIN,QMAX,args.marker_samples)
            values=np.array([shape(q) for q in qs])
            critical=critical_points(shape,qs,values)
            for eid,(qc,cls,val) in enumerate(critical):
                extrema.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'extremum_id':eid,
                     'phase_q':qc,'kind':cls,'shape_distance_3d':val,
                     'material_time_xi':rv+qc,'clock_theta_rad':float(back(rv+qc)[10]),
                     'is_threshold_independent_marker':True})
            fixed_by_q={}
            for q in (.35,.45,.4815,.50,.55,.65):
                h,pull,yy,xx=hidden(q,True)
                co=common_decomposition(pull,basis)
                clock_err=abs(((float(yy[10]-xx[10])+np.pi)%(2*np.pi))-np.pi)
                max_clock=max(max_clock,clock_err)
                row={'kappa_kind':kind,'ramp_xi':rv,'phase_q':q,
                     'shape_distance':shape(q),'hidden_norm':co['hidden'],'observed_fraction':co['fraction'],
                     'total_norm':co['total'],'clock_mismatch_rad':clock_err,
                     'energy_difference':float(physical.energy(yy,kap,params)-physical.energy(xx,kap,params))}
                fixed.append(row);fixed_by_q[q]=row
            parent=ref_profiles.get((kind,round(rv,7)))
            if parent is None:raise RuntimeError(f'Parent E reference absent for {kind} {rv}')
            max_parent=max(max_parent,abs(fixed_by_q[.5]['hidden_norm']-float(parent['common_hidden'])),
                                abs(fixed_by_q[.5]['observed_fraction']-float(parent['common_fraction'])))
            # Independent coarser sampling with refined continuous roots, to
            # prevent attributing missed subthreshold components to pixel density.
            qcoarse=np.linspace(QMIN,QMAX,601)
            vcoarse=np.array([shape(float(q)) for q in qcoarse])
            ccoarse=critical_points(shape,qcoarse,vcoarse)
            for threshold_check in (.008,.010,.012):
                fine_root=crossings_from_extrema(shape,qs,values,critical,threshold_check)
                coarse_root=crossings_from_extrema(shape,qcoarse,vcoarse,ccoarse,threshold_check)
                if len(fine_root)!=len(coarse_root):raise RuntimeError('Grid resolution changes marker count')
                max_grid_refinement=max(max_grid_refinement,max([abs(x['q']-y['q']) for x,y in zip(fine_root,coarse_root)] or [0.]))
            # Check frame at fixed q without re-integrating the historical adjoint.
            ff=F(rv+.5)
            max_frame=max(max_frame,float(np.linalg.cond(ff)))
            # Independent of threshold: same time-registered 2D plane and
            # same common-frame 10D material residual for every threshold.
            anchor_q=.35
            anch=hidden(anchor_q)
            hstep=2e-5
            e1=anch/np.linalg.norm(anch)
            vv=hidden(anchor_q+hstep)
            dv=vv/np.linalg.norm(vv)-e1
            dv=dv-e1*(dv@e1)
            e2=dv/np.linalg.norm(dv)
            ts=np.linspace(.25,.75,101)
            un=np.array([hidden(float(t))/np.linalg.norm(hidden(float(t))) for t in ts])
            x=un@e1;y=un@e2
            angles=np.unwrap(np.arctan2(y,x))
            leaks=np.sqrt(np.maximum(0.,1.-x*x-y*y))
            speed=np.gradient(angles,ts)
            for t,aa,ll,ss,cosx in zip(ts,angles,leaks,speed,un@e1):
                clock_profiles.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(t),
                   'reference_phase_q':anchor_q,'signed_orientation_in_reference_plane_deg':float(np.rad2deg(aa)),
                   'signed_rate_deg_per_xi':float(np.rad2deg(ss)),
                   'signed_rate_deg_per_clock_radian':float(-np.rad2deg(ss)/omega),
                   'off_reference_plane_fraction':float(ll),
                   'reference_direction_cosine_10d':float(cosx)})
            case_counts=[]
            for eps in THRESHOLDS:
                ee=crossings_from_extrema(shape,qs,values,critical,eps)
                pairs=paired_passages(ee)
                if len(ee)!=2*len(pairs):
                    raise RuntimeError(f'Unpaired threshold crossing for {kind}, {rv}, eps={eps}: {ee}')
                for event_id,ev in enumerate(ee):
                    q=ev['q'];yy,xx=both(q);h,pull,_,_=hidden(q,True)
                    max_event=max(max_event,abs(ev['residual']))
                    events.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,
                        'threshold':eps,'marker_id':event_id,**ev,
                        'physical_clock_theta':float(yy[10]),'clock_derivative_dtheta_dq':-omega,
                        'slope_wrt_clock_theta':float(-ev['slope_q']/omega),
                        'material_time_xi':rv+q,'hidden_norm_common_frame':float(np.linalg.norm(h)),
                        'material_separation_norm':float(np.linalg.norm(pull)),
                        'energy_difference':float(physical.energy(yy,kap,params)-physical.energy(xx,kap,params))})
                for pass_id,(entry,exit) in enumerate(pairs):
                    q0,q1=entry['q'],exit['q']
                    orient,oq,oa,oleak=orientation_trace(hidden,q0,q1,args.orientation_samples,reference_q=anchor_q)
                    # Check orientation path-length quadrature without changing physical integration.
                    if abs(eps-.01)<1e-12:
                        refined=orientation_trace(hidden,q0,q1,49,reference_q=anchor_q)[0]
                        max_turn_refinement=max(max_turn_refinement,abs(refined['path_total_turn_deg']-orient['path_total_turn_deg']))
                    # Algebraic sign of q and physical clock are opposite by model construction.
                    record={'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'threshold':eps,'passage_id':pass_id,
                     'entry_q':q0,'exit_q':q1,'phase_span_q':q1-q0,
                     'span_over_kappa0':(q1-q0)/kap,'clock_span_rad':-omega*(q1-q0),
                     'entry_slope_wrt_clock':-entry['slope_q']/omega,
                     'exit_slope_wrt_clock':-exit['slope_q']/omega,
                     'true_material_cycle_proven':False,**orient}
                    record['total_turn_per_clock_radian']=float(np.deg2rad(orient['path_total_turn_deg'])/(omega*(q1-q0)))
                    intervals.append(record)
                    for q,angle,leak in zip(oq,oa,oleak):
                        trace.append({'kappa_kind':kind,'ramp_xi':rv,'threshold':eps,'passage_id':pass_id,
                             'phase_q':float(q),'from_entry_q':float(q-q0),'relative_clock_rad':float(-omega*(q-q0)),
                             'projected_orientation_deg':float(np.rad2deg(angle)),
                             'off_plane_fraction':float(leak)})
                case_counts.append(len(pairs))
                summary.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'threshold':eps,
                 'connected_contact_components':len(pairs),'event_count':len(ee),
                 'contact_total_width_q':float(sum(x['q']-en['q'] for en,x in pairs)),
                 'max_connected_passage_q':float(max([ex['q']-en['q'] for en,ex in pairs],default=0)),
                 'fraction_of_phase_window_below_threshold':float(np.mean(values<eps)),
                 'min_shape_distance_3d':float(values.min()),
                 'orientation_mean_total_turn_deg':float(np.mean([p['path_total_turn_deg'] for p in intervals if p['kappa_kind']==kind and p['ramp_xi']==rv and p['threshold']==eps])) if pairs else float('nan')})
            print(f'v18.49f {kind}, ramp={rv:.6f}: threshold components={case_counts}, '
                  f'extrema={len(critical)}, parent_err={max_parent:.2e}',flush=True)
    for name,rows in [('threshold_marker_events.csv',events),('threshold_passage_orientation.csv',intervals),
     ('threshold_extrema.csv',extrema),('threshold_contact_summary.csv',summary),
     ('common_clock_orientation_traces.csv',trace),('clock_registered_orientation_profiles.csv',clock_profiles),('fixed_phase_controls.csv',fixed)]:output(name,rows)
    report={'version':'v18.49f','status':'AUTHENTIC_11D_THRESHOLD_CLOCK_DIAGNOSTIC_ONLY',
      'physical_integrations':cnt_physical,'frame_integrations':cnt_frame,
      'kappas':list(kinds),'ramps':list(ramps),'thresholds':list(THRESHOLDS),
      'phase_window':[QMIN,QMAX],'count_oriented_crossings':len(events),
      'count_complete_passages':len(intervals),'count_extrema':len(extrema),
      'count_orientation_trace_samples':len(trace),'count_clock_registered_samples':len(clock_profiles),
      'max_original_e_regression_error':max_parent,'max_original_11d_history_error':max_history,
      'max_energy_ledger_residual':max_energy,'max_clock_phase_mismatch_rad':max_clock,
      'max_threshold_crossing_residual':max_event,
      'max_frame_condition_number':max_frame,
      'max_coarse_fine_marker_difference_q':max_grid_refinement,
      'max_orientation_quadrature_difference_deg':max_turn_refinement,
      'original_e_an_ancestry_verified_to_j':provenance['nested_ancestry_authenticated_to_J'],
      'clock_registration':'q increases against physical drive theta; dtheta/dq=-omega',
      'material_metric':'Euclidean at initial turning-point common frame. NOT an observer-free material metric.',
      'interpretation':'Markers: crossings of chosen d3 threshold. Oriented traces use fixed q=0.35 vector and forward-q derivative as one common oriented plane per return; off-plane leakage is reported. Threshold-independent extrema are metric-dependent.',
      'limitation':'phaseblind branch0, two kappa0 only. Span approximately kappa0 does not prove a physical cycle. No global intrinsic winding or universal irreversibility proven.'}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    if max_parent>1e-7 or max_history>1e-7 or max_energy>1e-8 or max_clock>1e-8 or max_event>1e-8 or max_grid_refinement>1e-6 or max_turn_refinement>0.02:
        raise RuntimeError('Numerical regression or scientific gate failed')
    print(json.dumps(report,indent=2),flush=True)
    return report

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--smoke',action='store_true')
 p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
 p.add_argument('--max-step',type=float,default=.025)
 p.add_argument('--frame-rtol',type=float,default=8e-11);p.add_argument('--frame-atol',type=float,default=8e-13)
 p.add_argument('--frame-max-step',type=float,default=.008)
 p.add_argument('--marker-samples',type=int,default=1201)
 p.add_argument('--orientation-samples',type=int,default=25)
 p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
 p.add_argument('--maximum-regression',type=float,default=1e-7)
 run(p.parse_args())
