# Scientific decision rules — Q550 v18.49s

- **Null control:** `||U_reverse U_forward - I||_F < 1e-8`; otherwise reject.
- **Transport validation:** maximum endpoint aggregate-subspace reconstruction error `< 1e-4`; otherwise reject.
- **Connector validity:** smallest singular value `> 1e-7`, endpoint mapping residual `< 1e-6`.
- **Loop validity:** `||H10 S_Astart H10.T - S_Astart||_F < 2e-4`.
- **Parent regression:** endpoint r relative rotation to within `0.002°` at the same q-range.
- **Gauge tests:** angle invariant under independent eigenline signs and constant orthogonal chart changes.
- **Path dependence:** a nonzero angle above step/refinement scale under an explicitly defined connector is a numerical geometric result, not a material-memory claim.
- **Physical memory:** NOT tested as a closed physical outbound–return experiment because exact matching of all endpoint states and a physically reversed drive have not been established.
- **Causality:** no causal attribution to numerators/gaps or a physical torsional flip.
