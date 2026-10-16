"""Check published aggregate table and principal contrasts, without refitting models."""
import csv, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/VELE09_Integrated_CV_Metrics.csv').open(newline='',encoding='utf8') as f:
    rows={(r['dataset'],r['variant']):r for r in csv.DictReader(f)}
with (ROOT/'results/VELE09_Integrated_Paired_Topology_Comparisons.csv').open(newline='',encoding='utf8') as f:
    paired={(r['dataset'],r['baseline']):r for r in csv.DictReader(f)}
for dataset in ('NB101','NB201'):
    base=rows[(dataset,'GRAF_S2')];weighted=rows[(dataset,'GRAF_S2_WEIGHTED')]
    mu=float(base['mean_micro_mae_pp'])-float(weighted['mean_micro_mae_pp'])
    macro=float(base['mean_equal_topology_mae_pp'])-float(weighted['mean_equal_topology_mae_pp'])
    ref=float(paired[(dataset,'GRAF_S2')]['mean_topology_improvement_pp'])
    assert math.isclose(macro,ref,abs_tol=1e-10)
    assert math.isfinite(mu) and math.isfinite(macro)
    low=float(paired[(dataset,'GRAF_S2')]['exploratory_cluster_bootstrap_low_pp'])
    high=float(paired[(dataset,'GRAF_S2')]['exploratory_cluster_bootstrap_high_pp'])
    assert low < 0 < high, 'Reported conclusion relies on both intervals spanning zero'
    print(dataset,'architecture improvement',round(mu,5),'pp; topology improvement',round(macro,5),'pp')
print('PASS: the published summary-level comparisons are internally consistent; this is NOT a 288-model refit.')
