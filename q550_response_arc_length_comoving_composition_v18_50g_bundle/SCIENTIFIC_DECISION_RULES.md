# v18.50g — Scientific decision rules

1. The response curve is evaluated only at the five supplied horizon samples. Report its **sampled polygonal path length**; never label it an exact continuous integral.
2. A shorter, 3-sample polyline and endpoint chord must be no longer than the five-sample polyline. Any missed length warns of under-resolution.
3. Endpoint response identity `R=L+T` is algebraic within the chosen chart; verify its deviation from the independent parent IVP response, but do not interpret it as a physical force decomposition.
4. The chord co-moving frame has the direction of `R[i+1]-R[i]`. It is undefined for a zero chord, which must be flagged. The signed advances of `ΔL` and `ΔT` must sum to the resultant chord length.
5. The common inherited whitened chart is fixed; alternate diagonal weighting is explicitly called a measurement stress test, not a newly established physical metric.
6. Compensations, changes of chord direction, and path sensitivity are *descriptive*. With only five horizons, no regime boundary, local continuous derivative, material memory, causal law, or topological invariant can be established.
7. Classification: `SAMPLED_RESPONSE_ARC_DIAGNOSTIC_NOT_CONTINUOUS_ARCLENGTH_OR_PHYSICAL_MEMORY_CERTIFICATE`.
