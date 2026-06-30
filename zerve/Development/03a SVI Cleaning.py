import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
SVI_PATH = "california_healthcare_access/cdc_svi_ca_county_2022.csv"

# ── 1. Load raw file — dtype=str preserves leading zeros in FIPS codes ───────
svi_raw = pd.read_csv(SVI_PATH, dtype=str)
print(f"Raw SVI shape: {svi_raw.shape}")

# ── 2. Columns to keep and rename ────────────────────────────────────────────
RENAME_MAP = {
    "STCNTY":      "county_fips",
    "COUNTY":      "county_name",
    "E_TOTPOP":    "svi_population_2022",
    "RPL_THEMES":  "svi_overall",
    "RPL_THEME1":  "svi_socioeconomic",
    "RPL_THEME2":  "svi_household_characteristics",
    "RPL_THEME3":  "svi_racial_ethnic_minority",
    "RPL_THEME4":  "svi_housing_transportation",
}
KEEP_COLS = list(RENAME_MAP.keys())

svi_clean = svi_raw[KEEP_COLS].copy()
svi_clean = svi_clean.rename(columns=RENAME_MAP)

# ── 3. Confirm county_fips is a 5-char string starting with '06' ─────────────
assert (svi_clean["county_fips"].str.len() == 5).all(), "Not all FIPS are 5 chars"
assert svi_clean["county_fips"].str.startswith("06").all(), "Not all FIPS start with 06"
print("✓ All county_fips are 5-char strings beginning with '06'")

# ── 4. Convert numeric fields; replace sentinel -999 with NaN ─────────────────
# These columns arrive as strings; convert first, then mask -999.
NUMERIC_COLS = [
    "svi_population_2022",
    "svi_overall",
    "svi_socioeconomic",
    "svi_household_characteristics",
    "svi_racial_ethnic_minority",
    "svi_housing_transportation",
]
for col in NUMERIC_COLS:
    svi_clean[col] = pd.to_numeric(svi_clean[col], errors="coerce")
    neg999_count = (svi_clean[col] == -999).sum()
    if neg999_count > 0:
        print(f"  ⚠  {col}: {neg999_count} sentinel -999 values → replacing with NaN")
        svi_clean[col] = svi_clean[col].replace(-999, np.nan)
    else:
        print(f"  ✓ {col}: no -999 sentinels")

# ── 5. Standardized county name for matching ──────────────────────────────────
# Strip leading/trailing whitespace, normalize to title case,
# remove the trailing word " County" so names match AHRF format (e.g. "Alameda").
# The original human-readable county_name column is kept unchanged.
def standardize_county_name(name: str) -> str:
    """Strip whitespace, title-case, remove trailing ' County'."""
    name = str(name).strip().title()
    if name.endswith(" County"):
        name = name[: -len(" County")]
    return name

svi_clean["county_name_std"] = svi_clean["county_name"].apply(standardize_county_name)
print("\nSample county_name vs county_name_std:")
print(svi_clean[["county_name", "county_name_std"]].head(5).to_string(index=False))

# ── 6. Verifications ─────────────────────────────────────────────────────────
print("\n── Verification ─────────────────────────────────────────────────")

# 6a. Row count
assert len(svi_clean) == 58, f"Expected 58 rows, got {len(svi_clean)}"
print(f"✓ Row count : {len(svi_clean)} (expected 58)")

# 6b. Unique FIPS
n_unique_fips = svi_clean["county_fips"].nunique()
assert n_unique_fips == 58, f"Expected 58 unique FIPS, got {n_unique_fips}"
print(f"✓ Unique FIPS : {n_unique_fips} (expected 58)")

# 6c. One row per county
assert len(svi_clean) == n_unique_fips, "Duplicate FIPS detected"
print("✓ One row per county FIPS")

# 6d. RPL percentiles in [0, 1] or NaN (no -999 remaining)
RPL_COLS = [
    "svi_overall",
    "svi_socioeconomic",
    "svi_household_characteristics",
    "svi_racial_ethnic_minority",
    "svi_housing_transportation",
]
for col in RPL_COLS:
    vals = svi_clean[col].dropna()
    out_of_range = ((vals < 0) | (vals > 1)).sum()
    remaining_999 = (svi_clean[col] == -999).sum()
    assert out_of_range == 0, f"{col} has values outside [0,1]"
    assert remaining_999 == 0, f"{col} still has -999 sentinels"
    print(f"  ✓ {col}: range [{vals.min():.4f}, {vals.max():.4f}]  nulls={svi_clean[col].isna().sum()}")

# 6e. Population positive (no zeros, no negatives)
pop_issues = (svi_clean["svi_population_2022"] <= 0).sum()
print(f"\n  Population ≤ 0: {pop_issues}  (expected 0)")
assert pop_issues == 0

print("\n── svi_clean preview (first 5 rows) ──────────────────────────────")
print(svi_clean.head(5).to_string(index=False))
print(f"\nFinal svi_clean shape: {svi_clean.shape}")
