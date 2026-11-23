#!/usr/bin/env python3
"""Q550 v18.50c — Hidden-Tangent Conditioning & Turning-Response Audit.

Measure how the direction of hidden 4D state velocity evolves through the
turning of x. Directional change, temporal alignment and ramp comparisons
are observational diagnostics; no causal conditioning or material memory
is certified from a single common drive.
"""
import argparse,csv,json,platform,traceback
from pathlib import Path
from collections import defaultdict
import numpy as np
from verify_parent_b import verify
from geometry import direction_geometry,secant_angle,interp_row
ROOT=Path(__file__).resolve().parents[1]

def write_csv(path,rows):
 if not rows:return
 dest=ROOT/'results'/path;dest.parent.mkdir(exist_ok=True)
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with dest.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def finite_float(t):return float(t)

def run(args):
 broot,breport,ancestry=verify()
 from parent_o_experiment import Experiment
 with (broot/'results/equal_projection_tangent_pairs.csv').open() as f:
  source=list(csv.DictReader(f))
 with (broot/'results/case_summary.csv').open() as f:
  case_source=list(csv.DictReader(f))
 groups=defaultdict(list)
 for p in source:groups[(p['kappa_kind'],round(float(p['ramp_xi']),9),p['shape'])].append(p)
 scales=[]
 for p in case_source:
  vals=np.asarray(json.loads(p['scale5']),float)
  scales.append(vals[1:])
 # One fixed 4D scale across all 10 authenticated trajectories, not a new scale for each one.
 common_scale=np.max(scales,axis=0)
 if not np.all(common_scale>0):raise RuntimeError('Invalid common scale')
 keys=sorted(groups)
 if args.smoke:keys=[('original',.24,'beta:2:2')]
 if args.kind!='both':keys=[k for k in keys if k[0]==args.kind]
 if args.ramps:keys=[k for k in keys if any(abs(k[1]-v)<1e-9 for v in args.ramps)]
 if not keys:raise RuntimeError('No source events for selected cases')
 ex=Experiment(args)
 sample_records=[];pair_records=[];case_records=[];failures=[];refinements=[]
 for kind,r,shape in keys:
  print('v18.50c CASE',kind,r,shape,flush=True)
  try:
   design=ex.original_ramp.Design('50c_'+kind+'_'+str(r),shape,r)
   back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,
       ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
   def jet(t):
    y=np.asarray(back(float(t))[:11],float)
    f,J,_=ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)
    acc=J@f
    x=float(1/(1+np.exp(-y[8])))
    return x,float(x*(1-x)*f[8]),np.asarray([f[2],f[6],acc[2],acc[6]],float)
   turn=float(groups[kind,r,shape][0]['xi_turn'])
   if turn<=0 or turn>=r:raise RuntimeError('Source turning outside duration')
   x_turn,xdot_turn,_=jet(turn)
   if abs(xdot_turn)>args.max_turning_rate:raise RuntimeError('Authenticated turning rate mismatch '+str(xdot_turn))
   def trace(n):
    grid=np.linspace(0,r,n)
    # Uniform grid for finite differences; nonuniform near-duplicate events can
    # create artificial direction-curvature spikes. Exact events are evaluated
    # independently with the structural jet.
    js=[jet(t) for t in grid]
    x=np.asarray([q[0] for q in js]);xdot=np.asarray([q[1] for q in js]);h=np.asarray([q[2] for q in js])
    return grid,x,xdot,h
   grid,x,xdot,h=trace(args.samples)
   # Fixed pooled scale is the primary metric; native and rescaled common controls are sensitivity checks.
   metrics={'common':common_scale,'native':np.ones(4),
     'theta_half':common_scale*np.array([2,2,1,1],float),
     'theta_double':common_scale*np.array([.5,.5,1,1],float)}
   primary=None
   for metric,scale in metrics.items():
    u,du,k,omega=direction_geometry(grid,h,scale)
    # Exclude finite-difference boundary layers in peak localization.
    valid=(grid>=max(0,grid[0]+r*args.edge_fraction)) & (grid<=min(r,grid[-1]-r*args.edge_fraction))
    # Peak in a window centered on the real x-turn, not on zero of control.
    w=(abs(grid-turn)<=args.local_window_fraction*r)&valid
    if w.sum()<4:raise RuntimeError('Too few samples in turning window')
    idx=np.where(w)[0][np.argmax(k[w])]
    iturn=int(np.argmin(abs(grid-turn)))
    delta=min(args.probe_distance_xi, args.probe_fraction*r, turn*.4, (r-turn)*.4)
    if delta<=0:raise RuntimeError('Insufficient interior event support')
    # Direct structural jets at both probe sections, in the SAME case scale.
    from geometry import unit_tangent
    uminus=unit_tangent(jet(turn-delta)[2],scale)
    uplus=unit_tangent(jet(turn+delta)[2],scale)
    angle=secant_angle(uminus,uplus)
    kturn=float(np.interp(turn,grid,k));lag=float(grid[idx]-turn)
    total=float(np.trapezoid(k,grid))
    mask=(grid>=turn-delta)&(grid<=turn+delta)
    loc=float(np.trapezoid(k[mask],grid[mask]))
    if metric=='common':
     primary=(grid,x,xdot,h,u,k,omega)
     # Show the whole ramp for selected cases; all cases retain a sampled trace.
     for j in range(len(grid)):
      sample_records.append({'kind':kind,'ramp_xi':r,'shape':shape,'metric':'common',
        'xi':float(grid[j]),'sigma':float(grid[j]/r),'turn_xi':turn,'drive_zero_xi':r/2,
        'delta_xi_from_turn':float(grid[j]-turn),'x':float(x[j]),'xdot':float(xdot[j]),
        'hidden_speed_scaled':float(np.linalg.norm(h[j]/scale)),
        'hidden_dir_turn_rate':float(k[j]),'hidden_dir_theta1':float(u[j,0]),
        'hidden_dir_theta2':float(u[j,1]),'hidden_dir_theta1dot':float(u[j,2]),
        'hidden_dir_theta2dot':float(u[j,3]),
        'signed_orientation_bivector_01':float(omega[j,0]),
        'signed_orientation_bivector_02':float(omega[j,1]),
        'signed_orientation_bivector_03':float(omega[j,2]),
        'signed_orientation_bivector_12':float(omega[j,3]),
        'signed_orientation_bivector_13':float(omega[j,4]),
        'signed_orientation_bivector_23':float(omega[j,5])})
    case_records.append({'kind':kind,'ramp_xi':r,'shape':shape,'metric':metric,
      'source_pairs':len(groups[kind,r,shape]),'turn_xi':turn,'drive_zero_xi':r/2,
      'turn_minus_drive_zero_xi':turn-r/2,'turn_xdot':float(xdot_turn),
      'hidden_turn_rate_at_x_turn':kturn,'hidden_turn_rate_local_peak':float(k[idx]),
      'hidden_local_peak_xi':float(grid[idx]),'peak_minus_x_turn_xi':lag,
      'local_peak_boundary_flag':bool(abs(grid[idx]-turn)>=(args.local_window_fraction*r-2*r/args.samples)),
      'delta_probe_xi':delta,'hidden_direction_change_across_turn_deg':angle,
      'total_hidden_direction_arc_rad':total,'local_hidden_direction_arc_rad':loc,
      'max_mechanical_ledger_error':float(ledger)})
   assert primary is not None
   grid,x,xdot,h,u,k,omega=primary
   # Existing equal-x return pairs: consistent metric across all cases; do not infer equal full locus.
   for p in groups[kind,r,shape]:
    a,b=float(p['xi_in']),float(p['xi_out'])
    from geometry import unit_tangent
    u1=unit_tangent(jet(a)[2],common_scale);u2=unit_tangent(jet(b)[2],common_scale)
    ia=int(np.searchsorted(grid,a));ib=int(np.searchsorted(grid,b))
    # Integrate the turning rate with interpolated exact segment limits.
    tsegment=np.r_[a,grid[(grid>a)&(grid<b)],b]
    ksegment=np.interp(tsegment,grid,k)
    source_angle=float(p['angle_5d_deg_span'])
    pair_records.append({'kind':kind,'ramp_xi':r,'shape':shape,'pair_index':int(p['pair_index']),
       'xi_in':a,'xi_out':b,'turn_xi':turn,'delta_xi':b-a,
       'hidden_angle_deg_common':secant_angle(u1,u2),
       'hidden_cos_common':float(np.dot(u1,u2)),
       'hidden_arc_between_passages_rad':float(np.trapezoid(ksegment,tsegment)),
       'in_hidden_turn_rate':float(np.interp(a,grid,k)),'out_hidden_turn_rate':float(np.interp(b,grid,k)),
       'v18_50b_per_case_5d_angle_deg':source_angle,
       'x_return_error_from_parent':float(p['equal_projection_residual']),
       'turn_rate_at_x_turn':float(np.interp(turn,grid,k))})
   if args.refine:
    fine,x2,dx2,h2=trace(2*args.samples-1)
    _,_,kr,_=direction_geometry(fine,h2,common_scale)
    delta_rate=abs(float(np.interp(turn,grid,k))-float(np.interp(turn,fine,kr)))
    delta_arc=abs(float(np.trapezoid(k,grid))-float(np.trapezoid(kr,fine)))
    refinements.append({'kind':kind,'ramp_xi':r,'shape':shape,
     'coarse_n':len(grid),'fine_n':len(fine),'turn_rate_difference':delta_rate,
     'total_direction_arc_difference_rad':delta_arc})
   print('  turn xi',round(turn,9),'angular bending deg',round(next(z['hidden_direction_change_across_turn_deg'] for z in case_records[::-1] if z['metric']=='common'),4),'ledger',float(ledger),flush=True)
  except Exception as e:
   failures.append({'kind':kind,'ramp_xi':r,'shape':shape,'error':repr(e),'trace':traceback.format_exc(limit=8)})
   print('  CASE FAILED',repr(e),flush=True)
   if args.fail_fast:raise
 if not pair_records:raise RuntimeError('No pair records')
 write_csv('hidden_tangent_phase_trace.csv',sample_records)
 write_csv('equal_x_pair_hidden_orientation.csv',pair_records)
 write_csv('turning_clock_hidden_response.csv',case_records)
 write_csv('refinement.csv',refinements)
 write_csv('failures.csv',failures)
 primary_cases=[v for v in case_records if v['metric']=='common']
 stats={'cases':len(primary_cases),'pairs':len(pair_records),'failures':len(failures),
    'all_hidden_tangent_pairs_positive_common_metric':all(p['hidden_cos_common']>0 for p in pair_records),
    'hidden_angle_range_deg':[min(p['hidden_angle_deg_common'] for p in pair_records),max(p['hidden_angle_deg_common'] for p in pair_records)],
    'turning_curvature_range':[min(c['hidden_turn_rate_at_x_turn'] for c in primary_cases),max(c['hidden_turn_rate_at_x_turn'] for c in primary_cases)],
    'local_peak_lag_range_xi':[min(c['peak_minus_x_turn_xi'] for c in primary_cases),max(c['peak_minus_x_turn_xi'] for c in primary_cases)],
    'max_refinement_turn_rate_difference':max([p['turn_rate_difference'] for p in refinements],default=None),
    'max_refinement_arc_difference':max([p['total_direction_arc_difference_rad'] for p in refinements],default=None)}
 report={'audit':'v18.50c — Hidden-Tangent Conditioning & Turning-Response Audit',
  'classification':'NUMERICAL_HIDDEN_DIRECTION_RESPONSE_ASSOCIATION_NOT_CAUSAL_CONDITIONING_OR_MATERIAL_MEMORY_CERTIFICATE',
  'genealogy':ancestry,'common_scale_4d':list(map(float,common_scale)),
  'method':{'sampling':args.samples,'turning_clock':'authenticated natural zero of dx/dxi',
   'common_metric':'max of individual v18.50b trajectory coordinate spans (theta1,theta2,theta1dot,theta2dot), fixed for all cases',
   'hidden_direction':'unit of (theta1dot,theta2dot,theta1ddot,theta2ddot) under declared scale',
   'turn_rate':'Euclidean norm d(unit hidden tangent)/d xi; derivative from sampled exact structural jet',
   'local_peak_window_fraction':args.local_window_fraction,
   'controls':['native','theta_half','theta_double'],
   'limitations':['Co-evolution does not establish which coordinate causes which change.',
                  'Peak timing is window-dependent and may be pinned to its boundary.',
                  'Common metric remains a coordinate-chart convention; angles are not absolute physical rotations.',
                  'No spatial volume, cubical lift, physical fiber bundle or material memory is certified.',
                  'Source pair events share physical trajectories and are not independent replicates.']},
  'statistics':stats,'cases':primary_cases}
 (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__, 'scipy':__import__('scipy').__version__},indent=2)+'\n')
 return report

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--smoke',action='store_true');ap.add_argument('--kind',choices=['both','original','autonomous'],default='both')
 ap.add_argument('--ramps',nargs='*',type=float);ap.add_argument('--samples',type=int,default=201)
 ap.add_argument('--local-window-fraction',type=float,default=.18)
 ap.add_argument('--edge-fraction',type=float,default=.02)
 ap.add_argument('--probe-distance-xi',type=float,default=.025)
 ap.add_argument('--probe-fraction',type=float,default=.12)
 ap.add_argument('--max-turning-rate',type=float,default=1e-7)
 ap.add_argument('--refine',action='store_true',default=True);ap.add_argument('--no-refine',action='store_false',dest='refine')
 ap.add_argument('--fail-fast',action='store_true')
 # Historical solver interface, forwarded unchanged.
 ap.add_argument('--rtol',type=float,default=3e-12);ap.add_argument('--atol',type=float,default=3e-13)
 ap.add_argument('--max-step',type=float,default=.025);ap.add_argument('--maximum-ledger-error',type=float,default=1e-8)
 ap.add_argument('--maximum-regression',type=float,default=1e-7);ap.add_argument('--maximum_parent_share_difference',type=float,default=2e-6)
 ap.add_argument('--max_generator_identity_error',type=float,default=1e-7)
 args=ap.parse_args()
 if args.samples<41 or args.local_window_fraction<=0 or args.local_window_fraction>=.5:ap.error('Invalid sampling/window')
 run(args)
