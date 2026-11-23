#!/usr/bin/env python3
"""v18.50a — Equal-Projection Oriented Passage & Transport-Law Audit.

Replays 11D Q550 dynamics from authenticated x ancestry at precisely matched x event
pairs. Integrates signed (x,theta1/theta2) passage areas, explicitly checks opposite
x-crossing rate, and compares gauge-invariant triad projectors in a common kinetic
frame. This is NOT a material-memory, physical chirality, cubical-state, or spatial
volume certificate.
"""
import argparse,csv,json,platform,traceback
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import simpson
from verify_parent_x import verify
from passage_math import integrate_rates,transversality
ROOT=Path(__file__).resolve().parents[1]

def save(name,rows):
 if not rows:return
 dest=ROOT/'results'/name;dest.parent.mkdir(exist_ok=True)
 names=list(dict.fromkeys(k for row in rows for k in row))
 with dest.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=names);w.writeheader();w.writerows(rows)

def run(args):
 xroot,xreport,ancestry=verify()
 # x verification also installs all ancestor module paths and original solver.
 from parent_o_experiment import Experiment
 from frame_math import transport_frame
 from kinetic_metric import embedding_and_jac
 # Import source x spectral_at using path-bound module to avoid filename collision.
 import importlib.util,sys
 spec=importlib.util.spec_from_file_location('x_spectral_helper_50a',xroot/'scripts/run_audit.py')
 mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 spectral_at=mod.spectral_at; logistic=mod.logistic
 with (xroot/'results/equal_projection_return_pairs.csv').open() as f: paired=list(csv.DictReader(f))
 groups=defaultdict(list)
 for row in paired:
  key=(row['kappa_kind'],round(float(row['ramp_xi']),8),row['shape']);groups[key].append(row)
 keys=sorted(groups)
 if args.smoke:keys=[('original',.24,'beta:2:2')]
 elif args.kind!='both':keys=[k for k in keys if k[0]==args.kind]
 if args.ramps:keys=[k for k in keys if any(abs(k[1]-r)<1e-9 for r in args.ramps)]
 if not keys:raise RuntimeError('No authentic x source pairs for requested cases')
 ex=Experiment(args)
 cases=[];rows=[];failures=[];phase_rows=[]
 for kind,r,shape in keys:
  print('v18.50a CASE',kind,r,shape,flush=True)
  try:
   design=ex.original_ramp.Design('50a_'+kind+'_'+str(r),shape,r)
   back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
   def state(t):return np.asarray(back(float(t))[:11],float)
   def field(t):return ex.jet.structural_jet(state(t),ex.ks[kind],ex.params,ex.slope)[0]
   def x(t):return logistic(state(t)[8])
   def rate_x(t):
    xx=x(t);return xx*(1-xx)*float(field(t)[8])
   def jac(y,k,p,sl):return ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)[1]
   frame,frame_err=transport_frame(back,ex.ks[kind],ex.params,ex.slope,jac,r,rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
   _,J0=embedding_and_jac(state(0)[:10],ex.params.m_x,1.)
   this=[]
   for ordinal,src in enumerate(groups[(kind,r,shape)]):
    t1,t2=float(src['xi_in']),float(src['xi_out']);xlev=float(src['x_in'])
    a,b=state(t1),state(t2)
    if abs(x(t1)-xlev)>args.parent_tolerance or abs(x(t2)-xlev)>args.parent_tolerance:
     raise RuntimeError('Event projection mismatch with authenticated x root')
    # Evaluate the actual dense physical ODE at original model phase locations.
    def sample(n):
     ts=np.linspace(t1,t2,n);ss=np.asarray([state(t) for t in ts]);rr=np.asarray([field(t) for t in ts]);xx=np.asarray([logistic(v) for v in ss[:,8]])
     area=np.asarray([integrate_rates(ts,xx,rr[:,j],xlev) for j in (2,6)],float)
     delta=np.asarray([simpson(rr[:,j],x=ts) for j in (2,6)],float)
     return ts,ss,rr,xx,area,delta
    _,_,_,_,low,dlo=sample(args.quad_points)
    ts,ss,rr,xx,areas,dhi=sample(2*args.quad_points-1)
    delta=np.array([b[2]-a[2],b[6]-a[6]])
    quad_err=float(np.max(abs(areas-low)))
    integration_err=float(np.max(abs(dhi-delta)))
    if quad_err>args.max_area_refinement_error:raise RuntimeError(f'Area refinement failed: {quad_err:g}')
    if integration_err>args.max_angular_ledger_error:raise RuntimeError(f'Angular rate ledger failed: {integration_err:g}')
    rate1,rate2=rate_x(t1),rate_x(t2)
    proj1=spectral_at(ex,back,frame,J0,kind,t1,args.min_gap)
    proj2=spectral_at(ex,back,frame,J0,kind,t2,args.min_gap)
    p_err=None;max_angle=None
    if 'projector' in proj1 and 'projector' in proj2:
     p_err=float(np.linalg.norm(proj2['projector']-proj1['projector'],'fro'))
     s=np.linalg.svd(proj1['axes'].T@proj2['axes'],compute_uv=False)
     max_angle=float(np.degrees(np.arccos(np.clip(min(s),-1,1))))
     if abs(p_err-float(src['triad_projector_frobenius_gap']))>args.max_projector_regression:raise RuntimeError('Parent x triad regression failed')
    else:raise RuntimeError('Singular triad at an authenticated x pair: '+str(proj1.get('error',proj2.get('error'))))
    if transversality(rate1,rate2)!='opposed':raise RuntimeError('Matched pair does not cross opposite x branches')
    row={'kappa_kind':kind,'ramp_xi':r,'shape':shape,'pair_index':ordinal,
      'xi_in':t1,'xi_out':t2,'xi_turn':float(src['xi_turn']), 'sigma_in':t1/r,'sigma_out':t2/r,
      'delta_xi':t2-t1,'x_level':xlev,'x_return_error':x(t2)-x(t1),
      'dx_dxi_in':rate1,'dx_dxi_out':rate2,'transversality':transversality(rate1,rate2),
      'theta1_transport_rad':float(delta[0]),'theta2_transport_rad':float(delta[1]),
      'signed_area_x_theta1':float(areas[0]),'signed_area_x_theta2':float(areas[1]),
      'area_vector_norm':float(np.linalg.norm(areas)),
      'area_vector_angle_deg':float(np.degrees(np.arctan2(areas[1],areas[0]))),
      'area_refinement_error':quad_err,'angular_ledger_error':integration_err,
      'max_x_excursion':float(np.max(xx-xlev)),
      'radial_locus_gap':float(np.linalg.norm((b-a)[[0,4]])),
      'triad_projector_gap':p_err,'triad_max_principal_angle_deg':max_angle,
      'projector_parent_regression':abs(p_err-float(src['triad_projector_frobenius_gap'])),
      'min_endpoint_relative_gap':min(float(proj1['min_gap']),float(proj2['min_gap']))}
    rows.append(row);this.append(row)
    if args.sample_trace_pair and ordinal==0:
     for tt,yy in zip(ts[::8],ss[::8]):phase_rows.append({'kappa_kind':kind,'ramp_xi':r,'shape':shape,'pair_index':ordinal,'xi':tt,'x':logistic(yy[8]),'theta1':yy[2],'theta2':yy[6]})
   # All pairs must preserve their x event in same frame; summaries are not laws or independent samples.
   cases.append({'kind':kind,'ramp_xi':r,'shape':shape,'pairs':len(this),'mechanical_ledger_error':float(ledger),
     'max_area_quad_refinement':max(z['area_refinement_error'] for z in this),
     'max_projector_regression':max(z['projector_parent_regression'] for z in this),
     'theta1_area_signs':sorted(set(np.sign(z['signed_area_x_theta1']) for z in this)),
     'theta2_area_signs':sorted(set(np.sign(z['signed_area_x_theta2']) for z in this))})
   print('  PAIRS',len(this),'A1 range',[min(z['signed_area_x_theta1'] for z in this),max(z['signed_area_x_theta1'] for z in this)],'ledger',ledger,flush=True)
  except Exception as e:
   failures.append({'kind':kind,'ramp':r,'shape':shape,'error':repr(e),'trace':traceback.format_exc(limit=5)})
   if args.fail_fast:raise
   print('CASE FAILURE',repr(e),flush=True)
 if not rows:raise RuntimeError('No successful physical passage replays')
 save('oriented_equal_projection_passages.csv',rows)
 save('case_summary.csv',cases)
 save('selected_passage_trace.csv',phase_rows)
 save('failed_cases.csv',failures)
 report={'audit':'v18.50a — Equal-Projection Oriented Passage & Transport-Law Audit',
  'classification':'NUMERICAL_ORIENTED_EQUAL_PROJECTION_PASSAGE_NOT_PHYSICAL_CHIRALITY_OR_MATERIAL_MEMORY_CERTIFICATE',
  'genealogy':ancestry,
  'counts':{'successful_cases':len(cases),'failed_cases':len(failures),'matched_passages_replayed':len(rows),'parent_matched_passages':len(paired)},
  'statistics':{'opposed_x_branch_fraction':sum(v['transversality']=='opposed' for v in rows)/len(rows),
     'theta1_area_positive_fraction':sum(v['signed_area_x_theta1']>0 for v in rows)/len(rows),
     'theta2_area_positive_fraction':sum(v['signed_area_x_theta2']>0 for v in rows)/len(rows),
     'maximum_area_quadrature_refinement_error':max(v['area_refinement_error'] for v in rows),
     'maximum_parent_x_projector_difference':max(v['projector_parent_regression'] for v in rows),
     'maximum_angular_rate_ledger_error':max(v['angular_ledger_error'] for v in rows)},
  'cases':cases,'limitations':[
    'Signed (x, theta) area is a 2D chosen-coordinate projected diagnostic. It is not spatial volume, material torsion, or observer-independent chirality.',
    'The exact x returns are obtained from the authenticated x parent. No eight-state or quadrant label is assigned to Q550.',
    'Triad projector Frobenius gap is invariant under global orthogonal changes of the common kinetic frame but does not determine an oriented material body frame.',
    'Reintegration and quadrature are numerical not rigorous interval certificates.',
    'Selected return events share a solver trajectory; 34 source pairs are not 34 independent experiments.']}
 (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--smoke',action='store_true')
 p.add_argument('--kind',choices=('original','autonomous','both'),default='both')
 p.add_argument('--ramps',nargs='*',type=float)
 p.add_argument('--quad-points',type=int,default=129)
 p.add_argument('--min-gap',type=float,default=1e-6)
 p.add_argument('--sample-trace-pair',action='store_true',default=True)
 p.add_argument('--no-sample-trace',action='store_false',dest='sample_trace_pair')
 p.add_argument('--max-area-refinement-error',type=float,default=5e-8)
 p.add_argument('--max-angular-ledger-error',type=float,default=2e-7)
 p.add_argument('--max-projector-regression',type=float,default=5e-6)
 p.add_argument('--parent-tolerance',type=float,default=2e-9)
 p.add_argument('--fail-fast',action='store_true')
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
 args=p.parse_args()
 if args.quad_points%2!=1 or args.quad_points<9:p.error('quadrature points must be odd >=9')
 run(args)
