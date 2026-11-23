#!/usr/bin/env python3
from pathlib import Path
import json
p=Path(__file__).resolve().parents[1];r=json.loads((p/'results/report.json').read_text())
lines=['# Q550 v18.49o — Dominance-Boundary Continuation & Ramp-Shape Stress Audit','',
        '**Status:** '+r['status'],'',
        f"Parent v18.49n SHA256: `{r['parent']['n_parent_sha256']}`.",
        f"Parent cubic share regression max absolute error: {r['baseline_parent_max_abs_share_error']:.4e}.",
        f"Unique tested control cases: {r['number_of_unique_cases']}; numerical failures: {r['failed_evaluations']}.",
        '', '## Duration continuation at the identical cubic command shape','']
if r['duration_brackets_refined']:
 for b in r['duration_brackets_refined']:
    lines.append(f"- {b['kind']}: opposing endpoint margins in r=[{b['r_lower']:.9f}, {b['r_upper']:.9f}], M=[{b['margin_lower']:.6g}, {b['margin_upper']:.6g}]. Sample-based continuation, not an interval certificate.")
else:lines.append('No opposing-signed endpoint dominance margins were observed in the successfully evaluated duration probes. This does not rule out a boundary outside or between probes.')
lines+=['','## Shape perturbation at fixed r','']
if r['shape_stress_endpoint_negative_cases']:
 for c in r['shape_stress_endpoint_negative_cases']:
    lines.append(f"- **Observed loss** {c['kappa_kind']} r={c['ramp_xi']:.5g} shape={c['shape']}: M={c['margin_at_q065']:.6g}, leader={c['final_leader']}")
else:lines.append('No sampled shape-stress endpoint lost pair 6–7 dominance; no general shape-invariance theorem is implied.')
lines+=['','## Numeric controls', '',f"- Forward replay error: {r['numeric_controls']['forward_regression']:.3e}.",
 f"- Largest ledger error: {r['numeric_controls']['max_mechanical_ledger_error']:.3e}.",
 f"- Minimum relative eigen-gap: {r['numeric_controls']['min_relative_eigen_gap']:.3e}.",'',
 '## Evidence boundaries','']
for x in r['limitations']:lines.append('- '+x)
if r['failed_case_details']:
 lines+=['','## Unresolved numerical evaluations','']
 for x in r['failed_case_details']:lines.append(f"- {x['kind']} r={x['r']} {x['shape']}: {x['error_type']}: {x['error_message']}")
(p/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
print('Wrote v18.49o scientific report')
