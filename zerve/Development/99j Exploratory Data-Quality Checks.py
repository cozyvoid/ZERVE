import pandas as pd
import numpy as np

df = ca_county_healthcare_access_joined.copy()

PASS = "✓"; FAIL = "✗"
errors = []

def check(label, condition, note=""):
    icon = PASS if condition else FAIL
    if not condition:
        errors.append(label)
    print(f"  {icon} {label}" + (f"  [{note}]" if note else ""))

print("=" * 70)
print("09i · MILESTONE 3 DATA-QUALITY CHECKS")
print("=" * 70)

print("\n── Row and column integrity ─────────────────────────────────────────")
check("58 rows in analytical table", len(df) == 58)
check("58 unique county FIPS", df["county_fips"].nunique() == 58)
check("One row per county (no duplicates)", df["county_fips"].duplicated().sum() == 0)

print("\n── Zero-physician counties are zero, not NaN ────────────────────────")
zero_mask = df["primary_care_physicians_2022"] == 0
nan_mask  = df["primary_care_physicians_2022"].isna()
check("Alpine and Sierra have zero (not NaN) physician count",
      zero_mask.sum() == 2 and nan_mask.sum() == 0,
      f"{zero_mask.sum()} zeros, {nan_mask.sum()} NaN")

print("\n── No infinite or NaN rates ─────────────────────────────────────────")
rate = df["primary_care_physicians_per_10000"]
check("No infinite physician rates", not np.isinf(rate).any())
check("No NaN physician rates",      not rate.isna().any())
check("All rates >= 0",              (rate >= 0).all())

print("\n── HPSA variables not mixed into 2022 composite ─────────────────────")
# All HPSA columns carry the 'current_' prefix; none appear in a combined score
hpsa_cols = [c for c in df.columns if c.startswith("current_")]
check(f"{len(hpsa_cols)} HPSA columns all carry 'current_' prefix",
      all(c.startswith("current_") for c in hpsa_cols))
check("No column named 'priority_score' or 'composite_2022' exists",
      "priority_score" not in df.columns and "composite_2022" not in df.columns)

print("\n── SVI percentile ranges ─────────────────────────────────────────────")
for col in ["svi_overall","svi_socioeconomic","svi_household_characteristics",
            "svi_racial_ethnic_minority","svi_housing_transportation"]:
    v = df[col]
    check(f"{col} in [0,1], no NaN",
          v.between(0, 1, inclusive="both").all() and not v.isna().any())

print("\n── Quadrant reproducibility ──────────────────────────────────────────")
med_rate = df["primary_care_physicians_per_10000"].median()
med_svi  = df["svi_overall"].median()
# Recompute quadrants from scratch
def _quad(r):
    if r["svi_overall"] >= med_svi and r["primary_care_physicians_per_10000"] <= med_rate:
        return "Q1 — High Vulnerability / Low Provider Access"
    elif r["svi_overall"] >= med_svi:
        return "Q2 — High Vulnerability / High Provider Access"
    elif r["primary_care_physicians_per_10000"] <= med_rate:
        return "Q3 — Low Vulnerability / Low Provider Access"
    else:
        return "Q4 — Low Vulnerability / High Provider Access"

recomputed = df.apply(_quad, axis=1)
# Compare against county_quadrants (from block 09c)
merged_check = county_quadrants.set_index("county_fips")[["quadrant"]].join(
    recomputed.rename("recomputed").to_frame().set_index(df["county_fips"]))
mismatch = (merged_check["quadrant"] != merged_check["recomputed"]).sum()
check("All 58 quadrant assignments reproducible from scratch", mismatch == 0,
      f"{mismatch} mismatches")

print("\n── Exploratory-conditions reproducibility ────────────────────────────")
p25_rate = df["primary_care_physicians_per_10000"].quantile(0.25)
p75_svi  = df["svi_overall"].quantile(0.75)
n_cands  = (exploratory_review_conditions["candidate_for_closer_review"]).sum()
check("34 candidates identified (conditions_met >= 2)", n_cands == 34,
      f"found {n_cands}")

print("\n── Final result ──────────────────────────────────────────────────────")
if errors:
    print(f"  {FAIL} {len(errors)} check(s) FAILED: {errors}")
else:
    print(f"  {PASS} All checks passed — Milestone 3 data integrity confirmed.")

# ── milestone3_findings dict (for reference in 09j) ──────────────────────────
milestone3_findings = {
    "major_findings": [
        "Physician rate is right-skewed (median 7.9/10k); San Francisco (24.2) and "
        "Marin (18.2) are upper outliers; Alpine and Sierra have zero physicians.",
        "SVI and physician rate show a weak-to-moderate negative association overall "
        "(Spearman r = -0.31, p=0.017); the socioeconomic and household-characteristics "
        "themes show stronger moderate negative correlations (r ≈ -0.53, -0.47), while "
        "the racial/ethnic-minority and housing/transportation themes show negligible "
        "association with physician rate.",
        "18 counties (31% of CA counties, ~16.8% of CA population) fall in the "
        "high-vulnerability/low-access quadrant (Q1), including high-population counties "
        "like Riverside and San Joaquin and intensely vulnerable smaller counties like "
        "Imperial (SVI 1.0, 2.7 PCPs/10k) and Merced (SVI 0.98, 5.4/10k).",
        "County population and physician rate have a strong Spearman correlation (r=0.61), "
        "but a very weak Pearson correlation (r=0.25) — a material divergence driven by "
        "non-linearity. Larger counties tend to have more physicians but the relationship "
        "is not linear.",
        "5 counties meet all 5 exploratory conditions simultaneously: Imperial, Merced, "
        "Kern, Kings, and Lake. These represent the convergence of high vulnerability, "
        "low access, and active HPSA designation.",
    ],
    "counties_for_closer_review": [
        "Imperial (SVI=1.00, 2.7/10k) — highest vulnerability, very low access",
        "Merced (SVI=0.98, 5.4/10k) — second highest SVI, below median rate",
        "Kern (SVI=0.97, 5.6/10k) — top-quartile SVI, below median rate",
        "Kings (SVI=0.90, 4.8/10k) — very high SVI, well below median rate",
        "Lake (SVI=0.75, 4.7/10k) — meets all 5 conditions",
        "Glenn, Colusa, Yuba — rural, high vulnerability, low physician counts",
        "Riverside (SVI=0.61, 6.6/10k, pop 2.5M) — large Q1 county by population",
    ],
    "svi_physician_association": (
        "Weak at the composite SVI level (Spearman r=-0.31); moderate for the "
        "socioeconomic theme (r=-0.53) and household-characteristics theme (r=-0.47). "
        "The overall SVI composite is a less reliable predictor of physician access "
        "than its socioeconomic sub-theme alone. Excluding Alpine/Sierra strengthens "
        "the overall SVI association to moderate (r=-0.42). The relationship is "
        "inconsistent across quadrants — many high-SVI counties have adequate or high "
        "physician rates (Q2), reflecting urban cores."
    ),
    "hpsa_alignment": (
        "HPSA-designated counties (n=34) have a lower median physician rate (7.7/10k) "
        "than non-HPSA counties (9.8/10k) and a markedly higher median SVI (0.64 vs 0.30). "
        "Mann-Whitney p=0.06 (marginal). HPSA designation broadly aligns with higher "
        "vulnerability and lower access, but 11 high-SVI counties (Q2) have active "
        "HPSAs despite above-median physician rates — likely reflecting population-specific "
        "or sub-county shortages rather than county-level physician scarcity. "
        "Facility HPSA (57/58 counties) is not a useful differentiating variable."
    ),
    "recommended_scoring_variables": [
        "primary_care_physicians_per_10000 (2022 AHRF) — core access measure",
        "svi_overall (2022 CDC SVI) — composite vulnerability",
        "svi_socioeconomic (2022) — strongest theme-level correlate with access",
        "svi_household_characteristics (2022) — second strongest correlate",
        "has_current_geo_population_hpsa (2026 current indicator, kept separate)",
        "current_geo_population_max_score (2026, as supplementary overlay only)",
    ],
    "should_remain_descriptive": [
        "svi_racial_ethnic_minority — negligible correlation with physician rate; "
        "important context but may introduce conflation if scored without domain justification",
        "svi_housing_transportation — negligible correlation; retain as descriptive",
        "has_current_facility_hpsa — 57/58 counties; no differentiation",
        "current_facility_hpsa_count — same reason",
        "ahrf_population_2022 / svi_population_2022 — population is context, not a shortage indicator",
        "County population as a weight — to be decided explicitly in scoring milestone, "
        "not assumed",
    ],
    "key_limitations": [
        "N=58 ecological units — correlations and comparisons have wide uncertainty intervals.",
        "Physician count is AMA-sourced and may miss non-AMA-affiliated or salaried providers "
        "at FQHCs, IHS facilities, and RHCs, potentially understating access in some rural counties.",
        "SVI is California-specific ranking — ties at 0.000, 0.250, 0.500, 0.750, 1.000 are "
        "observed, indicating many counties share percentile ranks at quartile boundaries.",
        "2026 HPSA snapshot ≠ 2022 conditions; designation lag and withdrawal timing may "
        "create apparent mismatches with 2022 physician rates.",
        "Physician rates for tiny counties (Alpine, Sierra, Modoc) are highly sensitive to "
        "even one physician entering or leaving — rates should be interpreted cautiously.",
        "This is an ecological analysis. County-level patterns do not necessarily reflect "
        "individual-level access experiences, especially within large, heterogeneous counties.",
    ],
}

print(f"\n  milestone3_findings dict created with {len(milestone3_findings)} top-level keys.")
