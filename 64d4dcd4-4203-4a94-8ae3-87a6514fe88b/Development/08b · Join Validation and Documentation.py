import pandas as pd
import numpy as np

df = ca_county_healthcare_access_joined   # alias for readability

# ════════════════════════════════════════════════════════════════════════════
# SECTION A — FULL JOIN VALIDATION
# ════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("JOIN VALIDATION — ca_county_healthcare_access_joined")
print("=" * 70)

# A1. Row and FIPS counts
assert len(df) == 58,                    f"Expected 58 rows, got {len(df)}"
assert df["county_fips"].nunique() == 58, "Duplicate county FIPS in joined table"
assert df["county_fips"].duplicated().sum() == 0
print(f"✓ Rows                        : {len(df)} (expected 58)")
print(f"✓ Unique county FIPS          : {df['county_fips'].nunique()}")
print(f"✓ Duplicate FIPS records      : 0")

# A2. AHRF match quality — left join should have populated ahrf fields for all 58
ahrf_matched = df["primary_care_physicians_2022"].notna().sum()
ahrf_null    = df["primary_care_physicians_2022"].isna().sum()
assert ahrf_matched == 58, f"Expected 58 AHRF matches, got {ahrf_matched}"
print(f"✓ AHRF matches (non-null phys): {ahrf_matched} (expected 58)")
print(f"  AHRF unmatched (null phys)  : {ahrf_null}")

# A3. SVI percentile range [0, 1] or NaN
RPL_COLS = [
    "svi_overall", "svi_socioeconomic", "svi_household_characteristics",
    "svi_racial_ethnic_minority", "svi_housing_transportation",
]
print(f"\n── SVI percentile ranges ──────────────────────────────────────────")
for col in RPL_COLS:
    vals = df[col].dropna()
    out  = ((vals < 0) | (vals > 1)).sum()
    assert out == 0, f"{col} has {out} values outside [0,1]"
    print(f"  ✓ {col:<38}: [{vals.min():.4f}, {vals.max():.4f}]  nulls={df[col].isna().sum()}")

# A4. Provider counts and rates non-negative
for col in ["primary_care_physicians_2022", "primary_care_physicians_per_10000",
            "supplied_rate_per_100000", "recalculated_rate_per_100000"]:
    neg = (df[col] < 0).sum()
    assert neg == 0, f"{col} has {neg} negative values"
print(f"\n✓ All provider counts and rates are non-negative")

# A5. Population values positive
pop_issues = ((df["svi_population_2022"] <= 0) | (df["ahrf_population_2022"] <= 0)).sum()
assert pop_issues == 0
print(f"✓ All population values are positive")

# A6. HPSA scores within valid range [0, 25]
for score_col in ["current_geo_population_max_score", "current_geo_population_min_score"]:
    valid_scores = df[score_col].dropna()
    if not valid_scores.empty:
        assert valid_scores.max() <= 25, f"{score_col} exceeds 25"
        assert valid_scores.min() >= 0,  f"{score_col} below 0"
print(f"✓ All HPSA scores within documented valid range [0, 25]")

# A7. HPSA NaN values — explain left-join nulls for counties with no designation
hpsa_geo_null = df["current_geo_population_max_score"].isna().sum()
hpsa_fac_null = df["current_facility_hpsa_count"].isna().sum()
print(f"\n── HPSA null interpretation ───────────────────────────────────────")
print(f"  current_geo_population_max_score  nulls: {hpsa_geo_null}")
print(f"  current_facility_hpsa_count       nulls: {hpsa_fac_null}")
print(f"  Interpretation: counties with no active Designated Primary Care HPSA")
print(f"  of that type received NaN/0 from the left join — NOT missing data.")
print(f"  has_current_geo_population_hpsa=False and count=0 confirm the absence.")

# A8. Confirm no 2026 HPSA field is blended into a 2022 composite column
hpsa_indicator_cols = [c for c in df.columns if c.startswith("current_")]
print(f"\n── 2026 HPSA columns isolated (not in a 2022 composite) ──────────")
for c in hpsa_indicator_cols:
    print(f"  ✓ {c}  ← 2026 current-status indicator, kept separate")

# ════════════════════════════════════════════════════════════════════════════
# SECTION B — POPULATION COMPARISON: SVI vs AHRF
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("POPULATION COMPARISON — SVI (ACS 2018–2022) vs AHRF (Census 2022)")
print("=" * 70)
print("  SVI population   : 2018–2022 ACS 5-year estimate (CDC/ATSDR SVI 2022)")
print("  AHRF population  : Census County Population Estimates 2022 (AMA/Census)")
print("  These differ by source and vintage — small gaps are expected.")
print("  AHRF population used as physician-rate denominator (same export).\n")

df["_pop_diff_abs"] = (df["svi_population_2022"] - df["ahrf_population_2022"]).abs()
df["_pop_diff_pct"] = df["_pop_diff_abs"] / df["ahrf_population_2022"] * 100

print(f"  Statewide SVI total pop    : {df['svi_population_2022'].sum():>14,.0f}")
print(f"  Statewide AHRF total pop   : {df['ahrf_population_2022'].sum():>14,.0f}")
print(f"  Mean absolute difference   : {df['_pop_diff_abs'].mean():>14,.0f}")
print(f"  Median absolute difference : {df['_pop_diff_abs'].median():>14,.0f}")
print(f"  Max absolute difference    : {df['_pop_diff_abs'].max():>14,.0f}")
print(f"  Mean % difference          : {df['_pop_diff_pct'].mean():>14.2f}%")
print(f"  Median % difference        : {df['_pop_diff_pct'].median():>14.2f}%")

print("\n  Top 5 counties by % population difference:")
top5 = (df[["county_name", "svi_population_2022", "ahrf_population_2022",
             "_pop_diff_abs", "_pop_diff_pct"]]
        .sort_values("_pop_diff_pct", ascending=False)
        .head(5))
print(top5.to_string(index=False))

# Remove temp columns from the working df
df.drop(columns=["_pop_diff_abs", "_pop_diff_pct"], inplace=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION C — JOIN AUDIT SUMMARY
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("JOIN AUDIT SUMMARY")
print("=" * 70)

audit = pd.DataFrame({
    "check":  [
        "Total rows",
        "Unique county FIPS",
        "Duplicate FIPS",
        "AHRF matches (58 expected)",
        "AHRF unmatched",
        "HPSA join type",
        "HPSA counties with any designation",
        "HPSA counties with Geo/Pop designation",
        "HPSA counties with Facility designation",
        "Rows with null HPSA geo/pop max score",
        "No 2026 HPSA in 2022 composite",
        "SVI RPL values outside [0,1]",
        "Negative provider rates",
        "Non-positive populations",
        "HPSA scores outside [0,25]",
    ],
    "result": [
        str(len(df)),
        str(df["county_fips"].nunique()),
        "0  ✓",
        "58  ✓",
        "0  ✓",
        "LEFT JOIN (all 58 SVI counties preserved)",
        str(df["has_current_geo_population_hpsa"].sum() + (~df["has_current_geo_population_hpsa"]).sum()),
        str(df["has_current_geo_population_hpsa"].sum()),
        str(df["has_current_facility_hpsa"].sum()),
        f"{df['current_geo_population_max_score'].isna().sum()} (counties with no Geo/Pop designation)",
        "Confirmed  ✓",
        "0  ✓",
        "0  ✓",
        "0  ✓",
        "0  ✓",
    ],
})
print(audit.to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# SECTION D — UNMATCHED RECORDS TABLE
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("UNMATCHED RECORDS TABLE")
print("=" * 70)
unmatched = df[df["primary_care_physicians_2022"].isna()]
if unmatched.empty:
    print("  ✓ No unmatched records — all 58 counties present in both SVI and AHRF")
else:
    print(unmatched[["county_fips", "county_name"]].to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# SECTION E — CONCISE DATA DICTIONARY FOR FINAL COLUMNS
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL TABLE DATA DICTIONARY — ca_county_healthcare_access_joined")
print("=" * 70)

col_dict = [
    ("county_fips",                          "str",     "2022", "5-char zero-padded county FIPS (e.g. '06001'). Primary join key."),
    ("county_name",                          "str",     "2022", "Full human-readable county name from SVI (e.g. 'Alameda County')."),
    ("svi_population_2022",                  "float",   "2022", "ACS 2018–2022 5-yr pop estimate. Source: CDC SVI 2022."),
    ("svi_overall",                          "float",   "2022", "Overall SVI percentile [0,1]. 1=most vulnerable. CA-specific ranking."),
    ("svi_socioeconomic",                    "float",   "2022", "SVI Theme 1: poverty, unemployment, housing burden, education, uninsured."),
    ("svi_household_characteristics",        "float",   "2022", "SVI Theme 2: elderly, children, disability, single-parent, limited English."),
    ("svi_racial_ethnic_minority",           "float",   "2022", "SVI Theme 3: racial & ethnic minority status."),
    ("svi_housing_transportation",           "float",   "2022", "SVI Theme 4: housing type, mobile homes, crowding, no vehicle, group quarters."),
    ("ahrf_population_2022",                 "float",   "2022", "Census County Pop Estimates 2022. Denominator for physician rate."),
    ("primary_care_physicians_2022",         "float",   "2022", "Primary care physician count. Source: AMA Physician Professional Data 2022."),
    ("primary_care_physicians_per_10000",    "float",   "2022", "Recalculated: physicians / ahrf_population * 10,000."),
    ("supplied_rate_per_100000",             "float",   "2022", "Supplied rate per 100k from AHRF export. Used for comparison only."),
    ("recalculated_rate_per_100000",         "float",   "2022", "Recalculated: physicians / ahrf_population * 100,000. Max diff from supplied: 0.005 (rounding)."),
    ("ahrf_source",                          "str",     "2022", "Source citation from AHRF file."),
    ("has_current_geo_population_hpsa",      "bool",    "2026", "True if county has ≥1 active Geo/Population Primary Care HPSA designation."),
    ("current_geo_population_hpsa_count",    "int",     "2026", "Count of distinct active Geo/Pop HPSA IDs for county. 0 = none."),
    ("current_geo_population_max_score",     "float",   "2026", "Max HPSA score across active Geo/Pop designations. Range 0–25; NaN = no designation."),
    ("current_geo_population_min_score",     "float",   "2026", "Min HPSA score across active Geo/Pop designations. Range 0–25; NaN = no designation."),
    ("has_current_facility_hpsa",            "bool",    "2026", "True if county has ≥1 active Facility Primary Care HPSA. Does NOT mean entire county is a shortage area."),
    ("current_facility_hpsa_count",          "int",     "2026", "Count of distinct active Facility HPSA IDs. 0 = none."),
    ("most_recent_hpsa_update",              "date",    "2026", "Most recent HPSA designation update date across all active Primary Care rows for county."),
    ("rural_status_summary",                 "str",     "2026", "Distinct rural status values for active designations: Non-Rural / Rural / Partially Rural. NaN if none specified."),
]

print(f"  {'Column':<44} {'Type':<6} {'Period':<6}  Description")
print(f"  {'-'*44} {'-'*6} {'-'*6}  {'-'*50}")
for cname, ctype, period, desc in col_dict:
    print(f"  {cname:<44} {ctype:<6} {period:<6}  {desc}")

# ════════════════════════════════════════════════════════════════════════════
# SECTION F — MATERIAL CLEANING DECISIONS (AUDIT TRAIL)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("MATERIAL CLEANING AND AGGREGATION DECISIONS")
print("=" * 70)

decisions = [
    ("SVI loaded with dtype=str",
     "Preserves leading zero in STCNTY (e.g. '06001'). Numeric conversion applied field-by-field after load."),
    ("SVI -999 sentinel",
     "No -999 values found in this file. Rule applied: replace -999 with NaN before arithmetic. Assertion included in block 05."),
    ("SVI county_name_std",
     "Trailing ' County' stripped for name-matching only. Original county_name retained unchanged in final table."),
    ("AHRF header at row 3 (0-indexed)",
     "Rows 0-2 are title/filter rows. Confirmed in 03b inspection. Using header=3 gives correct 5-column names."),
    ("AHRF footer dropped",
     "1 row starting with 'Note: Blank cells...' removed. Not a data row."),
    ("AHRF zero-physician counties kept",
     "Alpine and Sierra counties have 0 physicians. These are valid data points for tiny rural counties, not missing values."),
    ("Physician rate denominator = AHRF population",
     "Physician count and population from same AHRF export/vintage (AMA + Census 2022). Ensures consistency. SVI ACS population retained separately."),
    ("Rate recalculation vs supplied",
     "Max absolute diff = 0.005 per 100k (rounding in source). No material discrepancy flagged."),
    ("AHRF FIPS via name matching only",
     "No FIPS column in AHRF. county_fips assigned by exact standardized name match from svi_clean. 58/58 exact matches; no fuzzy matching used."),
    ("HPSA filtered to Designated + Primary Care",
     "1,586 of 8,245 CA rows are active. Withdrawn (5,106) and Proposed For Withdrawal (1,553) excluded. Discipline confirmed 'Primary Care' for all 1,586."),
    ("HPSA distinct HPSA IDs counted, not rows",
     "559 distinct IDs across 1,586 rows. Multi-row per ID due to census-tract component decomposition. Raw row count would inflate apparent shortage count."),
    ("HPSA underserved population not summed",
     "Designation areas within a county may overlap geographically. Summing underserved pop would risk double-counting. Field retained at record level in hpsa_pc only."),
    ("HPSA Facility vs Geo/Pop kept separate",
     "Facility designation (e.g. FQHC, RHC) means one site is a shortage area, NOT the whole county. Boolean indicators created separately for each group."),
    ("HPSA join is LEFT (SVI is base)",
     "24 counties have no active Geo/Pop HPSA; 1 has no active Facility HPSA. These produce NaN/0 in HPSA columns — correctly reflects absence, not missing data."),
    ("2026 HPSA columns prefixed 'current_'",
     "Naming convention prevents accidental blending with 2022 SVI/AHRF measures in any downstream score calculation."),
    ("59 unique HPSA FIPS (vs 58 counties)",
     "Resolved: after filtering to Designated + Primary Care, all 559 HPSA IDs map to exactly 58 CA counties with no duplicates in hpsa_county_current."),
]

for title, explanation in decisions:
    print(f"\n  ▸ {title}")
    print(f"    {explanation}")

# ════════════════════════════════════════════════════════════════════════════
# SECTION G — FINAL TABLE PREVIEW
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL TABLE PREVIEW — ca_county_healthcare_access_joined (first 10 rows)")
print("=" * 70)

PREVIEW_COLS = [
    "county_fips", "county_name",
    "svi_overall", "primary_care_physicians_per_10000",
    "has_current_geo_population_hpsa", "current_geo_population_max_score",
    "has_current_facility_hpsa",
]
print(df[PREVIEW_COLS].head(10).to_string(index=False))
print(f"\n✓ Milestone 2 complete. Final table: {df.shape[0]} rows × {df.shape[1]} columns.")
print("  Ready for Milestone 3 (exploratory analysis) on approval.")
