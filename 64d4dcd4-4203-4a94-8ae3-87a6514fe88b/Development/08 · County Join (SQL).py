import pandas as pd

# ── Principal analytical join ────────────────────────────────────────────────
# svi_clean is the base table (58 CA counties; used as left table throughout).
# All joins are LEFT joins so every SVI county is preserved even if AHRF or
# HPSA data is absent for a county.
#
# Column groups are clearly separated:
#   - 2022 SVI columns  → prefix svi_*
#   - 2022 AHRF columns → primary_care_*, ahrf_*, supplied_rate_*, recalculated_*
#   - 2026 HPSA columns → current_*  (labelled to prevent blending with 2022 score)
#
# DuckDB is not available; we replicate the SQL join logic in pandas using
# explicit merge() calls with how="left" to match left-join semantics.

# ── AHRF columns to carry into the joined table ──────────────────────────────
AHRF_COLS = [
    "county_fips",
    "ahrf_population_2022",
    "primary_care_physicians_2022",
    "primary_care_physicians_per_10000",
    "supplied_rate_per_100000",
    "recalculated_rate_per_100000",
    "ahrf_source",
]

# ── HPSA columns to carry into the joined table ──────────────────────────────
HPSA_COLS = [
    "county_fips",
    "has_current_geo_population_hpsa",
    "current_geo_population_hpsa_count",
    "current_geo_population_max_score",
    "current_geo_population_min_score",
    "has_current_facility_hpsa",
    "current_facility_hpsa_count",
    "most_recent_hpsa_update",
    "rural_status_summary",
]

# ── Join 1: svi_clean LEFT JOIN ahrf_clean ────────────────────────────────────
ca_county_healthcare_access_joined = svi_clean.merge(
    ahrf_clean[AHRF_COLS],
    on="county_fips",
    how="left",
    validate="1:1",        # assert no fan-out; each FIPS appears once in both
)
print(f"After join 1 (SVI ⟕ AHRF)  : {ca_county_healthcare_access_joined.shape}")

# ── Join 2: result LEFT JOIN hpsa_county_current ──────────────────────────────
ca_county_healthcare_access_joined = ca_county_healthcare_access_joined.merge(
    hpsa_county_current[HPSA_COLS],
    on="county_fips",
    how="left",
    validate="1:1",
)
print(f"After join 2 (+ HPSA)       : {ca_county_healthcare_access_joined.shape}")

# ── Drop internal helper columns not needed in final table ────────────────────
# county_name_std was a matching key; keep county_name as the human-readable label.
# _rate_diff_abs was a temporary validation column; drop it.
DROP_COLS = ["county_name_std", "_rate_diff_abs"]
for c in DROP_COLS:
    if c in ca_county_healthcare_access_joined.columns:
        ca_county_healthcare_access_joined = ca_county_healthcare_access_joined.drop(columns=[c])

print(f"\nFinal column count : {ca_county_healthcare_access_joined.shape[1]}")
print(f"Final row count    : {ca_county_healthcare_access_joined.shape[0]}")
print("\nColumn list:")
for i, col in enumerate(ca_county_healthcare_access_joined.columns, 1):
    print(f"  [{i:02d}] {col}")
