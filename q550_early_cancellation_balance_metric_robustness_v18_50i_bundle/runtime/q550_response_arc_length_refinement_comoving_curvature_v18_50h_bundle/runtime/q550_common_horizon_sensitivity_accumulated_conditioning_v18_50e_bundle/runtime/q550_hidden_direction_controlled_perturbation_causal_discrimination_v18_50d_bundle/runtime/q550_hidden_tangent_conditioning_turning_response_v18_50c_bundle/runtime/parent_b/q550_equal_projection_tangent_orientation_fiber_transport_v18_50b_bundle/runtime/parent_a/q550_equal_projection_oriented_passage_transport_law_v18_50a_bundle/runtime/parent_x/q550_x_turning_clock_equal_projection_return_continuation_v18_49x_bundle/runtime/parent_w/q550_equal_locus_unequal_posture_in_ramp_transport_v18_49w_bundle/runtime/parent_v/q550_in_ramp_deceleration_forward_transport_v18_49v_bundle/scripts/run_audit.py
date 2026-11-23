#!/usr/bin/env python3
"""v18.49v — Observe the GENUINE 11D Q550 trajectory DURING the ramp.

Drive deceleration and material motion are distinct. The prescribed clock
sweeps +omega -> -omega; material motion is measured in explicitly declared
coordinates and fixed initial kinetic metric. No closure or material memory
is inferred from a nonzero movement, and a 10D spectral gap is required to
assign the triad's eigenprojectors.
"""
import argparse,csv,json,platform,sys,traceback
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.linalg import expm
from verify_v_parent import verify
from ramp_math import x_from_z,poly_sign,speed10,finite_motion,coordinate_gap
ROOT=Path(__file__).resolve().parents[1]

def emit_csv(name,rows):
    if not rows:return
    f=ROOT/'results'/name; f.parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with f.open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def run(args):
    pdir,pre,anc=verify()
    from parent_o_experiment import Experiment
    from frame_math import transport_frame
    from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
    from kinetic_metric import embedding_and_jac
    ex=Experiment(args)
    parent_hist=list((ROOT/'runtime/parent_u').rglob('physical_paths.npz'))
    parent_hist=[p for p in parent_hist if 'verified_sources/j/' in p.as_posix()]
    if len(parent_hist)!=1:raise RuntimeError('Historical Q550 source ambiguous')
    hist=np.load(parent_hist[0],allow_pickle=False)
    grouped=defaultdict(list)
    for i in range(len(hist['y'])):
        grouped[(str(hist['families'][i]),int(hist['seed_branches'][i]),str(hist['kappa_kind'][i]))].append(i)
    kinds=('original',) if args.smoke else ('original','autonomous') if args.kind=='both' else (args.kind,)
    ramps=args.ramp_values if args.ramp_values else ([.327375] if args.smoke else [.12,.327375] if args.focus else [.12,.24,.327375,.50])
    if any(r<.02 or r>1. for r in ramps):raise ValueError('Duration requires .02 <= r <= 1')
    forward_starts={}
    for kind in kinds:
        grp=sorted(next(v for (fam,branch,k),v in grouped.items() if fam.startswith('phaseblind') and branch==0 and k==kind),key=lambda j:float(hist['xi'][j]))
        forward_starts[kind]=np.asarray(hist['y'][grp[0]],float)
        yturn=ex.turning[kind]
        if not np.all(np.isfinite(yturn)):raise RuntimeError('Nonfinite turning state')
    sigma=np.linspace(0,1,args.samples)
    samples=[];cases=[];problems=[]
    controls={'max_11d_mechanical_ledger':0.,'max_in_ramp_energy_identity_residual':0.,
       'max_clock_command_difference':0.,'max_triad_generator_closure':0.,
       'max_cross_subspace_projector_derivative_error':0.,'min_spectral_gap':None,
       'forward_11d_regression':float(ex.regression)}
    for kind in kinds:
      kap=ex.ks[kind]
      for r in ramps:
        try:
            design=ex.original_ramp.Design('v_authentic_cubic','beta:2:2',float(r))
            back,err=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,kap,
                     ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
            if err>args.maximum_ledger_error:raise RuntimeError('Bad physical ledger')
            controls['max_11d_mechanical_ledger']=max(controls['max_11d_mechanical_ledger'],float(err))
            init=back(0.)[:11];Einit=ex.physical.energy(init,kap,ex.params)
            endpoints=[back(float(s*r)) for s in sigma]
            sp=finite_motion([y[:11] for y in endpoints])
            speeds=[];clock_times=[];triad_valid=[];triad_errors=[];triad_kcross=[]
            # Reuse precisely the original generator and fixed initial kinetic metric.
            def jac(y,k,p,sl):return ex.jet.structural_jet(y,kap,ex.params,ex.slope)[1]
            frame,frerr=transport_frame(back,kap,ex.params,ex.slope,jac,float(r),
                rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            _,J0=embedding_and_jac(init[:10],ex.params.m_x,1.)
            prev=None;Ucross=np.eye(10);start_axes=None;last_axes=None
            last_sigma=None;path_rotation=[];first_valid=None
            for i,(s,y) in enumerate(zip(sigma,endpoints)):
                t=float(s*r);st=y[:11];sign=float(ex.clock.cubic_clock_sign(t,design))
                prescribed=float(poly_sign([s])[0]); controls['max_clock_command_difference']=max(
                       controls['max_clock_command_difference'],abs(sign-prescribed))
                deriv=ex.physical.rhs_from_original(st,kap,ex.params,ex.slope,sign,ex.support,ex.audit)
                pwr=ex.physical.power_terms(st,kap,ex.params,ex.slope,sign)
                E=ex.physical.energy(st,kap,ex.params)
                ledger=float(E-Einit-sum(y[11:]))
                controls['max_in_ramp_energy_identity_residual']=max(controls['max_in_ramp_energy_identity_residual'],abs(ledger))
                x=x_from_z(st[8]);g=x*(1-x)
                locus_disp,posture_disp,xdisp=coordinate_gap(st,init)
                row={'kappa_kind':kind,'ramp_xi':float(r),'sigma':float(s),'return_time':t,
                  'clock_sign':sign,'clock_theta_rate':float(sign*ex.omega),
                  'theta_lift':float(st[10]),'theta_lift_change':float(st[10]-init[10]),
                  'material_10d_rate_norm':speed10(deriv),
                  'material_10d_coordinate_path':float(sp[i]),
                  'local_locus_logrho_gap':locus_disp,'local_locus_x_gap':xdisp,
                  'internal_posture_angle_gap':posture_disp,
                  'internal_angular_rate_norm':float(np.linalg.norm(deriv[[2,6]])),
                  'radial_log_rate_norm':float(np.linalg.norm(deriv[[0,4]])),
                  'x_rate':float(g*st[9]*2*np.pi*ex.slope/x),
                  'energy':float(E),'energy_change_from_turn':float(E-Einit),
                  'work_drive':float(y[11]),'damping_radial':float(y[12]),
                  'damping_x':float(y[13]),'source_x':float(y[14]),
                  'instant_power_drive':float(pwr[0]),'instant_power_total':float(sum(pwr)),
                  'energy_ledger_residual':ledger,
                  'triad_defined':0,'triad_relative_gap':None,'triad_internal_share':None,
                  'triad_cross_share':None,'triad_external_share':None,'triad_projector_speed':None,
                  'triad_rotation_from_first_valid_deg':None,'cross_connection_rot_deg':None,
                  'cross_transport_closure':None,'triad_error':None}
                speeds.append(row['material_10d_rate_norm'])
                # Spectral projectors are undefined exactly at t=0 (C=I).
                if i>0:
                    try:
                        field,Jmat,_=ex.jet.structural_jet(st,kap,ex.params,ex.slope)
                        _,J=embedding_and_jac(st,ex.params.m_x,1.)
                        Jdot=kinetic_frame_derivative(st,field,ex.params.m_x,1.,embedding_and_jac)
                        B,Bdot=deforming_frame(J,frame(t),J0,Jdot,Jmat[:10,:10])
                        spec=spectral_generator(B,Bdot,relative_gap_floor=args.min_gap)
                        P=spec['projectors'];K=spec['generator'];axes=spec['axes']
                        S=np.sum(P[[5,6,7]],axis=0);T=np.eye(10)-S
                        Ki=S@K@S;Kc=S@K@T+T@K@S;Ke=T@K@T
                        dS=K@S-S@K
                        er1=float(np.linalg.norm(K-Ki-Kc-Ke)/max(1.,np.linalg.norm(K)))
                        er2=float(np.linalg.norm(dS-(Kc@S-S@Kc)))
                        controls['max_triad_generator_closure']=max(controls['max_triad_generator_closure'],er1)
                        controls['max_cross_subspace_projector_derivative_error']=max(controls['max_cross_subspace_projector_derivative_error'],er2)
                        total=float(np.linalg.norm(K)**2)
                        if total<=1e-20:raise ValueError('Vanishing generator norm')
                        current_axes=axes[:,[5,6,7]].copy()
                        # An explicit SAME normalized-time reference for all grids,
                        # instead of an artificial moving first-valid point.
                        angle=None
                        if s>=args.orientation_start-1e-12:
                            if prev is not None:
                                h=t-prev['t']
                                mid=.5*(prev['Kc']+Kc)
                                Ucross=expm(h*mid)@Ucross
                                sign_fix=np.where(np.sum(prev['A']*current_axes,axis=0)<0,-1.,1.)
                                current_axes*=sign_fix[None,:]
                            if start_axes is None: start_axes=current_axes.copy();first_valid=float(s)
                            raw=start_axes.T@Ucross.T@current_axes
                            UU,sv,VV=np.linalg.svd(raw);Rot=UU@VV
                            # The orientation has an explicit initial sign convention.
                            if np.linalg.det(Rot)<0: UU[:,-1]*=-1;Rot=UU@VV
                            angle=float(np.degrees(np.arccos(np.clip((np.trace(Rot)-1)/2,-1,1))))
                            prev={'t':t,'A':current_axes,'Kc':Kc};last_axes=current_axes
                        row.update({'triad_defined':1,'triad_relative_gap':float(spec['min_relative_eigengap']),
                          'triad_internal_share':float(np.linalg.norm(Ki)**2/total),
                          'triad_cross_share':float(np.linalg.norm(Kc)**2/total),
                          'triad_external_share':float(np.linalg.norm(Ke)**2/total),
                          'triad_projector_speed':float(np.linalg.norm(dS)),
                          'triad_rotation_from_first_valid_deg':angle,
                          'cross_transport_closure':er2})
                        triad_valid.append(row)
                        controls['min_spectral_gap']=(float(spec['min_relative_eigengap']) if controls['min_spectral_gap'] is None
                            else min(controls['min_spectral_gap'],float(spec['min_relative_eigengap'])))
                    except (ValueError,np.linalg.LinAlgError,OverflowError) as e:
                        row['triad_error']=type(e).__name__+': '+str(e)
                        triad_errors.append({'kappa_kind':kind,'ramp_xi':r,'sigma':s,'message':row['triad_error']})
                        # Do not join a transport path across an invalid spectral section.
                        prev=None;Ucross=np.eye(10);start_axes=None;last_axes=None
                samples.append(row)
            # Duration-normalized clock phase excursion uses the exact lifted Theta.
            # Positive intrinsic transport is a measured 10D configuration path, not a proof of stable motion.
            signs=np.asarray([d['clock_sign'] for d in samples[-len(sigma):]])
            sample_speeds=np.asarray(speeds)
            speed_negative_fraction=float(np.mean(np.diff(sample_speeds)<0))
            atmid=next(d for d in samples[-len(sigma):] if abs(d['sigma']-.5)<1e-12)
            case={'kappa_kind':kind,'ramp_xi':float(r),'clock_start':float(signs[0]),
                'clock_middle':float(atmid['clock_sign']),'clock_end':float(signs[-1]),
                'theta_ramp_net_change':float(endpoints[-1][10]-init[10]),
                'theta_ramp_max_excursion':float(max(abs(y[10]-init[10]) for y in endpoints)),
                'full_10d_coordinate_path':float(sp[-1]),
                'full_10d_endpoint_displacement':float(np.linalg.norm(endpoints[-1][:10]-init[:10])),
                'rate_at_start':float(speeds[0]),'rate_at_zero_drive':float(atmid['material_10d_rate_norm']),
                'rate_at_end':float(speeds[-1]),'min_material_10d_rate':float(min(speeds)),
                'fraction_adjacent_speed_increments_negative':speed_negative_fraction,
                'total_energy_change':float(endpoints[-1][11]-endpoints[0][11]+endpoints[-1][12]-endpoints[0][12]+endpoints[-1][13]-endpoints[0][13]+endpoints[-1][14]-endpoints[0][14]),
                'mechanical_energy_delta':float(ex.physical.energy(endpoints[-1][:11],kap,ex.params)-Einit),
                'ramp_drive_work':float(endpoints[-1][11]),'ramp_radial_damping':float(endpoints[-1][12]),
                'ramp_x_damping':float(endpoints[-1][13]),'ramp_source_x':float(endpoints[-1][14]),
                'ramp_ledger_error':float(err),'defined_triad_samples':len(triad_valid),
                'undefined_triad_samples':len(sigma)-len(triad_valid),
                'final_valid_triad_angle_deg':float(triad_valid[-1]['triad_rotation_from_first_valid_deg']) if triad_valid else None,
                'last_triad_valid_sigma':float(triad_valid[-1]['sigma']) if triad_valid else None,
                'first_triad_valid_sigma':float(first_valid) if first_valid is not None else None,
                'min_triad_relative_gap':float(min(d['triad_relative_gap'] for d in triad_valid)) if triad_valid else None,
                'material_motion_while_clock_zero':bool(atmid['material_10d_rate_norm']>args.motion_floor),
                'closed_return_tested':False}
            cases.append(case)
            print('v18.49v',kind,'r=',r,'speed@clock0=',round(case['rate_at_zero_drive'],9),
                 'path=',round(case['full_10d_coordinate_path'],9),'triad=',len(triad_valid),flush=True)
        except Exception as e:
            if args.fail_fast:raise
            problems.append({'kappa_kind':kind,'ramp_xi':r,'error_type':type(e).__name__,
                 'error':str(e),'trace':traceback.format_exc(limit=4)})
            print('v18.49v CASE_FAIL',kind,r,str(e),flush=True)
    emit_csv('in_ramp_phase_resolved.csv',samples)
    emit_csv('in_ramp_case_summary.csv',cases)
    emit_csv('spectral_undefined_samples.csv',triad_errors)
    emit_csv('numerical_failures.csv',problems)
    if not cases:raise RuntimeError('No successful Q550 original physical returns')
    status='IN_RAMP_PHYSICAL_TRANSPORT_MEASURED_NOT_MATERIAL_MEMORY_CERTIFICATE'
    if problems:status+='__PARTIAL_CASES'
    report={'audit':'Q550 v18.49v — In-Ramp Deceleration & Forward Transport Audit',
       'status':status,'authentic_u_parent':anc,'in_ramp_time':'t=r*sigma, sigma in [0,1]',
       'control':'beta:2:2, clock_sign=1-2*(3 sigma^2-2 sigma^3)','orientation_reference_sigma':args.orientation_start,
       'counts':{'completed_return_integrations':len(cases),'failed_cases':len(problems),
                 'phase_samples':len(samples),'defined_triad_samples':sum(c['defined_triad_samples'] for c in cases)},
       'controls':controls,'cases':cases,
       'measurement_scope':{'material_speed':'Euclidean norm of original first ten dstate/dxi coordinates, excluding drive Theta and ledgers',
       'locus':'logrho1,logrho2 and logistic x; posture angles theta1,theta2',
       'spatial_distance':'NO dimensional physical-space metric assigned; 10D coordinate path is observer-defined',
       'drive_zero':'Zero of imposed drive clock sign, NOT guaranteed material standstill',
       'triad':'Eigenprojectors #6,#7,#8 in ORIGINAL initial return kinetic frame, only where spectrum is simple',
       'triad_rotation':'SO(3) from sign-aligned eigenaxes against discrete cross parallel transport, relative to an explicit fixed normalized-time spectral frame; not a physical rigid-body angle'},
       'limitations':['Ramps span declared finite durations only, no general deceleration law or threshold theorem.',
          'A monotonically decelerating drive does not imply monotonically decreasing material-coordinate speed.',
          'The original Q550 turn is an EXTERNALLY IMPOSED reversal of five velocities; no spontaneous physical reflection is asserted.',
          'The ratio and path lengths depend on the declared coordinate norm, and the triad depends on the specified kinetic metric.',
          'Eigenprojectors at t=0 are undefined because the material Cauchy–Green tensor is degenerate; no orientation is fabricated there.',
          'Triad angle approximated from sampled cross-connection; run sampling refinement to test its numerical convergence.',
          'Work, damping, and source terms are an exact ledger of the model; they do not imply conservation of mechanical energy.',
          'No return-to-same-state criterion, material memory or physical torsion has been certified.',
          'The separate autonomous cubical phase/quadrant reading is not automatically assigned to this Q550 dynamic.' ]}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
        'numpy':np.__version__,'scipy':__import__('scipy').__version__,'samples_per_ramp':len(sigma)},indent=2)+'\n')
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--focus',action='store_true')
    parser.add_argument('--kind',choices=['original','autonomous','both'],default='both')
    parser.add_argument('--ramp-values',type=float,nargs='+')
    parser.add_argument('--samples',type=int,default=61)
    parser.add_argument('--orientation-start',type=float,default=.1)
    parser.add_argument('--min-gap',type=float,default=1e-7)
    parser.add_argument('--motion-floor',type=float,default=1e-9)
    parser.add_argument('--fail-fast',action='store_true')
    parser.add_argument('--rtol',type=float,default=3e-12)
    parser.add_argument('--atol',type=float,default=3e-13)
    parser.add_argument('--max-step',type=float,default=.025)
    parser.add_argument('--frame-rtol',type=float,default=8e-11)
    parser.add_argument('--frame-atol',type=float,default=8e-13)
    parser.add_argument('--frame-max-step',type=float,default=.008)
    parser.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    parser.add_argument('--maximum-regression',type=float,default=1e-7)
    parser.add_argument('--maximum_parent_share_difference',type=float,default=2e-6)
    parser.add_argument('--max_generator_identity_error',type=float,default=1e-7)
    args=parser.parse_args()
    if args.samples<11 or args.samples%2==0:parser.error('--samples must be odd >= 11')
    if not .01<=args.orientation_start<=.75:parser.error('orientation-start outside [.01,.75]')
    if abs(args.orientation_start*(args.samples-1)-round(args.orientation_start*(args.samples-1)))>1e-10:parser.error('orientation-start must fall exactly on the uniform sigma grid')
    run(args)
