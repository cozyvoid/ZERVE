import pandas as pd
import numpy as np

df = ca_county_healthcare_access_joined.copy()

# ── Thresholds (county-level medians and quartiles) ───────────────────────────
med_svi    = df["svi_overall"].median()
med_rate   = df["primary_care_physicians_per_10000"].median()
p25_rate   = df["primary_care_physicians_per_10000"].quantile(0.25)
p75_svi    = df["svi_overall"].quantile(0.75)

print("Thresholds used (all exploratory — not official policy cutoffs):")
print(f"  Median SVI overall                    : {med_svi:.4f}")
print(f"  Median physician rate per 10,000      : {med_rate:.4f}")
print(f"  Bottom-quartile physician rate (≤ p25): {p25_rate:.4f}")
print(f"  Top-quartile SVI (≥ p75)              : {p75_svi:.4f}")

# ── Five binary conditions ────────────────────────────────────────────────────
# Condition labels use neutral language — this is NOT a priority ranking.
df["cond_svi_above_median"]      = df["svi_overall"] >= med_svi
df["cond_rate_below_median"]     = df["primary_care_physicians_per_10000"] <= med_rate
df["cond_has_geo_pop_hpsa"]      = df["has_current_geo_population_hpsa"].astype(bool)
df["cond_rate_bottom_quartile"]  = df["primary_care_physicians_per_10000"] <= p25_rate
df["cond_svi_top_quartile"]      = df["svi_overall"] >= p75_svi

COND_COLS = [
    "cond_svi_above_median",
    "cond_rate_below_median",
    "cond_has_geo_pop_hpsa",
    "cond_rate_bottom_quartile",
    "cond_svi_top_quartile",
]

df["exploratory_priority_conditions_met"] = df[COND_COLS].sum(axis=1)
df["candidate_for_closer_review"]         = df["exploratory_priority_conditions_met"] >= 2

# ── Build output table ────────────────────────────────────────────────────────
exploratory_review_conditions = df[[
    "county_fips", "county_name",
    "svi_overall", "primary_care_physicians_per_10000",
    "ahrf_population_2022", "has_current_geo_population_hpsa",
    "cond_svi_above_median", "cond_rate_below_median",
    "cond_has_geo_pop_hpsa", "cond_rate_bottom_quartile",
    "cond_svi_top_quartile",
    "exploratory_priority_conditions_met",
    "candidate_for_closer_review",
]].copy().sort_values(
    ["exploratory_priority_conditions_met", "svi_overall"],
    ascending=[False, False]
)

# ── Print full table ──────────────────────────────────────────────────────────
print("\n" + "=" * 86)
print("09g · CANDIDATE COUNTIES FOR CLOSER REVIEW")
print("  Counties meeting ≥ 2 of 5 exploratory conditions.")
print("  This is NOT a priority ranking or scoring formula.")
print("  Conditions met simultaneously — weighting not yet applied.")
print("=" * 86)

# Condition column abbreviations for compact display
SHORT = {
    "cond_svi_above_median":     "SVI≥med",
    "cond_rate_below_median":    "Rate≤med",
    "cond_has_geo_pop_hpsa":     "HPSA",
    "cond_rate_bottom_quartile": "Rate≤p25",
    "cond_svi_top_quartile":     "SVI≥p75",
}

print(f"\n{'County':<30} {'SVI':>6}  {'Rate':>7}  {'SVI≥med':>7}  "
      f"{'Rate≤med':>8}  {'HPSA':>4}  {'Rate≤p25':>8}  {'SVI≥p75':>7}  "
      f"{'#Cond':>5}  {'Candidate':>9}")
print("-" * 96)
for _, r in exploratory_review_conditions.iterrows():
    flag = "✓" if r["candidate_for_closer_review"] else ""
    print(f"  {r['county_name']:<28} {r['svi_overall']:>6.3f}  "
          f"{r['primary_care_physicians_per_10000']:>7.2f}  "
          f"{'Y' if r['cond_svi_above_median'] else 'N':>7}  "
          f"{'Y' if r['cond_rate_below_median'] else 'N':>8}  "
          f"{'Y' if r['cond_has_geo_pop_hpsa'] else 'N':>4}  "
          f"{'Y' if r['cond_rate_bottom_quartile'] else 'N':>8}  "
          f"{'Y' if r['cond_svi_top_quartile'] else 'N':>7}  "
          f"{r['exploratory_priority_conditions_met']:>5.0f}  {flag:>9}")

# Summary
cands = exploratory_review_conditions[exploratory_review_conditions["candidate_for_closer_review"]]
all5  = exploratory_review_conditions[exploratory_review_conditions["exploratory_priority_conditions_met"] == 5]

print(f"\n── Summary ──────────────────────────────────────────────────────────")
print(f"  Counties meeting ≥ 2 conditions (candidates): {len(cands)}")
print(f"  Counties meeting all 5 conditions            : {len(all5)}")
if not all5.empty:
    print(f"  All-5 counties: {', '.join(all5['county_name'].tolist())}")
print(f"\n  Condition distribution:")
for n_cond in range(6):
    ct = (exploratory_review_conditions["exploratory_priority_conditions_met"] == n_cond).sum()
    bar = "█" * ct
    print(f"    {n_cond} conditions: {ct:>3} counties  {bar}")
print("\n  Reminder: meeting more conditions does not imply greater true need.")
print("  Median/quartile thresholds are exploratory conveniences.")
print("  A transparent weighting framework will be applied in Milestone 4.")
