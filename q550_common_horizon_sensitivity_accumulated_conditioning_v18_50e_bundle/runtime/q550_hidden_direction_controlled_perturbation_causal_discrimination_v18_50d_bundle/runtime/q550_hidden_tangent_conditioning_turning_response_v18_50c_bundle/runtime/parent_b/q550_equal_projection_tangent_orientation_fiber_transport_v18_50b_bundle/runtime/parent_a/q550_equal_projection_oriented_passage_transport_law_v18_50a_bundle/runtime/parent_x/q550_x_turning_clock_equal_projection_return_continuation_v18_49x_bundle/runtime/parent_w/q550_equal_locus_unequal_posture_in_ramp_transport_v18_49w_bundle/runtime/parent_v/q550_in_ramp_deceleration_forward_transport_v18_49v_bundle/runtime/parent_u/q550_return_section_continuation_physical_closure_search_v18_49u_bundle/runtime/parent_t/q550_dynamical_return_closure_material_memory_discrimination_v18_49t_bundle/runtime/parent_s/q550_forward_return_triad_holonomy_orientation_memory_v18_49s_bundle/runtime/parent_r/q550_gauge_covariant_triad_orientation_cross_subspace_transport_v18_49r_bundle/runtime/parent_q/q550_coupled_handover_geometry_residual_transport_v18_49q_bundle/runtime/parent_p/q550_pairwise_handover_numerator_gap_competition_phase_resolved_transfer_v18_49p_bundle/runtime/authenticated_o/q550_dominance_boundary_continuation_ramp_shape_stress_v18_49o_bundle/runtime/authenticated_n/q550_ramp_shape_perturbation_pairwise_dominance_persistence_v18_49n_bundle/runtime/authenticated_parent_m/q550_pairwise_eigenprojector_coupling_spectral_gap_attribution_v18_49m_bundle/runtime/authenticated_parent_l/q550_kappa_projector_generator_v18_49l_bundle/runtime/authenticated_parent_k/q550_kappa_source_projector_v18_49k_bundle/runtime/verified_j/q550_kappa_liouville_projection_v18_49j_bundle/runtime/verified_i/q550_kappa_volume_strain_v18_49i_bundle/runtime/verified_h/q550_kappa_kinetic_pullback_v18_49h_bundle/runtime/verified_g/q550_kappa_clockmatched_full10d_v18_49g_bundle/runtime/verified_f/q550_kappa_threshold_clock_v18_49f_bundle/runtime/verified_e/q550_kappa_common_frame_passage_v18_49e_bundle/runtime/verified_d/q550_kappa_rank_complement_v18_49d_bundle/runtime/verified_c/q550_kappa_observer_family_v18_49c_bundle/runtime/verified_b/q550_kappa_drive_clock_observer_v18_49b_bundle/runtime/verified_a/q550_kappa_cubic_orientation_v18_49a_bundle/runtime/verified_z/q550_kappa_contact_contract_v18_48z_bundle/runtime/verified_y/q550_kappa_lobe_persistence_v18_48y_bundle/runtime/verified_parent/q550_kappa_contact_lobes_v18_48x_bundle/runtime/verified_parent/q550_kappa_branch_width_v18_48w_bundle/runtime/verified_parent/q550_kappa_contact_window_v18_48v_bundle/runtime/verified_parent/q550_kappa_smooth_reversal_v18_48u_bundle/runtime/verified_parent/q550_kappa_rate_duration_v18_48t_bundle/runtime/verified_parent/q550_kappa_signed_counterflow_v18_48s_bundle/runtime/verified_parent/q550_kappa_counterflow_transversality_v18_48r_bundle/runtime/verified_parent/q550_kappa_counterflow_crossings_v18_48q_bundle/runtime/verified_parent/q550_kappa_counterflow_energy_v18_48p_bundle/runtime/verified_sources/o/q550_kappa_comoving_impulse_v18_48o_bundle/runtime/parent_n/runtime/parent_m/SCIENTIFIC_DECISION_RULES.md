# Scientific decision rules (v18.48m)

- Never infer exact rank from float64 threshold or precision-floor singular values.
- Declare a numerical shared-direction candidate only if its principal angle is smaller than the chosen angular tolerance; always report rank and mandatory intersection dimension.
- Measure each candidate with the original two source maps on both adjacent states. Discard or flag candidates in which both source activities are unresolved.
- A 2D crossing does not imply any 10D intersection: compare full principal angles and projection norms.
- Large projector gap at a rank change can be purely an admission/removal event under the chosen cutoff.
- To claim physical observer transport, integrate and verify the adjoint system; this audit only compares instantaneous subspaces sampled along previous Q550 trajectories.
- To claim an exact shared algebraic direction, supply a symbolic identity or a certified bound, not just SVD.
