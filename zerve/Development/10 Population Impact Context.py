import pandas as pd
import numpy as np

# ── Input ─────────────────────────────────────────────────────────────────────
bpr = balanced_priority_results.copy()
total_ca_pop = bpr["ahrf_population_2022"].sum()

# ── Population totals for top tiers ──────────────────────────────────────────
def pop_tier(df, n):
    sub = df[df["rank_balanced"] <= n]
    pop = sub["ahrf_population_2022"].sum()
    pct = pop / total_ca_pop * 100
    return pop, pct, list(sub["county_name"])

pop5,  pct5,  names5  = pop_tier(bpr, 5)
pop10, pct10, names10 = pop_tier(bpr, 10)
top_q_n = 14  # top quartile of 58 counties
pop14, pct14, names14 = pop_tier(bpr, top_q_n)

# HPSA-designated counties
hpsa_pop = bpr.loc[bpr["has_current_geo_population_hpsa"], "ahrf_population_2022"].sum()
hpsa_pct = hpsa_pop / total_ca_pop * 100

# ── 2×2 planning classification ───────────────────────────────────────────────
# Dimensions: balanced priority vs county population, each split at median.
# This is a DESCRIPTIVE planning tool, NOT a second score.
med_score = bpr["priority_balanced"].median()
med_pop   = bpr["ahrf_population_2022"].median()

def classify_2x2(row):
    hi_priority = row["priority_balanced"] >= med_score
    hi_pop      = row["ahrf_population_2022"] >= med_pop
    if hi_priority and hi_pop:
        return "1 – Higher need / larger population"
    elif hi_priority and not hi_pop:
        return "2 – Higher need / smaller population"
    elif not hi_priority and hi_pop:
        return "3 – Lower need / larger population"
    else:
        return "4 – Lower need / smaller population"

bpr["planning_category"] = bpr.apply(classify_2x2, axis=1)

# Summaries per category
cat_summary = (
    bpr.groupby("planning_category")
    .agg(
        county_count    = ("county_name", "count"),
        total_pop       = ("ahrf_population_2022", "sum"),
        median_score    = ("priority_balanced", "median"),
        median_rate     = ("primary_care_physicians_per_10000", "median"),
    )
    .reset_index()
)
cat_summary["pct_ca_pop"] = (cat_summary["total_pop"] / total_ca_pop * 100).round(1)
cat_summary["total_pop"]  = cat_summary["total_pop"].map("{:,.0f}".format)
cat_summary["median_score"]  = cat_summary["median_score"].round(4)
cat_summary["median_rate"]   = cat_summary["median_rate"].round(2)

# Build population_impact_context — one row per county
KEEP = [
    "rank_balanced", "county_name", "priority_balanced",
    "primary_care_physicians_per_10000", "ahrf_population_2022",
    "has_current_geo_population_hpsa", "zero_primary_care_physicians",
    "planning_category",
]
population_impact_context = bpr[KEEP].copy().reset_index(drop=True)

# Notable counties in category 1 (high need, large pop)
cat1 = bpr[bpr["planning_category"] == "1 – Higher need / larger population"].sort_values("rank_balanced")

# High-score but small population
cat2 = bpr[bpr["planning_category"] == "2 – Higher need / smaller population"].sort_values("rank_balanced")

# ── Print ──────────────────────────────────────────────────────────────────────
print("=" * 72)
print("15 · POPULATION CONTEXT  (balanced scenario)")
print("    ⚠  This section does NOT create an alternative priority score.")
print("    Population is a planning dimension, not a scoring component.")
print("=" * 72)

print(f"\n  Total CA population (AHRF 2022): {total_ca_pop:>14,.0f}")

print(f"\n── Population represented by higher-priority counties ───────────────")
print(f"  Top  5 counties : {pop5:>14,.0f}  ({pct5:.1f}% of CA pop)  {names5}")
print(f"  Top 10 counties : {pop10:>14,.0f}  ({pct10:.1f}% of CA pop)")
print(f"  Top quartile    : {pop14:>14,.0f}  ({pct14:.1f}% of CA pop)  [{top_q_n} counties]")
print(f"  HPSA-designated : {hpsa_pop:>14,.0f}  ({hpsa_pct:.1f}% of CA pop)  [current geo/pop HPSA]")

print(f"\n── 2×2 Planning classification ──────────────────────────────────────")
print(f"  Split: priority ≥ median ({med_score:.4f})  ×  population ≥ median ({med_pop:,.0f})")
print(f"  ⚠  Medians are exploratory thresholds, not official policy cutoffs.\n")
print(cat_summary.to_string(index=False))

print(f"\n── Category 1 — Higher need / larger population ─────────────────────")
print(f"  These counties combine elevated exploratory priority with")
print(f"  comparatively large resident populations.")
c1_disp = cat1[["rank_balanced","county_name","priority_balanced",
                  "ahrf_population_2022","primary_care_physicians_per_10000"]].copy()
c1_disp["ahrf_population_2022"] = c1_disp["ahrf_population_2022"].map("{:,.0f}".format)
c1_disp["priority_balanced"]    = c1_disp["priority_balanced"].map("{:.4f}".format)
c1_disp["primary_care_physicians_per_10000"] = c1_disp["primary_care_physicians_per_10000"].map("{:.2f}".format)
print(c1_disp.to_string(index=False))

print(f"\n── Category 2 — Higher need / smaller population ────────────────────")
print(f"  These counties show elevated exploratory priority but smaller")
print(f"  populations. Intensity of need may be high; scale of impact smaller.")
c2_disp = cat2[["rank_balanced","county_name","priority_balanced",
                  "ahrf_population_2022","primary_care_physicians_per_10000"]].copy()
c2_disp["ahrf_population_2022"] = c2_disp["ahrf_population_2022"].map("{:,.0f}".format)
c2_disp["priority_balanced"]    = c2_disp["priority_balanced"].map("{:.4f}".format)
c2_disp["primary_care_physicians_per_10000"] = c2_disp["primary_care_physicians_per_10000"].map("{:.2f}".format)
print(c2_disp.to_string(index=False))

print(f"\n  population_impact_context shape: {population_impact_context.shape}")
