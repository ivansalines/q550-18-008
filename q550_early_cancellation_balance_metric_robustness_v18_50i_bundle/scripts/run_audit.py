#!/usr/bin/env python3
"""v18.50i: fresh original 11D Q550 IVPs, metric and amplitude controls.

Authenticates v18.50h ancestors, uses its byte-identical v18.50e solver,
and measures the early local/transport decomposition in declared charts.
No physical metric, causality, material memory or continuous maximizer is claimed.
"""
import argparse,csv,json,sys,os,zipfile,hashlib,importlib.util,platform,traceback
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[1]
H='q550_response_arc_length_refinement_comoving_curvature_v18_50h_bundle'
P=ROOT/'inputs/q550_response_arc_length_refinement_comoving_curvature_v18_50h_authenticated_server_sendback.zip'

def authenticate():
    with zipfile.ZipFile(P) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('CRC failure '+bad)
        m=json.loads(z.read(H+'/SHA256SUMS.json'))
        if m['root']!=H or m['version']!='v18.50h':raise RuntimeError('Unexpected h manifest')
        expected={H+'/'+x for x in m['files']}|{H+'/SHA256SUMS.json'}
        if set(z.namelist())!=expected:raise RuntimeError('Unexpected h archive members')
        for name,digest in m['files'].items():
            if Path(name).is_absolute() or '..' in Path(name).parts:raise RuntimeError('Unsafe path')
            if hashlib.sha256(z.read(H+'/'+name)).hexdigest()!=digest:
                raise RuntimeError('Parent hash mismatch '+name)
        dest=ROOT/'runtime'/H
        if not (dest/'SHA256SUMS.json').exists():
            for name in z.namelist():
                relative=Path(name).relative_to(H)
                p=dest/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
        parent_rows=list(csv.DictReader(z.read(H+'/results/early_cancellation_zoom.csv').decode().splitlines()))
        hreport=json.loads(z.read(H+'/results/report.json'))
    sys.path.insert(0,str(dest/'scripts'))
    from verify_ancestry import stage
    edest,ereport,oldcsv,anc=stage()
    sys.path.insert(0,str(edest/'scripts'))
    from verify_parent_d import verify
    dr,drpt,_=verify()
    from parent_o_experiment import Experiment
    from response_math import central_directional,unit
    return Experiment,unit,central_directional,ereport,drpt,anc,parent_rows,hreport

def write_csv(file,rows):
    if not rows:raise RuntimeError('Empty output '+str(file))
    cols=list(dict.fromkeys(k for r in rows for k in r.keys()))
    with file.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def normalized(v):
    v=np.asarray(v,float);n=np.linalg.norm(v)
    if n<1e-14:raise RuntimeError('vanishing vector')
    return v/n

def compose(L,T):
    l=float(np.linalg.norm(L));t=float(np.linalg.norm(T));a=float(np.linalg.norm(L+T))
    c=1-a/max(l+t,1e-30)
    return dict(L_norm=l,T_norm=t,R_norm=a,T_over_L=t/max(l,1e-30),
       LT_cos=float(np.dot(L,T)/max(l*t,1e-30)),cancellation=c,LT_dot=float(np.dot(L,T)))

def locate_peak(rows):
    idx=int(np.argmax([r['cancellation'] for r in rows]));p=rows[idx]
    return dict(peak_xi=float(p['horizon_xi']),peak_cancellation=float(p['cancellation']),
                ratio_at_peak=p['T_over_L'],cos_at_peak=p['LT_cos'],
                bracket=(float(rows[idx-1]['horizon_xi']),float(rows[idx+1]['horizon_xi'])) if 0<idx<len(rows)-1 else None,
                interior=0<idx<len(rows)-1,peak_index=idx)

def run(args):
    Experiment,unit,central_directional,ereport,drpt,anc,parent_rows,hreport=authenticate()
    exp=Experiment(args)
    scale=np.asarray(drpt['common_metric_scale_4d'],float)
    metrics={
        'common_parent_c':scale,
        'raw_coordinate':np.ones(4),
        'angles_weighted_2x':scale/np.array([2,2,1,1],float),
        'rates_weighted_2x':scale/np.array([1,1,2,2],float),
        'common_uniform_rescale_3x':scale*3,
    }
    # diagonal coordinate charts: unit(v / scale) is the declared direction map
    horizons=np.linspace(args.zoom_start,args.zoom_end,args.zoom_samples).tolist()
    horizons=sorted(set(horizons+[.0125,.05]))
    reference_h={round(float(z['horizon_xi']),12):float(z['cancellation']) for z in parent_rows}
    results=[];amplitude=[];diagnostics=[];baseline=[]
    max_reg=0.;reg_count=0;max_dir_err=0.;ivps=0;balance_checks=[]
    kinds=('original','autonomous')
    for kind in kinds:
        kappa=exp.ks[kind];r=.24;shape='beta:2:2'
        design=exp.original_ramp.Design('v18_50i_ref',shape,r)
        # the same natural turning state used by 50e/h, for each physical kappa family.
        # Read the verified v18.50c report from staged 50e parent runtime (as in original e engine).
        e_root=Path(sys.modules['verify_parent_d'].__file__).resolve().parents[1]
        cbase=e_root/'runtime'/drpt.get('not_a_path','q550_hidden_direction_controlled_perturbation_causal_discrimination_v18_50d_bundle')/'runtime'/'q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle'
        # verify_parent_d owns the verified d parent path; use the authenticated path rather than guessing.
        droot,_,_=sys.modules['verify_parent_d'].verify()
        croot=droot/'runtime'/'q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle'
        creport=json.loads((croot/'results/report.json').read_text())
        ev=next(z for z in creport['cases'] if z['kind']==kind and abs(float(z['ramp_xi'])-.24)<1e-9 and z['shape']==shape and z['metric']=='common')
        t_event=float(ev['turn_xi'])
        back,ledger=exp.original.integrate(exp.physical,exp.clock,exp.support,exp.audit,kappa,exp.params,exp.slope,exp.omega,exp.turning[kind],args,design=design)
        seed=np.asarray(back(t_event)[:11],float)
        th0=float(seed[10]);phase0=exp.clock.cubic_phase_excursion(t_event,design)
        def theta(t):return th0-exp.omega*(exp.clock.cubic_phase_excursion(t,design)-phase0)
        def ode(t,z):
            y=np.r_[z,theta(t)]
            return exp.physical.rhs_from_original(y,kappa,exp.params,exp.slope,exp.clock.cubic_clock_sign(t,design),exp.support,exp.audit)[:10]
        def hidden(y):
            f,j,_=exp.jet.structural_jet(y,kappa,exp.params,exp.slope)
            return np.asarray([f[2],f[6],(j@f)[2],(j@f)[6]],float)
        times=[t_event]+[t_event+t for t in horizons]
        amps=(1e-5,1e-4,1e-3)
        solutions={}
        for sign,eps in [(0,0.)]+[(s,a) for a in amps for s in [-1,1]]:
            y=seed[:10].copy();y[8]+=sign*eps
            sol=solve_ivp(ode,(times[0],times[-1]),y,method='DOP853',t_eval=times,
                          rtol=args.rtol,atol=args.atol,max_step=min(args.max_step,.05/25))
            ivps+=1
            if not sol.success:raise RuntimeError(f'IVP failed {kind} {sign} {eps}: {sol.message}')
            solutions[(sign,eps)]=np.asarray(sol.y).T
        for eps in amps:
            yp=solutions[(1,eps)];ym=solutions[(-1,eps)]
            baseline_positions=solutions[(0,0.)]
            for i,h in enumerate([0.]+horizons):
                y=np.r_[baseline_positions[i],theta(times[i])]
                tangent=(np.r_[yp[i],theta(times[i])]-np.r_[ym[i],theta(times[i])])/(2*eps)
                for mname,sc in metrics.items():
                    direction=lambda q:unit(hidden(q),sc)
                    e=np.zeros(11);e[8]=1
                    L=central_directional(direction,y,e,args.direction_step)
                    T=central_directional(direction,y,tangent-e,args.direction_step)
                    R=L+T
                    rivp=(direction(np.r_[yp[i],theta(times[i])])-direction(np.r_[ym[i],theta(times[i])]))/(2*eps)
                    relerr=float(np.linalg.norm(rivp-R)/max(1,np.linalg.norm(rivp)))
                    max_dir_err=max(max_dir_err,relerr)
                    rec={'kind':kind,'kappa0':kappa,'ramp_xi':r,'horizon_xi':h,'metric':mname,'epsilon':eps,**compose(L,T),
                         'R_IVP':float(np.linalg.norm(rivp)), 'relative_decomp_vs_IVP_error':relerr,
                         'L_vec':json.dumps(L.tolist()),'T_vec':json.dumps(T.tolist()),'R_vec':json.dumps(R.tolist())}
                    results.append(rec)
                    if kind=='original' and mname=='common_parent_c' and eps==1e-4 and round(h,12) in reference_h:
                        max_reg=max(max_reg,abs(rec['cancellation']-reference_h[round(h,12)]));reg_count+=1
        # Check uniform chart rescaling does not change geometry in Euclidean output coordinates.
        for eps in amps:
            a=[z for z in results if z['kind']==kind and z['epsilon']==eps and z['metric']=='common_parent_c']
            b=[z for z in results if z['kind']==kind and z['epsilon']==eps and z['metric']=='common_uniform_rescale_3x']
            assert len(a)==len(b)
            assert max(abs(x['cancellation']-y['cancellation']) for x,y in zip(a,b))<1e-8
        diagnostics.append(dict(kind=kind,kappa0=kappa,turn_xi=t_event,ledger_error=ledger,amp_count=len(amps)))
    if max_reg>2e-5:raise RuntimeError('Historical h cancellation regression too large '+str(max_reg))
    if max_dir_err>2e-3:raise RuntimeError('Linearized response mismatch '+str(max_dir_err))
    # summarize by kind/metric/epsilon and quantify sensitivity to metric and amplitude.
    for kind in kinds:
        for mname in metrics:
            for eps in amps:
                rows=sorted([z for z in results if z['kind']==kind and z['metric']==mname and z['epsilon']==eps and z['horizon_xi']<=args.zoom_end],key=lambda z:z['horizon_xi'])
                pk=locate_peak(rows)
                amplitude.append(dict(kind=kind,metric=mname,epsilon=eps,**pk,
                   initial_cancellation=rows[0]['cancellation'],endpoint_cancellation=rows[-1]['cancellation']))
    out=ROOT/'results'
    write_csv(out/'early_metric_amplitude_trace.csv',results)
    write_csv(out/'peak_metric_amplitude_summary.csv',amplitude)
    write_csv(out/'family_baseline_checks.csv',diagnostics)
    # reference historical metrics, amplitude 1e-4
    comparisons={k:{m:next(z for z in amplitude if z['kind']==k and z['metric']==m and z['epsilon']==1e-4) for m in metrics if m!='common_uniform_rescale_3x'} for k in kinds}
    reprt={'version':'v18.50i','title':'Early Cancellation Balance & Metric-Robustness Audit',
      'classification':'IN_MODEL_EARLY_CANCELLATION_METRIC_AND_AMP_STRESS_NOT_PHYSICAL_INVARIANCE_OR_MEMORY_CERTIFICATE',
      'parent_h_sha256':hashlib.sha256(P.read_bytes()).hexdigest(), 'authentic_parent_h_members':len(hreport),
      'genealogy':anc,'kappa0':{k:exp.ks[k] for k in kinds},
      'grid':{'xi_start':args.zoom_start,'xi_end':args.zoom_end,'samples':args.zoom_samples,'augmented_horizons':[.0125,.05]},
      'metric_charts':{k:v.tolist() for k,v in metrics.items()}, 'epsilons':list(amps),
      'counts':{'physical_ivps':ivps,'new_response_rows':len(results),'peak_cases':len(amplitude),'h_reference_regression_points':reg_count},
      'checks':{'h_max_absolute_cancel_regression':max_reg,'max_relative_response_linearization_error':max_dir_err},
      'reference_peak_comparison':comparisons,'limits':[
        'Cancellation is coordinate-chart dependent and neither a mechanical energy nor an invariant physical scalar.',
        'The ratio of local/transport norms and their cosine describe a declared finite-difference decomposition, not a separate causal pathway.',
        'Every reported extremum is sampled within a bounded zoom; no certified continuous stationary point or bifurcation.',
        'Metric and kick amplitude controls test numerical sensitivity of the model, not physical observer equivalence.',
        'Separate natural seeds under original and autonomous kappa; comparisons are not common-state interventions.',
        'No material-memory certificate, cubical packing realization or physical instability is inferred.'],
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (out/'report.json').write_text(json.dumps(reprt,indent=2,allow_nan=False)+'\n')
    plot_spec=importlib.util.spec_from_file_location("v18_50i_plot_module",ROOT/"scripts"/"plot_results.py")
    plot_mod=importlib.util.module_from_spec(plot_spec);plot_spec.loader.exec_module(plot_mod)
    plot_mod.plots(results,amplitude,out)
    print('v18.50i complete:',json.dumps({'checks':reprt['checks'],'kappa':reprt['kappa0'],'original_reference':comparisons['original']['common_parent_c'],'autonomous_reference':comparisons['autonomous']['common_parent_c']},indent=2),flush=True)
    return reprt
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--zoom-start',type=float,default=.000025);p.add_argument('--zoom-end',type=float,default=.004)
    p.add_argument('--zoom-samples',type=int,default=160)
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum-parent-share-difference',type=float,default=2e-6)
    p.add_argument('--max-generator-identity-error',type=float,default=1e-7)
    p.add_argument('--max-linearized-residual',type=float,default=5e-3)
    p.add_argument('--direction-step',type=float,default=1e-6)
    a=p.parse_args();a.smoke=False;a.focus=False;a.bisection_steps=5;a.dense_phase_points=31;a.max_brackets=8;run(a)
