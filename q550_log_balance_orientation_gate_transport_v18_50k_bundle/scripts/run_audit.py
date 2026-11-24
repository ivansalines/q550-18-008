#!/usr/bin/env python3
"""v18.50k Log-Balance/Orientation Gate Transport Audit.

Consumes the authenticated v18.50j server sendback. No new physical runs:
this is a structural reformulation and independent algebraic/differential check
of the 4800 recorded v18.50j chart-sensitive vector-sensitivity observations.
All model coordinate derivatives are w.r.t. Delta xi, not material strain.
"""
from __future__ import annotations
import csv,io,json,math,platform,sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

from gate_math import gate_fields
from verify_parent import load_parent

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'

def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

def gf(b,c,bprime,cprime):
    return gate_fields(float(b),float(c),float(bprime),float(cprime))

def main():
    text,events_text,parent,verified,metadata_diffs=load_parent()
    ledger=list(csv.DictReader(io.StringIO(text)))
    events=list(csv.DictReader(io.StringIO(events_text)))
    assert len(ledger)==4800 and len(events)==30
    evmap={(e['kind'],e['metric'],float(e['epsilon'])):e for e in events}
    samples=[];groups=defaultdict(list)
    max_identity_err=0.;max_rate_err=0.;max_curve_err=0.
    for r in ledger:
        k=(r['kind'],r['metric'],float(r['epsilon']))
        t=float(r['horizon_xi']);b=float(r['ratio']);c=float(r['cosine'])
        br=float(r['ratio_prime']);cr=float(r['cosine_prime'])
        g=gf(b,c,br,cr)
        orig_C=float(r['cancellation']);orig_Cprime=float(r['dC_sum'])
        max_identity_err=max(max_identity_err,abs(g['cancellation']-orig_C))
        max_rate_err=max(max_rate_err,abs(g['c_rate']-orig_Cprime))
        g.update(kind=k[0],metric=k[1],epsilon=k[2],horizon_xi=t,
             ratio=b,cosine=c,ratio_rate=br,cosine_rate=cr,
             resultant_rate=float(r['dR_direct_spline']),
             parent_cancellation=orig_C,parent_cancellation_rate=orig_Cprime)
        samples.append(g);groups[k].append(g)
    if max_identity_err>1e-11 or max_rate_err>2e-9:
        raise RuntimeError(f'Geometric identity/rate defect {max_identity_err} {max_rate_err}')

    summaries=[]
    for k,rows in sorted(groups.items()):
        kind,metric,eps=k
        rows.sort(key=lambda x:x['horizon_xi'])
        t=np.array([x['horizon_xi'] for x in rows])
        if len(rows)!=160 or not np.all(np.diff(t)>0):raise RuntimeError('Broken source time grid')
        bb=np.array([x['ratio'] for x in rows]);cc=np.array([x['cosine'] for x in rows])
        bs=CubicSpline(t,bb);cs=CubicSpline(t,cc)
        old=evmap[k]
        parity=float(old['norm_parity_xi']);peak=float(old['interpolated_stationary_xi'])
        has_event=math.isfinite(parity) and math.isfinite(peak)
        if has_event:
            # Parent brentq used default xtol ~2e-12; refine within the SAME
            # cubic spline (not a fresh physical trajectory) to floating precision.
            def bracket(x):
                idx=int(np.searchsorted(t,x))
                return float(t[max(0,idx-1)]),float(t[min(len(t)-1,idx)])
            p0,q0=bracket(parity)
            p1,q1=bracket(peak)
            parity_refined=float(brentq(lambda x:float(bs(x)-1),p0,q0,xtol=5e-16,rtol=9e-16))
            peak_refined=float(brentq(lambda x:gf(bs(x),cs(x),bs.derivative()(x),cs.derivative()(x))['log_gate_rate'],p1,q1,xtol=5e-16,rtol=9e-16))
            if abs(parity_refined-parity)>3e-12 or abs(peak_refined-peak)>3e-12:
                raise RuntimeError('Refined roots disagree with v18.50j')
            parity=parity_refined;peak=peak_refined
            fp=gf(bs(parity),cs(parity),bs.derivative()(parity),cs.derivative()(parity))
            fe=gf(bs(peak),cs(peak),bs.derivative()(peak),cs.derivative()(peak))
            if abs(fp['u'])>1e-10 or abs(fp['imbalance_log_cost'])>1e-7:
                raise RuntimeError('Parity identity failed')
            if abs(fe['log_gate_rate'])>2e-7:raise RuntimeError('Stationary identity failed')
            if not parity<peak:raise RuntimeError('Event order inverted')
            if not fp['orientation_log_gain']>0:raise RuntimeError('No orientation advance at parity')
            if not fe['orientation_log_gain']>0 or not fe['imbalance_log_cost']<0:
                raise RuntimeError('No signed rate competition at peak')
            if float(old['resultant_norm_rate_at_stationary'])<=0:
                raise RuntimeError('Resultant norm fails to grow at gate')
            # Nonlinear time reparam is a CHART relabelling and cannot move the physical point:
            # tau = xi + 100 xi^2, hence d/dtau=(d/dxi)/(1+200 xi).
            dtau_dxi=1+200*peak
            tau_peak=peak+100*peak*peak
            tau_parity=parity+100*parity*parity
            tau_rate=fe['log_gate_rate']/dtau_dxi
            if abs(tau_rate)>2e-7 or not tau_parity<tau_peak:
                raise RuntimeError('Coordinate relabel test failed')
            c_at_parity=fp['cancellation'];c_at_peak=fe['cancellation']
            # Verify reference v18.50j spline interpolation, not claim continuous roots.
            if abs(c_at_peak-float(old['estimated_peak_c']))>5e-12:
                raise RuntimeError('Mismatch with parent event')
            row=dict(kind=kind,metric=metric,epsilon=eps,
              parity_xi=parity,stationary_xi=peak,delay_xi=peak-parity,
              parity_theta_deg=fp['theta_degrees'],stationary_theta_deg=fe['theta_degrees'],
              parity_log_ratio=fp['u'],stationary_log_ratio=fe['u'],
              cancellation_parity=c_at_parity,cancellation_stationary=c_at_peak,
              orientation_rate_parity=fp['orientation_log_gain'],
              imbalance_rate_parity=fp['imbalance_log_cost'],
              orientation_rate_stationary=fe['orientation_log_gain'],
              imbalance_rate_stationary=fe['imbalance_log_cost'],
              log_gate_rate_stationary=fe['log_gate_rate'],
              resultant_rate_stationary=float(old['resultant_norm_rate_at_stationary']),
              reparametrized_stationary_tau=tau_peak,
              internal_event=True)
        else:
            # The raw-coordinate chart has no internal parity/stationarity; don't invent them.
            if (math.isfinite(parity) != math.isfinite(peak)):
                raise RuntimeError('Incomplete event status')
            row=dict(kind=kind,metric=metric,epsilon=eps,
              parity_xi='',stationary_xi='',delay_xi='',
              parity_theta_deg='',stationary_theta_deg='',
              parity_log_ratio='',stationary_log_ratio='',
              cancellation_parity='',cancellation_stationary='',
              orientation_rate_parity='',imbalance_rate_parity='',
              orientation_rate_stationary='',imbalance_rate_stationary='',
              log_gate_rate_stationary='',resultant_rate_stationary='',
              reparametrized_stationary_tau='',internal_event=False)
        summaries.append(row)

    meaningful=[r for r in summaries if r['internal_event']]
    if len(meaningful)!=24 or len(summaries)!=30:
        raise RuntimeError('Unexpected matched root count')
    ref=next(r for r in meaningful if r['kind']=='original' and r['metric']=='common_parent_c' and r['epsilon']==1e-4)
    auto=next(r for r in meaningful if r['kind']=='autonomous' and r['metric']=='common_parent_c' and r['epsilon']==1e-4)
    trace=next(v for k,v in groups.items() if k==('original','common_parent_c',1e-4))
    raw=next(v for k,v in groups.items() if k==('original','raw_coordinate',1e-4))

    # Symmetry tests at all 4800 points: L/T interchange must preserve C and its derivative.
    swap_error=0.;global_scaling_error=0.
    for row in samples:
        b,c=row['ratio'],row['cosine']
        bp,cp=row['ratio_rate'],row['cosine_rate']
        swapped=gf(1/b,c,-bp/b**2,cp)
        swap_error=max(swap_error,abs(swapped['cancellation']-row['cancellation']),
                       abs(swapped['log_gate_rate']-row['log_gate_rate']))
    if swap_error>1e-9:raise RuntimeError('Label symmetry broken')

    # Numerical redundant chart must be equal to chart uniformly scaled by 3 in parent;
    # compare corresponding values allowing round-off of physical response.
    for kind in ('original','autonomous'):
        for eps in (1e-5,1e-4,1e-3):
            a=groups[(kind,'common_parent_c',eps)]
            b=groups[(kind,'common_uniform_rescale_3x',eps)]
            for ra,rb in zip(a,b):
                global_scaling_error=max(global_scaling_error,
                   abs(ra['cancellation']-rb['cancellation']),
                   abs(ra['log_gate_rate']-rb['log_gate_rate'])/max(1.,abs(ra['log_gate_rate']),abs(rb['log_gate_rate'])))
    if global_scaling_error>5e-6:raise RuntimeError('Uniform scaling invariance failed')

    OUT.mkdir(exist_ok=True)
    write_csv(OUT/'geometric_gate_ledger.csv',samples)
    write_csv(OUT/'geometric_gate_events.csv',summaries)
    plot_results(groups,summaries,ref,auto)

    result=dict(version='v18.50k',title='Log-Balance / Orientation Gate & Advancing Response Audit',
      classification='AUTHENTICATED_REPARAMETRIZATION_DIAGNOSTIC_NOT_CONTINUOUS_FLOW_OR_MATERIAL_LAW_CERTIFICATE',
      input='v18.50j authenticated server ZIP (original 11D/10D genealogy nested)',
      mode='independent analytic postprocessing; NO NEW Q550 PHYSICAL INTEGRATIONS',
      source_entries_verified=verified,known_png_software_metadata_mismatches=metadata_diffs,
      input_rows=len(ledger),configurations=len(summaries),internal_event_cases=len(meaningful),
      raw_chart_without_internal_event=6,
      maximum_cancellation_identity_error=max_identity_err,
      maximum_derivative_identity_error=max_rate_err,
      maximum_interchange_identity_error=swap_error,
      maximum_uniform_scale_difference=global_scaling_error,
      reference=ref,autonomous=auto,
      statement='At equal local and transported norms, imbalance logarithmic rate vanishes identically. If orientation is still becoming more opposed, cancellation continues increasing. The later stationary event balances these two rates while resultant norm keeps increasing.',
      caveats=['All numbers are model-sensitivity quantities in declared coordinate charts.',
       'Event positions and derivatives from cubic splines of sampled data, not rigorous continuous roots.',
       'The monotone reparametrization is a mathematical relabeling, NOT new physical clock dynamics.',
       'Chart sensitivity persists: raw coordinate chart has no interior event on observed window.',
       'Orientation and imbalance are terms of a scalar identity, not independently measured physical mechanisms.',
       'No physical stress, strain, polymer or metallic-glass constitutive identification.'])
    (OUT/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('v18.50k completed |',len(summaries),'configurations |',len(ledger),'rows |',len(meaningful),'paired internal events')
    print('Reference | parity',ref['parity_xi'],'stationary',ref['stationary_xi'],
          'delay',ref['delay_xi'],'angle',ref['stationary_theta_deg'],
          'gate rates',ref['orientation_rate_stationary'],ref['imbalance_rate_stationary'],
          'd||R||/dxi',ref['resultant_rate_stationary'])
    print('Autonomous | parity',auto['parity_xi'],'stationary',auto['stationary_xi'])


def plot_results(groups,summaries,ref,auto):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r=groups[('original','common_parent_c',1e-4)]
    t=np.array([x['horizon_xi'] for x in r]);
    # Positive and negative contributions to d ln H, alongside the gate derivative.
    fig,ax=plt.subplots(figsize=(9.3,5.3))
    win=np.array([0.00097<=x<=0.00117 for x in t]);t2=t[win]
    ax.plot(t2,[x['orientation_log_gain'] for x,k in zip(r,win) if k],label='Orientation gain: d ln sin(theta/2)/d xi')
    ax.plot(t2,[x['imbalance_log_cost'] for x,k in zip(r,win) if k],label='Imbalance penalty: -d ln cosh(u/2)/d xi')
    ax.plot(t2,[x['log_gate_rate'] for x,k in zip(r,win) if k],label='d ln H / d xi',lw=2)
    ax.axhline(0,color='0.5',lw=.8);ax.axvline(ref['parity_xi'],ls=':',label='Norm parity b=1')
    ax.axvline(ref['stationary_xi'],ls='--',label='Cancellation stationary estimate')
    ax.set(xlabel='Q550 model coordinate Delta xi',ylabel='Logarithmic gate rate / Delta xi',title='Local gate passage: orientation gain versus norm-imbalance penalty')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'gate_rate_competition_reference.png',dpi=150);plt.close(fig)
    # Phase-space arc rather than seeing merely an overshoot C(xi).
    fig,ax=plt.subplots(figsize=(9.3,5.3))
    sc=ax.scatter([x['u'] for x in r],[x['theta_degrees'] for x in r],c=t,cmap='viridis',s=12)
    ax.plot([x['u'] for x in r],[x['theta_degrees'] for x in r],lw=.7,alpha=.4)
    ax.axvline(0,ls=':',color='0.45',label='Equal component norms (u=0)')
    from scipy.interpolate import CubicSpline
    bs=CubicSpline(t,[x['ratio'] for x in r]);cs=CubicSpline(t,[x['cosine'] for x in r])
    for label,z,marker in [('parity',ref['parity_xi'],'o'),('stationary',ref['stationary_xi'],'X')]:
        p=gf(bs(z),cs(z),bs.derivative()(z),cs.derivative()(z))
        ax.scatter([p['u']],[p['theta_degrees']],s=85,marker=marker,label=label,zorder=5)
    ax.set(xlabel='u = ln(||T||/||L||)',ylabel='Theta: relative angle (degrees)',title='The response passes norm parity and keeps turning')
    fig.colorbar(sc,ax=ax,label='Model coordinate Delta xi');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'internal_orientation_balance_passage.png',dpi=150);plt.close(fig)
    # Gauge dependence of numerical events; show both kappa families, three nontrivial metrics.
    fig,ax=plt.subplots(figsize=(9.4,5.2))
    metrics=['rates_weighted_2x','common_parent_c','angles_weighted_2x']
    for j,metric in enumerate(metrics):
        for i,kind in enumerate(('original','autonomous')):
            z=next(x for x in summaries if x['kind']==kind and x['metric']==metric and x['epsilon']==1e-4)
            yy=j+(i-.5)*.23
            ax.plot([z['parity_xi'],z['stationary_xi']],[yy,yy],lw=2,alpha=.8)
            ax.scatter([z['parity_xi']],[yy],marker='o',s=45)
            ax.scatter([z['stationary_xi']],[yy],marker='x',s=60)
    ax.set_yticks(range(3),['Rate weighted 2x','Common parent metric','Angle weighted 2x'])
    ax.set(xlabel='Model coordinate Delta xi',title='Event order survives; event clock does not')
    ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(OUT/'metric_dependent_event_passage.png',dpi=150);plt.close(fig)
    # Cancellation and advancing resultant on their native axes (no physical stress analogue).
    fig,ax=plt.subplots(figsize=(9.4,5.3))
    ax.plot(t,[x['cancellation'] for x in r],label='Cancellation C')
    ax.set(xlabel='Model coordinate Delta xi',ylabel='Normalized cancellation C')
    ax.axvline(ref['parity_xi'],ls=':',color='0.45')
    ax.axvline(ref['stationary_xi'],ls='--',color='0.45')
    bx=ax.twinx()
    # v18.50j only records d||R||/d xi, not ||R|| absolute; show rate explicitly.
    bx.plot(t,[x['resultant_rate'] for x in r],linestyle=':',label='Resultant norm rate')
    bx.set_ylabel('d||R|| / d Delta xi')
    lines=ax.lines[:1]+bx.lines[-1:];ax.legend(lines,[z.get_label() for z in lines],loc='center right')
    ax.set_title('Cancellation peaks while resulting response remains in motion')
    fig.tight_layout();fig.savefig(OUT/'advancing_resultant_with_gate.png',dpi=150);plt.close(fig)

if __name__=='__main__':main()
