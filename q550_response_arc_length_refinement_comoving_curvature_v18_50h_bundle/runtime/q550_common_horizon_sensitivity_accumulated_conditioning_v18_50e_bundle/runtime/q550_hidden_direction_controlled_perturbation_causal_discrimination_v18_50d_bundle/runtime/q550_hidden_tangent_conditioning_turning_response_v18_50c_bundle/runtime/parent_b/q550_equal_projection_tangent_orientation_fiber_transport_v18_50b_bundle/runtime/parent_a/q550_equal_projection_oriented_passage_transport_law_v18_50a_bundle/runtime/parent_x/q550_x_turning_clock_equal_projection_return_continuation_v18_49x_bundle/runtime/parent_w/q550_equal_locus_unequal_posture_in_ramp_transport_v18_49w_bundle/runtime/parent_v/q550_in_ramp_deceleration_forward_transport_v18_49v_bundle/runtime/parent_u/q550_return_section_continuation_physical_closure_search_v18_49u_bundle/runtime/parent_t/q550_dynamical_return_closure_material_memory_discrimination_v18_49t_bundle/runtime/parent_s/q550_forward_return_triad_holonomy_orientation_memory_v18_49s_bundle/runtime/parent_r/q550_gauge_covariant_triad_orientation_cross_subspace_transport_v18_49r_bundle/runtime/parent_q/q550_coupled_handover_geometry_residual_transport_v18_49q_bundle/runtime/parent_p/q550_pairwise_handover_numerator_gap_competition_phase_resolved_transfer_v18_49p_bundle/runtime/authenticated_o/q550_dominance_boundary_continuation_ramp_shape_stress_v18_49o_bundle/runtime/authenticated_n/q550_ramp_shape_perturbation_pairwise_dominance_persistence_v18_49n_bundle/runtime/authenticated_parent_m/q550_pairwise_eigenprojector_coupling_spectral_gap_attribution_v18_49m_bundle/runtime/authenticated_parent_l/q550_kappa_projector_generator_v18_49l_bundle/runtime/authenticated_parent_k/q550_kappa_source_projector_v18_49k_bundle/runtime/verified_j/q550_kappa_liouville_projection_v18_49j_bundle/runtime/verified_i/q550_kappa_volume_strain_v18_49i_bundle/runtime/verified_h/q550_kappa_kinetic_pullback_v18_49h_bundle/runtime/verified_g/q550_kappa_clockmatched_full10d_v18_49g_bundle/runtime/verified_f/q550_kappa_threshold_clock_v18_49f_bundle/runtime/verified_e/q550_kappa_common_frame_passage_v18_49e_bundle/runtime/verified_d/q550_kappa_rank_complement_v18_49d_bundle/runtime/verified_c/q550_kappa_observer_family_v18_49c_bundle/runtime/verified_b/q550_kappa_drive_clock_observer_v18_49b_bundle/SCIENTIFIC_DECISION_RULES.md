# Scientific decision rules — v18.49b

1. Historical v18.48j covectors are INITIAL conditions ONLY at the reversal point for newly integrated v18.49b cotangent IVPs.
2. The 11D physical state uses the original equations, with the already established smooth prescribed Θ(t) and same six ramp durations and kappa choices as v18.49a.
3. The tangent/adjoint equations are 10D at fixed prescribed external control Θ, not a complete 11D drive-control variation.
4. Use `g.T @ delta_y` as a signed, observer-sensitive **readout**; changing its sign alone cannot prove material chirality or phase skew.
5. Check `g(t).T @ v(t)` against its initial value, using the same analytic Jacobian and an independent RHS finite-difference check. The dual pairing is an identity in the linearized variational system, NOT in two finite-amplitude trajectories.
6. The original phase-clock root positions, phase-lobe component counts and scalar geometric distances are independent of this chosen observer. Coordinate charts transform cotangent and tangent by dual pullback/pushforward, keeping the pairing invariant when both are transformed.
7. In reports count **12 unique barrier states**, not 96 independent physical experiments (4 thresholds * 2 observer channels repeat each barrier).
8. This is a floating-point diagnostic on `phaseblind` branch0 only, not an interval theorem, and not a physical material observer-independent handedness claim. Observer norm and projective angles require declaration of the underlying chart metric.
9. Keep reference mathematical files byte-for-byte identical to parent sources, and validate all SHA manifests before computing new results.
