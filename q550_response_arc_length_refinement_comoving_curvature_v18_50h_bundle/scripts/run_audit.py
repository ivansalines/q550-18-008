#!/usr/bin/env python3
"""v18.50h -- Genuine 11D driven ODE replays, nested 5/9/17/33 response sampling.

Uses the original authenticated v18.50e numerical integration script unchanged.
Measures a polyline LOWER BOUND for the vector response arc. Does not infer a
continuous arc or a physical time, causal law, bifurcation or material memory.
"""
import argparse,csv,json,importlib.util,sys,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_ancestry import stage
ROOT=Path(__file__).resolve().parents[1]
GRIDS=(5,9,17,33)

def cosine(a,b):return float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))
def curve_metric(P):
    steps=np.diff(P,axis=0);lens=np.linalg.norm(steps,axis=1)
    arc=float(np.sum(lens));chord=float(np.linalg.norm(P[-1]-P[0]))
    turns=[]
    for a,b in zip(steps[:-1],steps[1:]):
        if np.linalg.norm(a)*np.linalg.norm(b)>0:
            turns.append(float(np.degrees(np.arccos(np.clip(cosine(a,b),-1,1)))))
    return arc,chord,float(max(turns) if turns else 0)

def write_csv(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def arr(r,key):return np.array(json.loads(r[key]),dtype=float)

def run(smoke=False):
    dest,ereport,original_csv,anc=stage()
    sys.path.insert(0,str(dest/'scripts'))
    sp=importlib.util.spec_from_file_location('e50h_integrator',dest/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(sp);sys.modules[sp.name]=mod;sp.loader.exec_module(mod)
    # Keep the full 11D Q550 ancestor, RHS, tangent model and normalisation untouched.
    args=argparse.Namespace(smoke=smoke,kind='both',horizons=[i*.05/32 for i in range(1,33)],
        epsilon=1e-4,direction_step=1e-6,rtol=3e-12,atol=3e-13,
        max_step=.025,maximum_ledger_error=1e-8,maximum_regression=1e-7,
        maximum_parent_share_difference=2e-6,max_generator_identity_error=1e-7,
        max_linearized_residual=5e-3,fail_fast=True)
    engine_report=mod.run(args)
    with (dest/'results/common_horizon_direction_responses.csv').open() as f:newrows=list(csv.DictReader(f))
    oldrows=list(csv.DictReader(original_csv.splitlines()))
    old={(r['mode'],r['kind'],r['ramp_xi'],r['shape'],round(float(r['horizon_xi']),12)):r for r in oldrows}
    grouped=defaultdict(list)
    max_reg=0.;reg_n=0
    for r in newrows:
        key=(r['mode'],r['kind'],r['ramp_xi'],r['shape'])
        grouped[key].append(r)
        k5=key+(round(float(r['horizon_xi']),12),)
        if k5 in old:
            a=arr(r,'direction_response');b=arr(old[k5],'direction_response')
            max_reg=max(max_reg,float(np.linalg.norm(a-b)/max(1,np.linalg.norm(b))))
            reg_n+=1
    if max_reg>2e-5:raise RuntimeError(f'Regression exceeded tolerance: {max_reg}')
    out=ROOT/'results';out.mkdir(parents=True,exist_ok=True)
    records=[];summary=[];points=[];events=[]
    for key,rs in sorted(grouped.items()):
        rs.sort(key=lambda z:float(z['horizon_xi']))
        if len(rs)!=33:raise RuntimeError('Not 33 independently sampled horizons')
        ts=np.array([float(x['horizon_xi']) for x in rs]);L=np.array([arr(x,'frozen_endpoint_response') for x in rs]);T=np.array([arr(x,'transported_component_response') for x in rs]);R=L+T
        nL=np.linalg.norm(L,axis=1);nT=np.linalg.norm(T,axis=1);nR=np.linalg.norm(R,axis=1)
        cancel=np.maximum(0,1-nR/np.maximum(nL+nT,1e-15))
        dot=np.sum(L*T,axis=1)
        for i in range(33):
            points.append(dict(mode=key[0],kind=key[1],ramp_xi=key[2],shape=key[3],horizon_xi=ts[i],
              cancellation=cancel[i],local_norm=nL[i],transported_norm=nT[i],resultant_norm=nR[i],
              LT_dot=dot[i],arc33_partial=sum(np.linalg.norm(np.diff(R[:i+1],axis=0),axis=1)),
              total_response_json=json.dumps(R[i].tolist())))
        for n in GRIDS:
            stride=32//(n-1);indices=np.arange(0,33,stride)
            arc,chord,turn=curve_metric(R[indices]);cmax_idx=indices[np.argmax(cancel[indices])]
            records.append(dict(mode=key[0],kind=key[1],ramp_xi=key[2],shape=key[3],
              samples=n,arc_lower_bound=arc,end_chord=chord,straightness=chord/arc,
              max_chord_turn_deg=turn,cancellation_max_sampled=cancel[cmax_idx],
              cancellation_argmax_xi=ts[cmax_idx],endpoint_cancellation=cancel[-1]))
        # Local maximum from measured samples, not a root or continuous maximizer.
        idx=int(np.argmax(cancel))
        has_interior=(idx>0 and idx<32)
        if has_interior:
            d_before=(cancel[idx]-cancel[idx-1]);d_after=(cancel[idx+1]-cancel[idx])
        else:d_before=d_after=float('nan')
        events.append(dict(mode=key[0],kind=key[1],ramp_xi=key[2],shape=key[3],
           peak_sample_xi=ts[idx],peak_sample_cancellation=cancel[idx],
           peak_is_interior=has_interior,peak_index=idx,difference_before=d_before,difference_after=d_after,
           endpoint_cancellation=cancel[-1],cancel_peak_above_endpoint=cancel[idx]-cancel[-1],
           min_L_T_dot=float(np.min(dot[1:]))))
        g={v['samples']:v for v in records[-4:]}
        summary.append(dict(mode=key[0],kind=key[1],ramp_xi=key[2],shape=key[3],
            arc5=g[5]['arc_lower_bound'],arc9=g[9]['arc_lower_bound'],arc17=g[17]['arc_lower_bound'],
            arc33=g[33]['arc_lower_bound'],relative_arc_5_to_33_increase=(g[33]['arc_lower_bound']-g[5]['arc_lower_bound'])/g[33]['arc_lower_bound'],
            arc17_to_33_change_fraction=(g[33]['arc_lower_bound']-g[17]['arc_lower_bound'])/g[33]['arc_lower_bound'],
            endpoint_chord=g[33]['end_chord'],straightness33=g[33]['straightness'],
            max_sampled_cancellation=float(cancel[idx]),peak_sample_xi=ts[idx],peak_interior=has_interior))
    write_csv(out/'dense_response_vectors.csv',newrows)
    write_csv(out/'arc_grid_refinement.csv',records)
    write_csv(out/'dense_cancellation_trace.csv',points)
    write_csv(out/'cancellation_peak_brackets.csv',events)
    write_csv(out/'case_summary.csv',summary)
    ref=next(r for r in summary if r['mode']=='same_seed' and r['kind']=='original' and abs(float(r['ramp_xi'])-.24)<1e-9 and r['shape']=='beta:2:2')
    report={'version':'v18.50h','title':'Response Arc-Length Refinement & Co-Moving Curvature Audit',
      'classification':'DENSE_Q550_SAMPLED_RESPONSE_CURVE_WITH_EARLY_PEAK_DIAGNOSTIC_NOT_CONTINUOUS_ARC_OR_PHYSICAL_MEMORY_CERTIFICATE',
      'ancestry':anc,'original_engine_counts':engine_report['counts'],
      'grids':GRIDS,'case_count':len(summary),'new_dense_response_observations':len(newrows),
      'authentic_5pt_regression_count':reg_n,'max_5pt_relative_vector_regression':max_reg,
      'common_horizons_end_xi':.05,'reference':ref,
      'interior_peak_count':sum(x['peak_is_interior'] for x in events),
      'limits':['Lengths remain sampled chord sums, lower bounds not continuous arc-length.',
        'The response vector depends on a declared common whitened chart rather than physical spatial metric.',
        'Peak indices denote sampled peaks, not proven stationary points of continuous cancellation.',
        'Natural_turn and same_seed are distinct interventions; comparisons are not randomized causal effects.',
        'No physical phase clock, regime transition, material memory, or dimensional volume is established.'],
      'environment':{'python':platform.python_version(),'numpy':np.__version__}}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    pp=ROOT/'scripts'/'plot_results.py'
    plot_spec=importlib.util.spec_from_file_location('v50h_plot_results',pp)
    plot_module=importlib.util.module_from_spec(plot_spec);plot_spec.loader.exec_module(plot_module)
    plot_module.plot(records,points,summary,out)
    print('v18.50h COMPLETE',json.dumps({'cases':len(summary),'rows':len(newrows),'regression':max_reg,'reference':ref},indent=2),flush=True)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');a=p.parse_args();run(smoke=a.smoke)
