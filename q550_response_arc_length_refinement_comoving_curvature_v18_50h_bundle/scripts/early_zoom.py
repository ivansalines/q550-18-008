#!/usr/bin/env python3
"""Refine cancellation only near the common-seed turning event (original kappa).

This is a targeted genuine 11D IVP replay, not an interpolation, and is NOT a
new physical clock. Parent engine is copied byte-identical from verified v18.50e.
"""
from pathlib import Path
import sys,importlib.util,argparse,csv,json
import numpy as np
from verify_ancestry import stage
ROOT=Path(__file__).resolve().parents[1]
def main():
    dest,_,_,_=stage()
    sys.path.insert(0,str(dest/'scripts'))
    sp=importlib.util.spec_from_file_location('e50h_zoom_integrator',dest/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(sp);sys.modules[sp.name]=mod;sp.loader.exec_module(mod)
    early=np.linspace(.000025,.004,160).tolist()
    h=sorted(set(early+[.0125,.025,.0375,.05]))
    a=argparse.Namespace(smoke=True,kind='original',horizons=h,epsilon=1e-4,
      direction_step=1e-6,rtol=3e-12,atol=3e-13,max_step=.025,
      maximum_ledger_error=1e-8,maximum_regression=1e-7,
      maximum_parent_share_difference=2e-6,max_generator_identity_error=1e-7,
      max_linearized_residual=5e-3,fail_fast=True)
    mod.run(a)
    with (dest/'results/common_horizon_direction_responses.csv').open() as f:rows=list(csv.DictReader(f))
    out=[];group=[]
    for r in rows:
        if r['mode']!='same_seed':continue
        L=np.array(json.loads(r['frozen_endpoint_response']));T=np.array(json.loads(r['transported_component_response']))
        cancel=1-np.linalg.norm(L+T)/(np.linalg.norm(L)+np.linalg.norm(T))
        out.append({'horizon_xi':r['horizon_xi'],'cancellation':cancel,
        'local_norm':np.linalg.norm(L),'transported_norm':np.linalg.norm(T),
        'LT_cos':float(np.dot(L,T)/(np.linalg.norm(L)*np.linalg.norm(T))) if np.linalg.norm(T)>1e-10 else float('nan')})
    out.sort(key=lambda z:float(z['horizon_xi']))
    keys=list(out[0]);path=ROOT/'results/early_cancellation_zoom.csv'
    with path.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(out)
    peak=max(out,key=lambda z:z['cancellation']);i=out.index(peak)
    if not 0<i<len(out)-1:raise RuntimeError('Peak unresolved, zoom must extend')
    bracket=(out[i-1]['horizon_xi'],peak['horizon_xi'],out[i+1]['horizon_xi'])
    diag={'zoom_points':len(out),'peak_sample_xi':float(peak['horizon_xi']),
      'peak_sample_cancellation':peak['cancellation'],'neighbor_bracket':bracket,
      'peak_inside_zoom':True,'new_zoom_IVPs':6,
      'limit':'Finite-sample peak in declared response-coordinate ledger; not a rigorous continuous stationary root or physical memory marker.'}
    (ROOT/'results/early_zoom_report.json').write_text(json.dumps(diag,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    q=[r for r in out if float(r['horizon_xi'])<=.00401]
    fig,ax=plt.subplots(figsize=(8.2,4.8))
    ax.plot([float(p['horizon_xi']) for p in q],[100*p['cancellation'] for p in q])
    ax.axvline(float(peak['horizon_xi']),linestyle='--',alpha=.6)
    ax.set(xlabel='Elapsed evolution Δξ',ylabel='Relative cancellation (%)',title='Early cancellation peak — targeted 160-point zoom')
    ax.grid(alpha=.25);fig.tight_layout();fig.savefig(ROOT/'results/early_cancellation_zoom.png',dpi=170);plt.close(fig)
    print('EARLY ZOOM RESULT',json.dumps(diag),flush=True)
if __name__=='__main__':main()
