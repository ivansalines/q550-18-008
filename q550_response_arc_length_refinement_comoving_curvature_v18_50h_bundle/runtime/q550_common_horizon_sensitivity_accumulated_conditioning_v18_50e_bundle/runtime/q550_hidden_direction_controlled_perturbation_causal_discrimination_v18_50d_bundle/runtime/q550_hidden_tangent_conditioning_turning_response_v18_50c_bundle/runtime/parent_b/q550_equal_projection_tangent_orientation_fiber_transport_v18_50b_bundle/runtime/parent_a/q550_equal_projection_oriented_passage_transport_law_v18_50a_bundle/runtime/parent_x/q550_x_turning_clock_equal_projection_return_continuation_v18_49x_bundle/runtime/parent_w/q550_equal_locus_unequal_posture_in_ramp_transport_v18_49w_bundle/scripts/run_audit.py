#!/usr/bin/env python3
"""v18.49w — Equal-Locus, Unequal-Posture & In-Ramp Transport Audit.

Reintegrate authentic 11D Q550 during prescribed cubic ramp and reconstruct
10D deformation eigenprojectors in the ORIGINAL kinetic reference. Identify
*nontrivially separated* equal-phase and near-locus events, then measure
posture and projectors directly. No physical volume/memory inference is made.
"""
import argparse,csv,json,platform,traceback
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from verify_w_parent import verify
from pair_math import compare,near_decision,logistic
ROOT=Path(__file__).resolve().parents[1]

def writecsv(filename,rows):
    if not rows:return
    dest=ROOT/'results'/filename;dest.parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with dest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def polar_so3(A):
    L,s,R=np.linalg.svd(A);O=L@R
    if np.linalg.det(O)<0:L[:,-1]*=-1;O=L@R
    return O

def run(args):
    vroot,report_v,anc=verify()
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    ex=Experiment(args)
    kinds=['original'] if args.smoke else ['original','autonomous'] if args.kind=='both' else [args.kind]
    ramps=args.ramp_values or ([.327375] if args.smoke else [.12,.24,.327375,.5])
    if any(r<.02 or r>1. for r in ramps):raise ValueError('Unsupported r outside [.02,1]')
    ss=np.linspace(0,1,args.samples)
    pair_rows=[];sym_rows=[];trajectory_rows=[];summary=[];problems=[]
    controls={'maximum_11d_ledger':0.,'max_v_endpoint_regression':0.,'min_relative_eigengap':None,
              'max_triad_projector_idempotence_error':0.,'max_so3_orthogonality_error':0.,
              'maximum_command_phase_mirror_gap':0.,'initial_v_forward_regression':float(ex.regression)}
    vreg={(d['kappa_kind'],round(float(d['ramp_xi']),8)):d for d in report_v['cases']}
    for kind in kinds:
        for r in ramps:
            try:
                design=ex.original_ramp.Design('authentic_cubic_v18_49w','beta:2:2',float(r))
                back,err=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,
                    ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
                controls['maximum_11d_ledger']=max(controls['maximum_11d_ledger'],float(err))
                states=[np.asarray(back(float(s*r))[:11],float) for s in ss]
                y0=states[0]
                energies=[float(ex.physical.energy(y,ex.ks[kind],ex.params)) for y in states]
                # Original fixed initial kinetic embedding, as in v18.49v.
                def jac(y,k,p,sl):return ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)[1]
                frame,frerr=transport_frame(back,ex.ks[kind],ex.params,ex.slope,jac,float(r),
                    rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
                _,J0=embedding_and_jac(y0[:10],ex.params.m_x,1.)
                samples=[];Ucross=np.eye(10);A0=None;prev_axes=None;prev_t=None;prev_Kc=None
                spectral_count=0
                for idx,(sigma,y,E) in enumerate(zip(ss,states,energies)):
                    t=float(r*sigma);S=None;A=None;R=None;mingap=None;Kc=None
                    if idx>0:
                        field,Jmat,_=ex.jet.structural_jet(y,ex.ks[kind],ex.params,ex.slope)
                        _,J=embedding_and_jac(y,ex.params.m_x,1.)
                        Jdot=kinetic_frame_derivative(y,field,ex.params.m_x,1.,embedding_and_jac)
                        B,Bdot=deforming_frame(J,frame(t),J0,Jdot,Jmat[:10,:10])
                        spec=spectral_generator(B,Bdot,relative_gap_floor=args.min_gap)
                        P=spec['projectors'];K=spec['generator']
                        S=np.sum(P[[5,6,7]],axis=0)
                        A=np.asarray(spec['axes'][:,[5,6,7]],float).copy()
                        Kc=S@K@(np.eye(10)-S)+(np.eye(10)-S)@K@S
                        mingap=float(spec['min_relative_eigengap']);spectral_count+=1
                        controls['max_triad_projector_idempotence_error']=max(controls['max_triad_projector_idempotence_error'],float(np.linalg.norm(S@S-S)))
                        controls['min_relative_eigengap']=mingap if controls['min_relative_eigengap'] is None else min(controls['min_relative_eigengap'],mingap)
                        if sigma>=args.orientation_start-1e-12:
                            if A0 is None:
                                A0=A.copy()
                            else:
                                # sign-align to previous step and transport cross block.
                                A*=np.where((prev_axes*A).sum(axis=0)<0,-1.,1.)[None,:]
                                h=t-prev_t
                                Ucross=expm(h*(Kc+prev_Kc)/2)@Ucross
                            R=polar_so3(A0.T@Ucross.T@A)
                            controls['max_so3_orthogonality_error']=max(controls['max_so3_orthogonality_error'],float(np.linalg.norm(R.T@R-np.eye(3))))
                            prev_axes=A.copy();prev_t=t;prev_Kc=Kc.copy()
                    samples.append({'state':y,'S':S,'A':A,'R':R,'energy':E,'sigma':float(sigma), 'gap':mingap})
                    trajectory_rows.append({'kappa_kind':kind,'ramp_xi':float(r),'sigma':float(sigma),
                         'x':float(logistic(y[8])),'logrho1':float(y[0]),'logrho2':float(y[4]),
                         'theta1':float(y[2]),'theta2':float(y[6]),'drive_theta_lift':float(y[10]),
                         'energy':E,'spectral_valid':int(S is not None),'spectral_gap':mingap})
                key=(kind,round(float(r),8))
                if key in vreg:
                    # v: 10D state endpoint displacement; ensure EXACT original replay.
                    disp=float(np.linalg.norm(states[-1][:10]-states[0][:10]))
                    regression=abs(disp-float(vreg[key]['full_10d_endpoint_displacement']))
                    controls['max_v_endpoint_regression']=max(controls['max_v_endpoint_regression'],regression)
                    if regression>args.max_parent_regression:raise RuntimeError('v18.49v replay regression failed')
                raw=np.array([[y[0],y[4],logistic(y[8])] for y in states])
                spans=np.maximum(np.ptp(raw,axis=0),args.span_floor)
                number_candidates=0;nearx=[];nearloc=[];minx=None;minxvalid=None;minloc=None;max_pose_x=None;max_pose_xvalid=None;max_pose_locus=None
                for i in range(len(ss)-1):
                    for j in range(i+1,len(ss)):
                        if ss[j]-ss[i]<args.min_separation-1e-12:continue
                        p=compare(samples[i],samples[j],spans)
                        flagx,flagloc=near_decision(p,args.x_fraction,args.locus_fraction,args.min_separation)
                        p.update({'kappa_kind':kind,'ramp_xi':float(r),'near_x':int(flagx),'near_3d_locus':int(flagloc)})
                        pair_rows.append(p);number_candidates+=1
                        if minx is None or p['x_gap_over_span']<minx['x_gap_over_span']:minx=p
                        if p['triad_projector_frobenius_gap'] is not None and (minxvalid is None or p['x_gap_over_span']<minxvalid['x_gap_over_span']):minxvalid=p
                        if minloc is None or p['locus_xyz_scaled_gap']<minloc['locus_xyz_scaled_gap']:minloc=p
                        if flagx:
                            nearx.append(p)
                            if max_pose_x is None or p['posture_theta_pair_gap_rad']>max_pose_x['posture_theta_pair_gap_rad']:max_pose_x=p
                            if p['cross_frame_triad_SO3_angle_deg'] is not None and (max_pose_xvalid is None or p['posture_theta_pair_gap_rad']>max_pose_xvalid['posture_theta_pair_gap_rad']):max_pose_xvalid=p
                        if flagloc:
                            nearloc.append(p)
                            if max_pose_locus is None or p['posture_theta_pair_gap_rad']>max_pose_locus['posture_theta_pair_gap_rad']:max_pose_locus=p
                # Same imposed phase: symmetric sample points; this equality is structural to cubic drive.
                mirror=[]
                for i in range(len(ss)//2):
                    j=len(ss)-1-i
                    if ss[j]-ss[i]<args.min_separation-1e-12:continue
                    p=compare(samples[i],samples[j],spans)
                    p.update({'kappa_kind':kind,'ramp_xi':float(r),'drive_phase_symmetry_expected':True})
                    mirror.append(p);sym_rows.append(p)
                    controls['maximum_command_phase_mirror_gap']=max(controls['maximum_command_phase_mirror_gap'],p['theta_lift_gap'])
                # Conclusive NOT based on best single scale/selected coordinate.
                def fields(p,prefix):
                    if p is None:return {}
                    return {prefix+'_'+k:v for k,v in p.items() if k in
                       ('sigma_a','sigma_b','delta_sigma','x_abs_gap','x_gap_over_span','locus_xyz_scaled_gap',
                        'posture_theta_pair_gap_rad','full_state_10d_gap','triad_projector_frobenius_gap','cross_frame_triad_SO3_angle_deg')}
                sr={'kappa_kind':kind,'ramp_xi':float(r),'candidate_pairs':number_candidates,
                    'near_x_pairs':len(nearx),'near_3d_locus_pairs':len(nearloc),'matched_equal_clock_phase_pairs':len(mirror),
                    'x_full_range':float(spans[2]),'logrho1_range':float(spans[0]),'logrho2_range':float(spans[1]),
                    'triad_valid_samples':spectral_count,'spectral_angle_reference_sigma':args.orientation_start,
                    **fields(minx,'closest_x'),**fields(minxvalid,'closest_x_both_triad_defined'),**fields(minloc,'closest_3d_locus'),
                    **fields(max_pose_x,'max_posture_among_near_x'),**fields(max_pose_xvalid,'max_posture_among_near_x_triad_defined'),**fields(max_pose_locus,'max_posture_among_near_3d_locus')}
                summary.append(sr)
                print('v18.49w',kind,r,'pairs',number_candidates,'nearX',len(nearx),'near3D',len(nearloc),
                      'best-locus',round(minloc['locus_xyz_scaled_gap'],6),flush=True)
            except Exception as e:
                if args.fail_fast:raise
                problems.append({'kappa_kind':kind,'ramp_xi':float(r),'error':repr(e),'trace':traceback.format_exc(limit=6)})
                print('CASE_FAILED',kind,r,repr(e),flush=True)
    writecsv('sampled_states_11d_projection.csv',trajectory_rows)
    writecsv('all_separated_pairs.csv',pair_rows)
    writecsv('equal_clock_phase_mirror_pairs.csv',sym_rows)
    writecsv('case_summary.csv',summary)
    writecsv('numerical_failures.csv',problems)
    if not summary:raise RuntimeError('No successful genuine Q550 integrations')
    report={'audit':'v18.49w — Equal-Locus, Unequal-Posture & In-Ramp Transport Audit',
        'classification':'IN_RAMP_EQUAL_LOCUS_DIAGNOSTIC_NOT_SPATIAL_VOLUME_OR_MATERIAL_MEMORY_CERTIFICATE',
        'genealogy':anc,'counts':{'successes':len(summary),'failures':len(problems),'candidate_pairs':len(pair_rows),
                                 'same_prescribed_phase_pairs':len(sym_rows),'near_x_total':sum(x['near_x_pairs'] for x in summary),
                                 'near_strict_3d_locus_total':sum(x['near_3d_locus_pairs'] for x in summary)},
        'criteria':{'min_sigma_separation':args.min_separation,'near_x_fraction_of_full_x_excursion':args.x_fraction,
                    'near_3d_locus_scaled_euclidean_threshold':args.locus_fraction,'span_floor':args.span_floor,
                    'triad_SO3_reference_sigma':args.orientation_start,'projectors':'same initial kinetic frame, no eigenaxis sign convention'},
        'controls':controls,'cases':summary,
        'limitations':['Clock-phase mirror equalities are imposed by the symmetric cubic ramp and are not independent physical return events.',
        'x is a single logistic coordinate, not a physical locus. Near-x does not imply near-(logrho1,logrho2,x).',
        'The 3D locus here is a declared coordinate projection only and normalized by case-specific coordinate spans.',
        'The triad projector distance is gauge-invariant to eigenvector signs in the declared common kinetic frame; its geometric meaning is model-dependent.',
        'Transported SO3 angle uses a sign-continuous eigenframe and an explicitly sampled cross connection; it is not physical body rotation.',
        'Results are finite-grid diagnostics, not a proof of repeated states, cubical packing, physical memory, or stability.',
        'No forced linkage is made to the autonomous seven-quarter-turn cubical construction.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--kind',choices=['original','autonomous','both'],default='both')
    p.add_argument('--ramp-values',nargs='+',type=float)
    p.add_argument('--samples',type=int,default=61)
    p.add_argument('--min-separation',type=float,default=.20)
    p.add_argument('--x-fraction',type=float,default=.10)
    p.add_argument('--locus-fraction',type=float,default=.20)
    p.add_argument('--span-floor',type=float,default=1e-12)
    p.add_argument('--orientation-start',type=float,default=.10)
    p.add_argument('--min-gap',type=float,default=1e-7)
    p.add_argument('--fail-fast',action='store_true')
    p.add_argument('--max-parent-regression',type=float,default=1e-7)
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
    if args.samples<21 or args.samples%2!=1:p.error('--samples odd >=21')
    if not .01<=args.orientation_start<=.5 or abs(args.orientation_start*(args.samples-1)-round(args.orientation_start*(args.samples-1)))>1e-10:
       p.error('--orientation-start requires a sampled normalized phase in [.01,.5]')
    run(args)
