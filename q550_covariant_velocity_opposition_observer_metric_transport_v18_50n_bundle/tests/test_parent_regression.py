#!/usr/bin/env python3
"""Regression against authenticated historical angles, no physical reintegration."""
from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parents[1]
f=root/'results/observer_velocity_angle_summary.csv'
if not f.exists():raise RuntimeError('Run audit first')
d=pd.read_csv(f)
r=d[(d.kind=='original')&(d.epsilon==1e-4)]
key={'common_parent_c':159.78518028221453,
     'model_jet_gram_alpha_0p1':114.94747910178374,
     'model_jet_gram_alpha_1':140.80393679581135,
     'raw_coordinate_separate_observable':124.14398319553797,
     'adversarial_derivative_bisector_spd_control':69.66084108176013}
for name,value in key.items():
    row=r[r.metric==name]
    assert len(row)==1,name
    assert abs(float(row.iloc[0].angle_between_derivatives_deg)-value)<5e-4,name
for row in r[r.metric.isin(['common_parent_c','model_jet_gram_alpha_0p1','model_jet_gram_alpha_1'])].itertuples():
    assert abs(row.angle_between_derivatives_deg-row.gauge_rate_300_covariant_angle_deg)<1e-10
    assert abs(row.angle_between_derivatives_deg-row.gauge_rate_minus1000_covariant_angle_deg)<1e-10
print('v18.50n authenticated Q550 numerical regressions PASS')
