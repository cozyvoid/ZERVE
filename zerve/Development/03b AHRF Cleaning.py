import pandas as pd
import numpy as np

# ── Path and header row (confirmed in 03b inspection) ────────────────────────
AHRF_PATH   = "hrsa_ahrf_ca_county_primary_care_physicians_population_2022.xlsx"
HEADER_ROW  = 3  # 0-indexed; row 4 in Excel contains the actual column names

# ── 1. Load raw sheet at the correct header row ───────────────────────────────
ahrf_raw = pd.read_excel(
    AHRF_PATH,
    sheet_name="AHRF Geo Data",
    header=HEADER_ROW,
    dtype=str,          # keep everything as string first; convert selectively below
)
print(f"Raw shape (before cleaning): {ahrf_raw.shape}")
print(f"Columns: {ahrf_raw.columns.tolist()}")

# ── 2. Drop fully blank rows ───────────────────────────────────────────────────
# A row is "fully blank" when every cell is NaN after the header-skip.
ahrf_raw = ahrf_raw.dropna(how="all")

# Drop the footer note row that begins with "Note: Blank cells …"
footer_mask = ahrf_raw.iloc[:, 0].astype(str).str.startswith("Note:")
n_footer = footer_mask.sum()
ahrf_raw = ahrf_raw[~footer_mask].reset_index(drop=True)
print(f"Dropped {n_footer} footer note row(s). Shape now: {ahrf_raw.shape}")
assert len(ahrf_raw) == 58, f"Expected 58 rows after cleaning, got {len(ahrf_raw)}"

# ── 3. Rename columns to clear analytical names ───────────────────────────────
RENAME_MAP = {
    "County":                                        "ahrf_county_raw",
    "Physicians, Primary Care (County Level File)":  "primary_care_physicians_2022",
    "Population, All (County Level File)":           "ahrf_population_2022",
    "Rate (per 100,000 population)":                 "supplied_rate_per_100000",
    "Source":                                        "ahrf_source",
}
ahrf_clean = ahrf_raw.rename(columns=RENAME_MAP).copy()

# ── 4. Convert numeric columns ────────────────────────────────────────────────
NUM_COLS = ["primary_care_physicians_2022", "ahrf_population_2022", "supplied_rate_per_100000"]
for col in NUM_COLS:
    ahrf_clean[col] = pd.to_numeric(ahrf_clean[col], errors="coerce")

# ── 5. Standardize county name (same function logic as svi_clean) ─────────────
# AHRF county names look like "Alameda County, CA" — strip the ", CA" suffix,
# then remove " County" so names match the SVI standardized form (e.g. "Alameda").
def standardize_county_name(name: str) -> str:
    """Strip whitespace, title-case, remove ', CA' suffix, remove trailing ' County'."""
    name = str(name).strip().title()
    if name.endswith(", Ca"):
        name = name[: -len(", Ca")]
    if name.endswith(" County"):
        name = name[: -len(" County")]
    return name

ahrf_clean["county_name_std"] = ahrf_clean["ahrf_county_raw"].apply(standardize_county_name)

# ── 6. Calculate provider rates ───────────────────────────────────────────────
# Use AHRF population as denominator: physician count and population come from
# the same AHRF export and are consistently denominated.
ahrf_clean["primary_care_physicians_per_10000"] = (
    ahrf_clean["primary_care_physicians_2022"] / ahrf_clean["ahrf_population_2022"] * 10_000
)
ahrf_clean["recalculated_rate_per_100000"] = (
    ahrf_clean["primary_care_physicians_2022"] / ahrf_clean["ahrf_population_2022"] * 100_000
)

# ── 7. Rate validation: recalculated vs supplied ──────────────────────────────
ahrf_clean["_rate_diff_abs"] = (
    ahrf_clean["recalculated_rate_per_100000"] - ahrf_clean["supplied_rate_per_100000"]
).abs()

print("\n── Rate comparison: recalculated vs supplied (per 100k) ────────────")
print(f"  Max absolute difference   : {ahrf_clean['_rate_diff_abs'].max():.4f}")
print(f"  Median absolute difference: {ahrf_clean['_rate_diff_abs'].median():.4f}")
print(f"  Mean absolute difference  : {ahrf_clean['_rate_diff_abs'].mean():.4f}")

THRESHOLD = 0.1   # physicians per 100,000 — any gap larger than this is flagged
material = ahrf_clean[ahrf_clean["_rate_diff_abs"] > THRESHOLD]
if material.empty:
    print(f"\n  ✓ No material discrepancies > {THRESHOLD} per 100k")
else:
    print(f"\n  ⚠  {len(material)} counties with discrepancy > {THRESHOLD} per 100k:")
    print(material[["county_name_std", "supplied_rate_per_100000",
                     "recalculated_rate_per_100000", "_rate_diff_abs"]].to_string(index=False))

# ── 8. Verifications ─────────────────────────────────────────────────────────
print("\n── Verification ─────────────────────────────────────────────────────")

assert len(ahrf_clean) == 58, f"Expected 58 rows, got {len(ahrf_clean)}"
print(f"✓ Row count: {len(ahrf_clean)} (expected 58)")

assert ahrf_clean["county_name_std"].nunique() == 58, "Duplicate standardized county names"
print(f"✓ Unique standardized county names: {ahrf_clean['county_name_std'].nunique()}")

neg_physicians = (ahrf_clean["primary_care_physicians_2022"] < 0).sum()
assert neg_physicians == 0, f"Negative physician counts: {neg_physicians}"
print(f"✓ Negative physician counts: {neg_physicians}")

# Counties with zero physicians are valid (Alpine, Sierra — tiny rural counties)
zero_phys = ahrf_clean[ahrf_clean["primary_care_physicians_2022"] == 0]["county_name_std"].tolist()
print(f"  Counties with 0 physicians (valid): {zero_phys}")

neg_pop = (ahrf_clean["ahrf_population_2022"] <= 0).sum()
assert neg_pop == 0, f"Non-positive population values: {neg_pop}"
print(f"✓ Non-positive populations: {neg_pop}")

neg_rate = (ahrf_clean["primary_care_physicians_per_10000"] < 0).sum()
assert neg_rate == 0
print(f"✓ Negative per-10k rates: {neg_rate}")

print("\n── ahrf_clean preview (first 6 rows) ────────────────────────────────")
SHOW = ["county_name_std", "primary_care_physicians_2022", "ahrf_population_2022",
        "supplied_rate_per_100000", "recalculated_rate_per_100000",
        "primary_care_physicians_per_10000"]
print(ahrf_clean[SHOW].head(6).to_string(index=False))
print(f"\nFinal ahrf_clean shape: {ahrf_clean.shape}")
