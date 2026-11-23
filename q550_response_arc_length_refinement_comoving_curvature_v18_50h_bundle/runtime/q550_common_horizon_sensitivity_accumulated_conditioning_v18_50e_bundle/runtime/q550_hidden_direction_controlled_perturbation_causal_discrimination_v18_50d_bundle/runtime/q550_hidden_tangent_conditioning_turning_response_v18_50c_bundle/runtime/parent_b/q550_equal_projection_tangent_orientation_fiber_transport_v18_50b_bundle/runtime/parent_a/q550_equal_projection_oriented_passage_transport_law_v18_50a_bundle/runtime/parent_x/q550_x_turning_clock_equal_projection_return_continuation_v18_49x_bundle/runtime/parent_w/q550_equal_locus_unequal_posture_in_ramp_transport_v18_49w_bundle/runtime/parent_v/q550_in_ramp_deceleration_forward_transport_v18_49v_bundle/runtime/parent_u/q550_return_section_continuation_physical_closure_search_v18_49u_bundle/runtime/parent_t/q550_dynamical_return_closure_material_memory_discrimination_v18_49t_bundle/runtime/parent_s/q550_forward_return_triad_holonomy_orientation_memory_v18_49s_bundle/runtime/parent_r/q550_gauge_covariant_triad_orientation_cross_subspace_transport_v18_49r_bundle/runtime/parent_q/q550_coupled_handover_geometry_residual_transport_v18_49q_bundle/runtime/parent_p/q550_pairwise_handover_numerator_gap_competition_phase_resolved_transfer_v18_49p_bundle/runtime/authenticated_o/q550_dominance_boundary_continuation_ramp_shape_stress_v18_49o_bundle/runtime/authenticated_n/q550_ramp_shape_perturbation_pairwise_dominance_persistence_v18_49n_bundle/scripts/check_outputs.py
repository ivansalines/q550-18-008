#!/usr/bin/env python3
"""Validate run-level output completeness and declared scientific scope."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
report=json.loads((R/'report.json').read_text())
def number(name):
    with (R/name).open(newline='') as f:
        return sum(1 for _ in csv.DictReader(f))
c=report['total_case_count'];q=report['phase_samples']
assert number('pairwise_generator_phase_profiles.csv')==c*q*45
assert number('pairwise_dominance_phase_profiles.csv')==c*q
assert number('pairwise_dominance_case_summary.csv')==c
assert number('shape_vs_cubic_control.csv')==c
assert number('cross_case_dominance_envelope.csv')==q
assert number('ramp_command_shapes.csv')==101*len(report['shape_set'])
assert report['integration_counts']['physical_return_11D']==c
assert report['integration_counts']['tangent_10D']==c
assert report['numeric_controls']['forward_regression']<1e-7
assert report['numeric_controls']['upstream_cubic_max_abs_share_difference']<2e-6
assert report['numeric_controls']['pair_frobenius_identity']<1e-7
print('PASS v18.49n output cardinality, ancestry regression, algebraic closure')
