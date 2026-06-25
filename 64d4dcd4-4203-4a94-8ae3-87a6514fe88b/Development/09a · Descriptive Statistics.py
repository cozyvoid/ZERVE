import pandas as pd
import numpy as np
from scipy import stats

df = ca_county_healthcare_access_joined.copy()

# ── Fields to summarise ──────────────────────────────────────────────────────
# Zero-physician counties (Alpine, Sierra) are valid observations, not missing.
# HPSA fields: zero means no active designation (left-join fill), not a true
# measurement of zero shortage severity.

FIELDS = [
    "primary_care_physicians_2022",
    "primary_care_physicians_per_10000",
    "svi_population_2022",
    "ahrf_population_2022",
    "svi_overall",
    "svi_socioeconomic",
    "svi_household_characteristics",
    "svi_racial_ethnic_minority",
    "svi_housing_transportation",
    "current_geo_population_hpsa_count",
    "current_geo_population_max_score",
]

# Labels explaining what zero means in each field
ZERO_MEANING = {
    "primary_care_physicians_2022":        "valid — county has zero PCPs (Alpine, Sierra)",
    "primary_care_physicians_per_10000":   "valid — rate is genuinely zero",
    "svi_population_2022":                 "N/A — no county has zero population",
    "ahrf_population_2022":                "N/A — no county has zero population",
    "svi_overall":                         "valid — lowest vulnerability percentile",
    "svi_socioeconomic":                   "valid — lowest percentile on this theme",
    "svi_household_characteristics":       "valid — lowest percentile on this theme",
    "svi_racial_ethnic_minority":          "valid — lowest percentile on this theme",
    "svi_housing_transportation":          "valid — lowest percentile on this theme",
    "current_geo_population_hpsa_count":   "means NO active geo/pop HPSA (left-join absence)",
    "current_geo_population_max_score":    "NaN means NO active geo/pop HPSA — not a zero score",
}

rows = []
for col in FIELDS:
    s = df[col]
    n_valid = s.notna().sum()
    n_miss  = s.isna().sum()
    skew    = stats.skew(s.dropna())
    rows.append({
        "field":   col,
        "count":   n_valid,
        "missing": n_miss,
        "mean":    s.mean(),
        "median":  s.median(),
        "std":     s.std(),
        "min":     s.min(),
        "p25":     s.quantile(0.25),
        "p75":     s.quantile(0.75),
        "max":     s.max(),
        "skewness": round(skew, 3),
        "zero_means": ZERO_MEANING[col],
    })

descriptive_summary = pd.DataFrame(rows).set_index("field")

# ── Display ──────────────────────────────────────────────────────────────────
pd.set_option("display.max_colwidth", 60)
pd.set_option("display.float_format", "{:,.4f}".format)

print("=" * 80)
print("09a · DESCRIPTIVE STATISTICS — ca_county_healthcare_access_joined (n=58)")
print("=" * 80)

# Numeric summary
num_cols = ["count", "missing", "mean", "median", "std", "min", "p25", "p75", "max", "skewness"]
print("\n── Numeric summary ─────────────────────────────────────────────────────")
print(descriptive_summary[num_cols].to_string())

# Zero-meaning note
print("\n── Meaning of zero / null for each field ───────────────────────────────")
for col in FIELDS:
    print(f"  {col:<45}  {ZERO_MEANING[col]}")

# Highlight key values for quick orientation
print("\n── Quick orientation ───────────────────────────────────────────────────")
med_rate = df["primary_care_physicians_per_10000"].median()
med_svi  = df["svi_overall"].median()
print(f"  Median physician rate (per 10,000)  : {med_rate:.2f}")
print(f"  Median overall SVI percentile       : {med_svi:.3f}")
print(f"  Counties with zero physicians       : {(df['primary_care_physicians_2022'] == 0).sum()}")
print(f"  Counties with active geo/pop HPSA   : {df['has_current_geo_population_hpsa'].sum()}")
print(f"  Counties WITHOUT active geo/pop HPSA: {(~df['has_current_geo_population_hpsa']).sum()}")
print(f"  Missing geo/pop HPSA max score      : {df['current_geo_population_max_score'].isna().sum()} "
      f"(counties with no active geo/pop HPSA)")
