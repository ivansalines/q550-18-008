#!/usr/bin/env python3
"""v18.49m — authenticated Q550 covariant projector generator and strain-rate audit.

True 11D return trajectories and 10x10 tangent frame, generated from the
original source ancestry. No interpolation-only surrogate for the dynamics.
An initial flat kinetic embedding with tau=1 defines the fixed material frame.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
from collections import defaultdict
from pairwise_math import PAIRS,pair_spectrum,shapley_pair_attribution,gap_only_and_num_only
import numpy as np
from verify_parent import verify,dynamic
from frame_math import transport_frame
from kinetic_metric import embedding_and_jac
from clock_math import projector_speed,projector_rates
from generator_math import (kinetic_frame_derivative,deforming_frame,spectral_generator,
                            log_strain_sum_rule)
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)
Q=np.linspace(.35,.65,121)
TARGETS=(1,3,8,10)

def write_csv(file,rows):
    p=ROOT/'results'/file
    if not rows:raise RuntimeError('Empty rows '+file)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    pk,pj,i,h,g,f,e,d,c,b,a,z,y,j,provenance=verify()
    sys.path[:0]=[str(c/'reference'),str(c/'scripts')]
    physical=dynamic(c/'reference/physical_math.py','m_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','m_original_ramp')
    original=dynamic(c/'reference/y_original_run_audit.py','m_original_y_audit')
    jet=dynamic(c/'reference/structural_jet.py','m_original_structural_jet')
    support_candidates=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_candidates)!=1:raise RuntimeError('Ambiguous historical original support')
    support=dynamic(support_candidates[0],'m_original_support')
    audit=dynamic(support_candidates[0].parent/'test_support_mobius_monodromy_audit.py','m_original_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    historical=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(historical['kappa_original']),'autonomous':float(historical['kappa_autonomous'])}
    speed=float(history['clock_speed']);slope=speed/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for n in range(len(history['y'])):
        groups[(str(history['families'][n]),int(history['seed_branches'][n]),str(history['kappa_kind'][n]))].append(n)
    source_old={}
    with (pk/'results/physical_sources_clockmatched.csv').open(newline='') as f0:
        for r in csv.DictReader(f0):
            source_old[(r['kappa_kind'],round(float(r['ramp_xi']),6),round(float(r['phase_q']),6))]=r
    p_old={}
    with (pk/'results/principal_projector_transport.csv').open(newline='') as f0:
        for r in csv.DictReader(f0):
            p_old[(r['kappa_kind'],round(float(r['ramp_xi']),6),round(float(r['phase_q']),6),int(r['axis_rank']))]=r
    rows=[];modes=[];summaries=[];pair_rows=[];pair_compare=[];pair_summary=[];tests={key:0. for key in ('forward_regression','log_volume_vs_parent','generator_vs_fd_projector',
                 'generator_vs_parent_speed','occupation_vs_parent','projector_closure','strain_logvolume_identity',
                 'c_rate_vs_finite_difference','sigma_rate_vs_finite_difference',
                 'source_vs_material_volume_rate','projector_rate_vs_fd','fixed_orthogonal_gauge',
                 'pair_frobenius_identity','pair_shapley_closure','pair_sign_independence','pair_orthogonal_gauge')}
    gaps=[];integrations={'physical_11D':0,'tangent_10D':0}
    for kind in ('original','autonomous'):
        inds=sorted(next(vals for (fam,br,k),vals in groups.items() if fam.startswith('phaseblind') and br==0 and k==kind),key=lambda n:float(history['xi'][n]))
        kap=kappas[kind];seed=history['y'][inds[0]].astype(float)
        forward,_=original.integrate(physical,ramp,support,audit,kap,params,slope,speed,seed,args)
        integrations['physical_11D']+=1
        tests['forward_regression']=max(tests['forward_regression'],max(float(np.linalg.norm(forward(q)[:11]-history['y'][n])) for q,n in zip(np.linspace(0,1,41),inds)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        for rv in RAMPS:
            back,_=original.integrate(physical,ramp,support,audit,kap,params,slope,speed,turning,args,design=ramp.Design('v18_49l','smoothstep',rv))
            integrations['physical_11D']+=1
            def local_jet(st):return jet.structural_jet(st,kap,params,slope)
            F,_=transport_frame(back,kap,params,slope,lambda st,k,p,sl:local_jet(st)[1],1.+rv,
                                rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            integrations['tangent_10D']+=1
            start=back(0.)[:10];_,J0=embedding_and_jac(start,params.m_x,1.)
            invJ0=np.linalg.inv(J0)
            outputs=[];dirs=[];pair_profiles=[]
            for qi,q in enumerate(Q):
                t=float(rv+q);st=back(t)[:11];fw=forward(1.-float(q))[:11]
                flow,Jmat,_=local_jet(st)
                H,J=embedding_and_jac(st,params.m_x,1.)
                Jdot=kinetic_frame_derivative(st,flow,params.m_x,1.,embedding_and_jac)
                Bt,Btdot=deforming_frame(J,F(t),J0,Jdot,Jmat[:10,:10])
                out=spectral_generator(Bt,Btdot)
                gaps.append(out['min_relative_eigengap'])
                pairs=pair_spectrum(out)
                pair_profiles.append(pairs)
                tests['pair_frobenius_identity']=max(tests['pair_frobenius_identity'],abs(pairs['total_K_frob_sq']-out['generator_frobenius']**2))
                for m_idx,(a_idx,b_idx) in enumerate(PAIRS):
                    pair_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                        'axis_rank_a':a_idx+1,'axis_rank_b':b_idx+1,
                        'numerator_abs':float(pairs['numerator'][m_idx]),
                        'lambda_gap':float(pairs['gap'][m_idx]),
                        'omega_abs':float(pairs['omega_abs'][m_idx]),
                        'generator_norm_sq_contribution':float(pairs['pair_K_frob_sq'][m_idx]),
                        'generator_fraction_sq':float(pairs['pair_K_frob_sq'][m_idx]/pairs['total_K_frob_sq'])})
                Hfw,_=embedding_and_jac(fw,params.m_x,1.)
                delta=np.linalg.solve(Bt,H-Hfw)
                u=delta/np.linalg.norm(delta)
                dirs.append(u);outputs.append(out)
                key=(kind,round(rv,6),round(float(q),6))
                prev=source_old[key]
                tests['log_volume_vs_parent']=max(tests['log_volume_vs_parent'],abs(float(np.linalg.slogdet(Bt)[1])-float(prev['log_kinetic_volume'])))
                tests['source_vs_material_volume_rate']=max(tests['source_vs_material_volume_rate'],abs(out['log_volume_rate']-float(prev['kinetic_volume_source'])))
                tests['projector_closure']=max(tests['projector_closure'],out['projector_reconstruction_error'])
                tests['strain_logvolume_identity']=max(tests['strain_logvolume_identity'],abs(log_strain_sum_rule(out)))
                if qi==60 and rv==.3:
                    rng=np.random.default_rng(20)
                    rot,_=np.linalg.qr(rng.normal(size=(10,10)))
                    from generator_math import constant_orthogonal_gauge
                    b_g,bd_g=constant_orthogonal_gauge(Bt,Btdot,rot)
                    gg=spectral_generator(b_g,bd_g)
                    tests['fixed_orthogonal_gauge']=max(tests['fixed_orthogonal_gauge'],float(np.linalg.norm(gg['generator']-rot@out['generator']@rot.T)))
                    testp=pair_spectrum(gg)
                    tests['pair_orthogonal_gauge']=max(tests['pair_orthogonal_gauge'],float(np.max(np.abs(testp['pair_K_frob_sq']-pairs['pair_K_frob_sq']))))
                    # Explicitly reverse the signs of four eigenvectors; squared
                    # coupling amplitudes must not change.
                    flip=out['axes'].copy();flip[:,[1,3,7,8]]*=-1
                    _MM=flip.T@out['Cdot']@flip
                    flipnum=np.array([abs(float(_MM[b,a])) for a,b in PAIRS])
                    tests['pair_sign_independence']=max(tests['pair_sign_independence'],float(np.max(np.abs(flipnum-pairs['numerator']))))
                rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'phase_q':float(q),
                    'log_volume_rate':out['log_volume_rate'],'log_volume':float(np.linalg.slogdet(Bt)[1]),
                    'kinetic_volume_source_parent':float(prev['kinetic_volume_source']),
                    'strain_trace_spatial':float(np.trace(out['spatial_strain_rate'])),
                    'projector_generator_norm':out['generator_frobenius'],
                    'aggregate_projector_angular_speed':float(np.linalg.norm(out['speed'])),
                    'offdiagonal_Cdot_fraction':out['offdiagonal_strain_fraction'],
                    'commutator_fraction':out['commutator_fraction'],
                    'min_relative_eigengap':out['min_relative_eigengap'],
                    'max_principal_stretch':float(out['sigma'][0]),
                    'min_principal_stretch':float(out['sigma'][-1]),
                    'max_principal_stretch_rate':float(out['sigma_rate'][0]),
                    'min_principal_stretch_rate':float(out['sigma_rate'][-1]),
                    'mean_principal_stretch_rate':float(np.mean(out['sigma_rate']))})
                for rank in TARGETS:
                    aa=rank-1;p=out['projectors'][aa]
                    frac=float(u@p@u)
                    keyp=key+(rank,)
                    old=p_old[keyp]
                    tests['generator_vs_parent_speed']=max(tests['generator_vs_parent_speed'],abs(out['speed'][aa]-float(old['projector_line_speed_rad_per_q'])))
                    tests['occupation_vs_parent']=max(tests['occupation_vs_parent'],abs(frac-float(old['occupation'])))
                    modes.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),'axis_rank':rank,
                        'stretch':float(out['sigma'][aa]),'stretch_derivative':float(out['sigma_rate'][aa]),
                        'stretch_log_derivative':float(out['sigma_rate'][aa]/out['sigma'][aa]),
                        'instantaneous_projector_speed':float(out['speed'][aa]),
                        'projector_occupation':frac,
                        'instantaneous_projector_rotation_contribution':None,
                        'material_direction_contribution':None})
            # Exactly partition the rise in ||K||_F^2 over the last 0.15 q
            # into numerator and inverse-gap effects, with BOTH endpoint cross-orders.
            before,after=pair_profiles[60],pair_profiles[120]
            attribution=shapley_pair_attribution(before,after)
            tests['pair_shapley_closure']=max(tests['pair_shapley_closure'],attribution['closure_error'],
                abs(float(np.sum(attribution['delta_pair_norm_sq']))-(after['total_K_frob_sq']-before['total_K_frob_sq'])))
            cf=gap_only_and_num_only(before,after)
            total_shift=after['total_K_frob_sq']-before['total_K_frob_sq']
            pair_summary.append({'kappa_kind':kind,'ramp_xi':rv,
                'generator_norm_at_q050':cf['base'],'generator_norm_at_q065':cf['both'],
                'generator_norm_if_only_numerator_changes':cf['numerator_only'],
                'generator_norm_if_only_gap_changes':cf['gap_only'],
                'delta_generator_norm_sq':total_shift,
                'numerator_attribution_norm_sq':float(np.sum(attribution['numerator_attribution'])),
                'gap_attribution_norm_sq':float(np.sum(attribution['gap_attribution'])),
                'relative_numerator_share_signed':float(np.sum(attribution['numerator_attribution'])/total_shift),
                'relative_gap_share_signed':float(np.sum(attribution['gap_attribution'])/total_shift),
                'top5_final_pair_share':float(np.sort(after['pair_K_frob_sq'])[-5:].sum()/after['total_K_frob_sq']),
                'leading_pair_final':f"{PAIRS[int(np.argmax(after['pair_K_frob_sq']))][0]+1}-{PAIRS[int(np.argmax(after['pair_K_frob_sq']))][1]+1}"})
            for ind,(i,jj) in enumerate(PAIRS):
                pair_compare.append({'kappa_kind':kind,'ramp_xi':rv,'axis_rank_a':i+1,'axis_rank_b':jj+1,
                    'numerator_q050':float(before['numerator'][ind]),
                    'numerator_q065':float(after['numerator'][ind]),
                    'gap_q050':float(before['gap'][ind]),'gap_q065':float(after['gap'][ind]),
                    'omega_q050':float(before['omega_abs'][ind]),'omega_q065':float(after['omega_abs'][ind]),
                    'delta_pair_generator_norm_sq':float(attribution['delta_pair_norm_sq'][ind]),
                    'numerator_attribution_norm_sq':float(attribution['numerator_attribution'][ind]),
                    'gap_attribution_norm_sq':float(attribution['gap_attribution'][ind]),
                    'pair_final_share':float(after['pair_K_frob_sq'][ind]/after['total_K_frob_sq'])})
            # Independent finite differences in phase of B^T B and exact rank-one projectors.
            uu=np.asarray(dirs)
            axes=np.stack([out['axes'] for out in outputs]);Qnp=Q
            projector_fd,dp_fd,v_fd=projector_speed(Qnp,axes)
            du_fd=np.gradient(uu,Qnp,axis=0,edge_order=2)
            C=np.stack([out['C'] for out in outputs]);Cdiff=np.gradient(C,Qnp,axis=0,edge_order=2)
            sigma=np.stack([out['sigma'] for out in outputs]);sdiff=np.gradient(sigma,Qnp,axis=0,edge_order=2)
            index={(r['kappa_kind'],r['ramp_xi'],r['phase_q'],r['axis_rank']):r for r in modes[-len(Q)*len(TARGETS):]}
            for qi,q in enumerate(Q):
                if 2<=qi<len(Q)-2:
                    out=outputs[qi]
                    tests['c_rate_vs_finite_difference']=max(tests['c_rate_vs_finite_difference'],float(np.linalg.norm(out['Cdot']-Cdiff[qi])/max(1,np.linalg.norm(out['Cdot']))))
                    tests['sigma_rate_vs_finite_difference']=max(tests['sigma_rate_vs_finite_difference'],float(np.max(np.abs(out['sigma_rate']-sdiff[qi]))))
                    tests['generator_vs_fd_projector']=max(tests['generator_vs_fd_projector'],float(np.max(np.abs(out['projector_dot']-dp_fd[qi]))))
                    tests['projector_rate_vs_fd']=max(tests['projector_rate_vs_fd'],float(np.max(np.abs(out['speed']-v_fd[qi]))))
                out=outputs[qi]
                for rank in TARGETS:
                    n=rank-1;P=out['projectors'][n];Pd=out['projector_dot'][n];u=uu[qi];up=du_fd[qi]
                    rr=index[(kind,rv,float(q),rank)]
                    rr['instantaneous_projector_rotation_contribution']=float(u@Pd@u)
                    rr['material_direction_contribution']=float(2*up@P@u)
            # A direct measure of the relative balance of rotational and stretching rates
            # is a clock-matched *comparison*, not a coupling or conservation law.
            sel=outputs[60]
            s=float(np.mean([o['generator_frobenius'] for o in outputs]))
            stretch=float(np.mean([np.linalg.norm(o['sigma_rate']/o['sigma']) for o in outputs]))
            off=float(np.mean([o['offdiagonal_strain_fraction'] for o in outputs]))
            summaries.append({'kappa_kind':kind,'ramp_xi':rv,'generator_norm_at_q050':sel['generator_frobenius'],
                'strain_lograte_norm_at_q050':float(np.linalg.norm(sel['sigma_rate']/sel['sigma'])),
                'generator_norm_mean_q035_to_065':s,'strain_lograte_norm_mean_q035_to_065':stretch,
                'offdiag_strain_fraction_mean':off,'log_volume_rate_at_q050':sel['log_volume_rate'],
                'min_relative_eigengap':float(min(o['min_relative_eigengap'] for o in outputs))})
            print(f'v18.49m {kind} ramp={rv:.6f}: generator={sel["generator_frobenius"]:.7g}, ' +
                  f'log-strain-rate={np.linalg.norm(sel["sigma_rate"]/sel["sigma"]):.7g}',flush=True)
    write_csv('covariant_generator_phase_profiles.csv',rows)
    write_csv('principal_strain_projector_phase_profiles.csv',modes)
    write_csv('ramp_kappa_summary.csv',summaries)
    write_csv('pairwise_generator_phase_profiles.csv',pair_rows)
    write_csv('pairwise_shapley_comparison.csv',pair_compare)
    write_csv('pairwise_case_summary.csv',pair_summary)
    report={'version':'v18.49m','classification':'AUTHENTIC_Q550_COVARIANT_TENSOR_DIAGNOSTIC_NOT_METRIC_UNIVERSAL_CERTIFICATE',
        'upstream':provenance,'kinetic_tau':1.,'phase_interval':[float(Q[0]),float(Q[-1])],
        'phase_grid_points':len(Q),'kappas':kappas,'ramp_set':list(RAMPS),'physical_integrations':integrations['physical_11D'],
        'tangent_frame_integrations':integrations['tangent_10D'],'minimum_relative_eigen_gap':float(min(gaps)),
        'test_max_errors':tests,'case_summary':summaries,'pairwise_case_summary':pair_summary,
        'pair_count':45,'attribution_interval_q':[0.5,0.65],
        'scientific_limits':['Generator is covariant under constant orthogonal gauge in the declared kinetic embedding.',
        'Time-dependent gauge rotations require a connection term; naive derivatives do not transform tensorially.',
        'Changing the kinetic scale or metric changes strain and generator values.',
        'Finite-difference direction between paths is not a nonlinear covariant separation vector.',
        '45 rank-pair attributions are exact algebraic squared-norm decompositions, not dynamic causes or energy transfers.',
        'The basis is ordered instantaneously by eigenvalue; rank crossings or degeneracy would invalidate rank-pair comparisons.',
        'Changing ramp shape is not tested; only six durations of the inherited smoothstep command are compared.',
        'No causality, conservation, physical energy transfer, holonomy, or coordinate-free absolute rotation is claimed.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,
        'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rtol',type=float,default=3e-12)
    p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    print(json.dumps(run(p.parse_args())['test_max_errors'],indent=2))
