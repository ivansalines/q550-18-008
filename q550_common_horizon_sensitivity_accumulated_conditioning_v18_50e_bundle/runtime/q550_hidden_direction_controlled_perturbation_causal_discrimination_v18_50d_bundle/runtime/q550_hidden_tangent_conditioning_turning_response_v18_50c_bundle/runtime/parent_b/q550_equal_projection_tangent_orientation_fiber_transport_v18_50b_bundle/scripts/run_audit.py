#!/usr/bin/env python3
"""v18.50b — Equal-Projection Tangent Orientation & Fiber-Transport Audit.

Numerically replay independently authenticated v18.50a equal-x event sections
using the genuine Q550 11D autonomous RHS. Compare instantaneous tangents,
projected directions, and hidden-coordinate separation under explicitly
specified native and per-case span metrics. No material-memory, topology,
physical fiber bundle, or spatial-volume certificate is asserted.
"""
import argparse,csv,json,platform,traceback
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_parent_a import verify
from tangent_math import (cosine,fiber_fraction,range_scales,equal_x_opposed,
                          five_state_and_tangent,ten_chart_and_tangent)
ROOT=Path(__file__).resolve().parents[1]

def write_csv(name,rows):
    if not rows:return
    p=ROOT/'results'/name;p.parent.mkdir(exist_ok=True)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def fmt(v):return None if v is None else float(v)
def ang(c):return None if c is None else float(np.degrees(np.arccos(np.clip(c,-1.,1.))))

def run(args):
    aroot,arpt,xroot,ancestry=verify()
    from parent_o_experiment import Experiment
    with (aroot/'results/oriented_equal_projection_passages.csv').open() as f:source=list(csv.DictReader(f))
    groups=defaultdict(list)
    for row in source:groups[(row['kappa_kind'],round(float(row['ramp_xi']),9),row['shape'])].append(row)
    keys=sorted(groups)
    if args.smoke:keys=[('original',.24,'beta:2:2')]
    if args.kind!='both':keys=[k for k in keys if k[0]==args.kind]
    if args.ramps:keys=[k for k in keys if any(abs(k[1]-v)<1e-9 for v in args.ramps)]
    if not keys:raise ValueError('Selected cases have no parent exact-x section')
    ex=Experiment(args)
    output=[];cases=[];traces=[];failed=[]
    for kind,r,shape in keys:
        print('v18.50b CASE',kind,r,shape,flush=True)
        try:
            design=ex.original_ramp.Design('50b_'+kind+'_'+str(r),shape,r)
            back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,
                ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
            def state(t):return np.asarray(back(float(t))[:11],float)
            def jet(t):
                y=state(t); f,j,_=ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)
                z5,v5=five_state_and_tangent(y,f,j);z10,v10=ten_chart_and_tangent(y,f)
                return z5,v5,z10,v10
            grid=np.linspace(0.,r,args.scale_samples)
            samples5=[];samples10=[]
            for t in grid:
                z5,_,z10,_=jet(t);samples5.append(z5);samples10.append(z10)
            scale5=range_scales(samples5,args.scale_floor_relative)
            scale10=range_scales(samples10,args.scale_floor_relative)
            records=[]
            for ix,row in enumerate(groups[(kind,r,shape)]):
                t1=float(row['xi_in']);t2=float(row['xi_out'])
                z1,v1,g1,u1=jet(t1);z2,v2,g2,u2=jet(t2)
                err=max(abs(z1[0]-float(row['x_level'])),abs(z2[0]-float(row['x_level'])))
                if err>args.max_parent_projection_error:raise RuntimeError('Parent x-event mismatch '+str(err))
                if abs(v1[0]-float(row['dx_dxi_in']))>args.max_parent_rate_error or abs(v2[0]-float(row['dx_dxi_out']))>args.max_parent_rate_error:
                    raise RuntimeError('Original x rate regressed')
                if equal_x_opposed(v1[0],v2[0])!='opposed':raise RuntimeError('Parent event is not opposite x crossing')
                # First-order projected and full tangent angles, in declared chart metrics.
                cp1=cosine(v1[:2],v2[:2]);cp2=cosine(v1[[0,2]],v2[[0,2]])
                cp1s=cosine(v1[:2],v2[:2],scale5[:2]);cp2s=cosine(v1[[0,2]],v2[[0,2]],scale5[[0,2]])
                c5=cosine(v1,v2);c5s=cosine(v1,v2,scale5)
                c10=cosine(u1,u2);c10s=cosine(u1,u2,scale10)
                metrics={
                    'tangent_x_cos':cosine(v1[:1],v2[:1]),
                    'tangent_x_theta1_cos_native':cp1,'tangent_x_theta2_cos_native':cp2,
                    'tangent_x_theta1_cos_span':cp1s,'tangent_x_theta2_cos_span':cp2s,
                    'tangent_5d_cos_native':c5,'tangent_5d_cos_span':c5s,
                    'tangent_10d_cos_native':c10,'tangent_10d_cos_span':c10s,
                    'angle_5d_deg_native':ang(c5),'angle_5d_deg_span':ang(c5s),
                    'angle_10d_deg_native':ang(c10),'angle_10d_deg_span':ang(c10s),
                    'angle_x_theta1_deg_span':ang(cp1s),'angle_x_theta2_deg_span':ang(cp2s),
                    'fiber_share_5d_in_span':fiber_fraction(v1,scale5),
                    'fiber_share_5d_out_span':fiber_fraction(v2,scale5),
                    'fiber_share_5d_in_native':fiber_fraction(v1,np.ones(5)),
                    'fiber_share_5d_out_native':fiber_fraction(v2,np.ones(5)),
                    'fiber_state_separation_5d_span':float(np.linalg.norm((z2-z1)[1:]/scale5[1:])),
                    'fiber_state_separation_5d_native':float(np.linalg.norm((z2-z1)[1:])),
                    'hidden_state_gap_10d_span':float(np.linalg.norm((g2-g1)[np.arange(10)!=8]/scale10[np.arange(10)!=8])),
                    'dx_dxi_in':float(v1[0]),'dx_dxi_out':float(v2[0]),
                    'dtheta1_dxi_in':float(v1[1]),'dtheta1_dxi_out':float(v2[1]),
                    'dtheta2_dxi_in':float(v1[2]),'dtheta2_dxi_out':float(v2[2]),
                    'instant_theta2_over_theta1_in':float(v1[2]/v1[1]) if abs(v1[1])>1e-12 else None,
                    'instant_theta2_over_theta1_out':float(v2[2]/v2[1]) if abs(v2[1])>1e-12 else None,
                    'ddtheta1_dxi2_in':float(v1[3]),'ddtheta1_dxi2_out':float(v2[3]),
                    'ddtheta2_dxi2_in':float(v1[4]),'ddtheta2_dxi2_out':float(v2[4]),
                }
                # Change of tangent orientation while travelling, not just its endpoints.
                times=np.linspace(t1,t2,args.path_samples)
                vs=[]
                for t in times:
                    z,v,_,_=jet(t);vs.append(v)
                vs=np.asarray(vs)
                dirs=vs/scale5
                dirs=dirs/np.linalg.norm(dirs,axis=1)[:,None]
                angles=np.arccos(np.clip(np.einsum('ij,ij->i',dirs[:-1],dirs[1:]),-1.,1.))
                turn_integral=float(np.degrees(angles.sum()))
                if ix==0 and (args.trace_all_cases or kind=='original' and abs(r-.24)<1e-9 and shape=='beta:2:2'):
                    for t,v in zip(times,vs):
                        zt,_,_,_=jet(t)
                        traces.append({'kappa_kind':kind,'ramp_xi':r,'shape':shape,'xi':float(t),
                            'sigma':float(t/r),'x':float(zt[0]),'theta1':float(zt[1]),'theta2':float(zt[2]),
                            'dx_dxi':float(v[0]),'dtheta1_dxi':float(v[1]),'dtheta2_dxi':float(v[2]),
                            'fiber_share_span':fiber_fraction(v,scale5),
                            'tangent_turn_from_in_deg_span':ang(cosine(v,vs[0],scale5))})
                rec={'kappa_kind':kind,'ramp_xi':r,'shape':shape,'pair_index':ix,
                    'xi_in':t1,'xi_out':t2,'sigma_in':t1/r,'sigma_out':t2/r,
                    'xi_turn':float(row['xi_turn']),'x_level':float(row['x_level']),
                    'equal_projection_residual':float(z2[0]-z1[0]),'parent_projection_replay_max_error':float(err),
                    'opposite_x_crossings':True,'triad_projector_gap_from_authenticated_parent_a':float(row['triad_projector_gap']),
                    'triad_principal_angle_deg_from_parent_a':float(row['triad_max_principal_angle_deg']),
                    'full_5d_tangent_path_turn_deg_span':turn_integral,
                    'tangent_start_end_turn_deg_span':ang(c5s),
                    'path_non_geodesicity_deg_span':float(turn_integral-ang(c5s)),
                    'source_theta2_over_theta1_area_ratio':float(row['signed_area_x_theta2'])/float(row['signed_area_x_theta1']),
                    **metrics}
                records.append(rec);output.append(rec)
            cases.append({'kind':kind,'ramp_xi':r,'shape':shape,'matched_passages':len(records),
                'mechanical_ledger_error':float(ledger),
                'minimum_angle_5d_span_deg':min(d['angle_5d_deg_span'] for d in records),
                'maximum_angle_5d_span_deg':max(d['angle_5d_deg_span'] for d in records),
                'scale5':list(map(float,scale5)),'scale10':list(map(float,scale10))})
            print('  passages',len(records),'5D span angle degrees',
                round(min(d['angle_5d_deg_span'] for d in records),4),
                round(max(d['angle_5d_deg_span'] for d in records),4),'ledger',ledger,flush=True)
        except Exception as e:
            failed.append({'kind':kind,'ramp_xi':r,'shape':shape,'error':repr(e),'trace':traceback.format_exc(limit=7)})
            print('  FAILED',repr(e),flush=True)
            if args.fail_fast:raise
    if not output:raise RuntimeError('All cases failed')
    write_csv('equal_projection_tangent_pairs.csv',output)
    write_csv('case_summary.csv',cases)
    write_csv('tangent_trace_selected.csv',traces)
    write_csv('failed_cases.csv',failed)
    stats={'mean_angle_5d_span_deg':float(np.mean([z['angle_5d_deg_span'] for z in output])),
       'range_angle_5d_span_deg':[float(min(z['angle_5d_deg_span'] for z in output)),float(max(z['angle_5d_deg_span'] for z in output))],
       'range_fiber_share_span_in':[float(min(z['fiber_share_5d_in_span'] for z in output)),float(max(z['fiber_share_5d_in_span'] for z in output))],
       'range_fiber_share_span_out':[float(min(z['fiber_share_5d_out_span'] for z in output)),float(max(z['fiber_share_5d_out_span'] for z in output))],
       'range_native_5d_angle_deg':[float(min(z['angle_5d_deg_native'] for z in output)),float(max(z['angle_5d_deg_native'] for z in output))],
       'max_parent_x_projection_error':float(max(z['parent_projection_replay_max_error'] for z in output)),
       'all_opposite_x':all(z['opposite_x_crossings'] for z in output),
       'range_instantaneous_theta2_theta1_ratio_in':[float(min(z['instant_theta2_over_theta1_in'] for z in output)),float(max(z['instant_theta2_over_theta1_in'] for z in output))],
       'range_instantaneous_theta2_theta1_ratio_out':[float(min(z['instant_theta2_over_theta1_out'] for z in output)),float(max(z['instant_theta2_over_theta1_out'] for z in output))]}
    report={'audit':'v18.50b — Equal-Projection Tangent Orientation & Fiber-Transport Audit',
      'classification':'NUMERICAL_EQUAL_PROJECTION_TANGENT_AND_FIBER_DIAGNOSTIC_NOT_PHYSICAL_FIBER_BUNDLE_OR_MATERIAL_MEMORY_CERTIFICATE',
      'counts':{'successful_cases':len(cases),'failed_cases':len(failed),'authenticated_equal_x_passages_replayed':len(output),'parent_passages':len(source)},
      'genealogy':ancestry,'statistics':stats,'cases':cases,
      'metric':'native Euclidean or per-trajectory range-scaled Euclidean in x,theta1,theta2,theta1_rate,theta2_rate and native 10D coordinates; both are declared chart diagnostics, not intrinsic mechanics',
      'limitations':['An equal x projection is not an equal 3D locus or same 10D physical state.',
        'The five-state tangent uses first and second derivatives from the authenticated 11D structural RHS and Jacobian.',
        'Angles are dependent on coordinate choice and metric; comparison of native and span-normalized metrics is mandatory.',
        'The word fiber denotes the hidden coordinates of a chosen projection, not a proved physical bundle or material transport structure.',
        'Triad projector metrics are inherited authenticated measurements from v18.50a; they are not new independent spectral integrations.',
        'Two endpoint samples on one return orbit are correlated; events are not independent experimental replicates.',
        'No physical chirality, material memory, eight-state rule, spatial volume, or closed full-state return is certified.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true');p.add_argument('--kind',choices=['both','original','autonomous'],default='both');p.add_argument('--ramps',nargs='*',type=float)
    p.add_argument('--scale-samples',type=int,default=61);p.add_argument('--path-samples',type=int,default=41)
    p.add_argument('--scale-floor-relative',type=float,default=1e-5)
    p.add_argument('--max-parent-projection-error',type=float,default=2e-9);p.add_argument('--max-parent-rate-error',type=float,default=1e-8)
    p.add_argument('--trace-all-cases',action='store_true');p.add_argument('--fail-fast',action='store_true')
    # Exact original 11D Q550 integrator tolerances (parent contract).
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025);p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum_parent_share_difference',type=float,default=2e-6)
    p.add_argument('--max_generator_identity_error',type=float,default=1e-7)
    args=p.parse_args()
    if args.path_samples<3 or args.scale_samples<3:p.error('Need >=3 samples per scan')
    run(args)
