#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
expected=['results/co_moving_phase_ledger.csv','results/gauge_covariance_velocity_control.png','results/moving_gauge_controls.csv','results/observer_velocity_angle_summary.csv','results/recovered_metric_validation.csv','results/report.json','results/response_locked_frame_comparison.png','results/velocity_opposition_metric_comparison.png']
if sorted(str(p.relative_to(root)) for p in (root/'results').iterdir() if p.is_file())!=expected:
    raise RuntimeError('Unexpected/missing output set in results/')
files={rel:hashlib.sha256((root/rel).read_bytes()).hexdigest() for rel in expected}
(root/'SHA256SUMS_OUTPUT.json').write_text(json.dumps({'root':root.name,'version':'v18.50n','file_sha256':files},indent=2)+'\n')
print('v18.50n regenerated output manifest WRITTEN',len(files))
