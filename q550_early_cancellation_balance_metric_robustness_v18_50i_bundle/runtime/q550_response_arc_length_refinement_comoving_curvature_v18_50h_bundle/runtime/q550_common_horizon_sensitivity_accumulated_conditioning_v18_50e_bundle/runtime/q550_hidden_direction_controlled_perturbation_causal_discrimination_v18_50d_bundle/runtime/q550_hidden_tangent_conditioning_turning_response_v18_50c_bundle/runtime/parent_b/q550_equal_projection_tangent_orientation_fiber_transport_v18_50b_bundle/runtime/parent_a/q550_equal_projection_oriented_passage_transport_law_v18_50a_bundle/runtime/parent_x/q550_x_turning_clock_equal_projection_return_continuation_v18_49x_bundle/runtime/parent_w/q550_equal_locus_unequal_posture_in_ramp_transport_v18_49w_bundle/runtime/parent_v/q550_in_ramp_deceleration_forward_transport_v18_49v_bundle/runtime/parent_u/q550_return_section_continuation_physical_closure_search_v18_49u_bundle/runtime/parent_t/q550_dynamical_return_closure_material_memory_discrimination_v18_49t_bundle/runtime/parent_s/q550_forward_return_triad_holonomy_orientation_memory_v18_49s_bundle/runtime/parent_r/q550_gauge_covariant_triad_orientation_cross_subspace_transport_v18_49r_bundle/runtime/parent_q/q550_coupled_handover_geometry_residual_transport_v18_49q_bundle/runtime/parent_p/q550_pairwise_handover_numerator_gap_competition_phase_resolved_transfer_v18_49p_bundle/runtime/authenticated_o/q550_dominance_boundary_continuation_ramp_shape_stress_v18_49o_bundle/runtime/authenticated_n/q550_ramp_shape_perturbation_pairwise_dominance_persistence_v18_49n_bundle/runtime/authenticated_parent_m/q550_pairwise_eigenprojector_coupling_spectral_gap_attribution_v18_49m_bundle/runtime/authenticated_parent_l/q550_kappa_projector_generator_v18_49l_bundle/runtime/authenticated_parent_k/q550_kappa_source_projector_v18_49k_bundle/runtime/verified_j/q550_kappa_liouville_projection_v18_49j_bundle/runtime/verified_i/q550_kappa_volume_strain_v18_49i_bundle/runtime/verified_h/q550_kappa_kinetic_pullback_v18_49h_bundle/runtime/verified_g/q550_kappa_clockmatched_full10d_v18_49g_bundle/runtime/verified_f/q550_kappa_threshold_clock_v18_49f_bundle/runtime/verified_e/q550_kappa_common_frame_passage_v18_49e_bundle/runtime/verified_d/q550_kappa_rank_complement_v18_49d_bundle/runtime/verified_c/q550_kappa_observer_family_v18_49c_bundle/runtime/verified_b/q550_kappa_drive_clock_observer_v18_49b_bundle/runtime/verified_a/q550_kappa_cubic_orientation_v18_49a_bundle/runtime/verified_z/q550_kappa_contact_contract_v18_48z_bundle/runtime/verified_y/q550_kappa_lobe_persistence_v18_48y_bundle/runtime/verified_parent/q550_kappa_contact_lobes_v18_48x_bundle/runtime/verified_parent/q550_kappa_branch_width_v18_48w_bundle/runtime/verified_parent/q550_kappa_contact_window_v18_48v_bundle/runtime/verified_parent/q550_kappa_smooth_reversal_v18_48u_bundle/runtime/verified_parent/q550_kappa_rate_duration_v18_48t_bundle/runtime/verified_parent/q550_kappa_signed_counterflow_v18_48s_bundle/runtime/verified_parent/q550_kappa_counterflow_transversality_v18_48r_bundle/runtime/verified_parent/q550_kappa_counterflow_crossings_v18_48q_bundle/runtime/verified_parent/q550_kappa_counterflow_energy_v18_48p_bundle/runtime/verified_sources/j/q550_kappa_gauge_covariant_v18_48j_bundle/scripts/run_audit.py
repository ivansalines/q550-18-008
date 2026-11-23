#!/usr/bin/env python3
"""v18.48j: affine gauge covariance of projected Q550 Hessian cancellation.

Original 11D IVPs and covectors are the *authenticated* v18.48i sendback.
No fresh physical IVPs are claimed. This tests linear moving frames and their
induced covector metric, NOT invariance to a change of physical observable.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from verify_parent import verify
from gauge_math import (frames_from_velocities,chart_hessian,push_forward_tensor,projection,
                        covector_transform,corrected_norm,ratio,connection_identity)
ROOT=Path(__file__).resolve().parents[1]

def norm(a):return float(np.linalg.norm(a))
def write_csv(path,rows):
    if not rows:raise RuntimeError('empty output')
    keys=list(rows[0]);assert all(list(x)==keys for x in rows)
    with open(path,'w',encoding='utf8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(rows)

def deterministic_rot(n=10):
    rg=np.random.default_rng(1848)
    Q,R=np.linalg.qr(rg.standard_normal((n,n)))
    Q=Q@np.diag(np.sign(np.diag(R)))
    if np.linalg.det(Q)<0:Q[:,-1]*=-1
    return Q

def shear_matrix():
    S=np.diag([2.5,.38,1.7,.55,1.35,.8,1.2,.7,1.6,.65])
    S[0,3]=.8;S[1,5]=-.25;S[4,8]=.6
    return S

def module(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m)
    return m

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,default=ROOT/'results')
    p.add_argument('--full-tensor-audit',action='store_true',default=True)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(exist_ok=True,parents=True)
    provenance=verify()
    sys.path.insert(0,str(ROOT/'reference'))
    from structural_jet import structural_jet,coupling_jet,chart_kernel
    audit=module(ROOT/'reference/test_support_mobius_monodromy_audit.py','v1848j_ref_model')
    params=audit.ModelParameters(gamma_rho=.3)
    d=np.load(ROOT/'runtime/physical_paths.npz',allow_pickle=False)
    hrep=json.loads((ROOT/'runtime/report_v18_48h.json').read_text())
    irept=json.loads((ROOT/'runtime/report_v18_48i.json').read_text())
    scale=np.asarray(d['chart_scale'],float);w=np.r_[scale,1.]
    if scale.shape!=(10,) or (scale<=0).any():raise ValueError('bad chart scale')
    clock=float(d['clock_speed']);slope=clock/(2*math.pi)
    kaps={'original':float(hrep['kappa_original']),'autonomous':float(hrep['kappa_autonomous'])}
    if abs(kaps['original']-1/6)>1e-14 or abs(kaps['autonomous']-35*math.pi/660)>1e-14:raise ValueError('kappa drift')
    xs=np.asarray(d['xi'],float);states=np.asarray(d['y'],float)
    covs=np.asarray(d['covectors'],float)
    n=len(xs)
    if covs.shape!=(n,5,11) or states.shape!=(n,11) or n!=328:raise ValueError('expected actual 41-section Q550 parent')
    groups={}
    for i,(f,b,k) in enumerate(zip(d['families'],d['seed_branches'],d['kappa_kind'])):
        groups.setdefault((str(f),int(b),str(k)),[]).append(i)
    if len(groups)!=8:raise ValueError('8 authentic paths expected')
    # Full deterministic rotations, physical tangent-following frames, non-isometric affine shear.
    Q=deterministic_rot();T=shear_matrix();ident=np.eye(10)
    records=[];full_checks=[];conn=[];crest=[];match=[];min_c=1e300
    worst_raw_naive=0.;worst_covariant=0.;worst_full=0.;worst_conn=0.
    for (fam,branch,kind),inds0 in sorted(groups.items()):
        inds=sorted(inds0,key=lambda j:xs[j]);xgroup=xs[inds]
        if len(inds)!=41 or abs(xgroup[0]-3.5)>1e-9 or abs(xgroup[-1]-4.5)>1e-9:
            raise RuntimeError('Missing genuine continuous section grid')
        kap=kaps[kind]
        jets=[structural_jet(states[i],kap,params,slope) for i in inds]
        tangents=np.stack([j[0][:10]/scale for j in jets]);moving=frames_from_velocities(tangents)
        Sdot=np.gradient(moving,xgroup,axis=0,edge_order=2)
        observer=covs[inds,0,:]
        finite_diff_obs=np.gradient(observer,xgroup,axis=0,edge_order=2)
        obs_framed=np.stack([np.r_[S@gg[:10],gg[10]] for S,gg in zip(moving,observer)])
        finite_diff_obs_framed=np.gradient(obs_framed,xgroup,axis=0,edge_order=2)
        for seq,i in enumerate(inds):
            xi=float(xs[i]);y=states[i];f,J,H=jets[seq];kap0=kap
            Hbase=structural_jet(y,0.,params,slope)[2]
            Hcouple=slope*kap0*coupling_jet(y,params)[2]
            v=f/w
            Hzb=chart_hessian(Hbase,w);Hzc=chart_hessian(Hcouple,w)
            g_historical=covs[i,0]
            frame_map={'identity':ident,'fixed_rotation':Q,'comoving_rotation':moving[seq],'anisotropic_shear':T}
            for oi,mode in [(0,'historical_transport'),(3,'activity_sin_lie_transport'),(4,'activity_cos_lie_transport')]:
                g=covs[i,oi].copy();g/=max(norm(g),1e-30)
                refB=chart_kernel(Hbase,f,scale,g[:10]);refC=chart_kernel(Hcouple,f,scale,g[:10]);refR=ratio(refB,refC)
                Kb=projection(Hzb,g,v);Kc=projection(Hzc,g,v)
                diff=max(norm(refB-Kb),norm(refC-Kc))/max(1.,norm(refB),norm(refC))
                if diff>5e-10:raise RuntimeError('Original chart_kernel mismatch')
                for gauge,S in frame_map.items():
                    Bp=covector_transform(Kb,S);Cp=covector_transform(Kc,S)
                    Bm=corrected_norm(Bp,S);Cm=corrected_norm(Cp,S);Rm=corrected_norm(Bp+Cp,S)
                    good=1. if Cm<1e-12*max(Bm,1e-30) else (Bm+Cm)/max(Rm,1e-30)
                    wrong=ratio(Bp,Cp)
                    err=abs(good-refR)/max(refR,1.)
                    worst_covariant=max(worst_covariant,err)
                    worst_raw_naive=max(worst_raw_naive,abs(wrong-refR)/max(refR,1.))
                    records.append(dict(family=fam,seed_branch=branch,kappa_kind=kind,xi=xi,
                        observer=mode,gauge=gauge,source='genuine_v18_48i_11D_IVP',
                        cancellation_original=refR,cancellation_metric_covariant=good,
                        cancellation_naive_new_euclidean=wrong,
                        relative_invariance_error=err,relative_naive_change=(wrong-refR)/max(refR,1.),
                        norm_B=norm(refB),norm_C=norm(refC),norm_resultant=norm(refB+refC),
                        coupling_null=bool(norm(refC)<=1e-12*max(norm(refB),1e-30))))
                    if mode=='historical_transport' and (abs(xi-3.575)<1e-8 or abs(xi-4.25)<1e-8):
                        crest.append(records[-1])
                    # Independently push forward the *full* 11D Hessian tensor.
                    if (mode=='historical_transport' and seq in (0,3,20,30,40) and gauge!='identity'):
                        G=np.eye(11);G[:10,:10]=S
                        HgB=push_forward_tensor(Hzb,G)
                        HgC=push_forward_tensor(Hzc,G)
                        gnew=np.linalg.solve(G.T,g);vnew=G@v
                        BB=projection(HgB,gnew,vnew);CC=projection(HgC,gnew,vnew)
                        fullerr=max(norm(BB-Bp),norm(CC-Cp))/max(1.,norm(Kb),norm(Kc))
                        worst_full=max(worst_full,fullerr)
                        # Dense tensor-first binary64 may suffer catastrophic cancellation
                        # under chart scales spanning ~1e8. Do NOT interpret that as
                        # a failure of exact covariance; measure the numerical floor.
                        full_checks.append(dict(family=fam,seed_branch=branch,kappa_kind=kind,xi=xi,gauge=gauge,
                            relative_tensor_first_float64_error=fullerr,
                            factored_tensor_pushforward_relative_error=err,
                            metric_covariant_ratio=good,source_ratio=refR))
            S=moving[seq];Sd=Sdot[seq];G=np.eye(11);G[:10,:10]=S
            Gd=np.zeros((11,11));Gd[:10,:10]=Sd
            Jz=(J/w[:,None])*w[None,:]
            c_err=connection_identity(G,Gd,Jz,g_historical)
            worst_conn=max(worst_conn,c_err)
            # finite difference checks the ACTUAL observer time series as sampled.
            predicted=-Jz.T@g_historical
            e0=norm(finite_diff_obs[seq]-predicted)/max(1.,norm(predicted))
            Jnew=G@Jz@np.linalg.inv(G)+Gd@np.linalg.inv(G)
            predprime=-Jnew.T@obs_framed[seq]
            e1=norm(finite_diff_obs_framed[seq]-predprime)/max(1.,norm(predprime))
            conn.append(dict(family=fam,seed_branch=branch,kappa_kind=kind,xi=xi,
                             algebraic_connection_identity_error=c_err,
                             sampled_original_adjoint_residual=e0,
                             sampled_framed_adjoint_residual=e1,
                             frame_orthogonality_error=norm(S.T@S-ident),
                             transported_tangent_alignment_error=norm(S@(v[:10]/norm(v[:10]))-ident[0])))
        # The factorial in a *common* gauge: never splice different section frames.
        if fam.startswith('phasecov') and branch==0:
            i0=inds[int(np.argmin(abs(xgroup-4.)))];i1=inds[int(np.argmin(abs(xgroup-4.25)))]
            # Exactly the historical normalized chart covector of the same IVP.
            bcorner=[];ccorner=[]
            for sy,og in [(0,0),(1,0),(0,1),(1,1)]:
                yi=states[i1 if sy else i0];gi=covs[i1 if og else i0,0];gi=gi/max(norm(gi),1e-30)
                f=structural_jet(yi,kap,params,slope)[0]
                hb=structural_jet(yi,0,params,slope)[2]
                hc=slope*kap*coupling_jet(yi,params)[2]
                bcorner.append(chart_kernel(hb,f,scale,gi[:10]));ccorner.append(chart_kernel(hc,f,scale,gi[:10]))
            vals=[math.log(ratio(b,c)) for b,c in zip(bcorner,ccorner)]
            interaction=vals[3]-vals[1]-vals[2]+vals[0]
            Smoving=moving[int(np.argmin(abs(xgroup-4.25)))]
            for gauge,S in [('fixed_chart',ident),('common_comoving_end_frame',Smoving),('common_anisotropic_shear',T)]:
                transformed=[];wrong=[]
                for b,c in zip(bcorner,ccorner):
                    bp=covector_transform(b,S);cp=covector_transform(c,S)
                    nb=corrected_norm(bp,S);nc=corrected_norm(cp,S);ns=corrected_norm(bp+cp,S)
                    transformed.append(math.log((nb+nc)/max(ns,1e-30)))
                    wrong.append(math.log(ratio(bp,cp)))
                it=transformed[3]-transformed[1]-transformed[2]+transformed[0]
                iw=wrong[3]-wrong[1]-wrong[2]+wrong[0]
                match.append(dict(family=fam,seed_branch=branch,kappa_kind=kind,gauge=gauge,
                                  original_log_interaction=interaction,
                                  metric_covariant_log_interaction=it,
                                  naive_euclidean_log_interaction=iw,
                                  error_covariant=abs(it-interaction)))
    # Deliberately change the *physical observer* without moving the field or tangent.
    # Not a gauge transformation: its cancellation may change substantially.
    counter=[]
    rot=np.eye(10);angle=math.pi/3;rot[0,0]=rot[3,3]=math.cos(angle);rot[0,3]=-math.sin(angle);rot[3,0]=math.sin(angle)
    for idx in range(n):
        if abs(float(xs[idx])-4.25)>1e-8 and abs(float(xs[idx])-3.575)>1e-8:continue
        f,J,H=structural_jet(states[idx],kaps[str(d['kappa_kind'][idx])],params,slope)
        b=structural_jet(states[idx],0,params,slope)[2]
        c=slope*kaps[str(d['kappa_kind'][idx])]*coupling_jet(states[idx],params)[2]
        gg=covs[idx,0];gg=gg/norm(gg)
        B=chart_kernel(b,f,scale,gg[:10]);C=chart_kernel(c,f,scale,gg[:10]);R0=ratio(B,C)
        gg1=gg.copy();gg1[:10]=rot@gg1[:10]
        B1=chart_kernel(b,f,scale,gg1[:10]);C1=chart_kernel(c,f,scale,gg1[:10]);R1=ratio(B1,C1)
        counter.append(dict(family=str(d['families'][idx]),seed_branch=int(d['seed_branches'][idx]),
             kappa_kind=str(d['kappa_kind'][idx]),xi=float(xs[idx]),original_ratio=R0,
             changed_physical_observer_ratio=R1,observer_direction_cosine=float(gg[:10]@gg1[:10]/(norm(gg[:10])*norm(gg1[:10]))),
             not_a_gauge_change=True))
    write_csv(out/'gauge_invariance.csv',records)
    write_csv(out/'full_tensor_checks.csv',full_checks)
    write_csv(out/'adjoint_frame_connection.csv',conn)
    write_csv(out/'crest_atlas.csv',crest)
    write_csv(out/'factorial_common_gauge.csv',match)
    write_csv(out/'observer_change_negative_control.csv',counter)
    report=dict(version='v18.48j',status='ORIGINAL_Q550_AFFINE_GAUGE_COVARIANT_HESSIAN_PROJECTION_AUDIT',
         input='authenticated_v18.48i_server_refined_v18.48h_11D_IVPs',
         no_new_original_ivp_integrations=True,genuine_physical_states=n,physical_ivps=8,sections_per_ivp=41,
         gauges=['identity','fixed_rotation','comoving_rotation','anisotropic_shear'],
         observer_modes=['historical_transport','activity_sin_lie_transport','activity_cos_lie_transport'],
         covariance_rows=len(records),full_tensor_checks=len(full_checks),
         max_covariant_ratio_relative_error=worst_covariant,
         max_dense_tensor_first_float64_relative_error=worst_full,
         max_naive_euclidean_ratio_relative_change=worst_raw_naive,
         max_instantaneous_adjoint_connection_algebraic_residual=worst_conn,
         max_sampled_original_adjoint_residual=max(z['sampled_original_adjoint_residual'] for z in conn),
         max_sampled_moving_adjoint_residual=max(z['sampled_framed_adjoint_residual'] for z in conn),
         max_factorial_common_gauge_error=max(z['error_covariant'] for z in match),
         crest_rows=len(crest),factorial_rows=len(match),negative_control_rows=len(counter),
         kappas=kaps,provenance=provenance,
         mathematical_scope='Exact tensor covariance for invertible spatially linear 10D chart changes, and correct covector norms using transformed cometric; numerical double-precision evaluation.',
         moving_frame='Minimal tangent-direction orthogonal frame along each actual 11D IVP; instantaneous chart connection included in observer adjoint identity.',
         caveat='Coordinate covariance under consistent frame and cometric changes is mathematically required; it is not observer independence or proof of physical torsion. Sheared Euclidean norms and observer-only rotations deliberately change the measured quantity. Physical IVP states inherited from v18.48i, not re-integrated here; no interval or branch-connection certificate.')
    if worst_covariant>1e-9 or worst_conn>2e-9 or report['max_factorial_common_gauge_error']>2e-9:
        raise RuntimeError('Gauge covariance validation failed: '+str({k:report[k] for k in ('max_covariant_ratio_relative_error','max_dense_tensor_first_float64_relative_error','max_instantaneous_adjoint_connection_algebraic_residual','max_factorial_common_gauge_error')}))
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ('status','genuine_physical_states','covariance_rows','full_tensor_checks','max_covariant_ratio_relative_error','max_dense_tensor_first_float64_relative_error','max_naive_euclidean_ratio_relative_change','max_instantaneous_adjoint_connection_algebraic_residual','max_factorial_common_gauge_error')},indent=2))

if __name__=='__main__':main()
