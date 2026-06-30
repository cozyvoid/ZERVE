import pandas as pd
import numpy as np

# ── Load raw HPSA file ────────────────────────────────────────────────────────
HPSA_PATH = "hrsa_primary_care_hpsa_national_2026-06-25.csv"
hpsa_raw = pd.read_csv(HPSA_PATH, dtype=str, low_memory=False)
print(f"National HPSA raw shape: {hpsa_raw.shape}")

# ── STEP 1: Preserve FIPS as zero-padded 5-char string ───────────────────────
# 'Common State County FIPS Code' confirmed correct in 03c inspection;
# 'County FIPS Code' drops leading zeros as integer — do NOT use it.
hpsa_raw["Common State County FIPS Code"] = (
    hpsa_raw["Common State County FIPS Code"].astype(str).str.zfill(5)
)

# ── STEP 2: Three sequential filters with row/ID counts at each step ──────────

# Filter A: California only
hpsa_ca = hpsa_raw[hpsa_raw["Primary State Abbreviation"] == "CA"].copy()
print(f"\nAfter filter — CA only              : {len(hpsa_ca):>6} rows | "
      f"{hpsa_ca['HPSA ID'].nunique():>5} distinct HPSA IDs")

# Filter B: Designated status only (active; excludes Withdrawn, Proposed For Withdrawal)
hpsa_ca_desig = hpsa_ca[hpsa_ca["HPSA Status"] == "Designated"].copy()
print(f"After filter — Designated only      : {len(hpsa_ca_desig):>6} rows | "
      f"{hpsa_ca_desig['HPSA ID'].nunique():>5} distinct HPSA IDs")

# Filter C: Primary Care discipline only
# Exact field and value confirmed via metadata: 'HPSA Discipline Class' == 'Primary Care'
hpsa_pc = hpsa_ca_desig[hpsa_ca_desig["HPSA Discipline Class"] == "Primary Care"].copy()
print(f"After filter — Primary Care only    : {len(hpsa_pc):>6} rows | "
      f"{hpsa_pc['HPSA ID'].nunique():>5} distinct HPSA IDs")

# ── STEP 3: Designation type classification ───────────────────────────────────
# Exact values from metadata (confirmed in 99d inspection output).
# Geographic/Population = area-wide or population-group shortages.
# Facility = shortage tied to a specific provider site, NOT the whole county.
GEO_POP_TYPES = {
    "Geographic HPSA",
    "High Needs Geographic HPSA",
    "HPSA Population",
}
# All other types observed in CA data are facility-based.
FACILITY_TYPES = {
    "Rural Health Clinic",
    "Federally Qualified Health Center",
    "Indian Health Service, Tribal Health, and Urban Indian Health Organizations",
    "Federally Qualified Health Center Look A Like",
    "Correctional Facility",
    "Other Facility",
}

# Classify every row
def classify_desig(desig_type: str) -> str:
    if desig_type in GEO_POP_TYPES:
        return "Geo/Population"
    elif desig_type in FACILITY_TYPES:
        return "Facility"
    else:
        return "Unknown"

hpsa_pc["_desig_group"] = hpsa_pc["Designation Type"].apply(classify_desig)

# Display all observed designation types and their assigned group before aggregating
print("\n── Designation types in filtered dataset (CA, Designated, Primary Care) ──")
type_summary = (
    hpsa_pc.groupby(["Designation Type", "_desig_group"])
    .agg(rows=("HPSA ID", "count"), distinct_ids=("HPSA ID", "nunique"))
    .reset_index()
)
print(type_summary.to_string(index=False))

unknown_types = hpsa_pc[hpsa_pc["_desig_group"] == "Unknown"]["Designation Type"].unique()
if len(unknown_types) > 0:
    print(f"\n  ⚠  Unknown designation types not classified: {unknown_types}")
else:
    print("\n  ✓ All designation types classified into Geo/Population or Facility groups")

# ── STEP 4: Convert numeric fields needed for aggregation ────────────────────
hpsa_pc["HPSA Score"] = pd.to_numeric(hpsa_pc["HPSA Score"], errors="coerce")
hpsa_pc["HPSA Designation Last Update Date"] = pd.to_datetime(
    hpsa_pc["HPSA Designation Last Update Date"], errors="coerce"
)

# ── STEP 5: Check for same HPSA ID associated with multiple counties ──────────
id_county_counts = (
    hpsa_pc.groupby("HPSA ID")["Common State County FIPS Code"].nunique()
)
multi_county_ids = id_county_counts[id_county_counts > 1]
if not multi_county_ids.empty:
    print(f"\n  ℹ  {len(multi_county_ids)} HPSA IDs span multiple counties "
          "(counted once per county in per-county distinct-ID aggregation):")
    print(multi_county_ids.head(10))
else:
    print("\n  ✓ No HPSA IDs span multiple counties")

# ── STEP 6: County-level aggregation ─────────────────────────────────────────
# Use distinct HPSA IDs — never raw row counts — as the unit.
# We aggregate separately for Geo/Pop and Facility groups, then merge.

geo_pop = hpsa_pc[hpsa_pc["_desig_group"] == "Geo/Population"].copy()
facility = hpsa_pc[hpsa_pc["_desig_group"] == "Facility"].copy()

def agg_group(df, prefix):
    """Aggregate one designation group to county level using distinct HPSA IDs."""
    return (
        df.groupby("Common State County FIPS Code")
        .agg(
            **{f"{prefix}_hpsa_count":    ("HPSA ID",    "nunique")},
            **{f"{prefix}_max_score":     ("HPSA Score", "max")},
            **{f"{prefix}_min_score":     ("HPSA Score", "min")},
        )
        .reset_index()
        .rename(columns={"Common State County FIPS Code": "county_fips"})
    )

geo_agg  = agg_group(geo_pop, "current_geo_population")
fac_agg  = agg_group(facility, "current_facility")

# Most recent HPSA update date across all designated Primary Care rows per county
update_agg = (
    hpsa_pc.groupby("Common State County FIPS Code")["HPSA Designation Last Update Date"]
    .max()
    .reset_index()
    .rename(columns={
        "Common State County FIPS Code":       "county_fips",
        "HPSA Designation Last Update Date":   "most_recent_hpsa_update",
    })
)

# Rural status: collect all distinct non-null, non-Unknown values per county
def summarize_rural(series):
    vals = series.dropna().unique()
    vals = [v for v in vals if str(v).strip() not in ("", "Unknown", "Not Applicable", "nan")]
    return "; ".join(sorted(set(vals))) if vals else None

rural_agg = (
    hpsa_pc.groupby("Common State County FIPS Code")["Rural Status"]
    .apply(summarize_rural)
    .reset_index()
    .rename(columns={
        "Common State County FIPS Code": "county_fips",
        "Rural Status":                  "rural_status_summary",
    })
)

# Merge all county-level pieces
hpsa_county_current = (
    geo_agg
    .merge(fac_agg,    on="county_fips", how="outer")
    .merge(update_agg, on="county_fips", how="outer")
    .merge(rural_agg,  on="county_fips", how="outer")
)

# Add boolean indicators
hpsa_county_current["has_current_geo_population_hpsa"] = (
    hpsa_county_current["current_geo_population_hpsa_count"].notna()
    & (hpsa_county_current["current_geo_population_hpsa_count"] > 0)
)
hpsa_county_current["has_current_facility_hpsa"] = (
    hpsa_county_current["current_facility_hpsa_count"].notna()
    & (hpsa_county_current["current_facility_hpsa_count"] > 0)
)

# Fill counts with 0 where a county has no designation of that type
# (outer merge leaves NaN for counties only in one group)
hpsa_county_current["current_geo_population_hpsa_count"] = (
    hpsa_county_current["current_geo_population_hpsa_count"].fillna(0).astype(int)
)
hpsa_county_current["current_facility_hpsa_count"] = (
    hpsa_county_current["current_facility_hpsa_count"].fillna(0).astype(int)
)

# Reorder columns for clarity
COL_ORDER = [
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
hpsa_county_current = hpsa_county_current[COL_ORDER]

# ── NOTE: Why underserved population is NOT summed at county level ────────────
print("\n── Note on HPSA Estimated Underserved Population ────────────────────")
print("  'HPSA Estimated Underserved Population' is NOT summed at county level.")
print("  Reason: HPSA designations within a county may cover overlapping geographic")
print("  areas or sub-populations (e.g. a census-tract designation may overlap a")
print("  county-subdivision or population-group designation). Summing these values")
print("  would double-count individuals. The field is retained at the record level")
print("  in the filtered dataset (hpsa_pc) for descriptive reference only.")

# ── STEP 7: Verification ──────────────────────────────────────────────────────
print("\n── hpsa_county_current verification ─────────────────────────────────")
print(f"  Counties with any HPSA designation : {len(hpsa_county_current)}")
dup_check = hpsa_county_current["county_fips"].duplicated().sum()
assert dup_check == 0, f"Duplicate county FIPS in hpsa_county_current: {dup_check}"
print(f"  Duplicate county_fips              : {dup_check}  ✓")

# HPSA scores should be in [0, 25] per metadata documentation
max_score = hpsa_county_current["current_geo_population_max_score"].max()
print(f"  Max geo/pop HPSA score             : {max_score}  (valid range 0–25)")
assert max_score <= 25, f"Score exceeds documented maximum of 25: {max_score}"
print(f"  ✓ All scores within valid range [0, 25]")

print(f"\n  Counties with Geo/Population HPSA  : "
      f"{hpsa_county_current['has_current_geo_population_hpsa'].sum()}")
print(f"  Counties with Facility HPSA        : "
      f"{hpsa_county_current['has_current_facility_hpsa'].sum()}")
print(f"  Counties with BOTH types           : "
      f"{(hpsa_county_current['has_current_geo_population_hpsa'] & hpsa_county_current['has_current_facility_hpsa']).sum()}")

print("\n── hpsa_county_current preview (first 10 rows) ─────────────────────")
print(hpsa_county_current.head(10).to_string(index=False))
print(f"\nFinal hpsa_county_current shape: {hpsa_county_current.shape}")
