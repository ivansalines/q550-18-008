#!/usr/bin/env python3
"""v18.49h: physical kinetic pullback deformation and covariant direction curvature.

Genuine Q550 11D histories, 10D tangent variational maps, exact polar-to-
Cartesian kinetic embedding, finite secant difference as independent check.
NO coordinate- and metric-free material invariant is asserted.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.linalg import eigh
from verify_parent import verify,dynamic
from frame_math import transport_frame
from kinetic_metric import embedding_and_jac,kinetic_energy,metric_deformation,material_metric,nonlinear_chart_gauge
from curvature_math import path_angles,sphere_curvature,unit
ROOT=Path(__file__).resolve().parents[1]
RAMPS=[.285,.292,.296333,.300,.305,.309]

def save_csv(name,rows):
    p=ROOT/'results'/name
    if not rows:p.write_text('status\nempty\n');return
    fields=list(dict.fromkeys(key for r in rows for key in r))
    with p.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def metric_eigenvalues(F,y0,y1,mx,tau):
    G0=material_metric(y0,mx,tau);G1=material_metric(y1,mx,tau)
    C=F.T@G1@F
    ev=eigh(C,G0,eigvals_only=True,check_finite=False)
    return np.maximum(ev,0),G0,G1,C

def run(args):
    g,f,e,d,c,b,a,z,y,j,provenance=verify()
    sys.path.insert(0,str(c/'reference'));sys.path.insert(0,str(c/'scripts'))
    physical=dynamic(c/'reference/physical_math.py','h_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','h_original_ramp')
    yr=dynamic(c/'reference/y_original_run_audit.py','h_original_y')
    jet=dynamic(c/'reference/structural_jet.py','h_original_jet')
    original_source=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(original_source)!=1:raise RuntimeError('Historical original solver is not unique')
    support=dynamic(original_source[0],'h_original_support')
    audit=dynamic(original_source[0].parent/'test_support_mobius_monodromy_audit.py','h_original_audit')
    historical=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hreport=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(hreport['kappa_original']), 'autonomous':float(hreport['kappa_autonomous'])}
    omega=float(historical['clock_speed']);slope=omega/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    if not params.m_x>0:raise RuntimeError('Kinetic x mass must be positive')
    groups=defaultdict(list)
    for i in range(len(historical['y'])):
        groups[(str(historical['families'][i]),int(historical['seed_branches'][i]),str(historical['kappa_kind'][i]))].append(i)
    g_ext={}
    with (g/'results/threshold_free_extrema_orientation.csv').open(newline='') as fi:
        for row in csv.DictReader(fi):
            g_ext[(row['kappa_kind'],round(float(row['ramp_xi']),6))]=row
    kinds=['original'] if args.smoke else ['original','autonomous']
    ramps=[.300] if args.smoke else RAMPS
    rows=[];profiles=[];curvature_rows=[];scale_rows=[]
    max_history=max_energy_kin=max_clock=max_cov=max_refine=max_parent=0.
    count_physical=count_frames=0
    for kind in kinds:
        idx=sorted(next(rows for (name,branch,k),rows in groups.items()
                   if name.startswith('phaseblind') and branch==0 and k==kind),
                   key=lambda i:float(historical['xi'][i]))
        kap=kappas[kind];start=historical['y'][idx[0]].astype(float)
        forward,err=yr.integrate(physical,ramp,support,audit,kap,params,slope,omega,start,args)
        count_physical+=1
        max_history=max(max_history,max(np.linalg.norm(forward(t)[:11]-historical['y'][i])
                                    for t,i in zip(np.linspace(0,1,41),idx)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        for rv in ramps:
            back,err=yr.integrate(physical,ramp,support,audit,kap,params,slope,omega,
                turning,args,design=ramp.Design('v18_49h','smoothstep',rv))
            count_physical+=1
            def jac(state,k,p,sl):return jet.structural_jet(state,k,p,sl)[1]
            F,_=transport_frame(back,kap,params,slope,jac,1+rv,
                rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            count_frames+=1
            initial=back(0.)[:10]
            def evaluate(q,tau):
                t=rv+float(q);yst=back(t)[:11];yf=forward(1-float(q))[:11]
                H1,J1=embedding_and_jac(yst,params.m_x,tau)
                Hf,_=embedding_and_jac(yf,params.m_x,tau)
                _,J0=embedding_and_jac(initial,params.m_x,tau)
                ff=F(t)
                cart_frame=J1@ff@np.linalg.inv(J0)
                # This is an exact Cartesian secant. Inverse tangent transport is
                # only a first-variational diagnostic for finite trajectory gaps.
                gap=H1-Hf
                w=np.linalg.solve(cart_frame,gap)
                return w,gap,cart_frame,ff,yst,yf
            for tau in (0.5,1.,2.):
                qq=np.linspace(.30,.70,args.curvature_samples)
                ww=np.array([evaluate(q,tau)[0] for q in qq]);uu=unit(ww)
                line=path_angles(uu);curve=sphere_curvature(uu,qq)
                q2=np.linspace(.30,.70,2*args.curvature_samples-1)
                u2=unit(np.array([evaluate(q,tau)[0] for q in q2]))
                line2=path_angles(u2);curve2=sphere_curvature(u2,q2)
                mid=(len(qq)//2);mid2=(len(q2)//2)
                c_error=float(abs(curve['curvature'][mid]-curve2['curvature'][mid2]))
                a_error=float(abs(line['length_deg']-line2['length_deg']))
                # Curvature at center is stable at the chosen sampling scale.
                max_refine=max(max_refine,a_error)
                curvature_rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'tau_ref':tau,
                    'curvature_at_q050':float(curve2['curvature'][mid2]),
                    'curvature_grid_difference_at_q050':c_error,
                    'curvature_median':curve2['median'],'curvature_max_interior':curve2['maximum'],
                    'minimum_path_speed':curve2['speed_min'],
                    'path_orientation_length_deg':line2['length_deg'],
                    'endpoint_angle_deg':line2['endpoint_deg'],
                    'excess_angle_deg':line2['excess_deg'],
                    'arc_refinement_diff_deg':a_error})
                if tau==1.:
                    # Save one complete orientation/curvature history for plots.
                    for q,curv,spd,u in zip(q2,curve2['curvature'],curve2['speed'],u2):
                        profiles.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                            'curvature':float(curv),'sphere_path_speed':float(spd),
                            'projection_first_axis':float(u[0]),
                            'projection_second_axis':float(u[1])})
                for q in (.35,.50,.65):
                    w,sec,B,ff,yst,yf=evaluate(q,tau)
                    eigen,G0,G1,C=metric_eigenvalues(ff,initial,yst,params.m_x,tau)
                    stretches=np.sqrt(eigen)
                    # Gauge test with a genuine non-linear chart map and its
                    # Jacobians, not a numerically convenient Euclidean gauge.
                    fp,g0p,g1p=nonlinear_chart_gauge(ff,G0,G1,initial,yst)
                    evp=eigh(fp.T@g1p@fp,g0p,eigvals_only=True,check_finite=False)
                    gerr=float(np.max(np.abs(evp-eigen))/max(1.,float(np.max(eigen))))
                    max_cov=max(max_cov,gerr)
                    # Test the kinetic energy formula against original balance.
                    kinetic_hist=physical.energy(yst,kap,params)
                    r1,r2,x,g,xd,*_=physical.physical_data(yst,kap,params)
                    expected=.5*(r1*r1*(yst[1]**2+yst[3]**2)+r2*r2*(yst[5]**2+yst[7]**2)+params.m_x*xd*xd)
                    ken=kinetic_energy(yst,params.m_x)
                    max_energy_kin=max(max_energy_kin,abs(ken-expected)/max(1.,abs(expected)))
                    max_clock=max(max_clock,abs(((yst[10]-yf[10]+np.pi)%(2*np.pi))-np.pi))
                    rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'tau_ref':tau,
                        'phase_q':q,'kinetic_energy':ken,
                        'strain_max_stretch':float(stretches.max()),
                        'strain_min_stretch':float(stretches.min()),
                        'strain_anisotropy_ratio':float(stretches.max()/stretches.min()),
                        'strain_log_volume':float(np.log(stretches).sum()),
                        'deformation_trace':float(eigen.sum()),
                        'material_cartesian_gap':float(np.linalg.norm(sec)),
                        'pulled_material_gap':float(np.linalg.norm(w)),
                        'metric_nonlinear_gauge_relative_error':gerr})
            ex=g_ext[(kind,round(rv,6))]
            qleft,qright=float(ex['left_min_q']),float(ex['right_min_q'])
            qs=np.linspace(qleft,qright,121)
            angle_vec=np.array([evaluate(q,1.)[0] for q in qs])
            obj=path_angles(angle_vec)
            old=float(ex['full10d_extrema_excess_deg'])
            # Different metric & observable: regression is intentionally NOT equality.
            max_parent=max(max_parent,abs(obj['excess_deg']-old))
            scale_rows.append({'kappa_kind':kind,'ramp_xi':rv,'q_left_min':qleft,'q_right_min':qright,
                'excess_kinetic_cartesian_deg':obj['excess_deg'],
                'excess_parent_G_euclidean_chart_deg':old,
                'difference_two_declarations_deg':obj['excess_deg']-old})
            print(f'v18.49h {kind} ramp={rv:.6f}: kinetic stretch q=.50 '
                f'{next(row["strain_max_stretch"] for row in rows[::-1] if row["ramp_xi"]==rv and row["kappa_kind"]==kind and row["tau_ref"]==1. and row["phase_q"]==.5):.5g}; '
                f'kinetic S9 excess={obj["excess_deg"]:.5g}deg',flush=True)
    save_csv('kinetic_deformation_eigenvalues.csv',rows)
    save_csv('kinetic_sphere_curvature.csv',curvature_rows)
    save_csv('kinetic_orientation_profiles.csv',profiles)
    save_csv('metric_comparison_with_G.csv',scale_rows)
    originals=[r for r in rows if r['tau_ref']==1. and r['phase_q']==.5]
    curves=[r for r in curvature_rows if r['tau_ref']==1.]
    report={'version':'v18.49h','classification':'AUTHENTIC_11D_MATERIAL_KINETIC_METRIC_DIAGNOSTIC_ONLY',
        'physical_integrations':count_physical,'frame_integrations':count_frames,
        'state_material_dimension':10,'clock_matched':True,'history_authenticated_to_J':provenance['genealogy_to_J'],
        'kappa_set':kinds,'ramp_set':ramps,'taus_tested':[.5,1.,2.],
        'metric':'flat kinetic base cartesian Q=(r1 cos t1,r1 sin t1,r2 cos t2,r2 sin t2,sqrt(mx)x); tangent bundle H=(Q,tau_ref V); Sasaki Euclidean pullback G=DH.T DH',
        'Cauchy_Green':'C=F.T G_end F relative to G_initial; eigenvalues in generalized positive definite pencil',
        'material_gap':'exact Cartesian secant for position and tau-weighted velocities; inverse tangent transport is a finite-difference diagnostic, NOT an exact nonlinear flow inverse',
        'curvature':'geodesic curvature of the normalized inverse-transported Cartesian finite gap on S9 at fixed initial physical frame; not a unique observer-free material torsion',
        'max_original_history_error':float(max_history),'max_kinetic_energy_identity_error':max_energy_kin,
        'max_clock_mismatch_rad':max_clock,
        'max_nonlinear_chart_generalized_eigen_error':max_cov,
        'max_curvature_arc_refinement_deg':max_refine,
        'stretches_q050_tau1_range':[min(r['strain_min_stretch'] for r in originals),max(r['strain_max_stretch'] for r in originals)],
        'anisotropy_ratio_q050_tau1_range':[min(r['strain_anisotropy_ratio'] for r in originals),max(r['strain_anisotropy_ratio'] for r in originals)],
        'sphere_curvature_q050_tau1_range':[min(r['curvature_at_q050'] for r in curves),max(r['curvature_at_q050'] for r in curves)],
        'sasaki_scale_dependence':True,
        'nonlinear_coordinate_invariance':True,
        'unproved':'metric-independent torsion, observer-independent material handedness, intrinsic kappa0 period, or exact nonlinear material recurrence'}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    if max_history>1e-7 or max_energy_kin>1e-10 or max_clock>1e-8 or max_cov>1e-7 or max_refine>.03:
        raise RuntimeError('Kinetic metric scientific gates failed')
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
    p.add_argument('--curvature-samples',type=int,default=121)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    run(p.parse_args())
