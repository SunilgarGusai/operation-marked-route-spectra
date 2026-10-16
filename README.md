# Operation-Marked Eccentricity-Weighted Route Spectra

**Public research reproducibility companion** for the manuscript *Operation-Marked Eccentricity-Weighted Route Spectra of Feedforward Architecture Graphs* by Sunilgar L. Gusai and Manoharsinh R. Jadeja.

## Scientific question

Can eccentricity-weighted operation-marked route matrices distinguish feedforward architectures whose ordinary operation-route matrix pencils and eccentricity-weighted adjacency controls are cospectral?

The paper constructs two seven-vertex operation-labelled seed-pair families, proves infinite-width spectral separation, and derives a balanced edge-transfer criterion. Mathematical verification is exact and does not require GPU training.

## Evidence and limitations

- Four standalone symbolic verification suites support exact polynomial, cospectrality, and weighted-transfer calculations.
- NAS-Bench-101 and NAS-Bench-201 model evaluations are **exploratory**. Their topology-level uncertainty intervals include zero; no predictive superiority is claimed.
- The original reserved holdout labels were not used, according to the archived development records.
- Full independent refitting of the 288 models requires licensed benchmark data and frozen features/checkpoints **not yet distributed here**.
- This repository is publicly visible, but an original-code license and final author approval of public software reuse have **not yet been granted**. Upstream GRAF code is separately MIT licensed.

## Repository publication status

The verified public-release archive is being populated. The final repository will contain mathematical verification source, frozen numerical summaries, methodological limitations, citation metadata, and an automated check workflow. This landing page is an initial checked-in record, not evidence that the full artifact is already available.

## Links

[Reviewer's reproduction quick start](QUICKSTART.md) · [Frozen results](docs/FROZEN_RESULTS.md) · [Claim boundaries](docs/CLAIM_BOUNDARIES.md) · [Data and benchmark provenance](docs/DATA_PROVENANCE.md) · [Upstream licensing](docs/LICENSING_STATUS.md)

**Authors:** Sunilgar L. Gusai (corresponding author), Manoharsinh R. Jadeja.
