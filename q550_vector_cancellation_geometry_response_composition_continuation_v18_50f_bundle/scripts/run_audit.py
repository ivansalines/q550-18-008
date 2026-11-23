#!/usr/bin/env python3
"""v18.50f: Replay-independent vector-composition analysis of verified v18.50e outputs.

No new Q550 ODE integration is performed. All diagnostics belong to the declared
metric-whitened hidden four-jet of the authentic v18.50e lineage.
"""
import sys,csv,io,json,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from geometry_math import ledger,angular_change
from verify_parent import verify
ROOT=HERE.parent

def parse_vector(s):
    v=np.asarray(json.loads(s),float)
    if v.shape!=(4,):raise ValueError('Unrecognized vector dimensionality')
    return v

def write_csv(path,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def run():
    csvbytes,pr,ancestry=verify()
    original=list(csv.DictReader(io.StringIO(csvbytes.decode('utf-8'))))
    if len(original)!=100:raise RuntimeError('Unexpected parent sample count')
    cases=defaultdict(list);rows=[];max_error=0;max_parent_mismatch=0
    for r in original:
        L=parse_vector(r['frozen_endpoint_response']);T=parse_vector(r['transported_component_response']);R=parse_vector(r['direction_response'])
        m=ledger(L,T,R);key=(r['mode'],r['kind'],r['ramp_xi'],r['shape'])
        tau=float(r['horizon_xi']);max_error=max(max_error,m['observed_vs_split_rel'])
        max_parent_mismatch=max(max_parent_mismatch,abs(m['resultant_norm']-float(r['gain'])))
        if m['observed_vs_split_rel']>5e-6:raise RuntimeError('Response residual exceeds parent IVP tolerance')
        if abs(m['local_norm']-float(r['frozen_endpoint_x_gain']))>1e-6:raise RuntimeError('local parent mismatch')
        if abs(m['transported_norm']-float(r['transported_component_gain']))>1e-6:raise RuntimeError('transport parent mismatch')
        d={k:r[k] for k in ('mode','kind','ramp_xi','shape','metric','turn_xi')}
        d.update(horizon_xi=tau,**{k:('' if v is None else v) for k,v in m.items()})
        d['parent_ivp_gain']=float(r['gain'])
        rows.append(d);cases[key].append(dict(tau=tau,L=L,T=T,R=R,**m))
    if len(cases)!=20 or any(len(x)!=5 for x in cases.values()):raise RuntimeError('Unexpected case/horizon structure')
    continuation=[];endpoints=[]
    for key,xx in sorted(cases.items()):
        xx.sort(key=lambda x:x['tau'])
        for i,x in enumerate(xx):
            if i==0:continue
            old=xx[i-1]
            tau=x['tau'];angle=angular_change(old['R'],x['R'])
            scale=float(tau-old['tau'])
            continuation.append(dict(mode=key[0],kind=key[1],ramp_xi=float(key[2]),shape=key[3],
             start_horizon=old['tau'],end_horizon=tau,delta_horizon=scale,
             resultant_reorientation_deg=angle,
             transported_reorientation_deg=angular_change(old['T'],x['T']),
             local_reorientation_deg=angular_change(old['L'],x['L']),
             finite_difference_gain_growth=(x['resultant_norm']-old['resultant_norm'])/scale,
             finite_difference_opposition_change=('' if old['alignment_cos'] is None else (x['alignment_cos']-old['alignment_cos'])/scale)))
        at=xx[-1]
        endpoints.append(dict(mode=key[0],kind=key[1],ramp_xi=float(key[2]),shape=key[3],
          endpoint_gain=at['resultant_norm'],endpoint_local=at['local_norm'],endpoint_transported=at['transported_norm'],
          alignment_cos=at['alignment_cos'],alignment_angle_deg=at['alignment_angle_deg'],
          cancellation_fraction=at['cancellation_fraction'],transport_share=at['transport_share'],
          residual_rel=at['observed_vs_split_rel']))
    output=ROOT/'results';output.mkdir(parents=True,exist_ok=True)
    write_csv(output/'response_vector_gram_ledger.csv',rows)
    write_csv(output/'response_direction_continuation.csv',continuation)
    write_csv(output/'endpoint_protocol_contrasts.csv',endpoints)
    same=[x for x in endpoints if x['mode']=='same_seed']
    nat=[x for x in endpoints if x['mode']=='natural_turn']
    opp=sum(1 for x in rows if x['alignment_cos']!='' and x['alignment_cos']<0)
    nonzero=sum(1 for x in rows if x['alignment_cos']!='')
    main=next(x for x in endpoints if x['mode']=='same_seed' and x['kind']=='original' and abs(x['ramp_xi']-0.24)<1e-8 and x['shape']=='beta:2:2')
    summary={'version':'v18.50f','title':'Vector Cancellation Geometry & Response-Composition Continuation Audit',
     'classification':'VERIFIED_V18_50E_VECTOR_LEDGER_POSTPROCESSING_NOT_INDEPENDENT_CAUSAL_OR_MATERIAL_CERTIFICATE',
     'ancestry':ancestry,'source':{'parent_csv_rows':len(original),'case_count':len(cases),'horizon_count_per_case':5,'new_Q550_ODE_integrations':0},
     'metric':'common_4d_parent_c; vectors inherited from v18.50e, not a physical metric',
     'results':{'negative_local_transport_inner_products':opp,'eligible_nonzero_transport_rows':nonzero,
       'max_IVP_vs_vector_split_relative_residual':max_error,'max_endpoint_gain_parent_mismatch':max_parent_mismatch,
       'same_seed_cancellation_fraction_range':[min(x['cancellation_fraction'] for x in same),max(x['cancellation_fraction'] for x in same)],
       'natural_cancellation_fraction_range':[min(x['cancellation_fraction'] for x in nat),max(x['cancellation_fraction'] for x in nat)],
       'reference_original_cubic_024_same_seed':main},
     'limitations':['The L + T split is an endpoint-coordinate ledger; it is not a uniquely causally separable decomposition.',
       'The angle and cancellation fraction depend on the parent selected metric; no physical scalar invariant is asserted.',
       'All samples are computed from existing v18.50e data. This is an independent algebraic review, not new dynamical integration.',
       'Finite differences across four horizons do not locate new physical turning events or regime thresholds.',
       'The Gram determinant is a squared oriented-area magnitude without intrinsic signed chirality.'],
     'environment':{'python':platform.python_version(),'numpy':np.__version__}}
    (output/'report.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    from plot_results import plot
    plot(rows,endpoints,output)
    print('RESULT',json.dumps(summary['results'],indent=2),flush=True)
    return summary
if __name__=='__main__':run()
