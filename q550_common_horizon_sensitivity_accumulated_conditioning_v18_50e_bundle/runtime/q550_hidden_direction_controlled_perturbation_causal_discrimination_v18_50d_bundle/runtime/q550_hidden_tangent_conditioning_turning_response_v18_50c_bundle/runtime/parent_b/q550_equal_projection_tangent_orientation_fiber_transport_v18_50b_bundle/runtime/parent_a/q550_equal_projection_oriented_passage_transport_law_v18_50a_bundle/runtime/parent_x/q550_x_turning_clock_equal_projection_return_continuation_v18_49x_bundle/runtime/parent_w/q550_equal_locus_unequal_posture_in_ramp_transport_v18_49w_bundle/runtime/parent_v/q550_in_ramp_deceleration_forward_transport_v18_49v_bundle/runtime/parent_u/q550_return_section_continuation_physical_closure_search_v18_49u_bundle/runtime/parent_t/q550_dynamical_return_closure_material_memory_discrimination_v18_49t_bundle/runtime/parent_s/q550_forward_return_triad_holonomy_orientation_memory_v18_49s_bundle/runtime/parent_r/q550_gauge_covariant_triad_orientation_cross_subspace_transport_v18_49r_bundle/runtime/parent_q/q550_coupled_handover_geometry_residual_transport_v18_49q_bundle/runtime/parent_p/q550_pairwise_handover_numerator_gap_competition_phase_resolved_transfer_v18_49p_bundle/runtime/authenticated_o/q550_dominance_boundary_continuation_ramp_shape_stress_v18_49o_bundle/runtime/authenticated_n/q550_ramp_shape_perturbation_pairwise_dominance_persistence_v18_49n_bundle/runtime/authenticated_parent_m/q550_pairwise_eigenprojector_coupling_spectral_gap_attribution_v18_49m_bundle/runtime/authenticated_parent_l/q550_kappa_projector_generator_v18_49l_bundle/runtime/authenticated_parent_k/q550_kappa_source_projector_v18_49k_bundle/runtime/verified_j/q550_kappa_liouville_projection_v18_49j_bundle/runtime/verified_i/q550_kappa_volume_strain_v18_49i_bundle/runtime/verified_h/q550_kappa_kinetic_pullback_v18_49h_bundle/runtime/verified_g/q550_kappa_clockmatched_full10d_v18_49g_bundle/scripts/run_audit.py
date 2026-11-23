#!/usr/bin/env python3
"""v18.49g -- clock-matched passage scaling and full-10D directional transport.

Original Q550 11D IVPs, reference tangent propagators and material lift are
SHA-pinned to actual v18.49f (and its verified E...J ancestry). No arbitrary
full-space rotation is inferred from two projected coordinates. Directional
arclength is measured in the Euclidean common frame anchored at the turning
point, not claimed intrinsic to the material without that metric.
"""
from __future__ import annotations
import argparse,csv,json,sys,platform,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from verify_parent import verify,dynamic
from frame_math import transport_frame,orthonormal_family
from full10d_math import spherical_path,unit,project_outside_basis,chart_covariance_error
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)

def read_csv(file):
    with file.open(newline='') as f:return list(csv.DictReader(f))

def save_csv(name,rows):
    path=ROOT/'results'/name
    if not rows:path.write_text('status\nempty\n');return
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    f,e,d,c,b,a,z,y,j,provenance=verify()
    sys.path.insert(0,str(c/'reference'));sys.path.insert(0,str(c/'scripts'))
    physical=dynamic(c/'reference/physical_math.py','g_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','g_original_ramp')
    yr=dynamic(c/'reference/y_original_run_audit.py','g_original_y')
    jet=dynamic(c/'reference/structural_jet.py','g_original_jet')
    family=dynamic(c/'scripts/family_math.py','g_original_family')
    support_candidates=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_candidates)!=1:raise RuntimeError('Authentic support generator not unique')
    support=dynamic(support_candidates[0],'g_original_support')
    audit=dynamic(support_candidates[0].parent/'test_support_mobius_monodromy_audit.py','g_original_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hreport=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(hreport['kappa_original']),
            'autonomous':float(hreport['kappa_autonomous'])}
    omega=float(history['clock_speed']);slope=omega/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(history['y'])):
        groups[(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))].append(i)
    parent_pass=read_csv(f/'results/threshold_passage_orientation.csv')
    parent_ext=read_csv(f/'results/threshold_extrema.csv')
    parent_clock=read_csv(f/'results/clock_registered_orientation_profiles.csv')
    source_report=json.loads((f/'results/report.json').read_text())
    expected_passages=len(parent_pass)
    if expected_passages!=121 or len(parent_ext)!=36:
        raise RuntimeError('Unexpected historical F morphology counts')
    pass_by=defaultdict(list);ext_by=defaultdict(list);clock_by=defaultdict(list)
    for row in parent_pass:pass_by[(row['kappa_kind'],round(float(row['ramp_xi']),7))].append(row)
    for row in parent_ext:ext_by[(row['kappa_kind'],round(float(row['ramp_xi']),7))].append(row)
    for row in parent_clock:clock_by[(row['kappa_kind'],round(float(row['ramp_xi']),7))].append(row)
    kinds=['original'] if args.smoke else ['original','autonomous']
    rv_list=[.300] if args.smoke else list(RAMPS)
    samples=[];threshold_free=[];passage=[];regression=[]
    max_parent_shape=max_ledger=max_history=max_chart=max_clock=max_duality=0.0
    max_full10d_quadrature_refinement=0.0
    cnt_physical=cnt_frame=0
    for kind in kinds:
        idx=sorted(next(rows for (name,branch,k),rows in groups.items()
                        if name.startswith('phaseblind') and branch==0 and k==kind),
                   key=lambda i:float(history['xi'][i]))
        kap=kappas[kind]
        start=history['y'][idx[0]].astype(float)
        forward,err=yr.integrate(physical,ramp,support,audit,kap,params,slope,omega,start,args)
        cnt_physical+=1;max_ledger=max(max_ledger,float(err))
        max_history=max(max_history,max(float(np.linalg.norm(forward(t)[:11]-history['y'][i]))
             for t,i in zip(np.linspace(0,1,41),idx)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        seeds=history['covectors'][idx[-1],:5,:10].astype(float)
        seeds/=np.linalg.norm(seeds,axis=1,keepdims=True)
        basis,_,_=orthonormal_family(seeds,1e-10)
        for rv in rv_list:
            back,err=yr.integrate(physical,ramp,support,audit,kap,params,slope,omega,
                                  turning,args,design=ramp.Design('v18_49g','smoothstep',rv))
            cnt_physical+=1;max_ledger=max(max_ledger,float(err))
            def jac(state,k,p,sl):return jet.structural_jet(state,k,p,sl)[1]
            F,_=transport_frame(back,kap,params,slope,jac,1.+rv,
               rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            cnt_frame+=1
            def both(q):return back(rv+float(q))[:11],forward(1.-float(q))[:11]
            def data(q):
                yy,xx=both(q)
                delta=family.local_lift(yy,xx)
                pulled=np.linalg.solve(F(rv+float(q)),delta)
                hidden=project_outside_basis(pulled,basis)
                return hidden,yy,xx,pulled
            def direction(q):return unit(data(q)[0]).reshape(-1)
            # Same command-clock q for every run, whether duration differs or not.
            qgrid=np.linspace(.25,.75,args.clock_samples)
            vectors=np.array([direction(q) for q in qgrid])
            angles=np.rad2deg(np.arccos(np.clip(vectors@direction(.35),-1,1)))
            metric_check=chart_covariance_error(vectors[::max(1,len(vectors)//30)])
            max_chart=max(max_chart,metric_check)
            full=spherical_path(vectors)
            previous=np.concatenate([[0.],np.cumsum(full['steps_deg'])])
            cf=clock_by[(kind,round(rv,7))]
            f_q=np.array([float(r['phase_q']) for r in cf]);f_an=np.array([float(r['signed_orientation_in_reference_plane_deg']) for r in cf]);
            qproj=f_q[int(np.argmax(f_an))]
            imax=int(np.argmax(angles));qfull=float(qgrid[imax])
            # Common clock is explicitly checked at each point.
            for q,vec,angle,travel in zip(qgrid,vectors,angles,previous):
                yy,xx=both(q)
                clock_err=abs(((float(yy[10]-xx[10])+np.pi)%(2*np.pi))-np.pi)
                max_clock=max(max_clock,clock_err)
                samples.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                    'clock_theta_rad':float(yy[10]),'clock_mismatch_rad':clock_err,
                    'angle_to_q035_full10d_deg':float(angle),
                    'full10d_cumulative_turn_from_q025_deg':float(travel),
                    'full10d_xi_orientation_rate_deg_per_xi':float('nan'),
                    'common_hidden_norm':float(np.linalg.norm(data(q)[0]))})
            # Clock samples from .25:.75 include the threshold-independent extrema.
            ex=sorted(ext_by[(kind,round(rv,7))],key=lambda r:float(r['phase_q']))
            if [r['kind'] for r in ex]!=['min','max','min']:
                raise RuntimeError('Threshold-independent marker order altered')
            qleft,qbar,qright=[float(row['phase_q']) for row in ex]
            dbar=float(ex[1]['shape_distance_3d'])
            for er in ex:
                q=float(er['phase_q']);hh,yy,xx,_=data(q)
                max_parent_shape=max(max_parent_shape,abs(float(physical.physical_shape_distance(yy,xx))
                                                       -float(er['shape_distance_3d'])))
            qext=np.linspace(qleft,qright,args.orientation_samples)
            curve=np.array([direction(q) for q in qext]);curve_10=spherical_path(curve)
            finer_curve=np.array([direction(q) for q in np.linspace(qleft,qright,2*args.orientation_samples-1)])
            finer_10=spherical_path(finer_curve)
            quad_diff=abs(finer_10['length_deg']-curve_10['length_deg'])
            max_full10d_quadrature_refinement=max(max_full10d_quadrature_refinement,quad_diff)
            ephase=omega*(qright-qleft)
            trace_duality_error=0.0
            for q in [qleft,qbar,qright]:
                yy,xx=both(q);delta=family.local_lift(yy,xx)
                A=F(rv+q);g0=seeds[:2]
                gt=np.linalg.solve(A.T,g0.T).T
                trace_duality_error=max(trace_duality_error,float(np.linalg.norm(gt@delta-g0@np.linalg.solve(A,delta))
                                           /max(1.,np.linalg.norm(gt@delta))))
            max_duality=max(max_duality,trace_duality_error)
            threshold_free.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,
                'left_min_q':qleft,'barrier_max_q':qbar,'right_min_q':qright,
                'extrema_span_q':qright-qleft,'extrema_span_over_kappa0':(qright-qleft)/kap,
                'extrema_span_clock_abs_rad':ephase,'barrier_height_d3':dbar,
                'projected_2d_angle_max_q':qproj,'full10d_angle_max_within_window_q':qfull,
                'full10d_angle_max_at_window_boundary':bool(imax==len(qgrid)-1),
                'full10d_arc_refinement_difference_deg':quad_diff,
                'projected_peak_minus_barrier_q':qproj-qbar,
                'full10d_peak_minus_barrier_q':qfull-qbar,
                'full10d_extrema_endpoint_angle_deg':curve_10['endpoint_deg'],
                'full10d_extrema_path_turn_deg':curve_10['length_deg'],
                'full10d_extrema_excess_deg':curve_10['excess_deg'],
                'full10d_extrema_path_over_endpoint':curve_10['length_deg']/max(1e-12,curve_10['endpoint_deg']),
                'max_metric_covariance_error_deg':metric_check,
                'max_tangent_cotangent_duality_residual':trace_duality_error})
            for p in pass_by[(kind,round(rv,7))]:
                q0,q1=float(p['entry_q']),float(p['exit_q'])
                qq=np.linspace(q0,q1,args.orientation_samples)
                sp=spherical_path(np.array([direction(q) for q in qq]))
                # Reconstruct source F's 10D endpoint angle independently.
                old=float(p['entry_exit_angle_deg'])
                err=abs(sp['endpoint_deg']-old)
                if err>2e-5:raise RuntimeError(f'F 10D endpoint regression failed: {err}')
                regression.append(err)
                passage.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,
                  'threshold':float(p['threshold']),'passage_id':int(p['passage_id']),
                  'entry_q':q0,'exit_q':q1,'phase_span_q':q1-q0,
                  'span_over_kappa0':(q1-q0)/kap,'distance_to_6_over_5':abs((q1-q0)/kap-1.2),
                  'clock_span_abs_rad':omega*(q1-q0),
                  'threshold_free_extrema_span_q':qright-qleft,
                  'threshold_free_span_over_kappa0':(qright-qleft)/kap,
                  'full10d_endpoint_angle_deg':sp['endpoint_deg'],
                  'full10d_path_turn_deg':sp['length_deg'],
                  'full10d_extra_turn_deg':sp['excess_deg'],
                  'full10d_path_endpoint_ratio':sp['length_deg']/max(1e-10,sp['endpoint_deg']),
                  'parent_f_projected_signed_angle_deg':float(p['signed_projected_angle_deg']),
                  'parent_f_plane_leakage_exit':float(p['plane_leakage_exit']),
                  'parent_f_path_turn_deg':float(p['path_total_turn_deg']),
                  'full10d_path_turn_difference_from_f_deg':sp['length_deg']-float(p['path_total_turn_deg']),
                  'observational_cycle_proven':False})
            print(f'v18.49g {kind:10s} ramp={rv:.6f}: '
                  f'full10D extrema path={curve_10["length_deg"]:.6f}deg, '
                  f'endpoint={curve_10["endpoint_deg"]:.6f}deg; '
                  f'barrier at q={qbar:.6f}; '+str(len(pass_by[(kind,round(rv,7))]))+' passages',flush=True)
    # Histograms and negative controls over EVERY original F passage, not selected best.
    for name,rows in [('full10d_clock_profiles.csv',samples),
                      ('threshold_free_extrema_orientation.csv',threshold_free),
                      ('clock_matched_threshold_passages.csv',passage)]:save_csv(name,rows)
    ratios=np.array([p['span_over_kappa0'] for p in passage]);
    near=[p for p in passage if abs(p['span_over_kappa0']-1.2)<0.01]
    best=min(passage,key=lambda p:abs(p['span_over_kappa0']-1.2))
    ext_ratios=np.array([p['extrema_span_over_kappa0'] for p in threshold_free]);
    report={'version':'v18.49g','status':'AUTHENTIC_11D_CLOCK_MATCHED_FULL10D_DIAGNOSTIC_ONLY',
       'physical_integrations':cnt_physical,'frame_integrations':cnt_frame,
       'number_threshold_passages':len(passage),'number_threshold_free_extrema_profiles':len(threshold_free),
       'clock_grid_samples':len(samples),'parent_f_passages':expected_passages,
       'ramp_set':rv_list,'kappa_set':kinds,'thresholds_from_parent_f':source_report['thresholds'],
       'nearest_6_over_5_threshold_passage':{k:best[k] for k in ['kappa_kind','ramp_xi','threshold','passage_id','span_over_kappa0','distance_to_6_over_5']},
       'count_passages_within_1_percent_of_6_over_5':len(near),
       'threshold_free_extrema_ratio_min':float(ext_ratios.min()),
       'threshold_free_extrema_ratio_max':float(ext_ratios.max()),
       'max_parent_11d_history_error':max_history,'max_parent_extrema_shape_error':max_parent_shape,
       'max_regression_endpoint_angle_deg':max(regression or [0]),
       'max_mechanical_ledger_error':max_ledger,'max_clock_phase_mismatch_rad':max_clock,
       'max_full10d_chart_covariance_error_deg':max_chart,
       'max_tangent_cotangent_duality_residual':max_duality,
       'max_full10d_arc_49_vs_97_refinement_deg':max_full10d_quadrature_refinement,
       'nested_ancestry_authenticated_to_J':provenance['history_authenticated_to_J'],
       'physical_clock':'q increases opposite to physical Theta; clock radians = -omega delta q',
       'metric':'Euclidean 10D common frame at turning point; chart transforms must carry metric',
       'invariant_scope':'S^9 arclength and endpoints invariant under a coherent affine chart and metric pushforward, not under replacing the metric or the observer family',
       'interpretation':'Threshold passage ratios depend on chosen threshold. Extrema are threshold-independent but metric/coordinate dependent. Full-10D arc versus endpoint distinguishes nongeodesic direction transport from 2D return. Full-10D angle maxima at q=.75 are WINDOW-BOUNDARY maxima, not interior turning events.',
       'limitation':'Only phaseblind branch0, 2 kappa0 and 6 ramps. No intrinsic kappa0 period, full return, material handedness or observer-free 10D metric proven.'}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    if (max_history>1e-7 or max_parent_shape>1e-7 or max(regression or [0])>2e-5 or max_ledger>1e-8
        or max_clock>1e-8 or max_chart>2e-5 or max_duality>1e-8 or max_full10d_quadrature_refinement>0.02):
        raise RuntimeError('Failed scientific regression/invariant gate')
    print(json.dumps(report,indent=2),flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--rtol',type=float,default=3e-12)
    p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--clock-samples',type=int,default=101)
    p.add_argument('--orientation-samples',type=int,default=49)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    run(p.parse_args())
