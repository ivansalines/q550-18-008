# v18.50d — Scientific decision rules

1. **Source verification:** original v18.50c sendback SHA-256 and every internal SHA-256 member MUST match; recursive parent-b → parent-a → ... original Q550 ancestry must verify. Any mismatch aborts.
2. **Common baseline:** at each dynamically observed turning, perturbations must start from one identical 11D state. For the drive pulse, the start and end imposed clock phase must coincide with the baseline.
3. **Independent counterfactual channels:** a logit-x state kick, a theta1 state kick, and a zero-net-phase drive-pulse must be tested separately and with symmetric signs.
4. **Structural cross derivative:** the model's analytic x→hidden field Jacobian must agree with a physical-RHS finite difference. Distinguish nonzero MODEL coupling from physical causal identification.
5. **Linearity window:** report derivative drift across three ε amplitudes without calling a continuous change a bifurcation.
6. **Shared metric:** use a single pooled 4D metric from v18.50c to avoid re-normalizing each trajectory; native/alternative metrics remain a separate future sensitivity check.
7. **No forced thresholds:** do not declare a regime transition without a bracketed change, parameter refinements, and numerical controls. Opposite signed perturbations alone are not evidence of a regime boundary.
8. **Scientific label:** `CONTROLLED_IN_MODEL_SENSITIVITY_NOT_ESTABLISHED_PHYSICAL_CAUSALITY_OR_MATERIAL_MEMORY_CERTIFICATE`.
9. **Reproduction:** all Python scripts, original authenticated ancestor archive, CSV/JSON/plots, tests, environment, reports, and full-name root directory must accompany the bundle.
