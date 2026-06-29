import pandas as pd
import numpy as np

# ── Authoritative AHRF → county_fips mapping ─────────────────────────────────
# Rule: do NOT calculate or guess FIPS from county names.
# Instead, match the standardized AHRF county name to the standardized SVI
# county name, then inherit county_fips from svi_clean.
# Expected result: 58 exact one-to-one matches, no fuzzy matching.

# Build lookup: standardized SVI name → county_fips
svi_lookup = svi_clean.set_index("county_name_std")["county_fips"].to_dict()

# Apply mapping to ahrf_clean
ahrf_clean["county_fips"] = ahrf_clean["county_name_std"].map(svi_lookup)

# ── Build full mapping-audit table ───────────────────────────────────────────
mapping_table = ahrf_clean[["ahrf_county_raw", "county_name_std", "county_fips"]].copy()
mapping_table["matched_svi_county"] = mapping_table["county_name_std"].map(
    svi_clean.set_index("county_name_std")["county_name"].to_dict()
)
mapping_table["match_status"] = mapping_table["county_fips"].apply(
    lambda x: "✓ matched" if pd.notna(x) else "✗ UNMATCHED"
)
mapping_table = mapping_table.rename(columns={
    "ahrf_county_raw":  "ahrf_original_name",
    "county_name_std":  "ahrf_standardized_name",
    "matched_svi_county": "svi_county_name",
    "county_fips":      "assigned_fips",
})

print("── AHRF → SVI county name mapping audit ─────────────────────────────")
print(mapping_table.to_string(index=False))

# ── Validation ────────────────────────────────────────────────────────────────
matched   = (mapping_table["match_status"] == "✓ matched").sum()
unmatched = (mapping_table["match_status"] == "✗ UNMATCHED").sum()

print(f"\n── Match summary ────────────────────────────────────────────────────")
print(f"  Total AHRF rows : {len(mapping_table)}")
print(f"  Matched         : {matched}")
print(f"  Unmatched       : {unmatched}")

if unmatched > 0:
    print("\n  ⚠  UNMATCHED RECORDS — manual review required:")
    print(mapping_table[mapping_table["match_status"] == "✗ UNMATCHED"].to_string(index=False))
else:
    print("  ✓ All 58 AHRF counties matched exactly to SVI counties")

# Check for duplicate many-to-one matches (two AHRF rows → same FIPS)
dup_fips = ahrf_clean["county_fips"].value_counts()
dup_fips = dup_fips[dup_fips > 1]
if dup_fips.empty:
    print("  ✓ No many-to-one FIPS matches (each FIPS assigned exactly once)")
else:
    print(f"\n  ⚠  Duplicate FIPS assignments detected:\n{dup_fips}")

assert matched == 58, f"Expected 58 matches, got {matched}"
assert unmatched == 0, f"Unexpected unmatched rows: {unmatched}"
assert dup_fips.empty, "Many-to-one FIPS matches exist — review required"

print("\n✓ Mapping complete: 58 exact one-to-one county matches")
print(f"ahrf_clean now has county_fips column. Shape: {ahrf_clean.shape}")
