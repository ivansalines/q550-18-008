#!/usr/bin/env python3
"""v18.50l: NEW dense physical RHS replays, event brackets and model-jet Gram metric.

Nested parent v18.50k -> v18.50j -> v18.50i -> v18.50h -> v18.50e ->
authentic solver ancestry. Derivative roots are numerical estimates, NOT validated
continuous roots. The Jacobian-Gram metric is an explicit candidate observer metric,
NOT an identified mechanical kinetic metric or an observer-invariant tensor.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,io,json,math,platform,sys,zipfile
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'inputs/q550_log_balance_orientation_gate_transport_v18_50k_bundle_sendback.zip'
KR='q550_log_balance_orientation_gate_transport_v18_50k_bundle'
JR='q550_early_cancellation_derivative_balance_flow_v18_50j_bundle'
IR='q550_early_cancellation_balance_metric_robustness_v18_50i_bundle'

def sha(data):return hashlib.sha256(data).hexdigest()

def stage_authenticated():
    """Read-only nested ZIP authenticity; stage only original i for its tested engine."""
    kbytes=INPUT.read_bytes()
    with zipfile.ZipFile(io.BytesIO(kbytes)) as kz:
        if kz.testzip():raise RuntimeError('Invalid parent k ZIP CRC')
        sm=json.loads(kz.read(KR+'/SOURCE_MANIFEST.json'))
        assert sm['root']==KR and sm['version']=='v18.50k'
        for name,expected in sm['files'].items():
            if name.startswith('/') or '..' in Path(name).parts:raise RuntimeError('unsafe k manifest')
            if sha(kz.read(KR+'/'+name))!=expected:raise RuntimeError('k immutable member drift: '+name)
        om=json.loads(kz.read(KR+'/SHA256SUMS_OUTPUT.json'))
        for name,expected in om['file_sha256'].items():
            if sha(kz.read(KR+'/'+name))!=expected:raise RuntimeError('k output drift: '+name)
        kreport=json.loads(kz.read(KR+'/results/report.json'))
        jbytes=kz.read(KR+'/inputs/q550_early_cancellation_derivative_balance_flow_v18_50j_server_sendback.zip')
        jpins=json.loads(kz.read(KR+'/inputs/SOURCE_PINS.json'))
        if sha(jbytes)!=jpins['parent_server_zip_sha256']:raise RuntimeError('k/j pinned ZIP mismatch')
    with zipfile.ZipFile(io.BytesIO(jbytes)) as jz:
        if jz.testzip():raise RuntimeError('Invalid j ZIP CRC')
        i_bytes=jz.read(JR+'/inputs/q550_early_cancellation_balance_metric_robustness_v18_50i_authenticated_bundle.zip')
        jreport=json.loads(jz.read(JR+'/results/report.json'))
    dest=ROOT/'runtime'/IR
    with zipfile.ZipFile(io.BytesIO(i_bytes)) as iz:
        if iz.testzip():raise RuntimeError('Invalid i ZIP CRC')
        m=json.loads(iz.read(IR+'/SHA256SUMS.json'))
        if m['root']!=IR or m['version']!='v18.50i':raise RuntimeError('Unrecognized i input')
        for name,expected in m['files'].items():
            if sha(iz.read(IR+'/'+name))!=expected:raise RuntimeError('i member hash drift: '+name)
        dest.mkdir(parents=True,exist_ok=True)
        for name in iz.namelist():
            rel=Path(name).relative_to(IR)
            if not rel.parts:continue
            p=dest/rel
            if name.endswith('/'):p.mkdir(parents=True,exist_ok=True);continue
            if p.exists() and sha(p.read_bytes())==sha(iz.read(name)):continue
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(iz.read(name))
        ireport=json.loads(iz.read(IR+'/results/report.json'))
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v18_50i_engine',dest/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    Experiment,unit,central_directional,ereport,drpt,anc,rows,hreport=mod.authenticate()
    return Experiment,unit,central_directional,drpt,ireport,jreport,kreport,{'k_zip_sha256':sha(kbytes),'j_zip_sha256':sha(jbytes),'i_zip_sha256':sha(i_bytes),'k_source_entries':len(sm['files']),'k_output_entries':len(om['file_sha256']),'i_verified_entries':len(m['files'])}

def write_csv(p,rs):
    if not rs:raise ValueError('Empty '+str(p))
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)

def geometry(L,T,W):
    a=float(np.sqrt(max(0,L@W@L)));b=float(np.sqrt(max(0,T@W@T)))
    r=float(np.sqrt(max(0,(L+T)@W@(L+T))))
    cos=float((L@W@T)/max(a*b,1e-40))
    return {'L_norm':a,'T_norm':b,'R_norm':r,'b_ratio':b/max(a,1e-40),'c_cos':cos,'angle_deg':math.degrees(math.acos(np.clip(cos,-1,1))), 'cancellation':1-r/max(a+b,1e-40),'LT_dot':float(L@W@T)}

def extract_events(rows):
    """Samples and C2 spline interpolation; uncertainty is a sampled bracket, NOT a proof."""
    x=np.array([r['horizon_xi'] for r in rows])
    ratio=np.array([r['b_ratio'] for r in rows]);cancel=np.array([r['cancellation'] for r in rows]);cos=np.array([r['c_cos'] for r in rows]);R=np.array([r['R_norm'] for r in rows]);
    sb=CubicSpline(x,np.log(ratio));sc=CubicSpline(x,cos);sr=CubicSpline(x,R)
    def balance(t):
        u=float(sb(t));c=float(sc(t));up=float(sb(t,1));cp=float(sc(t,1))
        orient=(-cp)/(2*max(1-c,1e-16))
        penalty=-0.5*math.tanh(u/2)*up
        return orient,penalty,orient+penalty
    def signs_for(vals):
        return [i for i in range(len(vals)-1) if vals[i]==0 or vals[i]*vals[i+1]<0]
    pi=signs_for([float(v) for v in np.log(ratio)])
    di=signs_for([balance(t)[2] for t in x])
    def chosen(indices,fn):
        if not indices:return None
        # The modeled event should be inside the bracket near 0.00106.
        near=sorted(indices,key=lambda k:abs(float((x[k]+x[k+1])/2)-.001065))[0]
        a,b=float(x[near]),float(x[near+1]);return {'bracket':[a,b], 'root':float(brentq(fn,a,b,xtol=5e-16,rtol=9e-16)),'bracket_width':b-a}
    parity=chosen(pi,lambda t:float(sb(t)))
    stationary=chosen(di,lambda t:balance(t)[2])
    npeak=int(np.argmax(cancel));sample_peak=float(x[npeak])
    result={'parity':parity,'stationary':stationary,'sample_peak_xi':sample_peak,'sample_peak_cancel':float(cancel[npeak]),'event_order':bool(parity and stationary and parity['root']<stationary['root'])}
    if parity and stationary:
        for key,t in [('parity',parity['root']),('stationary',stationary['root'])]:
            u=float(sb(t));c=float(sc(t));orient,penalty,net=balance(t)
            result[key].update({'u':u,'cos':c,'theta_deg':float(math.degrees(math.acos(np.clip(c,-1,1)))),'orientation_log_gain':orient,'imbalance_log_cost':penalty,'sum_rate':net,'R_rate':float(sr(t,1)),'cancellation_est':1-math.sqrt(1+math.exp(2*u)+2*math.exp(u)*c)/(1+math.exp(u))})
    return result

def gram_metrics(direction,seed,alpha):
    """Frozen model-induced inverse Gram. Input chart uses prescribed reference scales.

    B= d[normalized hidden-jet]/d[state_0..9] * diag(1/max(1,|seed_i|)).
    W=(B B^T + alpha * trace(B B^T)/4 I)^(-1), normalized so tr(W)/4=1.
    It is an OBSERVER CANDIDATE, not a physical kinetic metric. No affine gauge claim.
    """
    d=np.zeros((4,10))
    input_scales=np.maximum(1,np.abs(seed[:10]))
    for i in range(10):
        s=2e-6*input_scales[i]
        delta=np.zeros(11);delta[i]=s
        d[:,i]=(direction(seed+delta)-direction(seed-delta))/(2*s)* (1/input_scales[i])
    gram=d@d.T
    strength=float(np.trace(gram)/4)
    if strength<=1e-14:raise RuntimeError('Degenerate observable Gram')
    w=np.linalg.inv(gram+alpha*strength*np.eye(4));w=w/(np.trace(w)/4)
    eig=np.linalg.eigvalsh(w)
    if eig[0]<=0:raise RuntimeError('Nonpositive model-jet candidate metric')
    return w,{'alpha':alpha,'input_scale_rule':'input_j=max(1,|seed_j|); B_j=dDirection/dstate_j / input_j', 'gram_eigenvalues':np.linalg.eigvalsh(gram).tolist(),'metric_eigenvalues':eig.tolist(),'metric_condition_number':float(eig[-1]/eig[0])}

def run(args):
    Experiment,unit,central,drpt,ireport,jreport,kreport,genealogy=stage_authenticated()
    ex=Experiment(args)
    cscale=np.asarray(drpt['common_metric_scale_4d'],float)
    kinds=('original','autonomous')
    n=args.samples
    if n<65 or (n-1)%8:raise ValueError('Require at least 65 samples and nested grid divisions')
    grid=np.linspace(args.start,args.end,n)
    epslist=[float(x) for x in args.epsilons]
    rows=[]; summaries=[];checks=[];metric_meta={};ivps=0
    # Event ledger from authenticated v18.50k is used ONLY as comparison, never as a seed.
    historic={kind:kreport['reference' if kind=='original' else 'autonomous'] for kind in kinds}
    droot=Path(sys.modules['verify_parent_d'].__file__).resolve().parents[1]
    droot,_,_=sys.modules['verify_parent_d'].verify()
    croot=droot/'runtime'/'q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle'
    creport=json.loads((croot/'results/report.json').read_text())
    for kind in kinds:
        kappa=float(ex.ks[kind]);ramp=.24; shape='beta:2:2'
        des=ex.original_ramp.Design('v18_50l',shape,ramp)
        ev=next(z for z in creport['cases'] if z['kind']==kind and abs(float(z['ramp_xi'])-ramp)<1e-9 and z['shape']==shape and z['metric']=='common')
        event=float(ev['turn_xi'])
        back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,kappa,ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=des)
        seed=np.asarray(back(event)[:11],float)
        th0=float(seed[10]);phi0=ex.clock.cubic_phase_excursion(event,des)
        def theta(t):return th0-ex.omega*(ex.clock.cubic_phase_excursion(t,des)-phi0)
        def ode(t,z):
            y=np.r_[z,theta(t)]
            return ex.physical.rhs_from_original(y,kappa,ex.params,ex.slope,ex.clock.cubic_clock_sign(t,des),ex.support,ex.audit)[:10]
        def hidden(y):
            f,j,_=ex.jet.structural_jet(y,kappa,ex.params,ex.slope)
            return np.asarray([f[2],f[6],(j@f)[2],(j@f)[6]],float)
        # Frozen observer at natural turning seed; output Gram is from model jet.
        direction=lambda y:unit(hidden(y),cscale)
        raw_direction=lambda y:unit(hidden(y),np.ones(4))
        metrics={'common_parent_c':np.eye(4),'model_jet_gram_alpha_0p1':None,'model_jet_gram_alpha_1':None}
        for alpha,name in [(.1,'model_jet_gram_alpha_0p1'),(1.,'model_jet_gram_alpha_1')]:
            w,md=gram_metrics(direction,seed,alpha);metrics[name]=w;metric_meta[kind+'_'+name]=md
        times=np.r_[event,event+grid];times=np.unique(times)
        sol={}
        for e in sorted(set([0.]+epslist)):
            for sign in ([0] if e==0 else [-1,1]):
                initial=seed[:10].copy();initial[8]+=sign*e
                s=solve_ivp(ode,(float(times[0]),float(times[-1])),initial,t_eval=times,method='DOP853',rtol=args.rtol,atol=args.atol,max_step=args.max_step)
                ivps+=1
                if not s.success:raise RuntimeError(f'IVP failed {kind} epsilon={e} sign={sign} {s.message}')
                sol[(sign,e)]=np.asarray(s.y).T
        for eps in epslist:
            for ii,h in enumerate(grid):
                ind=ii+1
                t=event+float(h)
                y=np.r_[sol[(0,0.)][ind],theta(t)]
                zp=np.r_[sol[(1,eps)][ind],theta(t)]
                zm=np.r_[sol[(-1,eps)][ind],theta(t)]
                tangent=(zp-zm)/(2*eps)
                unit_basis=np.zeros(11);unit_basis[8]=1
                for observer,chart in [('common',direction),('raw',raw_direction)]:
                    L=central(chart,y,unit_basis,args.direction_step)
                    T=central(chart,y,tangent-unit_basis,args.direction_step)
                    rivp=(chart(zp)-chart(zm))/(2*eps)
                    err=float(np.linalg.norm((L+T)-rivp)/max(1,np.linalg.norm(rivp)))
                    if err>args.max_response_error:raise RuntimeError('Finite response/linearization mismatch '+repr((kind,h,err)))
                    Ws=metrics if observer=='common' else {'raw_coordinate':np.eye(4)}
                    for mname,W in Ws.items():
                        g=geometry(L,T,W)
                        rows.append({'kind':kind,'kappa0':kappa,'metric':mname,'epsilon':eps,'horizon_xi':float(h),**g,
                                     'linearized_vs_ivp_error':err,'L_vec':json.dumps(L.tolist()),'T_vec':json.dumps(T.tolist()),'tangent_x_logit':float(tangent[8])})
        checks.append({'kind':kind,'kappa0':kappa,'event_xi':event,'turn_ledger':ledger})
        print('REPLAY COMPLETE',kind,'kappa',kappa,'IVPs',len(sol),flush=True)
    assert len(rows)==len(kinds)*len(epslist)*len(grid)*4
    for kind in kinds:
        for eps in epslist:
            for metric in ('common_parent_c','raw_coordinate','model_jet_gram_alpha_0p1','model_jet_gram_alpha_1'):
                series=sorted((z for z in rows if z['kind']==kind and z['epsilon']==eps and z['metric']==metric),key=lambda r:r['horizon_xi'])
                e=extract_events(series)
                # Nested grid (513 vs 257 vs 129 samples) checks discretization on SAME numerical IVP.
                nested={}
                for stride in (1,2,4):
                    if (len(series)-1)%stride:continue
                    ee=extract_events(series[::stride]);nested[str(len(series[::stride]))]={'parity':ee['parity']['root'] if ee['parity'] else None,'stationary':ee['stationary']['root'] if ee['stationary'] else None,'delay':ee['stationary']['root']-ee['parity']['root'] if ee['event_order'] else None}
                record={'kind':kind,'epsilon':eps,'metric':metric,'has_parity':e['parity'] is not None,'has_stationary':e['stationary'] is not None,
                    'event_order':e['event_order'],'parity_xi':e['parity']['root'] if e['parity'] else '',
                    'stationary_xi':e['stationary']['root'] if e['stationary'] else '',
                    'delay_xi':e['stationary']['root']-e['parity']['root'] if e['event_order'] else '',
                    'parity_sample_bracket':json.dumps(e['parity']['bracket']) if e['parity'] else '',
                    'stationary_sample_bracket':json.dumps(e['stationary']['bracket']) if e['stationary'] else '',
                    'max_sample_cancel':e['sample_peak_cancel'],'sample_peak_xi':e['sample_peak_xi'],
                    'orientation_log_gain_at_stationary':e['stationary']['orientation_log_gain'] if e['stationary'] else '',
                    'imbalance_log_cost_at_stationary':e['stationary']['imbalance_log_cost'] if e['stationary'] else '',
                    'resultant_rate_at_stationary':e['stationary']['R_rate'] if e['stationary'] else '',
                    'parity_theta_deg':e['parity']['theta_deg'] if e['parity'] else '',
                    'stationary_theta_deg':e['stationary']['theta_deg'] if e['stationary'] else '',
                    'historical_k_stationary_xi':historic[kind]['stationary_xi'] if metric=='common_parent_c' else '',
                    'event_mesh_convergence':json.dumps(nested,sort_keys=True)}
                summaries.append(record)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    write_csv(out/'dense_gate_vector_ledger.csv',rows)
    write_csv(out/'dense_gate_event_brackets.csv',summaries)
    write_csv(out/'turn_replay_checks.csv',checks)
    ref=next(z for z in summaries if z['kind']=='original' and z['metric']=='common_parent_c' and z['epsilon']==1e-4)
    auto=next(z for z in summaries if z['kind']=='autonomous' and z['metric']=='common_parent_c' and z['epsilon']==1e-4)
    if not ref['event_order'] or not auto['event_order']:raise RuntimeError('Physical replay lost event sequence in reference chart')
    if float(ref['resultant_rate_at_stationary'])<=0 or float(auto['resultant_rate_at_stationary'])<=0:raise RuntimeError('Resultant no longer advancing')
    diff=max(abs(float(x['stationary_xi'])-float(historic[x['kind']]['stationary_xi'])) for x in (ref,auto))
    if diff>5e-6:raise RuntimeError('Unexpected departure from historical spline: '+str(diff))
    report={'version':'v18.50l','title':'Dense-Gate Physical Replay & Model-Jet Gram Metric Audit','classification':'NEW_SHORT_MODEL_RHS_REPLAYS_DENSE_EVENT_BRACKETS_NOT_KINETIC_METRIC_OR_CERTIFIED_CONTINUOUS_ROOT',
        'genealogy':genealogy,'kappa0':{k:float(ex.ks[k]) for k in kinds},
        'protocol':{'ramp_xi':.24,'shape':'beta:2:2','start':args.start,'end':args.end,'samples':n,'epsilons':epslist,'rtol':args.rtol,'atol':args.atol,'max_step':args.max_step,'direction_step':args.direction_step,'kick_state_component':8,'model_jet_gram_regularizations':[.1,1.]},
        'counts':{'short_10D_driven_clock_ivps':ivps,'dense_vector_rows':len(rows),'cases':len(summaries),'physical_natural_seed_replays':2},
        'checks':{'max_common_stationary_difference_from_interpolated_k':diff,'reference_event_order':ref['event_order'],'autonomous_event_order':auto['event_order'],'max_linearized_vs_ivp_error':max(z['linearized_vs_ivp_error'] for z in rows)},
        'reference':ref,'autonomous':auto,'observer_metric_meta':metric_meta,
        'limitations':['New short integrations of the authentic model RHS, not an independent experimental material law.',
            'The two kappa families begin from separately prepared natural turning seeds; do not interpret their agreement as a same-state physical experiment.',
            'Model-jet Gram is a frozen, regularized, coordinate-dependent candidate observer metric. It is NOT proven to be kinetic/physical/covariant.',
            'Event brackets are based on densely sampled numerical trajectories; spline root is NOT a mathematically certified continuous root.',
            'A sign-balanced derivative of a chosen normalized cancellation functional does not certify conserved energy or a material memory law.',
            'The plasticity and polymer/metallic-glass analogy is conceptual, not a constitutive identification.'],
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    plot(report,rows,summaries)
    print('v18.50l COMPLETED',json.dumps({'ivps':ivps,'rows':len(rows),'original':{k:ref[k] for k in ('parity_xi','stationary_xi','delay_xi')},'autonomous':{k:auto[k] for k in ('parity_xi','stationary_xi','delay_xi')},'historical_max_diff':diff},indent=2),flush=True)
    return report

def plot(report,rows,summaries):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=ROOT/'results'
    fig,ax=plt.subplots(figsize=(9,5))
    for kind in ('original','autonomous'):
        z=sorted((x for x in rows if x['kind']==kind and x['metric']=='common_parent_c' and x['epsilon']==1e-4),key=lambda x:x['horizon_xi'])
        ax.plot([x['horizon_xi'] for x in z],[100*x['cancellation'] for x in z],label=kind)
        ev=next(x for x in summaries if x['kind']==kind and x['metric']=='common_parent_c' and x['epsilon']==1e-4)
        for key,sym in [('parity_xi','o'),('stationary_xi','x')]:
            t=ev[key]
            if t!='':ax.axvline(t,ls=':' if sym=='o' else '--',alpha=.35)
    ax.set(xlabel='Model evolution horizon Delta xi',ylabel='Cancellation (%)',title='Dense NEW Q550 replay: near-parity passage')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(dest/'dense_replay_both_kappa.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for metric in ('common_parent_c','raw_coordinate','model_jet_gram_alpha_0p1','model_jet_gram_alpha_1'):
        z=sorted((x for x in rows if x['kind']=='original' and x['metric']==metric and x['epsilon']==1e-4),key=lambda x:x['horizon_xi'])
        ax.plot([x['horizon_xi'] for x in z],[100*x['cancellation'] for x in z],label=metric)
    ax.set(xlabel='Model evolution horizon Delta xi',ylabel='Cancellation (%)',title='Metric sensitivity: chart versus model-jet observer candidates')
    ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(dest/'metric_comparison_dense_replay.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for kind in ('original','autonomous'):
        z=sorted((x for x in rows if x['kind']==kind and x['metric']=='common_parent_c' and x['epsilon']==1e-4),key=lambda x:x['horizon_xi'])
        ax.plot([x['horizon_xi'] for x in z],[x['b_ratio'] for x in z],label=kind+' ratio')
    ax.axhline(1,color='0.4',ls=':');ax.set(xlabel='Model evolution horizon Delta xi',ylabel='||T||/||L||',title='Dense ratio crossings precede cancellation stationarity')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(dest/'dense_balance_ratio.png',dpi=160);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',type=float,default=.00104)
    p.add_argument('--end',type=float,default=.00109)
    p.add_argument('--samples',type=int,default=513)
    p.add_argument('--epsilons',nargs='+',type=float,default=[1e-4,1e-5])
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=1e-4)
    p.add_argument('--direction-step',type=float,default=1e-6)
    p.add_argument('--max-response-error',type=float,default=2e-3)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum-parent-share-difference',type=float,default=2e-6)
    p.add_argument('--max-generator-identity-error',type=float,default=1e-7)
    p.add_argument('--max-linearized-residual',type=float,default=5e-3)
    a=p.parse_args();a.smoke=False;a.focus=False;a.bisection_steps=5;a.dense_phase_points=31;a.max_brackets=8
    run(a)
