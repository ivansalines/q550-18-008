#!/usr/bin/env python3
"""Q550 v18.49j — Liouville Source-Cancellation & Directional Strain Projection.

Reintegrates authenticated physical 11D Q550 return histories, 10D material
fundamental matrices and the kinetic-volume source. Splits the derivative of
principal-axis occupation into moving-direction and moving-projector terms.
Explicit kappa contribution to the material trace is audited separately from
its indirect effect through different phase-matched physical solutions.
"""
import argparse,csv,json,sys,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from verify_parent import verify,dynamic
from frame_math import transport_frame
from kinetic_metric import embedding_and_jac
from strain_math import factor
from source_math import (log_kinetic_density,log_density_gradient,rate_split,
                         rate_occupation_split,alternate_volume_shift)
ROOT=Path(__file__).resolve().parents[1]
RAMPS=[.285,.292,.296333,.300,.305,.309]
QGRID=np.linspace(.35,.65,61)
Q0=.50

def csv_write(name,rows):
    p=ROOT/'results'/name;p.parent.mkdir(exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader();w.writerows(rows)

def run(args):
    i,h,g,f,e,d,c,b,a,z,y,j,prov=verify()
    sys.path[:0]=[str(c/'reference'),str(c/'scripts')]
    physical=dynamic(c/'reference/physical_math.py','j_original_physical')
    ramp=dynamic(c/'reference/parent_ramp_math.py','j_original_ramp')
    original=dynamic(c/'reference/y_original_run_audit.py','j_original_y_audit')
    jet=dynamic(c/'reference/structural_jet.py','j_original_structural_jet')
    support_files=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_files)!=1:raise RuntimeError('Original source ambiguity')
    support=dynamic(support_files[0],'j_original_support')
    audit=dynamic(support_files[0].parent/'test_support_mobius_monodromy_audit.py','j_original_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    historical=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(historical['kappa_original']),'autonomous':float(historical['kappa_autonomous'])}
    speed=float(history['clock_speed']);slope=speed/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for n in range(len(history['y'])):
        groups[(str(history['families'][n]),int(history['seed_branches'][n]),str(history['kappa_kind'][n]))].append(n)
    iref={}
    with (i/'results/liouville_volume_identity.csv').open(newline='') as fi:
        for r in csv.DictReader(fi):iref[(r['kappa_kind'],round(float(r['ramp_xi']),6))]=r
    iproj={}
    with (i/'results/all_ten_principal_stretches.csv').open(newline='') as fi:
        for r in csv.DictReader(fi):
            if abs(float(r['phase_q'])-.5)<1e-12:
                iproj[(r['kappa_kind'],round(float(r['ramp_xi']),6),int(r['axis_rank']))]=r
    source_rows=[];summary_rows=[];projection_rows=[];rate_rows=[];counter_rows=[]
    sources_by_pair={};integrations={'physical':0,'tangent':0}
    maxima={'parent_history':0.,'parent_logvolume':0.,'parent_occupation':0.,
            'liouville':0.,'metric_source_quadrature':0.,'density_formula':0.,
            'occupation_balance':0.,'occupations_sum':0.,'explicit_kappa_trace':0.}
    for kind in (['original'] if args.smoke else ['original','autonomous']):
        inds=sorted(next(vals for (fam,br,k),vals in groups.items() if fam.startswith('phaseblind') and br==0 and k==kind),key=lambda n:float(history['xi'][n]))
        kap=kappas[kind];seed=history['y'][inds[0]].astype(float)
        forward,_=original.integrate(physical,ramp,support,audit,kap,params,slope,speed,seed,args)
        integrations['physical']+=1
        maxima['parent_history']=max(maxima['parent_history'],max(float(np.linalg.norm(forward(q)[:11]-history['y'][n])) for q,n in zip(np.linspace(0,1,41),inds)))
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        for rv in ([.300] if args.smoke else RAMPS):
            back,_=original.integrate(physical,ramp,support,audit,kap,params,slope,speed,turning,args,
                                      design=ramp.Design('v18_49j','smoothstep',rv))
            integrations['physical']+=1
            def jet_rhs(st):return jet.structural_jet(st,kap,params,slope)
            F,_=transport_frame(back,kap,params,slope,lambda st,k,p,sl:jet_rhs(st)[1],1+rv,
                                rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
            integrations['tangent']+=1
            start=back(0.)[:10];_,J0=embedding_and_jac(start,params.m_x,1.)
            directions=[];axes=[];stretches=[];lens=[];traces=[];density_rates=[]
            for q in QGRID:
                t=float(rv+q);state=back(t)[:11];fw=forward(1.-float(q))[:11]
                flow,JJ,_=jet_rhs(state)
                tr,dr=rate_split(state,flow,JJ)
                _,J1=embedding_and_jac(state,params.m_x,1.)
                ld=log_kinetic_density(state,params.m_x)
                maxima['density_formula']=max(maxima['density_formula'],abs(ld-np.linalg.slogdet(J1)[1]))
                B=J1@F(t)@np.linalg.inv(J0)
                sig,axis,sign,lv=factor(B)
                H1,_=embedding_and_jac(state,params.m_x,1.)
                Hf,_=embedding_and_jac(fw,params.m_x,1.)
                gap=np.linalg.solve(B,H1-Hf)
                if np.linalg.norm(gap)<1e-13:raise RuntimeError('Undefined material direction')
                u=gap/np.linalg.norm(gap)
                axes.append(axis);stretches.append(sig);directions.append(u);lens.append((float(lv),state.copy()))
                traces.append(tr);density_rates.append(dr)
                # Analytic coupling does not touch the diagonal (velocity-only forcing).
                j_coupling=jet.coupling_jet(state,params)[1]
                maxima['explicit_kappa_trace']=max(maxima['explicit_kappa_trace'],abs(np.trace(j_coupling[:10,:10])))
                source_rows.append({'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'phase_q':float(q),
                                    'div_solver_trace':tr,'kinetic_density_derivative':dr,
                                    'physical_volume_source':tr+dr,'analytic_density_log':ld,
                                    'log_volume_from_tangent':float(lv),
                                    'explicit_kappa_trace_term':float(slope*np.trace(j_coupling[:10,:10]))})
            directions=np.array(directions);axes=np.array(axes)
            occ,dp,from_direction,from_axes=rate_occupation_split(QGRID,directions,axes)
            maxima['occupations_sum']=max(maxima['occupations_sum'],float(np.max(abs(occ.sum(axis=1)-1))))
            # Finite difference mismatch only checked INSIDE grid, avoiding edge extrapolation.
            mismatch=float(np.max(np.abs(dp[2:-2]-from_direction[2:-2]-from_axes[2:-2])))
            maxima['occupation_balance']=max(maxima['occupation_balance'],mismatch)
            for i_q,q in enumerate(QGRID):
                for k in range(10):
                    projection_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                        'axis_rank':k+1,'occupation':float(occ[i_q,k]),
                        'principal_stretch':float(stretches[i_q][k]),
                        'directional_rate':float(from_direction[i_q,k]),
                        'axis_rotation_rate':float(from_axes[i_q,k])})
                    if i_q in (12,30,48) and k in (0,2,7,9):
                        rate_rows.append({'kappa_kind':kind,'ramp_xi':rv,'phase_q':float(q),
                            'axis_rank':k+1,'occupation':float(occ[i_q,k]),
                            'rate_total_numeric':float(dp[i_q,k]),
                            'rate_from_direction':float(from_direction[i_q,k]),
                            'rate_from_eigenprojector':float(from_axes[i_q,k]),
                            'rate_sum_residual':float(dp[i_q,k]-from_direction[i_q,k]-from_axes[i_q,k])})
            mid=int(np.argmin(abs(QGRID-Q0)));tend=float(rv+Q0);finish=lens[mid][1]
            # Liouville: integrate the trace and analytic metric-density source
            # INDEPENDENTLY from the propagator. Split at the drive ramp boundary.
            def local_split(t):
                st=back(t)[:11];flow,JJ,_=jet_rhs(st);return rate_split(st,flow,JJ)
            tr_int=0.;dens_int=0.
            for lower,upper in ((0.,rv),(rv,tend)):
                tr_int+=quad(lambda t:local_split(t)[0],lower,upper,epsabs=5e-11,epsrel=5e-11,limit=90)[0]
                dens_int+=quad(lambda t:local_split(t)[1],lower,upper,epsabs=5e-11,epsrel=5e-11,limit=90)[0]
            endpoint_density=float(log_kinetic_density(finish,params.m_x)-log_kinetic_density(start,params.m_x))
            lv=float(lens[mid][0]);maxima['liouville']=max(maxima['liouville'],abs(lv-tr_int-endpoint_density))
            maxima['metric_source_quadrature']=max(maxima['metric_source_quadrature'],abs(dens_int-endpoint_density))
            maxima['parent_logvolume']=max(maxima['parent_logvolume'],abs(lv-float(iref[(kind,round(rv,6))]['volume_log_from_tangent'])))
            for k in range(10):
                ref=iproj[(kind,round(rv,6),k+1)]
                angle=float(ref['axis_to_material_gap_deg'])
                maxima['parent_occupation']=max(maxima['parent_occupation'],abs(occ[mid,k]-np.cos(np.deg2rad(angle))**2))
            summary={'kappa_kind':kind,'kappa0':kap,'ramp_xi':rv,'phase_q':Q0,
                     'log_volume':lv,'volume_factor':float(np.exp(lv)),
                     'integrated_solver_trace':tr_int,'integrated_kinetic_density_rate':dens_int,
                     'endpoint_kinetic_density_change':endpoint_density,
                     'liouville_residual':float(lv-tr_int-endpoint_density),
                     'density_rate_integral_residual':float(dens_int-endpoint_density),
                     'axis8_fraction_q050':float(occ[mid,7]),'axis10_fraction_q050':float(occ[mid,9]),
                     'axis1_fraction_q050':float(occ[mid,0]),
                     'projection_sum_error':float(abs(occ[mid].sum()-1)),
                     'max_projector_rate_balance_residual':mismatch}
            summary_rows.append(summary)
            for alpha in (-2.,-1.,0.,1.,2.):
                shift=alternate_volume_shift(start,finish,alpha)
                counter_rows.append({'kappa_kind':kind,'ramp_xi':rv,'alpha':alpha,
                   'volume_form':'exp(alpha*(l1-l2)) * physical kinetic density',
                   'log_volume_alternate':float(lv+shift),
                   'extra_endpoint_density':shift})
            sources_by_pair[(kind,rv)]=np.column_stack([np.asarray(traces),np.asarray(density_rates),np.asarray(traces)+np.asarray(density_rates)])
            print(f'v18.49j {kind} ramp={rv:.6f} log_volume={lv:.9f} '
                  f'| Liouville residual={abs(summary["liouville_residual"]):.2e} '
                  f'| projection-rate residual={mismatch:.2e}',flush=True)
    pair_rows=[]
    if not args.smoke:
        by={(r['kappa_kind'],r['ramp_xi']):r for r in summary_rows}
        for rv in RAMPS:
            old=by[('original',rv)];new=by[('autonomous',rv)]
            dt=float(new['integrated_solver_trace']-old['integrated_solver_trace'])
            dg=float(new['endpoint_kinetic_density_change']-old['endpoint_kinetic_density_change'])
            dl=float(new['log_volume']-old['log_volume'])
            denom=abs(dt)+abs(dg)
            pair_rows.append({'ramp_xi':rv,'delta_kappa0':kappas['autonomous']-kappas['original'],
                 'delta_integrated_trace':dt,'delta_kinetic_density':dg,
                 'delta_log_volume':dl,'identity_residual':float(dl-dt-dg),
                 'normalized_cancellation_fraction':float(1-abs(dt+dg)/denom),
                 'raw_component_difference':float(dt+dg)})
            s=sources_by_pair[('autonomous',rv)]-sources_by_pair[('original',rv)]
            for q,parts in zip(QGRID,s):
                rate_rows.append({'ramp_xi':rv,'phase_q':float(q),'kappa_pair':'autonomous-minus-original',
                  'delta_local_solver_divergence':float(parts[0]),
                  'delta_local_metric_density_rate':float(parts[1]),
                  'delta_local_physical_volume_source':float(parts[2])})
    csv_write('liouville_source_integrals.csv',summary_rows)
    csv_write('clockmatched_kappa_cancellation.csv',pair_rows)
    csv_write('instantaneous_volume_sources.csv',source_rows)
    csv_write('ten_axis_occupation_and_split.csv',projection_rows)
    csv_write('occupation_rate_and_local_kappa_comparison.csv',rate_rows)
    csv_write('counterfactual_volume_forms.csv',counter_rows)
    report={'version':'v18.49j','classification':'AUTHENTIC_Q550_LIOUVILLE_AND_STRAIN_PROJECTION_DIAGNOSTIC',
       'parent_i_authenticated_to_J':bool(prov['ancestry_to_J']),
       'physical_integrations':integrations['physical'],'frame_integrations':integrations['tangent'],
       'ramp_set':RAMPS if not args.smoke else [.300],
       'kappas':kappas,'phase_grid_samples':len(QGRID),'source_max_errors':maxima,
       'explicit_kappa_trace_is_zero':'exact in analytic coupling_jet: kappa acts on velocities, no material diagonal term',
       'integrated_cancellation_ratio_range':( [min(r['normalized_cancellation_fraction'] for r in pair_rows),max(r['normalized_cancellation_fraction'] for r in pair_rows)] if pair_rows else []),
       'interpretation':'Liouville identity is geometric under declared metric form. Near cancellation across kappa is empirical, not an additional identity. Occupation derivative separates moving vector and moving eigenprojectors; neither alone is energy transfer. Finite-gap pullback is a diagnostic.'}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    if maxima['parent_history']>1e-7 or maxima['parent_logvolume']>1e-7 or maxima['parent_occupation']>1e-7 or maxima['liouville']>1e-7 or maxima['metric_source_quadrature']>1e-7 or maxima['density_formula']>1e-8 or maxima['occupation_balance']>.03 or maxima['occupations_sum']>1e-8 or maxima['explicit_kappa_trace']>1e-12:
        raise RuntimeError('v18.49j numerical acceptance gate failed: '+repr(maxima))
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
