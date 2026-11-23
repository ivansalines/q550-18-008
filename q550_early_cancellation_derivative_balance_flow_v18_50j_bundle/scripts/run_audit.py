#!/usr/bin/env python3
"""Q550 v18.50j: derivative ledger for the v18.50i early-response vector split.

Postprocessing of authenticated 11D Q550 data; NO new physical integrations.
The derivative is with respect to model evolution coordinate Delta-xi, NOT
physical strain or an invariant clock. The decomposition is chart-dependent.
"""
from __future__ import annotations
import csv, io, json, zipfile, hashlib, math, argparse, platform
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
PARENT='q550_early_cancellation_balance_metric_robustness_v18_50i_bundle'
ARCHIVE=ROOT/'inputs'/f'{PARENT.replace("_bundle", "_authenticated_bundle")}.zip'


def authenticated_parent_rows():
    # Never accept an unauthenticated CSV as numerical evidence.
    with zipfile.ZipFile(ARCHIVE) as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f'Parent ZIP CRC failed: {bad}')
        root=PARENT+'/'
        names=set(z.namelist())
        manifest=json.loads(z.read(root+'SHA256SUMS.json'))
        assert manifest['root']==PARENT and manifest['version']=='v18.50i'
        expected={root+x for x in manifest['files']}|{root+'SHA256SUMS.json'}
        if names!=expected: raise RuntimeError('Parent manifest does not cover all ZIP entries')
        for short,sha in manifest['files'].items():
            if '..' in Path(short).parts or Path(short).is_absolute(): raise RuntimeError('Unsafe member path')
            if hashlib.sha256(z.read(root+short)).hexdigest()!=sha:
                raise RuntimeError('Parent hash mismatch: '+short)
        report=json.loads(z.read(root+'results/report.json'))
        rows=list(csv.DictReader(io.StringIO(z.read(root+'results/early_metric_amplitude_trace.csv').decode('utf-8'))))
    return rows,report,len(manifest['files'])


def curve_C(b,c):
    return 1.-np.sqrt(np.maximum(0.,1.+b*b+2.*b*c))/(1.+b)


def derivative_terms(b,c,bprime,cprime):
    """Exact differential of C(b,c) along an observed curve.

    Cancellation C=1-sqrt(1+b^2+2bc)/(1+b), b=||T||/||L||, c=cos(L,T).
    Splits dC/dxi into the norm-balance and orientation terms.
    """
    S=np.sqrt(1+b*b+2*b*c)
    if not S>1e-10: raise RuntimeError('Degenerate resultant / undefined derivative')
    coef_b=S/(1+b)**2-(b+c)/(S*(1+b))
    coef_c=-b/(S*(1+b))
    return coef_b*bprime,coef_c*cprime


def crossing(spline,target,t):
    vals=spline(t)-target
    ids=np.flatnonzero(vals[:-1]*vals[1:]<0)
    if not len(ids):return float('nan'),None
    # The first crossing is selected; do not infer uniqueness between samples.
    j=int(ids[0]);return float(brentq(lambda x: float(spline(x)-target),float(t[j]),float(t[j+1]))), [float(t[j]),float(t[j+1])]


def derivative_root(bsp,csp,lo,hi):
    def f(x):
        b,c=float(bsp(x)),float(csp(x))
        db,dc=float(bsp.derivative()(x)),float(csp.derivative()(x))
        u,v=derivative_terms(b,c,db,dc)
        return u+v
    if f(lo)*f(hi)>0:return float('nan')
    return float(brentq(f,lo,hi,xtol=1e-14))


def analysis(rows, parent):
    groups=defaultdict(list)
    for row in rows:
        horizon=float(row['horizon_xi'])
        if horizon > .004000000001:continue
        key=(row['kind'],row['metric'],float(row['epsilon']))
        groups[key].append(row)
    summaries=[];ledger=[]
    for (kind,metric,epsilon),raw in sorted(groups.items()):
        raw.sort(key=lambda x:float(x['horizon_xi']))
        t=np.array([float(x['horizon_xi']) for x in raw])
        if len(t)!=161 or t[0]!=0 or np.any(np.diff(t)<=0):
            raise RuntimeError(f'Unexpected grid for {kind}/{metric}/{epsilon}: {len(t)}')
        L=np.array([float(x['L_norm']) for x in raw]);T=np.array([float(x['T_norm']) for x in raw]);R=np.array([float(x['R_norm']) for x in raw])
        B=np.array([float(x['T_over_L']) for x in raw]);C=np.array([float(x['LT_cos']) for x in raw]);cancel=np.array([float(x['cancellation']) for x in raw])
        if np.max(abs(cancel-curve_C(B,C)))>5e-12: raise RuntimeError('Cancellation identity fails')
        if np.max(abs(R-(L+T)*(1-cancel)))>5e-12:raise RuntimeError('Resultant norm identity fails')
        # The first row has T=0, hence c is undefined; derivatives start at t[1].
        tp=t[1:];bp=B[1:];cp=C[1:]
        bs=CubicSpline(tp,bp);cs=CubicSpline(tp,cp)
        los=np.array([derivative_terms(float(b),float(c),float(db),float(dc)) for b,c,db,dc in zip(bp,cp,bs.derivative()(tp),cs.derivative()(tp))])
        bterms,cterms=los[:,0],los[:,1]
        direct_spline=CubicSpline(tp,cancel[1:]);direct=direct_spline.derivative()(tp)
        residual=float(np.max(abs(direct-(bterms+cterms))))
        # Discretized derivatives should agree to first order, but do not assert exact
        # agreement of distinct interpolation schemes. Near the peak the crosscheck is sharp.
        peakidx=int(np.argmax(cancel[1:]))+1
        if peakidx<2 or peakidx>=len(t)-1: peak_bracket=None;peakroot=float('nan')
        else:
            peak_bracket=[float(t[peakidx-1]),float(t[peakidx+1])]
            peakroot=derivative_root(bs,cs,*peak_bracket)
        eqroot,eqbracket=crossing(bs,1.,tp)
        at_ref=peakroot if np.isfinite(peakroot) else t[peakidx]
        bb,cc=float(bs(at_ref)),float(cs(at_ref))
        dr,dc=float(bs.derivative()(at_ref)),float(cs.derivative()(at_ref))
        dnorm,dangle=derivative_terms(bb,cc,dr,dc)
        Rprime=float(CubicSpline(tp,R[1:]).derivative()(at_ref))
        dtotal=dnorm+dangle
        summaries.append(dict(kind=kind,metric=metric,epsilon=epsilon,kappa0=parent['kappa0'][kind],
          sample_peak_xi=float(t[peakidx]),sample_peak_c=float(cancel[peakidx]),peak_bracket=json.dumps(peak_bracket),
          interpolated_stationary_xi=float(peakroot),estimated_peak_c=float(curve_C(bb,cc)),
          norm_parity_xi=float(eqroot),norm_parity_bracket=json.dumps(eqbracket),
          delta_peak_minus_parity_xi=float(peakroot-eqroot),
          ratio_at_stationary=bb,cos_at_stationary=cc,ratio_rate_at_stationary=dr,cos_rate_at_stationary=dc,
          balance_derivative_at_stationary=dnorm,orientation_derivative_at_stationary=dangle,
          total_derivative_at_stationary=dtotal,resultant_norm_rate_at_stationary=Rprime,
          interpolator_derivative_disagreement_max=residual,
          maximum_is_interior=peak_bracket is not None,
          interpolation_only=True))
        for i,z in enumerate(tp):
            ledger.append(dict(kind=kind,metric=metric,epsilon=epsilon,horizon_xi=float(z),
                L_norm=float(L[i+1]),T_norm=float(T[i+1]),R_norm=float(R[i+1]),
                ratio=float(bp[i]),cosine=float(cp[i]),cancellation=float(cancel[i+1]),
                ratio_prime=float(bs.derivative()(z)),cosine_prime=float(cs.derivative()(z)),
                dC_from_balance=float(bterms[i]),dC_from_orientation=float(cterms[i]),
                dC_sum=float(bterms[i]+cterms[i]),dC_direct_spline=float(direct[i]),
                dR_direct_spline=float(CubicSpline(tp,R[1:]).derivative()(z))))
    return summaries,ledger


def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0].keys()));wr.writeheader();wr.writerows(rows)


def plots(summaries,ledger):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=ROOT/'results'
    reference=[x for x in ledger if x['kind']=='original' and x['metric']=='common_parent_c' and abs(x['epsilon']-1e-4)<1e-10]
    auto=[x for x in ledger if x['kind']=='autonomous' and x['metric']=='common_parent_c' and abs(x['epsilon']-1e-4)<1e-10]
    ref=next(x for x in summaries if x['kind']=='original' and x['metric']=='common_parent_c' and abs(x['epsilon']-1e-4)<1e-10)
    for kind,curve in [('original',reference),('autonomous',auto)]:
        t=np.array([z['horizon_xi'] for z in curve])
        c=np.array([z['cancellation'] for z in curve])
        plt.figure(figsize=(9,5.3));plt.plot(t,c*100,label=f'{kind} cancellation')
        s=next(z for z in summaries if z['kind']==kind and z['metric']=='common_parent_c' and abs(z['epsilon']-1e-4)<1e-10)
        if np.isfinite(s['norm_parity_xi']):plt.axvline(s['norm_parity_xi'],linestyle=':',label='||L||=||T||')
        if np.isfinite(s['interpolated_stationary_xi']):plt.axvline(s['interpolated_stationary_xi'],linestyle='--',label='dC/dξ≈0')
        plt.xlabel('Model horizon Δξ');plt.ylabel('Cancellation C (%)');plt.title('Q550: balance and cancellation are distinct events');plt.grid(alpha=.2);plt.legend();plt.tight_layout()
        plt.savefig(out/f'{kind}_event_order.png',dpi=150);plt.close()
    # Derivative decomposition: zero crossing is cancellation rate balance; display near event.
    zz=[x for x in reference if .00055<=x['horizon_xi']<=.0017]
    t=np.array([z['horizon_xi'] for z in zz]);plt.figure(figsize=(9.5,5.5))
    plt.plot(t,[z['dC_from_balance'] for z in zz],label='Norm ratio contribution dC_balance/dξ')
    plt.plot(t,[z['dC_from_orientation'] for z in zz],label='Orientation contribution dC_angle/dξ')
    plt.plot(t,[z['dC_sum'] for z in zz],label='Total dC/dξ',linewidth=2)
    plt.axhline(0,color='gray',linewidth=1)
    plt.axvline(ref['interpolated_stationary_xi'],linestyle=':',color='gray',label='Interpolated stationary point')
    plt.xlabel('Model horizon Δξ');plt.ylabel('Rate of normalized cancellation per Δξ');plt.title('Q550: derivative competition near the early cancellation maximum')
    plt.grid(alpha=.2);plt.legend(fontsize=8);plt.tight_layout();plt.savefig(out/'derivative_competition_reference.png',dpi=150);plt.close()
    # Cross-chart event positions. We do NOT interpret x positions as universal time.
    fig,ax=plt.subplots(figsize=(9.5,5.3));metrics=['common_parent_c','raw_coordinate','angles_weighted_2x','rates_weighted_2x']
    for j,metric in enumerate(metrics):
        for k,kind in enumerate(['original','autonomous']):
            z=next(z for z in summaries if z['kind']==kind and z['metric']==metric and abs(z['epsilon']-1e-4)<1e-10)
            if np.isfinite(z['norm_parity_xi']):ax.scatter(z['norm_parity_xi'],j+(k-.5)*.22,marker='o' if kind=='original' else 's',c='tab:blue')
            if np.isfinite(z['interpolated_stationary_xi']):ax.scatter(z['interpolated_stationary_xi'],j+(k-.5)*.22,marker='o' if kind=='original' else 's',c='tab:orange')
    ax.set_yticks(np.arange(len(metrics)),['Common chart','Raw coordinates','Angles ×2','Rates ×2'])
    ax.invert_yaxis();ax.set_xlabel('Model horizon Δξ');ax.set_title('Parity (blue) versus cancellation stationarity (orange)')
    ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(out/'metric_event_order.png',dpi=150);plt.close(fig)


def main():
    rows,report,checked=authenticated_parent_rows()
    summaries,ledger=analysis(rows,report)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    write_csv(out/'derivative_balance_events.csv',summaries)
    write_csv(out/'derivative_balance_phase_ledger.csv',ledger)
    plots(summaries,ledger)
    focus=[x for x in summaries if x['metric']=='common_parent_c' and abs(x['epsilon']-1e-4)<1e-10]
    data={'version':'v18.50j','title':'Early Cancellation Derivative Balance & Response-Flow Audit',
     'classification':'VERIFIED_PARENT_DERIVATIVE_FLOW_INTERPOLATION_NOT_CONTINUOUS_ROOT_OR_CONSTITUTIVE_PHYSICS_CERTIFICATE',
     'parent_i_sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
     'verified_parent_members':checked,'mode':'authenticated numerical postprocessing, no new Q550 integrations',
     'kappa':report['kappa0'],'rows_consumed':len(rows),'cases':len(summaries),
     'sampled_phase_rows':len(ledger),'reference':focus,
     'assumptions':['C is chart-dependent: no intrinsic energy metric inferred','C derivative is NOT stress derivative',
        'Interpolation uses a cubic spline of 160 positive-time samples, not certified continuous roots',
        'L and T are terms of a coordinate-defined sensitivity split, not independently measured material stresses',
        'Only the relative changes of the coefficients in the decomposition are compared, not physical mechanisms']}
    (out/'report.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print('v18.50j completed | parent manifest:',checked,'| cases:',len(summaries),'| positive rows:',len(ledger))
    for z in focus:print(z['kind'],'parity',z['norm_parity_xi'],'stationary',z['interpolated_stationary_xi'],
         'dC_components',z['balance_derivative_at_stationary'],z['orientation_derivative_at_stationary'],'dR',z['resultant_norm_rate_at_stationary'])

if __name__=='__main__':main()
