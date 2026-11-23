#!/usr/bin/env python3
"""Q550 v18.48p genuine counter-drive IVPs and mechanical balance.

The three return protocols start at THE SAME verified physical endpoint:
(1) mathematical backward solve of the ORIGINAL ODE (negative integration time);
(2) forward-time inversion of the externally imposed Theta clock only;
(3) same inverted clock with flipped initial tau-velocities.
A fourth forward-drive continuation is a negative control. Recomputes genuine
forward IVPs for provenance regression before studying return dynamics.
No route is interpreted as a time-reversed material history by assumption.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from physical_math import energy,power_terms,rhs_from_original,signed_displacement,physical_shape_distance
from verify_parent import verify
ROOT=Path(__file__).resolve().parents[1]
def norm(x):return float(np.linalg.norm(x))
def csvwrite(path,rows):
    if not rows:return
    with path.open('w',newline='',encoding='utf8') as w:
        wr=csv.DictWriter(w,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('--rtol',type=float,default=3e-12)
    pa.add_argument('--atol',type=float,default=3e-13)
    pa.add_argument('--max-step',type=float,default=.0125)
    pa.add_argument('--sections',type=int,default=41)
    pa.add_argument('--output-dir',type=Path,default=ROOT/'results')
    a=pa.parse_args()
    if a.sections!=41:raise ValueError('41 is pinned to authentic parent section grid')
    if a.rtol<=0 or a.atol<=0 or a.max_step<=0:raise ValueError('positive precision settings required')
    out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
    original_npz,original_report,provenance=verify()
    sys.path[:0]=[str(ROOT/'reference'),str(ROOT/'scripts')]
    audit=load_module(ROOT/'reference/test_support_mobius_monodromy_audit.py','audit_v1848p')
    support=load_module(ROOT/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','support_v1848p')
    from structural_jet import structural_jet
    p=audit.ModelParameters(gamma_rho=.3)
    z=np.load(original_npz,allow_pickle=False);hrep=json.loads(original_report.read_text())
    scale=np.asarray(z['chart_scale'],float);xs=np.asarray(z['xi'],float);states=np.asarray(z['y'],float)
    slope=float(z['clock_speed'])/(2*math.pi)
    kaps={'original':float(hrep['kappa_original']),'autonomous':float(hrep['kappa_autonomous'])}
    if states.shape!=(328,11) or abs(kaps['original']-1/6)>1e-15 or abs(kaps['autonomous']-35*math.pi/660)>1e-14:
        raise RuntimeError('Original physical data/kappa drift')
    groups={}
    for i in range(len(xs)):
        key=(str(z['families'][i]),int(z['seed_branches'][i]),str(z['kappa_kind'][i]))
        groups.setdefault(key,[]).append(i)
    if len(groups)!=8:raise RuntimeError('Expected 8 authentic physical 11D paths')
    section=np.linspace(0.,1.,41)
    summary=[];trajectory=[];balance=[];regress=[];saved_ivps=[]
    worst_regression=0.;worst_rhs=0.;worst_energy=0.;integrations=0
    def original_rhs(y,k,s):return rhs_from_original(y,k,p,slope,s,support,audit)
    for (fam,branch,kind),inds_unsorted in sorted(groups.items()):
        inds=sorted(inds_unsorted,key=lambda ix:xs[ix]);historical=states[inds];k=kaps[kind]
        if not np.allclose(xs[inds],section+3.5,atol=1e-13,rtol=0.):raise RuntimeError('not a 41-section authentic path')
        for j in (0,20,40):
            f=original_rhs(historical[j],k,+1)
            f_analytic=structural_jet(historical[j],k,p,slope)[0]
            re=norm(f-f_analytic)/max(norm(f),1e-30)
            worst_rhs=max(worst_rhs,re)
            if re>1e-11:raise RuntimeError('11D original structural RHS mismatch')
        y_start=historical[0]
        def solve(name,tspan,seed,clock_sign,teval):
            nonlocal integrations,worst_energy
            yseed=np.r_[seed,np.zeros(4)]
            def f(t,state):
                y=state[:11]
                return np.r_[original_rhs(y,k,clock_sign),power_terms(y,k,p,slope,clock_sign)]
            sol=solve_ivp(f,tspan,yseed,method='DOP853',t_eval=teval,
                          atol=a.atol,rtol=a.rtol,max_step=a.max_step)
            integrations+=1
            if not sol.success or sol.y.shape!=(15,len(teval)):
                raise RuntimeError(f'{fam}/{branch}/{kind}/{name}: IVP failed: {sol.message}')
            e0=energy(sol.y[:11,0],k,p);e1=energy(sol.y[:11,-1],k,p)
            components=np.asarray(sol.y[11:,-1]-sol.y[11:,0]);residual=(e1-e0)-float(sum(components))
            relres=abs(residual)/max(1.,abs(e1-e0),sum(abs(components)))
            worst_energy=max(worst_energy,relres)
            if relres>2e-7:raise RuntimeError(f'Energy identity drift {name}: {relres:.3e}')
            bal=dict(family=fam,branch=branch,kappa_kind=kind,protocol=name,initial_E=e0,
                     final_E=e1,delta_E=e1-e0,drive_work=components[0],
                     radial_dissipation=components[1],x_dissipation=components[2],
                     nonconservative_x_work=components[3],balance_residual=residual,
                     balance_relative_residual=relres)
            balance.append(bal)
            saved_ivps.append((fam,branch,kind,name,np.asarray(sol.y[:11].T).copy(),np.asarray(sol.y[11:].T).copy()))
            return sol.y[:11].T
        fwd=solve('forward_replay',(0.,1.),y_start,+1,section)
        drift=np.array([signed_displacement(y,b) for y,b in zip(fwd,historical)])
        worst_regression=max(worst_regression,float(max(drift)))
        if max(drift)>5e-6:raise RuntimeError('Original forward integration regression: '+str(max(drift)))
        y_end=fwd[-1]
        backward=solve('mathematical_inverse',(1.,0.),y_end,+1,section[::-1])
        clock_reverse=solve('reverse_drive',(0.,1.),y_end,-1,section)
        with_velocity_reverse=y_end.copy();with_velocity_reverse[[1,3,5,7,9]]*=-1
        drive_and_velocity=solve('reverse_drive_velocity_flip',(0.,1.),with_velocity_reverse,-1,section)
        forward_control=solve('forward_drive_continuation',(0.,1.),y_end,+1,section)
        expected=historical[::-1]
        matched={'mathematical_inverse':backward,'reverse_drive':clock_reverse,
                 'reverse_drive_velocity_flip':drive_and_velocity,
                 'forward_drive_continuation':forward_control}
        for name,ys in matched.items():
            gaps=[];shapes=[];theta_gaps=[]
            for j,(y,yr) in enumerate(zip(ys,expected)):
                dist=signed_displacement(y,yr,scale=scale)
                shape=physical_shape_distance(y,yr)
                angle=abs((float(y[10])-float(yr[10])+math.pi)%(2*math.pi)-math.pi)
                gaps.append(dist);shapes.append(shape);theta_gaps.append(angle)
                trajectory.append(dict(family=fam,branch=branch,kappa_kind=kind,protocol=name,
                    return_fraction=float(section[j]),reference_xi=float(4.5-section[j]),
                    xi_clock=float(y[10]),relative_phase=float((y[2]+y[6]-p.phi0-y[10]+math.pi)%(2*math.pi)-math.pi),
                    energy=energy(y,k,p),reference_energy=energy(yr,k,p),
                    chart_distance=dist,physical_shape_distance=shape,clock_phase_distance_rad=angle,
                    rho1=math.exp(float(y[0])),rho2=math.exp(float(y[4])),
                    x=1/(1+math.exp(-float(y[8])))))
            summary.append(dict(family=fam,branch=branch,kappa_kind=kind,protocol=name,
                endpoint_chart_distance=gaps[-1],max_chart_distance=max(gaps),
                median_chart_distance=float(np.median(gaps)),endpoint_shape_distance=shapes[-1],
                max_shape_distance=max(shapes),endpoint_phase_clock_error=theta_gaps[-1],
                phase_clock_max_error=max(theta_gaps)))
        regress.append(dict(family=fam,branch=branch,kappa_kind=kind,
                     max_forward_to_historical_full11D_norm=max(drift),
                     endpoint_forward_difference=drift[-1],
                     mathematical_inverse_endpoint_closure=norm(backward[-1]-y_start)))
        print('v18.48p',fam,branch,kind,'replay',f'{max(drift):.3e}',
              'inverse',f'{norm(backward[-1]-y_start):.3e}',
              'drive-only distance',f'{summary[-3]["endpoint_shape_distance"]:.3e}',flush=True)
    csvwrite(out/'trajectory_samples.csv',trajectory);csvwrite(out/'protocol_summary.csv',summary)
    csvwrite(out/'energy_balance.csv',balance);csvwrite(out/'reference_regression.csv',regress)
    np.savez_compressed(out/'full_11d_protocol_trajectories.npz',
        family=np.array([q[0] for q in saved_ivps]),branch=np.array([q[1] for q in saved_ivps]),
        kappa_kind=np.array([q[2] for q in saved_ivps]),protocol=np.array([q[3] for q in saved_ivps]),
        state=np.stack([q[4] for q in saved_ivps]),cumulative_work=np.stack([q[5] for q in saved_ivps]),
        progression=section,source_parent_sha256=np.array(provenance['physical_paths_sha256']))
    def metric(name,key):
        values=[float(r[key]) for r in summary if r['protocol']==name]
        return dict(min=float(min(values)),median=float(np.median(values)),max=float(max(values)))
    def emetric(name,key):
        values=[float(r[key]) for r in balance if r['protocol']==name]
        return dict(min=float(min(values)),median=float(np.median(values)),max=float(max(values)))
    report=dict(version='v18.48p',title='Controlled Counterflow Trajectory & Mechanical Balance Audit',
        authentic_original_states=328,authentic_original_flows=8,genuine_new_11D_integrations=integrations,
        newly_saved_11D_states=len(saved_ivps)*41,
        protocol_counts={'forward_replay':8,'mathematical_inverse':8,'reverse_drive':8,
                         'reverse_drive_velocity_flip':8,'forward_drive_continuation':8},
        reverse_drive_definition="Forward xi time; original material support RHS; externally prescribed dTheta/dxi=-2*pi*slope",
        velocity_flip_definition="Reverse-drive with initial (v1,omega1,v2,omega2,vz) signs inverted at turnaround only",
        exact_clock_speed=2*math.pi*slope,original_kappa=kaps['original'],autonomous_kappa=kaps['autonomous'],
        numerical={'rtol':a.rtol,'atol':a.atol,'max_step':a.max_step,'sections':a.sections},
        original_rhs_relative_error=worst_rhs,original_forward_max_absolute_error=worst_regression,
        max_energy_relative_balance_error=worst_energy,
        diagnostics={name:{'endpoint_shape_distance':metric(name,'endpoint_shape_distance'),
                           'endpoint_chart_distance':metric(name,'endpoint_chart_distance'),
                           'endpoint_phase_clock_error':metric(name,'endpoint_phase_clock_error'),
                           'delta_E':emetric(name,'delta_E'),'drive_work':emetric(name,'drive_work'),
                           'radial_dissipation':emetric(name,'radial_dissipation'),
                           'x_dissipation':emetric(name,'x_dissipation'),
                           'nonconservative_x_work':emetric(name,'nonconservative_x_work')}
                     for name in ['mathematical_inverse','reverse_drive','reverse_drive_velocity_flip','forward_drive_continuation']},
        provenance=provenance,
        scientific_boundary='Mechanical E is a defined model-derived diagnostic; active x force breaks conservation; reverse-drive is a new driven IVP, mathematical inverse is the same-flow backwards-in-time reference. Different terminal states alone do not certify thermodynamic irreversibility.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'integrations':integrations,'max_energy_balance_relative_residual':worst_energy,
        'forward_regression':worst_regression,'inverse_endpoint_shape':metric('mathematical_inverse','endpoint_shape_distance'),
        'reverse_drive_endpoint_shape':metric('reverse_drive','endpoint_shape_distance'),
        'reverse_drive_flip_endpoint_shape':metric('reverse_drive_velocity_flip','endpoint_shape_distance')},indent=2))
if __name__=='__main__':main()
