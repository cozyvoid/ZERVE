import pandas as pd
import numpy as np

# ── Input: scoring dataframe with all four scenario scores ───────────────────
ps = county_priority_scores.copy()

# ── Ranking helper ────────────────────────────────────────────────────────────
# Ties broken alphabetically by county_name (deterministic display order only).
# Uses a two-step sort: sort by score DESC then county_name ASC,
# then assign sequential integers starting at 1.
# This preserves tied scores while providing a stable, reproducible row order.

def rank_scenario(df, score_col):
    """
    Return integer ranks 1..58 sorted by score descending, then county_name asc.
    Counties with identical scores receive adjacent ranks, not averaged.
    This is intentional: it makes ties visible in the table without implying
    substantive differences between tied counties.
    """
    sorted_df = df.sort_values(
        [score_col, "county_name"], ascending=[False, True]
    ).reset_index(drop=True)
    sorted_df["_rank"] = sorted_df.index + 1
    # Restore original row order by merging back
    result = df[["county_fips"]].merge(
        sorted_df[["county_fips", "_rank"]], on="county_fips", how="left"
    )
    return result["_rank"].values

# ── Assign ranks for each scenario ───────────────────────────────────────────
ps["rank_balanced"]         = rank_scenario(ps, "priority_balanced")
ps["rank_access_focused"]   = rank_scenario(ps, "priority_access_focused")
ps["rank_equity_focused"]   = rank_scenario(ps, "priority_equity_focused")
ps["rank_empirical_themes"] = rank_scenario(ps, "priority_empirical_themes")

# Update exported variable
county_priority_scores = ps

# ── Build long-form scenario_rankings ────────────────────────────────────────
SCENARIO_MAP = {
    "balanced":          ("priority_balanced",         "rank_balanced"),
    "access_focused":    ("priority_access_focused",   "rank_access_focused"),
    "equity_focused":    ("priority_equity_focused",   "rank_equity_focused"),
    "empirical_themes":  ("priority_empirical_themes", "rank_empirical_themes"),
}

CONTEXT_COLS = [
    "county_fips",
    "county_name",
    "provider_scarcity",
    "svi_overall",
    "primary_care_physicians_per_10000",
    "ahrf_population_2022",
    "has_current_geo_population_hpsa",
    "zero_primary_care_physicians",
]

long_rows = []
for scenario, (score_col, rank_col) in SCENARIO_MAP.items():
    tmp = ps[CONTEXT_COLS + [score_col, rank_col]].copy()
    tmp.rename(columns={score_col: "score", rank_col: "rank"}, inplace=True)
    tmp["scenario"] = scenario
    long_rows.append(tmp)

scenario_rankings = (
    pd.concat(long_rows, ignore_index=True)
    [[
        "county_fips",
        "county_name",
        "scenario",
        "score",
        "rank",
        "provider_scarcity",
        "svi_overall",
        "primary_care_physicians_per_10000",
        "ahrf_population_2022",
        "has_current_geo_population_hpsa",
        "zero_primary_care_physicians",
    ]]
    .sort_values(["scenario", "rank"])
    .reset_index(drop=True)
)

# ── Print summary ─────────────────────────────────────────────────────────────
print("=" * 70)
print("12 · SCENARIO RANKINGS")
print("=" * 70)
print(f"\nscenario_rankings shape: {scenario_rankings.shape}")
print(f"  4 scenarios × 58 counties = {4 * 58} rows")

for scenario in SCENARIO_MAP:
    sub = scenario_rankings[scenario_rankings["scenario"] == scenario]
    top5 = sub.nsmallest(5, "rank")[["county_name", "score", "rank"]]
    print(f"\n── {scenario} — top 5 ────────────────────────────────────────────")
    print(top5.to_string(index=False))

# Verify all ranks 1..58 used exactly once per scenario
print("\n── Rank completeness check ──────────────────────────────────────────")
PASS = "✓"; FAIL = "✗"; errors = []
for scenario in SCENARIO_MAP:
    sub = scenario_rankings[scenario_rankings["scenario"] == scenario]
    ranks = sorted(sub["rank"].tolist())
    expected = list(range(1, 59))
    if ranks != expected:
        errors.append(f"  {FAIL} {scenario}: ranks not 1..58")
    else:
        print(f"  {PASS} {scenario}: ranks 1–58 assigned exactly once")

if not errors:
    print(f"\n  {PASS} All ranking checks passed.")
else:
    for e in errors:
        print(e)
