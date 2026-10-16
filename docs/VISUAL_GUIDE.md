# Visual guide

Every SVG in this folder is a text-based vector source, scales to high-density monitors, works in GitHub's Markdown viewer, and requires no licensed font files.

| File | Scientific role | Interpretation |
| :--- | :--- | :--- |
| [Repository header](assets/repository-banner.svg) | Recognizable project identity | The small DAG on the right is schematic, not a theorem witness |
| [Exact witness families](assets/witness-pairs.svg) | Displays the two operation-labelled seven-vertex DAG pairs | Generated from the frozen [arc lists](../figures/seed_arc_lists.json); solid α, dashed β |
| [Spectral mechanism](assets/spectral-mechanism.svg) | Explains route counting, operation separation, eccentricity weighting | Definitions and workflow; not a performance chart |
| [Evidence layers](assets/evidence-layers.svg) | Keeps exact proofs, summary checks, and unavailable full refits distinct | Does not imply benchmark predictive superiority |

The publication diagrams in the LaTeX manuscript are generated separately using TikZ. Verify scientific graph diagrams against source arc lists before editing. Avoid adding numerical performance figures that exaggerate the small, uncertain incremental benefit.
