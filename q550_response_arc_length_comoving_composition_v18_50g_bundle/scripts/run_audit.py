#!/usr/bin/env python3
"""v18.50g: sampled response arc-length and co-moving composition postprocessor.

NO new 11D or tangent IVPs. Numerical arc is a sampled polygonal lower bound.
The inherited common 4D whitened chart is not a physical metric.
"""
import csv,io,json,sys,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_ancestry import load_source
from geometry_math import arc_diagnostics,metric_matrix,safe_angle

def vec(s):
    v=np.asarray(json.loads(s),float)
    if v.shape!=(4,) or not np.all(np.isfinite(v)):raise ValueError('Expected finite length-4 vector')
    return v

def save_csv(file, rows):
    if not rows:raise ValueError('No rows')
    fields=list(dict.fromkeys(k for row in rows for k in row.keys()))
    with file.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def run():
    source,e_source,verification=load_source()
    frows=list(csv.DictReader(io.StringIO(source.decode())))
    erows=list(csv.DictReader(io.StringIO(e_source.decode())))
    if len(frows)!=100 or len(erows)!=100:raise RuntimeError('Unexpected parent row count')
    key=lambda d:(d['mode'],d['kind'],round(float(d['ramp_xi']),8),d['shape'],round(float(d['horizon_xi']),8))
    emap={key(r):r for r in erows}
    grouped=defaultdict(list)
    max_source_diff=0.
    for r in frows:
        er=emap[key(r)]
        L,T,obs=vec(er['frozen_endpoint_response']),vec(er['transported_component_response']),vec(er['direction_response'])
        max_source_diff=max(max_source_diff,abs(float(r['resultant_norm'])-np.linalg.norm(L+T)))
        grouped[key(r)[:4]].append((float(r['horizon_xi']),L,T,obs))
    if len(grouped)!=20:raise RuntimeError('Expected 20 cases')
    for k,v in grouped.items():
        v.sort(key=lambda x:x[0]);ts=[x[0] for x in v]
        if len(v)!=5 or not np.allclose(ts,[0,.0125,.025,.0375,.05],atol=1e-12):raise RuntimeError('Unexpected horizon grid')
    point_rows=[];segment_rows=[];case_rows=[]
    for key4,points in sorted(grouped.items()):
        mode,kind,ramp,shape=key4
        for metric_name in ('parent_whitened','declared_diagonal_stress'):
            P,S,agg=arc_diagnostics(points,metric_matrix(metric_name))
            prefix=dict(mode=mode,kind=kind,ramp_xi=ramp,shape=shape,metric=metric_name)
            for p in P:
                point_rows.append(dict(**prefix,tau=p['tau'],arc_length=p['ell'],normalized_arc=p['normalized_arc'],
                    response_gain=p['gain'],cancellation=p['c'],observed_minus_split_norm=p['obs_res']))
            for s in S:
                segment_rows.append(dict(**prefix,tau0=s['tau0'],tau1=s['tau1'],mid_tau=s['mid_tau'],
                   arc0=s['arc0'],arc1=s['arc1'],normalized_mid_arc=s['normalized_mid_arc'],
                   segment_length=s['length'],segment_speed_lower_bound=s['avg_speed'],
                   local_signed_advance=s['local_signed_advance'],
                   transported_signed_advance=s['transported_signed_advance'],
                   local_transverse=s['local_transverse'],transported_transverse=s['transported_transverse'],
                   segment_cancellation=s['segment_cancellation'],
                   increment_angle_deg=s['increment_angle'],
                   turn_from_previous_deg=s['turn_from_previous_deg'],
                   d_cancellation_per_arc=s['dc_dell']))
            case_rows.append(dict(**prefix,**agg,endpoint_gain=P[-1]['gain'],endpoint_cancellation=P[-1]['c'],
                     max_chord_turn_deg=max(x['turn_from_previous_deg'] for x in S if x['turn_from_previous_deg'] is not None),
                     samples=len(P)))
    out=ROOT/'results';out.mkdir(exist_ok=True)
    save_csv(out/'sampled_response_arc_trace.csv',point_rows)
    save_csv(out/'comoving_response_segment_ledger.csv',segment_rows)
    save_csv(out/'sampled_response_arc_case_summary.csv',case_rows)
    parent=[r for r in case_rows if r['metric']=='parent_whitened'];ref=next(r for r in parent if r['mode']=='same_seed' and r['kind']=='original' and abs(r['ramp_xi']-.24)<1e-10 and r['shape']=='beta:2:2')
    summary={'version':'v18.50g','title':'Response Arc-Length & Co-Moving Composition Audit',
      'classification':'SAMPLED_RESPONSE_ARC_DIAGNOSTIC_NOT_CONTINUOUS_ARCLENGTH_OR_PHYSICAL_MEMORY_CERTIFICATE',
      'ancestry':verification,'source':{'verified_parent_f_rows':len(frows),'verified_parent_e_rows':len(erows),
       'cases':len(grouped),'horizons_per_case':5,'new_Q550_ODE_integrations':0,'metric_charts':2},
      'reference':ref,'results':{'max_parent_ledger_mismatch':max_source_diff,
        'max_parent_split_residual':max(float(r['max_composition_residual']) for r in parent),
        'parent_arc5_range':[min(r['arc5'] for r in parent),max(r['arc5'] for r in parent)],
        'parent_three_point_underestimate_fraction_range':[min(r['coarse_loss_fraction'] for r in parent),max(r['coarse_loss_fraction'] for r in parent)],
        'parent_straightness_range':[min(r['straightness'] for r in parent),max(r['straightness'] for r in parent)],
        'number_segments':len(segment_rows),'number_point_rows':len(point_rows)},
      'important_limits':['Polyline length from only five measured horizon samples is a lower bound on true Euclidean response-curve arc-length, not the continuous arc.',
       'Segment rate and curvature are finite sample diagnostics, not local derivatives or detected phase events.',
       'Arc is measured in inherited metric-whitened four-component sensitivity coordinates, not physical distance or clock.',
       'The diagonal-stress second chart changes metric intentionally to reveal coordinate sensitivity.',
       'L and T are inherited endpoint bookkeeping contributions, not independent physical forces.',
       'No Q550 ODE rerun or independent causal/memory/regime certification occurs in this audit.'],
      'environment':{'python':platform.python_version(),'numpy':np.__version__}}
    (out/'report.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    from plot_results import plot
    plot(point_rows,segment_rows,case_rows,out)
    print('DONE:',json.dumps(summary['results'],indent=2),flush=True)
    return summary
if __name__=='__main__':run()
