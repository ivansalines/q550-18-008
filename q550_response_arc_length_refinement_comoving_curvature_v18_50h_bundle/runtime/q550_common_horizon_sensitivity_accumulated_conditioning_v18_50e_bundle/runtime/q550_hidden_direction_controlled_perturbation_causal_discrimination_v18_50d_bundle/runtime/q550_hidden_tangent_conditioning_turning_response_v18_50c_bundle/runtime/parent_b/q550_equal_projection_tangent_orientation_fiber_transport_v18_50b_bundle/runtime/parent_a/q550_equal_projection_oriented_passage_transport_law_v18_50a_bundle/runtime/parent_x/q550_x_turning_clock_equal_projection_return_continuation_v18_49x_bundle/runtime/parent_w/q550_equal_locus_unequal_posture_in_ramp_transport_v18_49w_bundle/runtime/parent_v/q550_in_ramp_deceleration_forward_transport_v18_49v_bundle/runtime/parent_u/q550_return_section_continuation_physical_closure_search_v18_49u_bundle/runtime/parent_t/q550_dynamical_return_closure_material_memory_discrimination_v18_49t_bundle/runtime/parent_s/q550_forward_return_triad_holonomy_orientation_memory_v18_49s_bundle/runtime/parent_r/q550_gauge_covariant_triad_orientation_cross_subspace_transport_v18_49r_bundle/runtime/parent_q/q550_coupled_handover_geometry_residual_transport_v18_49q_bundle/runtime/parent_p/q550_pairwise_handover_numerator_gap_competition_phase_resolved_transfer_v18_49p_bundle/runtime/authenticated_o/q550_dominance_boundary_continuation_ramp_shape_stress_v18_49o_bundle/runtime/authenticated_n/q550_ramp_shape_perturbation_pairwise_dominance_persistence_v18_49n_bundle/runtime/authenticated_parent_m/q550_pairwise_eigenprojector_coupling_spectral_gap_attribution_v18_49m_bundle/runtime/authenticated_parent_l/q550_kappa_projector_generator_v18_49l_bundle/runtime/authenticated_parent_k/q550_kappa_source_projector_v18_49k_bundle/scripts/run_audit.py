#!/usr/bin/env python3
"""Q550 v18.49k — Source-Zero & Principal-Projector Clock-Transport Audit.

Rebuilds the historical Q550 11D forward/return trajectories and 10D
variational equations from immutable authenticated v18.49j ancestry.
Measures genuine sign-bracketed local volume-source difference roots,
transport of eigenprojectors in a declared fixed kinetic frame, half-turn
clock markers, counterfactual volume forms, and ramp-permutation controls.
No causal or observer-universal claim is inferred from event alignment.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from verify_parent import verify,dynamic
from frame_math import transport_frame
from kinetic_metric import embedding_and_jac
from strain_math import factor,nearby_eigen_gaps
from source_math import rate_split,log_density_gradient
from clock_math import projector_rates,projector_speed,half_turn_clock,smooth_root,exact_permutation_p
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)
QGRID=np.linspace(.35,.65,121)
ALPHAS=(-1.,-.1,-.01,-.001,0.,.001,.01,.1,1.)
TARGETS=(1,3,8,10)

def write_csv(name,rows):
    p=ROOT/'results'/name;p.parent.mkdir(parents=True,exist_ok=True)
    if not rows:raise RuntimeError('Empty output '+name)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    parent,i,h,g,f,e,d,c,b,a,z,y,j,provenance=verify()
    sys.path[:0]=[str(c/'reference'),str(c/'scripts')]
    physical=dynamic(c/'reference/physical_math.py','k_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','k_original_ramp')
    original=dynamic(c/'reference/y_original_run_audit.py','k_original_y_audit')
    jet=dynamic(c/'reference/structural_jet.py','k_original_structural_jet')
    support_candidates=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_candidates)!=1:raise RuntimeError('Original support module ambiguity')
    support=dynamic(support_candidates[0],'k_original_support')
    audit=dynamic(support_candidates[0].parent/'test_support_mobius_monodromy_audit.py','k_original_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    historical=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(historical['kappa_original']),'autonomous':float(historical['kappa_autonomous'])}
    speed=float(history['clock_speed']);slope=speed/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for n in range(len(history['y'])):
        groups[(str(history['families'][n]),int(history['seed_branches'][n]),str(history['kappa_kind'][n]))].append(n)
    parent_sources={}
    with (parent/'results/instantaneous_volume_sources.csv').open(newline='') as fh:
        for r in csv.DictReader(fh):
            parent_sources[(r['kappa_kind'],round(float(r['ramp_xi']),6),round(float(r['phase_q']),6))]=r
    parent_occ={}
    with (parent/'results/ten_axis_occupation_and_split.csv').open(newline='') as fh:
        for r in csv.DictReader(fh):
            parent_occ[(r['kappa_kind'],round(float(r['ramp_xi']),6),round(float(r['phase_q']),6),int(r['axis_rank']))]=r
    trajectory_rows=[];projector_rows=[];roots_rows=[];marker_rows=[];lag_rows=[];permutation_rows=[]
    source_history={};markers={};min_gap=1.;regression={'historical_forward':0.,'parent_source':0.,'parent_occupation':0.,
           'occupation_derivative_balance':0.,'source_identity':0.,'projector_sum':0.,'explicit_kappa_trace':0.,
            'projector_halfturn_coarse_grid_difference_q':0.}
    integrals={'physical_11D':0,'tangent_10D':0}
    for kind in (('original',) if args.smoke else ('original','autonomous')):
        inds=sorted(next(vals for (fam,br,k),vals in groups.items() if fam.startswith('phaseblind') and br==0 and k==kind),key=lambda n:float(history['xi'][n]))
        kap=kappas[kind];seed=history['y'][inds[0]].astype(float)
        forward,_=original.integrate(physical,ramp,support,audit,kap,params,slope,speed,seed,args)
        integrals['physical_11D']+=1
        regression['historical_forward']=max(regression['historical_forward'],max(float(np.linalg.norm(forward(q)[:11]-history['y'][n])) for q,n in zip(np.linspace(0,1,41),inds)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        for rv in ((.3,) if args.smoke else RAMPS):
            back,_=original.integrate(physical,ramp,support,audit,kap,params,slope,speed,turning,args,
                design=ramp.Design('v18_49k','smoothstep',rv))
            integrals['physical_11D']+=1
            def local_jet(st):return jet.structural_jet(st,kap,params,slope)
            F,_=transport_frame(back,kap,params,slope,lambda st,k,p,sl:local_jet(st)[1],1.+rv,
                                  rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            integrals['tangent_10D']+=1
            start=back(0.)[:10];_,J0=embedding_and_jac(start,params.m_x,1.)
            directions=[];axes=[];sigmas=[];srcs=[];extra=[];paths=[]
            for qi,q in enumerate(QGRID):
                t=float(rv+q);state=back(t)[:11];fw=forward(1.-float(q))[:11]
                flow,JJ,_=local_jet(state)
                div,density=rate_split(state,flow,JJ)
                extra_a=float(flow[0]-flow[4])
                _,J1=embedding_and_jac(state,params.m_x,1.)
                B=J1@F(t)@np.linalg.inv(J0)
                sig,axis,sgn,log_volume=factor(B)
                H1,_=embedding_and_jac(state,params.m_x,1.)
                Hfw,_=embedding_and_jac(fw,params.m_x,1.)
                gap=np.linalg.solve(B,H1-Hfw)
                norm=float(np.linalg.norm(gap))
                if norm<1e-14:raise RuntimeError('Zero material gap')
                u=gap/norm
                directions.append(u);axes.append(axis);sigmas.append(sig);srcs.append((div,density,div+density));extra.append(extra_a)
                paths.append((state,flow))
                # Historical J regression at the exactly shared 61 grid points.
                key=(kind,round(rv,6),round(float(q),6))
                if key in parent_sources:
                    old=parent_sources[key]
                    regression['parent_source']=max(regression['parent_source'],abs(div-float(old['div_solver_trace'])),
                        abs(density-float(old['kinetic_density_derivative'])))
                cjet=jet.coupling_jet(state,params)[1]
                regression['explicit_kappa_trace']=max(regression['explicit_kappa_trace'],abs(float(np.trace(cjet[:10,:10]))))
                trajectory_rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'phase_q':float(q),
                    'return_clock_t':t,'solver_trace':div,'kinetic_density_rate':density,
                    'kinetic_volume_source':div+density,'alternate_density_rate_coefficient':extra_a,
                    'material_gap_norm':norm,'log_kinetic_volume':log_volume})
                min_gap=min(min_gap,float(np.min(nearby_eigen_gaps(sig))))
            directions=np.asarray(directions);axes=np.asarray(axes);srcs=np.asarray(srcs);extra=np.asarray(extra)
            occup,rdir,rproj,speeds=projector_rates(QGRID,directions,axes)
            all_speed=np.sqrt(np.einsum('nk,nk->n',speeds,speeds))
            o_prime=np.gradient(occup,QGRID,axis=0,edge_order=2)
            regression['occupation_derivative_balance']=max(regression['occupation_derivative_balance'],float(np.max(np.abs(o_prime[2:-2]-rdir[2:-2]-rproj[2:-2]))))
            regression['projector_sum']=max(regression['projector_sum'],float(np.max(np.abs(occup.sum(axis=1)-1))))
            for qi,q in enumerate(QGRID):
                for axis_rank in range(10):
                    key=(kind,round(rv,6),round(float(q),6),axis_rank+1)
                    if key in parent_occ:
                        regression['parent_occupation']=max(regression['parent_occupation'],abs(occup[qi,axis_rank]-float(parent_occ[key]['occupation'])))
                    if axis_rank+1 in TARGETS:
                        projector_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                           'axis_rank':axis_rank+1,'occupation':float(occup[qi,axis_rank]),
                           'rate_direction':float(rdir[qi,axis_rank]),'rate_projector':float(rproj[qi,axis_rank]),
                           'rate_total':float(rdir[qi,axis_rank]+rproj[qi,axis_rank]),
                           'projector_line_speed_rad_per_q':float(speeds[qi,axis_rank]),
                           'full_spectral_angular_speed_rad_per_q':float(all_speed[qi])})
            coarse_P,coarse_dP,coarse_v=projector_speed(QGRID[::2],axes[::2])
            for rank in TARGETS:
                median,turn=half_turn_clock(QGRID,speeds[:,rank-1]);
                coarse_median,_=half_turn_clock(QGRID[::2],coarse_v[:,rank-1])
                regression['projector_halfturn_coarse_grid_difference_q']=max(regression['projector_halfturn_coarse_grid_difference_q'],abs(median-coarse_median))
                markers[(kind,rv,rank)]={'q50':median,'turn_rad':turn}
                marker_rows.append({'kappa_kind':kind,'ramp_xi':rv,'axis_rank':rank,
                     'half_turn_clock_q':median,'integrated_projector_turn_rad':turn,
                     'phase_grid_n':len(QGRID),'kinetic_tau':1.})
            mid,turn=half_turn_clock(QGRID,all_speed)
            coarse_combined=np.sqrt(np.einsum('nk,nk->n',coarse_v,coarse_v))
            coarse_combined_mid,_=half_turn_clock(QGRID[::2],coarse_combined)
            regression['projector_halfturn_coarse_grid_difference_q']=max(regression['projector_halfturn_coarse_grid_difference_q'],abs(mid-coarse_combined_mid))
            markers[(kind,rv,0)]={'q50':mid,'turn_rad':turn}
            marker_rows.append({'kappa_kind':kind,'ramp_xi':rv,'axis_rank':0,
                 'half_turn_clock_q':mid,'integrated_projector_turn_rad':turn,
                 'phase_grid_n':len(QGRID),'kinetic_tau':1.})
            source_history[(kind,rv)]={'source':srcs,'extra':extra}
            print(f'v18.49k {kind} ramp={rv:.6f} all-projector half-turn={mid:.6f} min-relative-gap={min_gap:.3e}',flush=True)
    for rv in ((.3,) if args.smoke else RAMPS):
        if args.smoke:continue
        os=source_history[('original',rv)];au=source_history[('autonomous',rv)]
        delta=au['source']-os['source'];delta_extra=au['extra']-os['extra']
        for alpha in ALPHAS:
            signal=delta[:,2]+alpha*delta_extra
            zero,count=smooth_root(QGRID,signal)
            # An unbracketed root is NOT inferred from an interpolation extrapolation.
            roots_rows.append({'ramp_xi':rv,'alpha':alpha,'root_count':count,
                'clock_source_zero_q':zero,'root_status':'ONE_BRACKETED' if count==1 else ('NONE' if count==0 else 'MULTIPLE'),
                'source_at_q035':float(signal[0]),'source_at_q065':float(signal[-1]),
                'counterfactual_form':'exp(alpha*(l1-l2))*kinetic_volume'})
            for kind in ('original','autonomous'):
                for rank in (0,1,3,8,10):
                    marker=markers[(kind,rv,rank)]
                    lag_rows.append({'ramp_xi':rv,'alpha':alpha,'kappa_kind':kind,'axis_rank':rank,
                        'source_zero_q':zero,'projector_half_turn_q':marker['q50'],
                        'lag_projector_minus_source_q':marker['q50']-zero if np.isfinite(zero) else float('nan'),
                        'projector_turn_rad':marker['turn_rad'],'root_count':count})
        for qi,q in enumerate(QGRID):
            regression['source_identity']=max(regression['source_identity'],abs(delta[qi,0]+delta[qi,1]-delta[qi,2]))
    if not args.smoke:
        for rank in (0,1,3,8,10):
            roots=np.array([next(r['clock_source_zero_q'] for r in roots_rows if r['ramp_xi']==rv and r['alpha']==0.) for rv in RAMPS])
            for kind in ('original','autonomous'):
                q50=np.array([markers[(kind,rv,rank)]['q50'] for rv in RAMPS])
                correlation,pval=exact_permutation_p(roots,q50)
                # Trend-control: report slopes vs ramp separately; raw significance
                # is not interpreted as causal once both events share the ramp trend.
                rvs=np.asarray(RAMPS)
                slope_root=float(np.polyfit(rvs,roots,1)[0]);slope_projector=float(np.polyfit(rvs,q50,1)[0])
                permutation_rows.append({'axis_rank':rank,'kappa_kind':kind,'root_phase_alpha':0,
                     'pearson_r':correlation,'exhaustive_ramp_permutation_p_two_sided':pval,
                     'root_ramp_slope':slope_root,'projector_ramp_slope':slope_projector,
                     'mean_clock_lag_q':float(np.mean(q50-roots)),
                     'std_clock_lag_q':float(np.std(q50-roots,ddof=1))})
    write_csv('physical_sources_clockmatched.csv',trajectory_rows)
    write_csv('principal_projector_transport.csv',projector_rows)
    write_csv('source_zero_counterfactual_roots.csv',roots_rows if roots_rows else [{'mode':'smoke','source_zero_q':float('nan')}])
    write_csv('principal_projector_halfturn_markers.csv',marker_rows)
    write_csv('clock_lag_and_volume_form_controls.csv',lag_rows if lag_rows else [{'mode':'smoke','lag':float('nan')}])
    write_csv('ramp_permutation_controls.csv',permutation_rows if permutation_rows else [{'mode':'smoke','r':float('nan')}])
    report={'version':'v18.49k','classification':'AUTHENTIC_Q550_CLOCK_PROJECTOR_DIAGNOSTIC_NOT_CAUSAL_CERTIFICATE',
       'authentic_ancestry_to_v18_48j':provenance['ancestry_to_v18_48j'],
       'kappas':kappas,'ramp_set':RAMPS if not args.smoke else [.300],
       'phase_interval':[float(QGRID[0]),float(QGRID[-1])],'phase_samples':len(QGRID),
       'alphas':ALPHAS,'physical_integrations':integrals['physical_11D'],
       'tangent_frame_integrations':integrals['tangent_10D'],
       'minimum_all_principal_relative_eigengap':min_gap,
       'max_regression_or_identity_errors':regression,
       'alpha_zero_source_roots':[{'ramp_xi':r['ramp_xi'],'q':r['clock_source_zero_q']} for r in roots_rows if r['alpha']==0.],
       'notes':['Source zeros depend on the selected volume form, even if Liouville identity holds.',
                'Half-turn event is a continuous median of projector speed on a finite phase window, not a critical point.',
                'A correlation across six ramp values is an association, not causal lag, invariant holonomy or physical energy transfer.',
                'The 10D finite path separation pulled back linearly is a diagnostic, not a nonlinear parallel transport invariant.',
                'Principal axes are compared in a declared common initial kinetic frame with tau_ref=1.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    if (regression['historical_forward']>1e-7 or regression['parent_source']>1e-7 or
        regression['parent_occupation']>1e-7 or regression['projector_sum']>1e-9 or
        regression['source_identity']>1e-11 or regression['explicit_kappa_trace']>1e-12 or
        regression['occupation_derivative_balance']>.02 or regression['projector_halfturn_coarse_grid_difference_q']>.002 or min_gap<1e-6):
        raise RuntimeError('Acceptance gate failed: '+json.dumps(report['max_regression_or_identity_errors']))
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
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    print(json.dumps(run(p.parse_args()),indent=2))
