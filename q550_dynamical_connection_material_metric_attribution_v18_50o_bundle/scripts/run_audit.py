#!/usr/bin/env python3
"""Q550 v18.50o: build a candidate projected connection from the 10D model RHS.

The connection is computed independently of response vectors L,T,R. Requires the
original v18.50n server sendback (including nested m/l source and physical solver).
This is a chart- and observer-dependent diagnostic, NOT a material Levi-Civita or
kinetic connection. No closure of projected dynamics is assumed.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, io, json, math, platform, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

ROOT=Path(__file__).resolve().parents[1]
N='q550_covariant_velocity_opposition_observer_metric_transport_v18_50n_bundle'
M='q550_resultant_advance_intensity_orientation_rate_v18_50m_bundle'
L='q550_dense_gate_replay_model_gram_metric_v18_50l_bundle'
K='q550_log_balance_orientation_gate_transport_v18_50k_bundle'
PARENT=ROOT/'inputs'/f'{N}_server_sendback.zip'


def digest(data:bytes):return hashlib.sha256(data).hexdigest()

def authenticate(z:zipfile.ZipFile,name:str):
    if z.testzip() is not None:raise RuntimeError(f'ZIP CRC failure: {name}')
    sm=json.loads(z.read(name+'/SOURCE_MANIFEST.json'))
    om=json.loads(z.read(name+'/SHA256SUMS_OUTPUT.json'))
    if sm['root']!=name or ('root' in om and om['root']!=name):raise RuntimeError('Wrong manifest root: '+name)
    for rel,h in sm['files'].items():
        if Path(rel).is_absolute() or '..' in Path(rel).parts:raise RuntimeError('Unsafe source path: '+rel)
        if digest(z.read(f'{name}/{rel}'))!=h:raise RuntimeError('Source mismatch: '+rel)
    for rel,h in om['file_sha256'].items():
        if digest(z.read(f'{name}/{rel}'))!=h:raise RuntimeError('Result mismatch: '+rel)
    return {'source_count':len(sm['files']),'output_count':len(om['file_sha256'])}


def parent_data():
    with zipfile.ZipFile(PARENT) as zn:
        attest_n=authenticate(zn,N)
        mblob=zn.read(f'{N}/inputs/{M}_server_sendback.zip')
        nrep=json.loads(zn.read(f'{N}/results/report.json'))
    with zipfile.ZipFile(io.BytesIO(mblob)) as zm:
        attest_m=authenticate(zm,M)
        lblob=zm.read(f'{M}/inputs/{L}_server_sendback.zip')
    with zipfile.ZipFile(io.BytesIO(lblob)) as zl:
        attest_l=authenticate(zl,L)
        ledger=pd.read_csv(io.BytesIO(zl.read(f'{L}/results/dense_gate_vector_ledger.csv')))
        events=pd.read_csv(io.BytesIO(zl.read(f'{L}/results/dense_gate_event_brackets.csv')))
        lrep=json.loads(zl.read(f'{L}/results/report.json'))
        lscript=zl.read(f'{L}/scripts/run_audit.py')
        kblob=zl.read(f'{L}/inputs/{K}_sendback.zip')
    return {'n':attest_n,'m':attest_m,'l':attest_l,'parent_sha256':digest(PARENT.read_bytes()),'lreport':lrep,'nreport':nrep},ledger,events,lscript,kblob


def angle(a,b,W):
    p=float(a@W@b)/np.sqrt(float(a@W@a)*float(b@W@b))
    return float(np.degrees(np.arccos(np.clip(p,-1.,1.))))


def model_observer(B,alpha):
    A=B@B.T
    strength=np.trace(A)/4.
    W=np.linalg.inv(A+alpha*strength*np.eye(4))
    return W/(np.trace(W)/4)


def projected_transport(B,Bdot,J,rcond):
    # Hidden tangent state is 10D; observable derivative B is 4x10.
    U,s,Vt=np.linalg.svd(B,full_matrices=False)
    thresh=rcond*s[0]
    si=np.where(s>thresh,1/s,0.)
    Bsharp=(Vt.T*si)@U.T
    M=Bdot+B@J
    K=M@Bsharp
    residual=M@(np.eye(10)-Bsharp@B)
    return K,{
        'singular_values':s.tolist(),
        'retained_rank':int(np.sum(s>thresh)),
        'retained_condition':float(s[0]/s[s>thresh][-1]),
        'projection_leakage_fraction':float(np.linalg.norm(residual)/max(np.linalg.norm(M),1e-30)),
        'source_operator_norm':float(np.linalg.norm(M)),
        'projected_operator_norm':float(np.linalg.norm(K)),
        'right_inverse_defect':float(np.linalg.norm(B@Bsharp-np.eye(4)))
    }


def candidate_connection(K,W,Wdot):
    # Dv=v'+Gamma v, with Gamma^T W+W Gamma=Wdot.
    # The skew component is determined by the projected source-driven K,
    # NOT fitted to L,T,R or their derivatives.
    W_inv_KtW=np.linalg.solve(W,K.T@W)
    omega=.5*(K-W_inv_KtW)
    gamma=.5*np.linalg.solve(W,Wdot)-omega
    compatible=gamma.T@W+W@gamma-Wdot
    return gamma,omega,float(np.linalg.norm(compatible)/max(1.,np.linalg.norm(Wdot)))


def response_at(ledger,kind,xi,epsilon=1e-4):
    d=ledger[(ledger.kind==kind)&(ledger.metric=='common_parent_c')&(np.isclose(ledger.epsilon,epsilon))].sort_values('horizon_xi')
    if len(d)!=513:raise RuntimeError('Missing authenticated 513-point response from v18.50l')
    x=d.horizon_xi.to_numpy(float)
    L=np.stack([json.loads(s) for s in d.L_vec]);T=np.stack([json.loads(s) for s in d.T_vec])
    sl=CubicSpline(x,L,axis=0,bc_type='natural');st=CubicSpline(x,T,axis=0,bc_type='natural')
    return sl(xi),st(xi),sl(xi,1),st(xi,1)


def numerical_B(direction,y,state_scales,step):
    B=np.zeros((4,10))
    for j in range(10):
        h=step*state_scales[j]
        shift=np.zeros(11);shift[j]=h
        B[:,j]=(direction(y+shift)-direction(y-shift))/(2*h*state_scales[j])
    return B


def numerical_J(ode,t,z,state_scales,step):
    Jz=np.zeros((10,10))
    for j in range(10):
        h=step*state_scales[j]
        dz=np.zeros(10);dz[j]=h
        Jz[:,j]=(ode(t,z+dz)-ode(t,z-dz))/(2*h)
    return state_scales[:,None]*Jz/state_scales[None,:]


def stage_original_model(lscript,kblob,stage_path):
    """Stage authenticated v18.50l source in temporary workdir; never pack runtime."""
    lroot=stage_path/L
    (lroot/'scripts').mkdir(parents=True)
    (lroot/'inputs').mkdir(parents=True)
    (lroot/'scripts/run_audit.py').write_bytes(lscript)
    (lroot/'inputs'/f'{K}_sendback.zip').write_bytes(kblob)
    spec=importlib.util.spec_from_file_location('v18_50o_authentic_l_engine',lroot/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod


def make_engine_args():
    a=argparse.Namespace()
    a.start=.00104;a.end=.00109;a.samples=513;a.epsilons=[1e-4,1e-5]
    a.rtol=3e-12;a.atol=3e-13;a.max_step=1e-4
    a.direction_step=1e-6;a.max_response_error=2e-3
    a.maximum_ledger_error=1e-8;a.maximum_regression=1e-7
    a.maximum_parent_share_difference=2e-6
    a.max_generator_identity_error=1e-7;a.max_linearized_residual=5e-3
    a.smoke=False;a.focus=False;a.bisection_steps=5;a.dense_phase_points=31;a.max_brackets=8
    return a


def compute_model_connection(ex,unit,drpt,kind,events,ledger,creport,args):
    a=make_engine_args();kappa=float(ex.ks[kind]);ramp=.24;shape='beta:2:2'
    des=ex.original_ramp.Design('v18_50o',shape,ramp)
    ev=next(z for z in creport['cases'] if z['kind']==kind and abs(float(z['ramp_xi'])-ramp)<1e-9 and z['shape']==shape and z['metric']=='common')
    event=float(ev['turn_xi'])
    back,turn_ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,kappa,ex.params,ex.slope,ex.omega,ex.turning[kind],a,design=des)
    seed=np.asarray(back(event)[:11],float)
    theta0=float(seed[10]);phase0=ex.clock.cubic_phase_excursion(event,des)
    def theta(t):return theta0-ex.omega*(ex.clock.cubic_phase_excursion(t,des)-phase0)
    def ode(t,z):
        y=np.r_[z,theta(t)]
        return np.asarray(ex.physical.rhs_from_original(y,kappa,ex.params,ex.slope,ex.clock.cubic_clock_sign(t,des),ex.support,ex.audit)[:10],float)
    def hidden(y):
        f,j,_=ex.jet.structural_jet(y,kappa,ex.params,ex.slope)
        return np.asarray([f[2],f[6],(j@f)[2],(j@f)[6]],float)
    cscale=np.asarray(drpt['common_metric_scale_4d'],float)
    direction=lambda y:unit(hidden(y),cscale)
    scale=np.maximum(1.,np.abs(seed[:10]))
    # This IVP is independent of measured L,T; no response direction used for source connection.
    sol=solve_ivp(ode,(event,event+0.001092),seed[:10],method='DOP853',rtol=a.rtol,atol=a.atol,max_step=a.max_step,dense_output=True)
    if not sol.success:raise RuntimeError('Natural driven 10D replay failed: '+sol.message)
    source_records=[];summary=[]
    e=events[(events.kind==kind)&(events.metric=='common_parent_c')&(np.isclose(events.epsilon,1e-4))]
    if len(e)!=1:raise RuntimeError('Missing inherited 50l events')
    ev=e.iloc[0]; parity=float(ev.parity_xi); stationary=float(ev.stationary_xi)
    horizons=[parity,(parity+stationary)/2,stationary]
    for xi in horizons:
        t=event+xi;z=np.asarray(sol.sol(t),float);y=np.r_[z,theta(t)]
        L,T,vL,vT=response_at(ledger,kind,xi)
        for fstep,dt in ((1e-6,1e-6),(2e-6,2e-6)):
            B=numerical_B(direction,y,scale,fstep)
            plus_t,minus_t=t+dt,t-dt
            yp=np.r_[sol.sol(plus_t),theta(plus_t)];ym=np.r_[sol.sol(minus_t),theta(minus_t)]
            Bdot=(numerical_B(direction,yp,scale,fstep)-numerical_B(direction,ym,scale,fstep))/(2*dt)
            J=numerical_J(ode,t,z,scale,fstep)
            source=np.asarray(Bdot+B@J,float)
            for alpha in (0.1,1.0):
                W=model_observer(B,alpha)
                Wp=model_observer(numerical_B(direction,yp,scale,fstep),alpha)
                Wm=model_observer(numerical_B(direction,ym,scale,fstep),alpha)
                Wdot=(Wp-Wm)/(2*dt)
                for rcond in (1e-6,1e-10):
                    K,diag=projected_transport(B,Bdot,J,rcond)
                    gamma,omega,compat=candidate_connection(K,W,Wdot)
                    aL=vL+gamma@L;aT=vT+gamma@T
                    aR=aL+aT
                    R=L+T;vR=vL+vT
                    closure=float(np.linalg.norm(vR-K@R)/max(np.linalg.norm(vR),np.linalg.norm(K@R),1e-30))
                    entry={'kind':kind,'xi':xi,'position': 'parity' if xi==parity else 'stationary' if xi==stationary else 'midpoint',
                        'kappa0':kappa,'observer':'common_4d_model_jet','alpha':alpha,'rcond':rcond,'fd_step':fstep,'time_step':dt,
                        'frozen_angle_deg':angle(vL,vT,W),
                        'model_connection_corrected_angle_deg':angle(aL,aT,W),
                        'fixed_common_angle_deg':angle(vL,vT,np.eye(4)),
                        'model_connection_corrected_dot':float(aL@W@aT),
                        'fixed_metric_uncorrected_dot':float(vL@W@vT),
                        'source_omega_operator_norm':float(np.linalg.norm(omega)),
                        'connection_operator_norm':float(np.linalg.norm(gamma)),
                        'relative_response_closure_error':closure,
                        'source_metric_compatibility_relative_error':compat,
                        'modeled_R_speed':float(np.sqrt(max(0,aR@W@aR))),
                        **diag}
                    source_records.append(entry)
        summary.append({'kind':kind,'kappa0':kappa,'xi':xi,'event':'parity' if xi==parity else 'stationary' if xi==stationary else 'midpoint',
                        'turn_xi':event,'source_method':'natural driven Q550 10D RHS Jacobian + 4D structural jet Jacobian',
                        'new_driven_IVPs':1,'new_natural_seed_replay':1})
        print('SOURCE SAMPLED',kind,'xi',xi,flush=True)
    return source_records,summary,{'kind':kind,'seed_turn_xi':event,'turn_ledger':turn_ledger,'integrator_nfev':int(sol.nfev)}


def preflight_only(pdata,ledger,events):
    """State precisely what the inherited data identify and do not identify."""
    rows=[]
    for kind in ('original','autonomous'):
        e=events[(events.kind==kind)&(events.metric=='common_parent_c')&(np.isclose(events.epsilon,1e-4))].iloc[0]
        L,T,vL,vT=response_at(ledger,kind,float(e.stationary_xi))
        X=np.column_stack((L,T))
        s=np.linalg.svd(X,compute_uv=False)
        rows.append({'kind':kind,'xi':float(e.stationary_xi),'observable_dimension':4,'measured_probe_vectors':2,
                     'probe_rank':int(np.linalg.matrix_rank(X)),'unconstrained_linear_map_dimensions_at_least':int(4*(4-np.linalg.matrix_rank(X))),
                     'probe_condition_number':float(s[0]/s[-1]),'uncorrected_velocity_angle_deg':angle(vL,vT,np.eye(4))})
    return rows


def write_csv(rows,path):
    df=pd.DataFrame(rows)
    df.to_csv(path,index=False,float_format='%.17g')


def plot(rows,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    df=pd.DataFrame(rows)
    fig,ax=plt.subplots(figsize=(10,5.2))
    colors={'original':'tab:blue','autonomous':'tab:orange'}
    for kind in ('original','autonomous'):
        for rcond,style,label in ((1e-6,'-','rank 3'),(1e-10,':','rank 4')):
            d=df[(df.kind==kind)&np.isclose(df.alpha,.1)&np.isclose(df.rcond,rcond,rtol=1e-8,atol=0)&np.isclose(df.fd_step,1e-6,rtol=1e-8,atol=0)].sort_values('xi')
            ax.plot(d.xi,d.model_connection_corrected_angle_deg,'o'+style,color=colors[kind],label=kind+' '+label)
        d=df[(df.kind==kind)&np.isclose(df.alpha,.1)&np.isclose(df.rcond,1e-6,rtol=1e-8,atol=0)&np.isclose(df.fd_step,1e-6,rtol=1e-8,atol=0)].sort_values('xi')
        ax.plot(d.xi,d.frozen_angle_deg,'s--',color=colors[kind],alpha=.35,label=kind+' frozen metric')
    ax.axhline(90,c='0.3',ls=':',lw=1)
    ax.set(xlabel='Model evolution offset Δξ',ylabel='Angle between derivative contributions (degrees)',title='Q550 v18.50o — Source-derived connection: rank choice matters')
    ax.grid(alpha=.2);ax.legend(fontsize=8,ncol=2);fig.tight_layout();fig.savefig(out/'model_source_connection_angles.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5.2))
    d=df[(np.isclose(df.alpha,.1))&np.isclose(df.fd_step,1e-6,rtol=1e-8,atol=0)]
    for kind in ('original','autonomous'):
        for rcond in (1e-6,1e-10):
            z=d[(d.kind==kind)&np.isclose(d.rcond,rcond,rtol=1e-8,atol=0)].sort_values('xi')
            ax.plot(z.xi,z.projection_leakage_fraction,'o-',label=f'{kind} cutoff={rcond:g}')
    ax.set(xlabel='Model evolution offset Δξ',ylabel='Unclosed-generator fraction (Frobenius)',title='Q550 v18.50o — Hidden-complement / cutoff leakage')
    ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'observer_projection_leakage.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.5,5.2))
    d=df[(df.position=='stationary')&np.isclose(df.fd_step,1e-6,rtol=1e-8,atol=0)&(df.kind=='original')]
    labels=['Gram 0.1, rank 3','Gram 0.1, rank 4','Gram 1, rank 3','Gram 1, rank 4']
    vals=[]
    for alpha,rcond in ((.1,1e-6),(.1,1e-10),(1.,1e-6),(1.,1e-10)):
        z=d[np.isclose(d.alpha,alpha)&np.isclose(d.rcond,rcond,rtol=1e-8,atol=0)]
        vals.append(float(z.model_connection_corrected_angle_deg.iloc[0]))
    ax.bar(labels,vals)
    for i,v in enumerate(vals):ax.text(i,v+2,f'{v:.2f}°',ha='center',fontsize=9)
    ax.axhline(159.78518,ls='--',c='.35',lw=1,label='v18.50n common fixed 159.785°')
    ax.set(ylabel='Model-connected derivative angle (degrees)',title='The weak observer singular direction changes the candidate connection',ylim=(0,190))
    ax.tick_params(axis='x',rotation=10);ax.legend(fontsize=9)
    fig.tight_layout();fig.savefig(out/'rank_metric_sensitivity.png',dpi=150);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preflight-only',action='store_true',help='Check source chain and identification rank; no physics replay')
    p.add_argument('--keep-runtime',action='store_true',help='Keep extracted intermediate historical runtime; may exceed 1.4 GB')
    a=p.parse_args()
    out=ROOT/'results';out.mkdir(exist_ok=True)
    pdata,ledger,events,lscript,kblob=parent_data()
    preflight=preflight_only(pdata,ledger,events)
    write_csv(preflight,out/'identifiability_preflight.csv')
    if a.preflight_only:
        print('v18.50o PREFLIGHT PASS',json.dumps({'parent_chain':{k:pdata[k] for k in ('n','m','l')},'identifiability':preflight},indent=2))
        return
    runtime=ROOT/'runtime'
    if a.keep_runtime:
        runtime.mkdir(parents=True,exist_ok=True)
        temp_context=None;temp_path=runtime
    else:
        temp_context=tempfile.TemporaryDirectory(prefix='q550_50o_',dir=str(ROOT))
        temp_path=Path(temp_context.name)
    records=[];summ=[];replays=[]
    try:
        lmod=stage_original_model(lscript,kblob,temp_path)
        print('STAGING AND AUTHENTICATING ORIGINAL Q550 MODEL ...',flush=True)
        Experiment,unit,central,drpt,ireport,jreport,kreport,genealogy=lmod.stage_authenticated()
        ex=Experiment(make_engine_args())
        # Use the parent verified natural-turn event; no user response defines a moving frame.
        droot,_,_=sys.modules['verify_parent_d'].verify()
        creport=json.loads((droot/'runtime/q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle/results/report.json').read_text())
        for kind in ('original','autonomous'):
            r,s,prov=compute_model_connection(ex,unit,drpt,kind,events,ledger,creport,a)
            records.extend(r);summ.extend(s);replays.append(prov)
    finally:
        if temp_context is not None:
            print('CLEANING temporary historical solver runtime ...',flush=True)
            temp_context.cleanup()
    if len(records)!=48:raise RuntimeError('Expected 2 kappa × 3 events × 2 FD × 2 metrics × 2 rank cutoffs = 48 rows')
    if any(d['source_metric_compatibility_relative_error']>2e-8 for d in records):raise RuntimeError('Metric compatibility defect')
    write_csv(records,out/'dynamical_connection_ledger.csv')
    write_csv(summ,out/'dynamical_event_sections.csv')
    plot(records,out)
    report={
        'version':'v18.50o',
        'title':'Dynamical Connection & Material-Metric Attribution Audit',
        'classification':'MODEL_RHS_DERIVED_CANDIDATE_CONNECTION_NOT_UNIQUE_PHYSICAL_MATERIAL_TRANSPORT',
        'parent':{k:pdata[k] for k in ('n','m','l','parent_sha256')},
        'protocol':{'replays':'original nonautonomous Q550 10D RHS with separately prepared natural turning states',
            'model_jacobian':'finite-difference 10D RHS in fixed seed-normalized chart',
            'observer_jacobian':'finite-difference original 4D structural jet observable',
            'observer_time_derivative':'along unperturbed physical RHS trajectory',
            'source_model_operator':'M=Bdot + B @ J_10D',
            'projected_K':'M Bsharp with truncated SVD right inverse',
            'metric_W':'normalized (B B^T + alpha tr(BB^T)/4 I)^-1, alpha 0.1 or 1',
            'connection':'Gamma=1/2 W^-1 Wdot - 1/2 (K-W^-1 K^T W)',
            'metric_compatibility':'Gamma^T W + W Gamma=Wdot',
            'rcond':[1e-6,1e-10], 'state_fd_steps':[1e-6,2e-6], 'time_steps':[1e-6,2e-6]},
        'counts':{'connection_measurements':len(records),'new_natural_seed_replays':2,'new_driven_10D_ivps':2},
        'identifiability':preflight,'natural_replays':replays,
        'summary':{'max_metric_compatibility_error':float(max(d['source_metric_compatibility_relative_error'] for d in records)),
          'min_observable_singular_value':float(min(min(d['singular_values']) for d in records)),
          'max_projection_leakage':float(max(d['projection_leakage_fraction'] for d in records)),
          'min_projection_leakage':float(min(d['projection_leakage_fraction'] for d in records)),
          'max_response_closure_error':float(max(d['relative_response_closure_error'] for d in records)),
          'stationary_original_angles':[{ 'alpha':v['alpha'],'rcond':v['rcond'],'retained_rank':v['retained_rank'],
             'candidate_angle_deg':v['model_connection_corrected_angle_deg'], 'frozen_angle_deg':v['frozen_angle_deg']}
             for v in records if v['kind']=='original' and v['position']=='stationary' and v['fd_step']==1e-6]},
        'limitations':[
          'The initial 10D state-space Euclidean metric is set in a declared seed-normalized chart; it is not derived from measured kinetic energy.',
          'The output Gram observer, its inverse metric, SVD threshold and temporal differentiation are conventions. No unique physical material metric or connection is identified.',
          'The local/transport response decomposition has only two 4D vectors; 4D transport is underdetermined absent the 10D model.',
          'Projecting 10D linearized dynamics onto 4D can have a nonzero hidden-complement source; closure residual is reported, not suppressed.',
          'The computed connection uses model RHS and observable, not L/T/R direction, but is still observer/chart dependent.',
          'Sensitivity angles are not spatial torsion, stress, strain, or material memory; link to polymers/metallic glasses remains conceptual.',
          'Finite differencing and interpolation have numerical errors; no interval enclosures or continuous unique-root proof.'
        ], 'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('v18.50o COMPLETED',json.dumps(report['summary'],indent=2),flush=True)

if __name__=='__main__':main()
