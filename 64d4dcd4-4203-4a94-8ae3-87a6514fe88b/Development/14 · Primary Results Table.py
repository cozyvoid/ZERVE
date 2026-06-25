import pandas as pd
import numpy as np

# ── Input ─────────────────────────────────────────────────────────────────────
ps = county_priority_scores.copy()
stab = rank_stability_summary.copy()

# ── Build balanced_priority_results ──────────────────────────────────────────
# Merge rank range from stability summary
ps = ps.merge(
    stab[["county_fips", "rank_range", "rank_mean"]],
    on="county_fips", how="left"
)

COLS = [
    "rank_balanced",
    "county_name",
    "priority_balanced",
    "provider_scarcity",
    "primary_care_physicians_per_10000",
    "svi_overall",
    "svi_socioeconomic",
    "svi_household_characteristics",
    "svi_racial_ethnic_minority",
    "svi_housing_transportation",
    "ahrf_population_2022",
    "zero_primary_care_physicians",
    "has_current_geo_population_hpsa",
    "current_geo_population_max_score",
    "rank_access_focused",
    "rank_equity_focused",
    "rank_empirical_themes",
    "rank_range",
]

balanced_priority_results = (
    ps[COLS]
    .sort_values("rank_balanced")
    .reset_index(drop=True)
)

# ── Display helper ────────────────────────────────────────────────────────────
DISPLAY_COLS = [
    "rank_balanced", "county_name",
    "priority_balanced", "provider_scarcity", "svi_overall",
    "primary_care_physicians_per_10000",
    "ahrf_population_2022",
    "has_current_geo_population_hpsa",
    "zero_primary_care_physicians",
    "rank_access_focused", "rank_equity_focused", "rank_empirical_themes",
    "rank_range",
]

def fmt_table(df):
    """Return a copy with readable formatting for display."""
    d = df[DISPLAY_COLS].copy()
    d["priority_balanced"]                = d["priority_balanced"].map("{:.4f}".format)
    d["provider_scarcity"]                = d["provider_scarcity"].map("{:.4f}".format)
    d["svi_overall"]                      = d["svi_overall"].map("{:.3f}".format)
    d["primary_care_physicians_per_10000"] = d["primary_care_physicians_per_10000"].map("{:.2f}".format)
    d["ahrf_population_2022"]             = d["ahrf_population_2022"].map("{:,.0f}".format)
    d["has_current_geo_population_hpsa"]  = d["has_current_geo_population_hpsa"].map(
        lambda x: "Yes" if x else "No"
    )
    d["zero_primary_care_physicians"]     = d["zero_primary_care_physicians"].map(
        lambda x: "⚠ Zero" if x else ""
    )
    return d

print("=" * 90)
print("14 · PRIMARY RESULTS TABLE  —  balanced_priority_results")
print("    Scores are EXPLORATORY. Rankings are relative to California's 58 counties.")
print("    Terms: 'higher exploratory priority' and 'lower exploratory priority'.")
print("=" * 90)

print("\n── Top 10 counties — higher exploratory priority (balanced scenario) ─────────────────")
top10_display = fmt_table(balanced_priority_results.head(10))
print(top10_display.to_string(index=False))

print("\n── Bottom 10 counties — lower exploratory priority (balanced scenario) ──────────────")
bot10_display = fmt_table(balanced_priority_results.tail(10))
print(bot10_display.to_string(index=False))

print("\n── Counties with largest rank movement across scenarios (rank_range ≥ 12) ────────────")
# Pull from rank_stability_summary for range/movement details
big_movers = (
    balanced_priority_results[balanced_priority_results["rank_range"] >= 12]
    .sort_values("rank_range", ascending=False)
)
print(fmt_table(big_movers).to_string(index=False))
print(f"\n  Interpretation: large rank_range = result sensitive to weighting assumptions;")
print(f"  small rank_range = result robust across all four scenarios.")

print(f"\n── Table shape: {balanced_priority_results.shape}  (58 rows × {len(COLS)} cols)")
