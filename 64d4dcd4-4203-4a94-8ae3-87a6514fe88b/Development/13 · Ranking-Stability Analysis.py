import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations

# ── Input ─────────────────────────────────────────────────────────────────────
ps = county_priority_scores.copy()

RANK_COLS = {
    "balanced":         "rank_balanced",
    "access_focused":   "rank_access_focused",
    "equity_focused":   "rank_equity_focused",
    "empirical_themes": "rank_empirical_themes",
}
N = 58
TOP_Q = N // 4  # top quartile = top 14 (floor)

# ── Per-county stability stats ─────────────────────────────────────────────────
ranks_df = ps[["county_fips", "county_name"] + list(RANK_COLS.values())].copy()

rank_matrix = ranks_df[list(RANK_COLS.values())].values  # shape (58, 4)

ranks_df["rank_min"]   = rank_matrix.min(axis=1)
ranks_df["rank_max"]   = rank_matrix.max(axis=1)
ranks_df["rank_range"] = rank_matrix.max(axis=1) - rank_matrix.min(axis=1)
ranks_df["rank_mean"]  = rank_matrix.mean(axis=1).round(2)
ranks_df["rank_std"]   = rank_matrix.std(axis=1, ddof=1).round(3)

# Top-5 and top-10 flags per scenario
for scen, col in RANK_COLS.items():
    ranks_df[f"top5_{scen}"]  = ranks_df[col] <= 5
    ranks_df[f"top10_{scen}"] = ranks_df[col] <= 10

# Number of scenarios in which county appears in top quartile (top 14)
ranks_df["top_quartile_scenario_count"] = sum(
    (ranks_df[col] <= TOP_Q).astype(int) for col in RANK_COLS.values()
)

# Consistent top-5: in top 5 across ALL four scenarios
ranks_df["consistent_top5"]  = ranks_df[[f"top5_{s}"  for s in RANK_COLS]].all(axis=1)
ranks_df["consistent_top10"] = ranks_df[[f"top10_{s}" for s in RANK_COLS]].all(axis=1)

rank_stability_summary = ranks_df.drop(columns=list(RANK_COLS.values())).copy()

# ── Spearman rank correlations between scenario pairs ─────────────────────────
scenario_names = list(RANK_COLS.keys())
pairs = list(combinations(scenario_names, 2))

corr_rows = []
for s1, s2 in pairs:
    r, p = stats.spearmanr(ps[RANK_COLS[s1]], ps[RANK_COLS[s2]])
    corr_rows.append({
        "scenario_1": s1, "scenario_2": s2,
        "spearman_r": round(r, 4), "p_value": round(p, 6),
    })
scenario_pair_correlations = pd.DataFrame(corr_rows)

# ── Top-10 overlap and Jaccard similarity ─────────────────────────────────────
jaccard_rows = []
for s1, s2 in pairs:
    top10_s1 = set(ps.loc[ps[RANK_COLS[s1]] <= 10, "county_fips"])
    top10_s2 = set(ps.loc[ps[RANK_COLS[s2]] <= 10, "county_fips"])
    intersect = len(top10_s1 & top10_s2)
    union     = len(top10_s1 | top10_s2)
    jaccard   = round(intersect / union, 4) if union > 0 else 0.0
    jaccard_rows.append({
        "scenario_1": s1, "scenario_2": s2,
        "top10_overlap_count": intersect,
        "jaccard_similarity": jaccard,
    })
top10_jaccard = pd.DataFrame(jaccard_rows)

# ── Print results ─────────────────────────────────────────────────────────────
print("=" * 72)
print("13 · RANKING-STABILITY ANALYSIS")
print("=" * 72)

print(f"\n── Counties consistently in top 5 across ALL scenarios ─────────────")
t5 = rank_stability_summary[rank_stability_summary["consistent_top5"]][
    ["county_name", "rank_min", "rank_max", "rank_range", "rank_mean"]
]
print(t5.to_string(index=False) if len(t5) else "  (none in top 5 under all 4 scenarios)")

print(f"\n── Counties consistently in top 10 across ALL scenarios ────────────")
t10 = rank_stability_summary[rank_stability_summary["consistent_top10"]].sort_values("rank_mean")[
    ["county_name", "rank_min", "rank_max", "rank_range", "rank_mean"]
]
print(t10.to_string(index=False))

print(f"\n── Counties with LARGEST rank movement (range ≥ 10) ────────────────")
movers = (
    rank_stability_summary[rank_stability_summary["rank_range"] >= 10]
    .sort_values("rank_range", ascending=False)
    [["county_name", "rank_min", "rank_max", "rank_range", "rank_mean", "rank_std"]]
)
print(movers.to_string(index=False) if len(movers) else "  (no counties with range ≥ 10)")

print(f"\n── Spearman rank correlations between scenario pairs ────────────────")
print(scenario_pair_correlations.to_string(index=False))
print("  Interpretation: r close to 1.0 = scenarios agree; lower r = divergence")

print(f"\n── Top-10 overlap and Jaccard similarity ────────────────────────────")
print(top10_jaccard.to_string(index=False))
print(f"  Jaccard = |intersection| / |union|; 1.0 = identical top-10 sets")

print(f"\n── Top-quartile consistency (# scenarios where county ranks ≤ {TOP_Q}) ──")
tq = (
    rank_stability_summary[rank_stability_summary["top_quartile_scenario_count"] == 4]
    .sort_values("rank_mean")
    [["county_name", "rank_mean", "rank_range", "top_quartile_scenario_count"]]
)
print(f"  Counties in top quartile under ALL 4 scenarios (n={len(tq)}):")
print(tq.to_string(index=False))
