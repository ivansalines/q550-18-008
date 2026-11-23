#!/usr/bin/env python3
"""Q550 v18.49i — Volume-Form Invariance and Principal-Strain Transport.

Authentic Q550 11D forward/reversal histories and material tangent propagators.
The 10D material metric is the already-authenticated physical kinetic embedding
H=(Q,tau_ref V). Pullback axes are expressed in the SAME initial Cartesian
kinetic frame for comparisons within one trajectory. The instantaneous volume
factor is a metric-density Jacobian, not a universal coordinate-only det(F).
"""
import argparse,csv,json,platform,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.linalg import eigh
from verify_parent import verify,dynamic
from frame_math import transport_frame
from kinetic_metric import embedding_and_jac,material_metric
from curvature_math import unit,sphere_curvature
from strain_math import factor,nearby_eigen_gaps,line_angle,subspace_angles,anisotropic_length,gauge_strain_check,fixed_metric_volume,volume_form_coordinate_change
ROOT=Path(__file__).resolve().parents[1]
RAMPS=[.285,.292,.296333,.300,.305,.309]
QS=np.array([.35,.40,.45,.50,.55,.60,.65])

def save_csv(name,rows):
    path=ROOT/'results'/name
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run(args):
    h,g,f,e,d,c,b,a,z,y,j,prov=verify()
    sys.path[:0]=[str(c/'reference'),str(c/'scripts')]
    physical=dynamic(c/'reference/physical_math.py','i_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','i_original_ramp')
    original=dynamic(c/'reference/y_original_run_audit.py','i_original_y')
    jet=dynamic(c/'reference/structural_jet.py','i_original_jet')
    support_files=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_files)!=1:raise RuntimeError('Nonunique historical model source')
    support=dynamic(support_files[0],'i_original_support')
    audit=dynamic(support_files[0].parent/'test_support_mobius_monodromy_audit.py','i_original_audit')
    hist=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hr=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(hr['kappa_original']), 'autonomous':float(hr['kappa_autonomous'])}
    omega=float(hist['clock_speed']);slope=omega/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(hist['y'])):
        groups[(str(hist['families'][i]),int(hist['seed_branches'][i]),str(hist['kappa_kind'][i]))].append(i)
    reference={}
    with (h/'results/kinetic_deformation_eigenvalues.csv').open(newline='') as fi:
        for row in csv.DictReader(fi):
            if float(row['tau_ref'])==1 and float(row['phase_q'])==.5:
                reference[(row['kappa_kind'],round(float(row['ramp_xi']),6))]=row
    profiles=[];axis_rows=[];cross_rows=[];volume_rows=[];spectral_arrays={}
    max_history=max_gauge=max_volume_chart=max_tau=max_H=max_liouville=max_kinetic=0.
    counts={'physical':0,'frame':0}
    initial_gap_alignment=[]
    for kind in (['original'] if args.smoke else ['original','autonomous']):
        inds=sorted(next(vals for (fam,br,k),vals in groups.items() if fam.startswith('phaseblind') and br==0 and k==kind),key=lambda i:float(hist['xi'][i]))
        kap=kappas[kind];seed=hist['y'][inds[0]].astype(float)
        forward,_=original.integrate(physical,ramp,support,audit,kap,params,slope,omega,seed,args)
        counts['physical']+=1
        max_history=max(max_history,max(np.linalg.norm(forward(q)[:11]-hist['y'][i]) for q,i in zip(np.linspace(0,1,41),inds)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        for rv in ([.300] if args.smoke else RAMPS):
            back,_=original.integrate(physical,ramp,support,audit,kap,params,slope,omega,turning,args,
                design=ramp.Design('v18_49i','smoothstep',rv))
            counts['physical']+=1
            def jfull(state):return jet.structural_jet(state,kap,params,slope)[1]
            F,_=transport_frame(back,kap,params,slope,lambda st,k,p,sl:jfull(st),1+rv,
                rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            counts['frame']+=1
            initial=back(0.)[:10]
            axes_list=[];gaps_list=[];sigmas_list=[]
            axis_prev=None;sub_prev=None
            for qi,q in enumerate(QS):
                t=rv+float(q);state=back(t)[:11];historical_forward=forward(1.-float(q))[:11]
                H1,J1=embedding_and_jac(state,params.m_x,1.)
                Hf,_=embedding_and_jac(historical_forward,params.m_x,1.)
                H0,J0=embedding_and_jac(initial,params.m_x,1.)
                fm=F(t);B=J1@fm@np.linalg.inv(J0)
                sigma,axes,det_sign,logvol=factor(B)
                vg=(np.linalg.solve(B,H1-Hf))
                u=unit(vg)
                # Cauchy-Green right axes are all represented in the common
                # initial kinetic Cartesian frame for this same return.
                a1=axes[:,0];a2=axes[:,:2]
                gap=nearby_eigen_gaps(sigma)
                a1angle=line_angle(axis_prev,a1) if axis_prev is not None else np.nan
                a2angle=float(max(subspace_angles(sub_prev,a2))) if sub_prev is not None else np.nan
                axis_prev=a1;sub_prev=a2
                g0=material_metric(initial,params.m_x,1.);g1=material_metric(state,params.m_x,1.)
                max_gauge=max(max_gauge,gauge_strain_check(fm,g0,g1,initial,state))
                max_volume_chart=max(max_volume_chart,volume_form_coordinate_change(fm,g0,g1,
                    np.diag(np.linspace(.7,1.3,10)),np.diag(np.linspace(1.4,.8,10))))
                volume_form=fixed_metric_volume(fm,J0,J1)
                max_volume_chart=max(max_volume_chart,abs(logvol-volume_form))
                hrow=reference.get((kind,round(rv,6)))
                if hrow is not None and abs(q-.5)<1e-12:
                    max_H=max(max_H,abs(sigma[0]-float(hrow['strain_max_stretch'])),abs(sigma[-1]-float(hrow['strain_min_stretch'])),
                        abs(logvol-float(hrow['strain_log_volume'])))
                sigma_tau=[];tau_log=[]
                for tau in (.5,1.,2.):
                    _,e0=embedding_and_jac(initial,params.m_x,tau)
                    _,e1=embedding_and_jac(state,params.m_x,tau)
                    bt=e1@fm@np.linalg.inv(e0)
                    tau_log.append(float(np.linalg.slogdet(bt)[1]))
                    if abs(q-.5)<1e-12:sigma_tau.append(np.linalg.svd(bt,compute_uv=False))
                max_tau=max(max_tau,np.ptp(tau_log))
                row={'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'phase_q':float(q),
                    'log_volume':logvol,'volume_factor':float(np.exp(logvol)),
                    'volume_orientation_sign':det_sign,'max_stretch':float(sigma[0]),
                    'min_stretch':float(sigma[-1]),'anisotropy':float(sigma[0]/sigma[-1]),
                    'top1_axis_angle_prev_deg':a1angle,'top2_subspace_max_angle_prev_deg':a2angle,
                    'top_stretch_gap_relative':float(gap[0]),'min_eigen_gap_relative':float(gap.min()),
                    'top_axis_to_material_gap_deg':line_angle(a1,u),
                    'material_gap_norm':float(np.linalg.norm(vg)),
                    'material_gap_stretch_factor':anisotropic_length(sigma,axes,vg),
                    'covariant_metric_error':max_gauge}
                profiles.append(row)
                for rank in range(10):
                    axis_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),'axis_rank':rank+1,
                        'stretch':float(sigma[rank]),'axis_to_material_gap_deg':line_angle(axes[:,rank],u)})
                axes_list.append(axes);gaps_list.append(u);sigmas_list.append(sigma)
                if abs(q-.5)<1e-12:
                    # Liouville formula: d/dt log det F = tr J(t), plus endpoint
                    # kinetic volume-density ratio from H's nonlinear chart.
                    integr,err=quad(lambda tt:float(np.trace(jfull(back(tt)[:11])[:10,:10])),0.,t,
                                     epsabs=1e-10,epsrel=1e-10,limit=100)
                    volpred=float(integr+np.linalg.slogdet(J1)[1]-np.linalg.slogdet(J0)[1])
                    lres=abs(logvol-volpred)
                    max_liouville=max(max_liouville,lres)
                    volume_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                        'volume_log_from_tangent':logvol,'log_volume_from_liouville':volpred,
                        'liouville_abs_error':lres,'volume_factor':float(np.exp(logvol)),
                        'position_velocity_tau_log_spread':float(np.ptp(tau_log)),
                        'tangent_trace_integral':float(integr),
                        'kinetic_metric_density_log_change':float(np.linalg.slogdet(J1)[1]-np.linalg.slogdet(J0)[1]),
                        'top_stretch_tau_half':float(sigma_tau[0][0]),
                        'top_stretch_tau_one':float(sigma_tau[1][0]),
                        'top_stretch_tau_two':float(sigma_tau[2][0])})
            # Curvature is a separately derived finite-gap direction audit.
            # The axes live at starting state and are compared to it in the
            # same flat kinetic reference; their alignment is descriptive.
            cqs=np.linspace(.35,.65,81)
            direction=[]
            H0,J0=embedding_and_jac(initial,params.m_x,1.)
            for q in cqs:
                t=rv+float(q);st=back(t)[:11];fw=forward(1.-float(q))[:11]
                H1,J1=embedding_and_jac(st,params.m_x,1.);Hf,_=embedding_and_jac(fw,params.m_x,1.)
                B=J1@F(t)@np.linalg.inv(J0)
                direction.append(unit(np.linalg.solve(B,H1-Hf)))
            direction=np.asarray(direction)
            curve=sphere_curvature(direction,cqs)
            tdir=np.gradient(direction,cqs,axis=0,edge_order=2)
            tdir=unit(tdir)
            for ii in (12,40,68):
                q=float(cqs[ii]);mi=int(np.argmin(abs(QS-q)))
                a1=axes_list[mi][:,0]
                cross_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':q,
                    'curvature':float(curve['curvature'][ii]),
                    'principal_axis_to_direction_tangent_deg':line_angle(a1,tdir[ii]),
                    'principal_axis_to_gap_deg':line_angle(a1,direction[ii]),
                    'sphere_path_speed':float(curve['speed'][ii]),
                    'phase_axis_nearest_q':float(QS[mi])})
            spectral_arrays[f'{kind}_r{rv:.6f}_axes']=np.asarray(axes_list)
            spectral_arrays[f'{kind}_r{rv:.6f}_stretches']=np.asarray(sigmas_list)
            print(f'v18.49i {kind} ramp={rv:.6f}: log volume q=.5={volume_rows[-1]["volume_log_from_tangent"]:.8f}; '
                f'axis turn q=.35→.65={line_angle(axes_list[0][:,0],axes_list[-1][:,0]):.4f} deg',flush=True)
    save_csv('strain_axes_phase_profiles.csv',profiles)
    save_csv('all_ten_principal_stretches.csv',axis_rows)
    save_csv('liouville_volume_identity.csv',volume_rows)
    save_csv('strain_axis_vs_material_curvature.csv',cross_rows)
    np.savez_compressed(ROOT/'results/principal_axes_common_frame.npz',**spectral_arrays)
    vvals=[r['volume_factor'] for r in volume_rows]
    gap=[r['top_stretch_gap_relative'] for r in profiles]
    result={'version':'v18.49i','classification':'AUTHENTIC_Q550_KINETIC_VOLUME_AND_STRAIN_DIAGNOSTIC',
        'history_authenticated_to_J':prov['ancestry_to_J'],
        'physical_integrations':counts['physical'],'frame_integrations':counts['frame'],
        'branch':'phaseblind, 0','kappas':list(kappas),'ramp_set':RAMPS,'phase_q':list(QS),
        'metric':'flat kinetic Cartesian H(y)=(Q,tau_ref V); tau_ref convention is declared, not unique',
        'volume_form':'sqrt(det G(y))dy; log volume = log|det F|+log|det DH_end/DH_initial|',
        'volume_factor_q050_range':[min(vvals),max(vvals)],
        'max_liouville_log_volume_residual':max_liouville,
        'max_tau_volume_log_spread':max_tau,
        'max_chart_metric_volume_residual':max_volume_chart,
        'max_nonlinear_chart_strain_error':max_gauge,
        'max_H_strain_regression':max_H,
        'max_history_error':max_history,
        'min_top_eigen_gap':min(gap),
        'top_axis_total_turn_deg_range':[min(line_angle(spectral_arrays[f'{k}_r{r:.6f}_axes'][0,:,0],spectral_arrays[f'{k}_r{r:.6f}_axes'][-1,:,0]) for k in kappas for r in RAMPS if f'{k}_r{r:.6f}_axes' in spectral_arrays),
                                        max(line_angle(spectral_arrays[f'{k}_r{r:.6f}_axes'][0,:,0],spectral_arrays[f'{k}_r{r:.6f}_axes'][-1,:,0]) for k in kappas for r in RAMPS if f'{k}_r{r:.6f}_axes' in spectral_arrays)],
        'limits':'finite 11D history differences are not Jacobi fields; metric choice and phase window declared; no metric-free physical torsion; volume is not universal for any arbitrary density'}
    (ROOT/'results/report.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    if max_history>1e-7 or max_H>1e-7 or max_gauge>1e-8 or max_volume_chart>1e-8 or max_tau>1e-8 or max_liouville>1e-7:
        raise RuntimeError('v18.49i numerical scientific gate failed')
    return result

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
    run(p.parse_args())
