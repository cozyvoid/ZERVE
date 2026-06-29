import pandas as pd
import numpy as np

# ── Input: merge county_fips back in (balanced_priority_results has no FIPS col) ──
bpr = balanced_priority_results.merge(
    county_priority_scores[["county_name", "county_fips"]],
    on="county_name", how="left"
)

top_q_n = 14  # top quartile of 58 counties

# ── Alignment category ────────────────────────────────────────────────────────
def align_category(row):
    hi_hist  = row["rank_balanced"] <= top_q_n
    has_hpsa = bool(row["has_current_geo_population_hpsa"])
    if hi_hist and has_hpsa:
        return "A – High historical priority / current HPSA"
    elif hi_hist and not has_hpsa:
        return "B – High historical priority / no current HPSA"
    elif not hi_hist and has_hpsa:
        return "C – Lower historical priority / current HPSA"
    else:
        return "D – Lower historical priority / no current HPSA"

bpr["alignment_category"] = bpr.apply(align_category, axis=1)

# ── Build hpsa_alignment_summary ──────────────────────────────────────────────
hpsa_alignment_summary = bpr[[
    "county_fips", "rank_balanced", "county_name",
    "priority_balanced", "provider_scarcity", "svi_overall",
    "primary_care_physicians_per_10000",
    "has_current_geo_population_hpsa", "current_geo_population_max_score",
    "ahrf_population_2022", "zero_primary_care_physicians",
    "alignment_category",
]].copy()

# Category-level summaries
cat_stats = (
    hpsa_alignment_summary.groupby("alignment_category")
    .agg(
        n_counties   = ("county_name",          "count"),
        median_score = ("priority_balanced",     "median"),
        median_rate  = ("primary_care_physicians_per_10000", "median"),
        median_svi   = ("svi_overall",           "median"),
        total_pop    = ("ahrf_population_2022",  "sum"),
    )
    .reset_index()
)
cat_stats["pct_ca_pop"] = (
    cat_stats["total_pop"] / bpr["ahrf_population_2022"].sum() * 100
).round(1)

# Score distribution by HPSA status
hpsa_yes_scores = bpr.loc[bpr["has_current_geo_population_hpsa"],  "priority_balanced"]
hpsa_no_scores  = bpr.loc[~bpr["has_current_geo_population_hpsa"], "priority_balanced"]

# Notable disagreements
cat_b = hpsa_alignment_summary[
    hpsa_alignment_summary["alignment_category"] == "B – High historical priority / no current HPSA"
].sort_values("rank_balanced")

cat_c = hpsa_alignment_summary[
    hpsa_alignment_summary["alignment_category"] == "C – Lower historical priority / current HPSA"
].sort_values("rank_balanced")

# ── Print ──────────────────────────────────────────────────────────────────────
print("=" * 80)
print("16 · HPSA ALIGNMENT ANALYSIS")
print("    Historical score = 2022 SVI + physician data. HPSA = 2026 current snapshot.")
print("    Disagreement does NOT prove either measure is incorrect.")
print("=" * 80)

print(f"\n── Alignment categories (top-quartile = rank ≤ {top_q_n}) ──────────────────────────")
cs = cat_stats.copy()
cs["total_pop"] = cs["total_pop"].map("{:,.0f}".format)
cs["median_score"] = cs["median_score"].round(4)
cs["median_rate"]  = cs["median_rate"].round(2)
cs["median_svi"]   = cs["median_svi"].round(3)
print(cs.to_string(index=False))

print(f"\n── Balanced score by current HPSA status ────────────────────────────────────────")
print(f"  HPSA-designated (n={len(hpsa_yes_scores)}): "
      f"median={hpsa_yes_scores.median():.4f}  "
      f"mean={hpsa_yes_scores.mean():.4f}  "
      f"min={hpsa_yes_scores.min():.4f}  max={hpsa_yes_scores.max():.4f}")
print(f"  Not designated  (n={len(hpsa_no_scores)}): "
      f"median={hpsa_no_scores.median():.4f}  "
      f"mean={hpsa_no_scores.mean():.4f}  "
      f"min={hpsa_no_scores.min():.4f}  max={hpsa_no_scores.max():.4f}")

print(f"\n── Top-10 counties vs current HPSA status ──────────────────────────────────────")
top10_disp = hpsa_alignment_summary[hpsa_alignment_summary["rank_balanced"] <= 10][[
    "rank_balanced", "county_name", "priority_balanced",
    "primary_care_physicians_per_10000", "svi_overall",
    "has_current_geo_population_hpsa", "alignment_category"
]].copy()
top10_disp["priority_balanced"] = top10_disp["priority_balanced"].map("{:.4f}".format)
top10_disp["primary_care_physicians_per_10000"] = top10_disp["primary_care_physicians_per_10000"].map("{:.2f}".format)
print(top10_disp.to_string(index=False))

print(f"\n── Category B: High historical priority / NO current geo/pop HPSA ──────────────")
print(f"  Possible reasons: sub-county adequacy, 4-yr reporting gap, different provider")
print(f"  types in HPSA criteria, or near-but-below designation threshold.")
b_disp = cat_b[["rank_balanced","county_name","priority_balanced",
                  "primary_care_physicians_per_10000","svi_overall","ahrf_population_2022"]].copy()
b_disp["ahrf_population_2022"] = b_disp["ahrf_population_2022"].map("{:,.0f}".format)
b_disp["priority_balanced"] = b_disp["priority_balanced"].map("{:.4f}".format)
b_disp["primary_care_physicians_per_10000"] = b_disp["primary_care_physicians_per_10000"].map("{:.2f}".format)
print(b_disp.to_string(index=False))

print(f"\n── Category C: Current HPSA / LOWER historical priority (n={len(cat_c)}) ────────")
print(f"  Possible reasons: sub-county/population-group designation, earlier criteria,")
print(f"  or provider mix not captured in AHRF physician count.")
c_disp = cat_c.head(15)[["rank_balanced","county_name","priority_balanced",
                           "primary_care_physicians_per_10000","svi_overall",
                           "current_geo_population_max_score"]].copy()
c_disp["priority_balanced"] = c_disp["priority_balanced"].map("{:.4f}".format)
c_disp["primary_care_physicians_per_10000"] = c_disp["primary_care_physicians_per_10000"].map("{:.2f}".format)
print(c_disp.to_string(index=False))

print(f"\n  hpsa_alignment_summary shape: {hpsa_alignment_summary.shape}")
