# Dataset and source provenance

- NAS-Bench-101: Ying et al., ICML 2019. Local frozen record set contained 3,976 architecture records; the manuscript's grouped CV pooled 3,359 previously observed training/development records while 617 reserved records remained masked.
- NAS-Bench-201: Dong and Yang, ICLR 2020. Local frozen usable cohort contained 15,040 architecture records; grouped CV pooled 12,544 previously observed training/development records and retained 2,496 reserved records.
- GRAF: Kadlecová et al., ICML 2024; the adapted graph-feature implementation is *source-aligned*, not an official end-to-end reproduction. MIT notice retained.
- `docs/SOURCE_SHA256.json` records frozen source fingerprints; original data and protected labels have **not** been redistributed.

For a future full independent refit, obtain benchmark archives directly from the authoritative providers and reconstruct all transforms, record-selection decisions and fixed partitions according to `docs/HISTORICAL_COMPUTATIONAL_PROTOCOL.md`. Do not infer that the present checkout includes all those prerequisites.
