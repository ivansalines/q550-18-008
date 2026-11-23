#!/usr/bin/env python3
"""v18.48r: real 11D near-passes, 2D crossing orientation, phase-locked recurrence.

Every physical curve is produced from the ORIGINAL Q550 support RHS.  The
source q report determines which near-pass basins to audit; we independently
reintegrate each q protocol, derive analytic 3D tangents, and solve exact
external-drive phase constraints in continuous output.  Numerical crossing
roots are not globally certified intersections of full material trajectories.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent import verify
from transversality_math import (shape,shape_tangent,tangent_angles,wrap,phase_locked_min,
                                 segment_cross_candidates,refine_2d_crossing)
ROOT=Path(__file__).resolve().parents[1]
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def readcsv(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def writecsv(path,rows):
    if not rows:return
    names=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf8') as stream:
        w=csv.DictWriter(stream,fieldnames=names);w.writeheader();w.writerows(rows)

def row_stats(rows,key):
    a=np.array([float(r[key]) for r in rows],float)
    a=a[np.isfinite(a)]
    return dict(count=len(a),median=float(np.median(a)),min=float(a.min()),max=float(a.max())) if len(a) else {}

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rtol',type=float,default=3e-12)
    cli.add_argument('--atol',type=float,default=3e-13)
    cli.add_argument('--max-step',type=float,default=.0125)
    cli.add_argument('--projection-nodes',type=int,default=141)
    cli.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=cli.parse_args()
    if min(args.rtol,args.atol,args.max_step)>0 and args.projection_nodes>=30:pass
    else:raise ValueError('Invalid numerical parameters')
    output=args.output_dir;output.mkdir(parents=True,exist_ok=True)
    q,provenance=verify()
    p=q/'runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    j=p/'runtime/verified_sources/j/q550_kappa_gauge_covariant_v18_48j_bundle'
    physical=load_module(ROOT/'reference/physical_math.py','physical_v1848r')
    audit=load_module(p/'reference/test_support_mobius_monodromy_audit.py','audit_v1848r')
    support=load_module(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','support_v1848r')
    original=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hist=np.asarray(original['y'],float)
    xi=np.asarray(original['xi'],float)
    report_h=json.loads((j/'runtime/report_v18_48h.json').read_text())
    ks={'original':float(report_h['kappa_original']),
        'autonomous':float(report_h['kappa_autonomous'])}
    slope=float(original['clock_speed'])/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    parent_pairs=readcsv(q/'results/near_crossing_pairs.csv')
    pair_index={(r['family'],int(r['branch']),r['kappa_kind'],r['protocol'],r['comparison']):r for r in parent_pairs}
    parent_sweep=readcsv(q/'results/sweep_summary.csv')
    sweep_index={(r['family'],int(r['branch']),r['kappa_kind'],r['protocol']):r for r in parent_sweep}
    groups={}
    for i in range(328):
        key=(str(original['families'][i]),int(original['seed_branches'][i]),str(original['kappa_kind'][i]))
        groups.setdefault(key,[]).append(i)
    assert len(groups)==8
    comparisons=[];crossings=[];ledger=[];regression=[]
    total_ivps=0;max_regression=0.;max_bal_res=0.;max_q_gap_reg=0.
    selected=None
    umin,umax=.25,.96;smin,smax=.04,.75
    design=[('phase_closed',.5,2.),('phase_closed',1.,1.),('phase_closed',2.,.5),
            ('fixed_duration',.5,1.),('fixed_duration',2.,1.)]
    projected_axis_pairs=[(0,1),(0,2),(1,2)]
    all_projection_candidates=0

    def rhs(y,k,clock_sign):return physical.rhs_from_original(y,k,params,slope,clock_sign,support,audit)

    def integrate(tfinal,y0,k,clock_sign):
        nonlocal total_ivps,max_bal_res
        y15=np.r_[y0,np.zeros(4)]
        def derivative(t,y):return np.r_[rhs(y[:11],k,clock_sign),physical.power_terms(y[:11],k,params,slope,clock_sign)]
        sol=solve_ivp(derivative,(0.,tfinal),y15,method='DOP853',rtol=args.rtol,atol=args.atol,
                      max_step=args.max_step,dense_output=True)
        total_ivps+=1
        if not sol.success:raise RuntimeError(sol.message)
        works=sol.y[11:,-1]-sol.y[11:,0]
        deltaE=float(physical.energy(sol.y[:11,-1],k,params)-physical.energy(sol.y[:11,0],k,params))
        res=abs(deltaE-sum(works))/max(1.,abs(deltaE),np.sum(abs(works)))
        max_bal_res=max(res,max_bal_res)
        if res>1e-7:raise RuntimeError('Energy identity failed '+str(res))
        def evaluate(frac):
            x=np.asarray(frac,float)
            val=sol.sol(x*float(tfinal))[:11]
            return val.T if x.ndim else val
        return evaluate,dict(delta_E=deltaE,drive_work=float(works[0]),
                            radial_dissipation=float(works[1]),x_dissipation=float(works[2]),
                            active_x_work=float(works[3]),relative_balance_residual=float(res))

    def evaluate_pair(fwd,rev,u,s,k,rate,duration):
        a,b=rev(u),fwd(s)
        a3,b3=shape(a),shape(b)
        dr=shape_tangent(a,rhs(a,k,-rate))*duration
        df=shape_tangent(b,rhs(b,k,1.))
        tau=tangent_angles(dr,df)
        sep=a3-b3
        original_derivatives=np.array([np.dot(sep,dr),-np.dot(sep,df)])
        speed_r=float(np.linalg.norm(dr));speed_f=float(np.linalg.norm(df))
        phases=wrap(a[[2,6,10]]-b[[2,6,10]])
        velocities=a[[1,3,5,7,9]]-b[[1,3,5,7,9]]
        full_diff=a-b
        full_diff[[2,6,10]]=phases
        energy_delta=float(physical.energy(a,k,params)-physical.energy(b,k,params))
        return dict(shape_distance=float(np.linalg.norm(sep)),
                    delta_logrho1=float(sep[0]),delta_logrho2=float(sep[1]),delta_x=float(sep[2]),
                    full11D_delta_L2=float(np.linalg.norm(full_diff)),
                    velocity_delta_L2=float(np.linalg.norm(velocities)),
                    theta1_delta_rad=float(phases[0]),theta2_delta_rad=float(phases[1]),
                    Theta_delta_rad=float(phases[2]),energy_delta=energy_delta,
                    tangent_R_speed_per_normalized_u=speed_r,tangent_F_speed_per_normalized_s=speed_f,
                    stationarity_gradient_half_squared_d_u=float(original_derivatives[0]),
                    stationarity_gradient_half_squared_d_s=float(original_derivatives[1]),
                    projected_tangent_rank_sigma_min=float(np.linalg.svd(np.column_stack([dr,df]),compute_uv=False)[-1]),
                    transverse_line_angle_deg=tau['line_angle_deg'],
                    chronological_tangent_angle_deg=tau['chronic_angle_deg'],
                    sin_tangent_angle=tau['sin_3d'],
                    separation_normal_projection_fraction=float(abs(np.dot(sep,np.cross(dr,df)))/
                         max(1e-30,np.linalg.norm(sep)*np.linalg.norm(np.cross(dr,df)))) if np.linalg.norm(sep)>0 else 0.)

    for (fam,branch,kind),idx in sorted(groups.items()):
        idx=sorted(idx,key=lambda i:xi[i]);states=hist[idx];k=ks[kind]
        if not np.allclose(xi[idx],np.linspace(3.5,4.5,41),atol=1e-12):raise RuntimeError('Wrong historical sections')
        forward,b_fwd=integrate(1.,states[0],k,1.)
        regression_error=float(np.max(np.linalg.norm(forward(np.linspace(0.,1.,41))-states,axis=1)))
        max_regression=max(max_regression,regression_error)
        if regression_error>1e-7:raise RuntimeError('Original trajectory not recovered')
        regression.append(dict(family=fam,branch=branch,kappa_kind=kind,source_state_error_max=regression_error))
        yturn=forward(1.)
        for design_name,rate,duration in design:
            for flip in [False,True]:
                protocol=f'{design_name}_rate{rate:g}_flip{int(flip)}'
                key=(fam,branch,kind,protocol)
                parent=sweep_index[key]
                y0=yturn.copy()
                if flip:y0[[1,3,5,7,9]]*=-1.
                reverse,b_rev=integrate(duration,y0,k,-rate)
                # Audited q async minimum, evaluated independently on newly solved IVPs.
                old=pair_index[(*key,'asynchronous_free_pair')]
                uq,sq=float(old['return_progress']),float(old['forward_progress'])
                free=evaluate_pair(forward,reverse,uq,sq,k,rate,duration)
                qerr=abs(free['shape_distance']-float(old['shape_distance']))
                max_q_gap_reg=max(max_q_gap_reg,qerr)
                if qerr>1e-7:raise RuntimeError('q crossing regression failed '+str(qerr))
                freekind=dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                               design=design_name,rate=rate,duration_xi=duration,flip_tau_velocities=int(flip),
                               comparison='q_asynchronous_min_reintegrated',return_progress=uq,
                               forward_progress=sq,interior_minimum=str(old['interior_minimum'])=='True',
                               phase_closure_residual_abs_rad=abs(free['Theta_delta_rad']),**free)
                comparisons.append(freekind)
                conditioned=phase_locked_min(forward,reverse,rate,duration)
                if conditioned is None:raise RuntimeError('Empty phase-lock domain')
                u,s=conditioned['u'],conditioned['s']
                con=evaluate_pair(forward,reverse,u,s,k,rate,duration)
                clockphase=abs(con['Theta_delta_rad'])
                if clockphase>1e-10:raise RuntimeError('Phase-locked clock is not locked '+str(clockphase))
                locked=dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                            design=design_name,rate=rate,duration_xi=duration,flip_tau_velocities=int(flip),
                            comparison='phase_conditioned_min',return_progress=u,forward_progress=s,
                            interior_minimum=conditioned['interior'],
                            phase_closure_residual_abs_rad=clockphase,
                            phase_domain_lower_u=conditioned['lo'],phase_domain_upper_u=conditioned['hi'],**con)
                comparisons.append(locked)
                ledger.append(dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                                   q_free_shape_distance=free['shape_distance'],free_interior=int(freekind['interior_minimum']),
                                   q_free_tangent_line_angle_deg=free['transverse_line_angle_deg'],
                                   q_free_phase_mismatch_rad=abs(free['Theta_delta_rad']),
                                   q_free_energy_delta=free['energy_delta'],
                                   phase_locked_shape_distance=con['shape_distance'],
                                   phase_locked_tangent_line_angle_deg=con['transverse_line_angle_deg'],
                                   phase_locked_energy_delta=con['energy_delta'],
                                   phase_locked_11d_distance=con['full11D_delta_L2'],
                                   phase_lock_penalty=con['shape_distance']-free['shape_distance'],
                                   **b_rev))
                # Intersections of sampled 2D projections; refine on actual dense IVP.
                # Several different projection crossings can be images of one separated 3D near-pass.
                nodes_u=np.linspace(umin,umax,args.projection_nodes)
                nodes_s=np.linspace(smin,smax,args.projection_nodes)
                rv=shape(reverse(nodes_u));fv=shape(forward(nodes_s))
                for ax in projected_axis_pairs:
                    candidates=segment_cross_candidates(rv[:,ax],fv[:,ax])
                    all_projection_candidates+=len(candidates)
                    if not candidates:continue
                    seeds=[]
                    for i,j,t,v in candidates:
                        seed_u=float(nodes_u[i]*(1-t)+nodes_u[i+1]*t)
                        seed_s=float(nodes_s[j]*(1-v)+nodes_s[j+1]*v)
                        interpolated_residual=float(np.linalg.norm(rv[i]*(1-t)+rv[i+1]*t-
                                                    (fv[j]*(1-v)+fv[j+1]*v)))
                        seeds.append((interpolated_residual,seed_u,seed_s))
                    # Best 4 unrefined 3D candidates; record candidate count separately.
                    for ri,(_,u0,s0) in enumerate(sorted(seeds)[:4]):
                        ref=refine_2d_crossing(forward,reverse,
                            lambda y:rhs(y,k,1.),lambda y:rhs(y,k,-rate)*duration,
                            u0,s0,ax,urange=(umin,umax),srange=(smin,smax))
                        # The input tangent is already normalized du, ds above.
                        # Correction: rhs_reverse returns derivative w.r.t. normalized u.
                        delta=evaluate_pair(forward,reverse,ref['u'],ref['s'],k,rate,duration)
                        axname=f'{ax[0]}-{ax[1]}'
                        crossings.append(dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                            projection_axes=axname,number_sampled_crossings=len(candidates),
                            root_index=ri,return_progress=ref['u'],forward_progress=ref['s'],
                            projection_root_residual=ref['residual'],projection_jacobian_det=ref['jacobian_det'],
                            regular_projection_crossing=int(abs(ref['jacobian_det'])>1e-7),
                            root_interior=int(umin+1e-6<ref['u']<umax-1e-6 and smin+1e-6<ref['s']<smax-1e-6),
                            **delta))
                if fam.startswith('phasecov') and branch==0 and kind=='original' and protocol=='phase_closed_rate1_flip1':
                    grid=np.linspace(0,1,301)
                    selected=dict(grid=grid,forward=forward(grid),reverse=reverse(grid),
                                  free_u=uq,free_s=sq,locked_u=u,locked_s=s)
        print('v18.48r',fam,'branch',branch,kind,'source-regression',f'{regression_error:.3e}',flush=True)
    writecsv(output/'crossing_transversality.csv',comparisons)
    writecsv(output/'projection_crossings_2d.csv',crossings)
    writecsv(output/'phase_conditioned_protocols.csv',ledger)
    writecsv(output/'source_regression.csv',regression)
    if selected is not None:np.savez_compressed(output/'phasecov_selected_trajectories.npz',**selected)
    async_interior=[a for a in comparisons if a['comparison']=='q_asynchronous_min_reintegrated' and a['interior_minimum']]
    phase=[a for a in comparisons if a['comparison']=='phase_conditioned_min']
    roots=[a for a in crossings if a['projection_root_residual']<1e-8 and a['root_interior']]
    # Since a 3D distance below this threshold is not attained, no full intersection is asserted.
    report={'version':'v18.48r','title':'Counterflow Crossing Transversality & Phase-Conditioned Recurrence Audit',
            'genuine_11D_integrations':total_ivps,'forward_11D_integrations':8,
            'counterflow_11D_integrations':80,'historical_11D_states':328,
            'q_free_minima_reassessed':len(comparisons)//2,'q_free_interior_minima':len(async_interior),
            'phase_locked_continuous_minima':len(phase),
            'sampled_projection_intersection_candidates':all_projection_candidates,
            'refined_projection_roots':len(crossings),'resolved_2d_projection_crossings':len(roots),
            'regular_resolved_2d_projection_crossings':sum(a['regular_projection_crossing'] for a in roots),
            'smallest_2d_root_full3D_shape_distance':min([a['shape_distance'] for a in roots],default=None),
            'smallest_phase_conditioned_shape_distance':min(a['shape_distance'] for a in phase),
            'max_parent_q_gap_regression':max_q_gap_reg,
            'max_historical_regression':max_regression,
            'max_energy_balance_relative_residual':max_bal_res,
            'phase_lock_definition':'Theta_R(u) = Theta_F(s) unwrapped; s=1-rate*duration*u, within q search bounds. Phase-closed protocol reduces to s=1-u; fixed duration changes admissible pairs.',
            'async_interior_tangent_line_angle':row_stats(async_interior,'transverse_line_angle_deg'),
            'async_interior_shape_distance':row_stats(async_interior,'shape_distance'),
            'async_interior_full11D_distance':row_stats(async_interior,'full11D_delta_L2'),
            'phase_conditioned_shape_distance':row_stats(phase,'shape_distance'),
            'resolved_2d_root_full3D_shape_distance':row_stats(roots,'shape_distance'),
            'thresholds':{'2d_root_residual':1e-8,'projection_regular_det':1e-7,
                          'full3d_proximity_descriptive':1e-4,'not_a_proof_of_intersection':True},
            'numerical':{'solver':'DOP853','rtol':args.rtol,'atol':args.atol,
                         'max_step':args.max_step,'projection_nodes':args.projection_nodes,
                         'q_pair_optimizer':'inherits authenticated q near-pair minima; independently evaluates 11D dense IVPs'},
            'provenance':provenance,
            'scientific_boundary':'In 3D two 1D curves generally do not intersect; 2D projection root does not establish a 3D or 11D root. The line-angle is an unoriented chart tangent angle, not material torsion. An optimized short distance is not a certified global minimum. Phase-matched state differences do not prove intrinsic dissipation or a unique memory lag.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('genuine_11D_integrations','q_free_interior_minima','refined_projection_roots','resolved_2d_projection_crossings','smallest_phase_conditioned_shape_distance','max_historical_regression','max_energy_balance_relative_residual')},indent=2))
if __name__=='__main__':main()
