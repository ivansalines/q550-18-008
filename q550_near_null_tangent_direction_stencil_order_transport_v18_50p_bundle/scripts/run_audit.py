#!/usr/bin/env python3
"""Q550 v18.50p: test weak observer singular direction vs centered-FD truncation.

This stage does not assume that the fourth 4x10 observer singular direction
is a physical tangent mode. It verifies the authenticated v18.50o parent,
checks h^2 scaling, then independently reconstructs the 10D natural trajectory
and scans observer Jacobians using multiple 2nd/4th-order stencils. A local
10D linearized transport check is also performed in a declared state chart.
Comments, reports, and source documents intentionally remain in English.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, io, json, os, platform, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
O = 'q550_dynamical_connection_material_metric_attribution_v18_50o_bundle'
PARENT=ROOT/'inputs'/f'{O}_server_sendback.zip'


def sha(data): return hashlib.sha256(data).hexdigest()


def verify_parent():
    with zipfile.ZipFile(PARENT) as z:
        if z.testzip() is not None: raise RuntimeError('Parent CRC mismatch')
        for manifest,field in (('SOURCE_MANIFEST.json','files'),('SHA256SUMS_OUTPUT.json','file_sha256')):
            dat=json.loads(z.read(f'{O}/{manifest}'))
            for path,expected in dat[field].items():
                if sha(z.read(f'{O}/{path}'))!=expected: raise RuntimeError('Parent digest mismatch: '+path)
        pre=pd.read_csv(io.BytesIO(z.read(f'{O}/results/dynamical_connection_ledger.csv')))
        o_script=z.read(f'{O}/scripts/run_audit.py')
        n_path='q550_covariant_velocity_opposition_observer_metric_transport_v18_50n_bundle_server_sendback.zip'
        n_blob=z.read(f'{O}/inputs/{n_path}')
        parent_report=json.loads(z.read(f'{O}/results/report.json'))
    return pre,o_script,n_blob,parent_report


def old_scaling(rows):
    out=[]
    for (kind,position),grp in rows.groupby(['kind','position']):
        d=grp[(np.isclose(grp.alpha,0.1))&(grp.rcond<1e-8)].sort_values('fd_step')
        if len(d)!=2: raise RuntimeError('Historical 2-step SVD missing')
        x,y=[json.loads(s) for s in d.singular_values]
        low,high=[float(x) for x in d.fd_step]
        ratio=y[-1]/x[-1]
        out.append({'kind':kind,'position':position,'small_step':low,'large_step':high,
                    's4_small':x[-1],'s4_large':y[-1],'s4_ratio':ratio,
                    'h_ratio':high/low,'h2_prediction':(high/low)**2,
                    'small_s4_over_s1':x[-1]/x[0],
                    'large_s4_over_s1':y[-1]/y[0],
                    's4_zero_intercept_h2_model':(y[-1]*low**2-x[-1]*high**2)/(low**2-high**2)})
    return out


def stage_o(o_script,n_blob,tmp):
    stage=Path(tmp)/O
    (stage/'scripts').mkdir(parents=True,exist_ok=True)
    (stage/'inputs').mkdir(parents=True,exist_ok=True)
    (stage/'scripts/run_audit.py').write_bytes(o_script)
    (stage/'inputs/q550_covariant_velocity_opposition_observer_metric_transport_v18_50n_bundle_server_sendback.zip').write_bytes(n_blob)
    spec=importlib.util.spec_from_file_location('q550_v18_50p_authenticated_o',stage/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    return mod


def make_context(o,kind,engine,unit,drpt,creport):
    a=o.make_engine_args();ramp=.24;shape='beta:2:2';kappa=float(engine.ks[kind])
    des=engine.original_ramp.Design('v18_50p',shape,ramp)
    entries=[z for z in creport['cases'] if z['kind']==kind and abs(float(z['ramp_xi'])-ramp)<1e-9 and z['shape']==shape and z['metric']=='common']
    if len(entries)!=1: raise RuntimeError('Could not identify the natural turning section')
    event=float(entries[0]['turn_xi'])
    back,turn_ledger=engine.original.integrate(engine.physical,engine.clock,engine.support,engine.audit,kappa,engine.params,engine.slope,engine.omega,engine.turning[kind],a,design=des)
    seed=np.asarray(back(event)[:11],float)
    theta0=float(seed[10]);phase0=engine.clock.cubic_phase_excursion(event,des)
    def theta(t):return theta0-engine.omega*(engine.clock.cubic_phase_excursion(t,des)-phase0)
    def ode(t,z):
        y=np.r_[z,theta(t)]
        return np.asarray(engine.physical.rhs_from_original(y,kappa,engine.params,engine.slope,engine.clock.cubic_clock_sign(t,des),engine.support,engine.audit)[:10],float)
    def hidden(y):
        f,j,_=engine.jet.structural_jet(y,kappa,engine.params,engine.slope)
        return np.asarray([f[2],f[6],(j@f)[2],(j@f)[6]],float)
    cscale=np.asarray(drpt['common_metric_scale_4d'],float)
    direction=lambda y:unit(hidden(y),cscale)
    scale=np.maximum(1.,np.abs(seed[:10]))
    sol=solve_ivp(ode,(event,event+0.001092),seed[:10],method='DOP853',rtol=a.rtol,atol=a.atol,max_step=a.max_step,dense_output=True)
    if not sol.success:raise RuntimeError('10D natural IVP failed: '+sol.message)
    return {'kind':kind,'kappa0':kappa,'event':event,'turn_ledger':turn_ledger,'seed':seed.tolist(),
            'sol':sol,'theta':theta,'ode':ode,'direction':direction,'scale':scale,'nfev':sol.nfev}


def obs_jac(o,ctx,xi,step):
    t=ctx['event']+xi
    z=np.asarray(ctx['sol'].sol(t),float)
    y=np.r_[z,ctx['theta'](t)]
    return o.numerical_B(ctx['direction'],y,ctx['scale'],step)


def svd_stats(B):
    U,s,Vt=np.linalg.svd(B,full_matrices=False)
    return U,s,Vt


def sign_free_cos(a,b):
    return float(abs(np.dot(a,b))/max(np.linalg.norm(a)*np.linalg.norm(b),1e-300))


def compute_dense(o,ctx,events,segments,steps):
    kind=ctx['kind']
    ev=events[(events.kind==kind)&(events.metric=='common_parent_c')&(np.isclose(events.epsilon,1e-4))]
    if len(ev)!=1:raise RuntimeError('Parent event missing')
    parity=float(ev.iloc[0].parity_xi);station=float(ev.iloc[0].stationary_xi)
    xi_grid=np.linspace(parity,station,segments)
    jacobians={};rows=[];transport=[]
    for idx,xi in enumerate(xi_grid):
        Bs={h:obs_jac(o,ctx,float(xi),h) for h in steps}
        # Two fourth-order Richardson estimates constructed from the same authentic observer.
        rich={(h/2): (4*Bs[h/2]-Bs[h])/3 for h in steps if h/2 in Bs}
        for meth,collection in (('central_2',Bs),('richardson_4',rich)):
            for h,B in collection.items():
                _,s,Vt=svd_stats(B)
                rows.append({'kind':kind,'kappa0':ctx['kappa0'],'xi':xi,'section_index':idx,
                             'method':meth,'h':h,'s1':s[0],'s2':s[1],'s3':s[2],'s4':s[3],
                             's4_over_s1':s[3]/s[0], 'smallest_direction':json.dumps(Vt[-1,:].tolist()),
                             'strong_projector_trace':float(np.sum(Vt[:3,:]**2))})
        jacobians[idx]=Bs
    # Use h=1e-6 as the baseline stencil, plus corrected 4th-order comparison.
    h0=1e-6
    if h0 not in jacobians[0]:raise RuntimeError('missing h=1e-6 base')
    _,_,Vt0=svd_stats(jacobians[0][h0]);q0=Vt0[-1].copy()
    # A numerical tangent vector is advanced using the model's 10D J, independently of measured L,T.
    def q_ode(t,q):
        z=np.asarray(ctx['sol'].sol(t),float)
        J=o.numerical_J(ctx['ode'],t,z,ctx['scale'],1e-6)
        return J@q
    t0=ctx['event']+parity;t1=ctx['event']+station
    qsol=solve_ivp(q_ode,(t0,t1),q0,method='DOP853',rtol=3e-11,atol=3e-12,
                   max_step=max((t1-t0)/4,1e-8),dense_output=True)
    if not qsol.success:raise RuntimeError('Tangent transport IVP failed')
    for idx,xi in enumerate(xi_grid):
        B=jacobians[idx][h0]
        U,s,Vt=svd_stats(B)
        q=Vt[-1]
        qt=np.asarray(qsol.sol(ctx['event']+xi),float);qt/=np.linalg.norm(qt)
        q_rich=svd_stats((4*jacobians[idx][1e-6]-jacobians[idx][2e-6])/3)[2][-1]
        q_small=svd_stats(jacobians[idx][5e-7])[2][-1]
        q_2h=svd_stats(jacobians[idx][2e-6])[2][-1]
        strong=Vt[:3].T@Vt[:3]
        transport.append({'kind':kind,'kappa0':ctx['kappa0'],'xi':xi,'section_index':idx,
                          'baseline_s4':s[-1], 'transported_q_to_local_weak_abs_cos':sign_free_cos(qt,q),
                          'stencil_2h_to_h_weak_abs_cos':sign_free_cos(q_2h,q),
                          'richardson_to_h_weak_abs_cos':sign_free_cos(q_rich,q),
                          'smallh_to_h_weak_abs_cos':sign_free_cos(q_small,q),
                          'transported_q_observer_norm':float(np.linalg.norm(B@qt)),
                          'local_weak_observer_norm':float(np.linalg.norm(B@q)),
                          'transported_q_strong_subspace_fraction':float(np.linalg.norm(strong@qt)),
                          'transported_q_norm':float(np.linalg.norm(qsol.sol(ctx['event']+xi)))})
    return rows,transport,{'kind':kind,'kappa0':ctx['kappa0'],'turn_xi':ctx['event'],'parity':parity,'stationary':station,
                            'new_seed_replay':1,'new_natural_ivp':1,'new_tangent_ivp':1,
                            'natural_ivp_nfev':ctx['nfev'],'tangent_ivp_nfev':qsol.nfev}


def plots(old,dense,transport,dest):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    z=pd.DataFrame(old);d=pd.DataFrame(dense);t=pd.DataFrame(transport)
    fig,ax=plt.subplots(figsize=(9,5))
    for kind in ('original','autonomous'):
        a=z[(z.kind==kind)&(z.position=='stationary')].iloc[0]
        ax.loglog([a.small_step,a.large_step],[a.s4_small,a.s4_large], 'o-',label=kind+' 2-point parent')
    ax.set(xlabel='Centered FD step h',ylabel='Fourth observer singular value s4',title='Q550 v18.50p — The inherited weak singular value scales as h²')
    ax.grid(alpha=.2,which='both');ax.legend();fig.tight_layout();fig.savefig(dest/'historical_quadratic_scaling.png',dpi=150);plt.close(fig)
    if d.empty: return
    fig,ax=plt.subplots(figsize=(9,5))
    for kind in ('original','autonomous'):
        a=d[(d.kind==kind)&(d.method=='central_2')&(d.section_index==len(d[d.kind==kind].section_index.unique())-1)]
        b=d[(d.kind==kind)&(d.method=='richardson_4')&(d.section_index==len(d[d.kind==kind].section_index.unique())-1)]
        ax.loglog(a.h,a.s4,'o-',label=kind+' second order')
        ax.loglog(b.h,b.s4,'s--',label=kind+' Richardson')
    ax.set(xlabel='Normalized state FD step',ylabel='Smallest singular value s4',title='Q550 v18.50p — Stencil-order test at stationary section')
    ax.grid(alpha=.2,which='both');ax.legend();fig.tight_layout();fig.savefig(dest/'stencil_order_near_null.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for kind in ('original','autonomous'):
        a=t[t.kind==kind].sort_values('xi')
        ax.plot(a.xi,a.transported_q_to_local_weak_abs_cos,'o-',label=kind+' transported/local')
        ax.plot(a.xi,a.richardson_to_h_weak_abs_cos,':',label=kind+' Richardson/local')
    ax.set(xlabel='Evolution offset Δξ',ylabel='Absolute cosine in declared 10D chart',ylim=(0,1.03),
           title='Q550 v18.50p — Tracking weak SVD direction (not a physical mode)')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(dest/'weak_direction_10d_transport.png',dpi=150);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preflight-only',action='store_true',help='Run authenticated historical h² test only; no physical integration')
    p.add_argument('--points',type=int,default=17)
    p.add_argument('--keep-runtime',action='store_true',help='Retain temporary 1.4GB genealogical expansion for debugging')
    a=p.parse_args()
    if a.points<3:raise RuntimeError('points must be >= 3')
    out=ROOT/'results';out.mkdir(exist_ok=True)
    history,o_source,n_blob,oreport=verify_parent()
    old=old_scaling(history)
    pd.DataFrame(old).to_csv(out/'historical_stencil_scaling.csv',index=False,float_format='%.17g')
    ratios=[x['s4_ratio'] for x in old]
    print('v18.50p AUTHENTICATED PARENT',json.dumps({'source':11,'outputs':7,'h2_s4_ratios':ratios}),flush=True)
    dense=[];transport=[];replays=[]
    if not a.preflight_only:
        with tempfile.TemporaryDirectory(prefix='q550_50p_',dir=str(ROOT)) as temp:
            temp=Path(temp)
            o=stage_o(o_source,n_blob,temp)
            pdata,ledger,events,lscript,kblob=o.parent_data()
            lmod=o.stage_original_model(lscript,kblob,temp)
            print('STAGING AUTHENTICATED ORIGINAL 10D Q550 SOLVER ...',flush=True)
            Experiment,unit,central,drpt,ireport,jreport,kreport,genealogy=lmod.stage_authenticated()
            ex=Experiment(o.make_engine_args())
            droot,_,_=sys.modules['verify_parent_d'].verify()
            creport=json.loads((droot/'runtime/q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle/results/report.json').read_text())
            # h pairs are exact dyadic multiples for Richardson construction.
            steps=[2.5e-7,5e-7,1e-6,2e-6,4e-6]
            for kind in ('original','autonomous'):
                print('REPLAYING ORIGINAL Q550 10D',kind,flush=True)
                ctx=make_context(o,kind,ex,unit,drpt,creport)
                rows,tr,rep=compute_dense(o,ctx,events,a.points,steps)
                dense+=rows;transport+=tr;replays.append(rep)
                print('10D WEAK DIRECTION COMPLETE',kind,'samples',len(tr),flush=True)
            if a.keep_runtime:
                # Kept runtime is intentionally not supported with TemporaryDirectory.
                print('WARNING: keep-runtime requested, but stage remains safely temporary',flush=True)
        pd.DataFrame(dense).to_csv(out/'ten_d_stencil_singular_spectrum.csv',index=False,float_format='%.17g')
        pd.DataFrame(transport).to_csv(out/'weak_direction_tangent_transport.csv',index=False,float_format='%.17g')
    plots(old,dense,transport,out)
    summ={
        'version':'v18.50p',
        'title':'Near-Null 10D Tangent Direction & Stencil-Order Provenance Audit',
        'classification':'NUMERICAL_WEAK_OBSERVER_MODE_UNDER_STENCIL_AUDIT_NOT_MATERIAL_DIRECTION_CERTIFICATE',
        'parent_sha256':sha(PARENT.read_bytes()),
        'parent_classification':oreport['classification'],
        'historical_h2_scaling_ratios':ratios,
        'historical_max_abs_ratio_minus_4':max(abs(r-4) for r in ratios),
        'counts':{'preflight_six_sections':len(old),'dense_svd_rows':len(dense),'ten_d_transport_rows':len(transport)},
        'replays':replays,
        'diagnostics':{},
        'limitations':[
            'The smallest right-singular direction of a 4x10 Jacobian is chart- and stencil-dependent and not automatically a physical or material mode.',
            'A fourth singular value scaling approximately as h² is consistent with centered-difference truncation and may indicate an exact rank-3 observer map.',
            'No exact rank claim follows from two h points, a finite series of stencil steps, or a finite-difference Richardson extrapolation.',
            'The 10D tangent transport uses a declared Euclidean normalized chart, not a kinetic metric from a Lagrangian.',
            'Separate original/autonomous seeds mean their 10D singular vectors are not directly gauge-matched.',
            'No continuous unique-root proof, material memory certificate, physical torsion or stress law is claimed.'
        ],
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}
    }
    if dense:
        d=pd.DataFrame(dense);t=pd.DataFrame(transport)
        summ['diagnostics']={
            'central_s4_range':[float(d[d.method=='central_2'].s4.min()),float(d[d.method=='central_2'].s4.max())],
            'richardson_s4_range':[float(d[d.method=='richardson_4'].s4.min()),float(d[d.method=='richardson_4'].s4.max())],
            'transported_q_abs_cos_range':[float(t.transported_q_to_local_weak_abs_cos.min()),float(t.transported_q_to_local_weak_abs_cos.max())],
            'richardson_vs_central_abs_cos_range':[float(t.richardson_to_h_weak_abs_cos.min()),float(t.richardson_to_h_weak_abs_cos.max())],
            'small_step_ratio_by_kind':{}
        }
        for kind in ('original','autonomous'):
            a=d[(d.kind==kind)&(d.method=='central_2')&(np.isclose(d.h,2e-6,rtol=1e-9,atol=0))].sort_values('section_index')
            b=d[(d.kind==kind)&(d.method=='central_2')&(np.isclose(d.h,1e-6,rtol=1e-9,atol=0))].sort_values('section_index')
            summ['diagnostics']['small_step_ratio_by_kind'][kind]=(a.s4.to_numpy()/b.s4.to_numpy()).tolist()
    (out/'report.json').write_text(json.dumps(summ,indent=2,allow_nan=False)+'\n')
    print('v18.50p COMPLETED',json.dumps({'counts':summ['counts'],'diagnostics':summ['diagnostics']},indent=2),flush=True)

if __name__=='__main__':main()
