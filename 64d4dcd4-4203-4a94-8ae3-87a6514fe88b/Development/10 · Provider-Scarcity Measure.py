import pandas as pd
import numpy as np

# ── Input: validated 58-county joined table ──────────────────────────────────
df = ca_county_healthcare_access_joined.copy()

N = len(df)  # 58

# ── Step 1: rank physician rate ascending (average ties) ─────────────────────
# Lowest rate → rank 1 (highest scarcity)
df["_rate_rank"] = df["primary_care_physicians_per_10000"].rank(
    method="average", ascending=True, na_option="bottom"
)

# ── Step 2: rescale rank to [0, 1] ────────────────────────────────────────────
# Formula: (rank - 1) / (N - 1)  →  rank 1 maps to 0.0, rank N maps to 1.0
df["provider_availability_percentile"] = (df["_rate_rank"] - 1) / (N - 1)

# ── Step 3: reverse so that higher value = greater scarcity ──────────────────
df["provider_scarcity"] = 1 - df["provider_availability_percentile"]

# ── Step 4: Boolean flag for zero-physician counties ─────────────────────────
df["zero_primary_care_physicians"] = df["primary_care_physicians_2022"] == 0

# ── Assemble county_priority_scores base table ───────────────────────────────
KEEP = [
    "county_fips",
    "county_name",
    "primary_care_physicians_2022",
    "primary_care_physicians_per_10000",
    "ahrf_population_2022",
    "svi_overall",
    "svi_socioeconomic",
    "svi_household_characteristics",
    "svi_racial_ethnic_minority",
    "svi_housing_transportation",
    "current_geo_population_hpsa_count",
    "current_geo_population_max_score",
    "has_current_geo_population_hpsa",
    "has_current_facility_hpsa",
    "provider_availability_percentile",
    "provider_scarcity",
    "zero_primary_care_physicians",
]

county_priority_scores = df[KEEP].copy().reset_index(drop=True)

# ── Validation ────────────────────────────────────────────────────────────────
PASS = "✓"; FAIL = "✗"
errors = []

# All provider_scarcity values in [0, 1]
bad_range = county_priority_scores["provider_scarcity"].between(0, 1, inclusive="both").sum()
if bad_range != N:
    errors.append("provider_scarcity out of [0,1]")

# Alpine and Sierra tied (both zero physicians → same rank → same scarcity)
zero_counties = county_priority_scores.loc[
    county_priority_scores["zero_primary_care_physicians"], ["county_name", "provider_scarcity"]
]
scarcity_vals = zero_counties["provider_scarcity"].unique()
if len(scarcity_vals) != 1:
    errors.append("Alpine and Sierra NOT tied in provider_scarcity")

# No NaN in provider_scarcity
if county_priority_scores["provider_scarcity"].isna().any():
    errors.append("NaN found in provider_scarcity")

# No infinite values
if np.isinf(county_priority_scores["provider_scarcity"]).any():
    errors.append("Infinite value in provider_scarcity")

# ── Print results ─────────────────────────────────────────────────────────────
print("=" * 70)
print("10 · PROVIDER-SCARCITY MEASURE")
print("=" * 70)
print(f"\nMethod : rank-based percentile reversal")
print(f"  Step 1: rank primary_care_physicians_per_10000 ascending (avg ties)")
print(f"  Step 2: provider_availability_percentile = (rank − 1) / (N − 1)")
print(f"  Step 3: provider_scarcity = 1 − provider_availability_percentile")
print(f"\nScale  : 0 = most availability (lowest scarcity)")
print(f"         1 = most scarcity (highest relative shortage)")
print(f"\n⚠  NOTE: This is a RELATIVE measure within California's 58 counties.")
print(f"         It does NOT define absolute adequacy or shortage thresholds.")

print(f"\n── Zero-physician counties ──────────────────────────────────────────")
print(zero_counties.to_string(index=False))
print(f"  provider_scarcity value: {scarcity_vals[0]:.6f}  (tied ✓)")

print(f"\n── provider_scarcity distribution ──────────────────────────────────")
ps = county_priority_scores["provider_scarcity"]
print(f"  min      : {ps.min():.4f}")
print(f"  25th pct : {ps.quantile(0.25):.4f}")
print(f"  median   : {ps.median():.4f}")
print(f"  75th pct : {ps.quantile(0.75):.4f}")
print(f"  max      : {ps.max():.4f}")

print(f"\n── Top 10 most scarce counties (highest provider_scarcity) ─────────")
top10 = (
    county_priority_scores[["county_name", "primary_care_physicians_per_10000", "provider_scarcity"]]
    .sort_values("provider_scarcity", ascending=False)
    .head(10)
)
print(top10.to_string(index=False))

print(f"\n── Bottom 5 (lowest scarcity = highest availability) ────────────────")
bot5 = (
    county_priority_scores[["county_name", "primary_care_physicians_per_10000", "provider_scarcity"]]
    .sort_values("provider_scarcity", ascending=True)
    .head(5)
)
print(bot5.to_string(index=False))

print(f"\n── Validation ───────────────────────────────────────────────────────")
if errors:
    for e in errors:
        print(f"  {FAIL} {e}")
else:
    print(f"  {PASS} All checks passed — provider_scarcity is valid.")

print(f"\ncounty_priority_scores shape: {county_priority_scores.shape}")
