"""
Section 03 — Raw File Inspection
Block 03a: CDC/ATSDR SVI California County 2022
"""
import pandas as pd
import numpy as np

SVI_PATH = "california_healthcare_access/cdc_svi_ca_county_2022.csv"

# ── Load raw ──────────────────────────────────────────────────────────────────
svi_raw = pd.read_csv(SVI_PATH, dtype=str)  # read all as str first to catch FIPS zeros

print("=" * 60)
print("FILE: cdc_svi_ca_county_2022.csv")
print("=" * 60)
print(f"Shape          : {svi_raw.shape[0]} rows × {svi_raw.shape[1]} columns")

# ── Column list ───────────────────────────────────────────────────────────────
print("\n── All column names ──────────────────────────────────────────")
for i, col in enumerate(svi_raw.columns):
    print(f"  [{i:>3}] {col}")

# ── Key field presence ────────────────────────────────────────────────────────
key_fields = ["STCNTY", "COUNTY", "E_TOTPOP", "RPL_THEMES",
              "RPL_THEME1", "RPL_THEME2", "RPL_THEME3", "RPL_THEME4",
              "ST", "STATE", "ST_ABBR", "FIPS"]
print("\n── Key field presence ────────────────────────────────────────")
for f in key_fields:
    status = "✓ PRESENT" if f in svi_raw.columns else "✗ MISSING"
    print(f"  {status} : {f}")

# ── Sample rows ───────────────────────────────────────────────────────────────
display_cols = [c for c in ["STCNTY","COUNTY","STATE","ST_ABBR","E_TOTPOP",
                            "RPL_THEMES","RPL_THEME1","RPL_THEME2",
                            "RPL_THEME3","RPL_THEME4"] if c in svi_raw.columns]
print("\n── First 3 rows (selected columns) ──────────────────────────")
print(svi_raw[display_cols].head(3).to_string(index=False))

# ── Geographic coverage: is this CA-only? county-level? ───────────────────────
print("\n── Geographic coverage ───────────────────────────────────────")
if "STATE" in svi_raw.columns:
    print(f"  Unique STATE values : {svi_raw['STATE'].unique().tolist()}")
if "ST_ABBR" in svi_raw.columns:
    print(f"  Unique ST_ABBR values : {svi_raw['ST_ABBR'].unique().tolist()}")
if "STCNTY" in svi_raw.columns:
    n_stcnty = svi_raw["STCNTY"].nunique()
    print(f"  Unique STCNTY values  : {n_stcnty}")
    print(f"  STCNTY sample         : {svi_raw['STCNTY'].head(5).tolist()}")
    print(f"  STCNTY length check   : {svi_raw['STCNTY'].str.len().value_counts().to_dict()}")

# ── Is this county-level data? (county FIPS = 5 digits, no tract suffix) ──────
# Tract FIPS are 11 digits; ZCTA are 5-digit zip codes starting with different values
print("\n── Record-level check (county vs tract/ZCTA) ─────────────────")
if "STCNTY" in svi_raw.columns:
    lengths = svi_raw["STCNTY"].str.len().value_counts()
    print(f"  STCNTY char lengths  : {lengths.to_dict()}")
    # County FIPS = 5 chars, tract = 11; if all 5 → county-level confirmed
    all_5 = (svi_raw["STCNTY"].str.len() == 5).all()
    print(f"  All STCNTY = 5 chars : {all_5}  → {'COUNTY-LEVEL ✓' if all_5 else 'NOT pure county-level !'}")

# ── -999 sentinel values ──────────────────────────────────────────────────────
print("\n── -999 sentinel value counts ────────────────────────────────")
# Convert numeric-looking cols to float to check for -999
rpl_cols = [c for c in svi_raw.columns if c.startswith("RPL_") or c.startswith("E_") or c.startswith("EP_")]
svi_num = svi_raw[rpl_cols].apply(pd.to_numeric, errors="coerce")
neg999_counts = (svi_num == -999).sum()
neg999_nonzero = neg999_counts[neg999_counts > 0]
if len(neg999_nonzero):
    print(neg999_nonzero.to_string())
else:
    print("  No -999 values found in RPL_ / E_ / EP_ columns")

# ── RPL_ field summary ────────────────────────────────────────────────────────
print("\n── RPL_ field statistics (excluding -999) ────────────────────")
rpl_theme_cols = [c for c in ["RPL_THEMES","RPL_THEME1","RPL_THEME2","RPL_THEME3","RPL_THEME4"]
                  if c in svi_raw.columns]
for col in rpl_theme_cols:
    vals = pd.to_numeric(svi_raw[col], errors="coerce")
    valid = vals[vals != -999]
    print(f"  {col}: n={len(valid)}, nulls={vals.isna().sum()}, "
          f"min={valid.min():.4f}, max={valid.max():.4f}, mean={valid.mean():.4f}")

# ── E_TOTPOP ─────────────────────────────────────────────────────────────────
print("\n── E_TOTPOP (population estimate) ───────────────────────────")
if "E_TOTPOP" in svi_raw.columns:
    pop = pd.to_numeric(svi_raw["E_TOTPOP"], errors="coerce")
    print(f"  n={len(pop)}, nulls={pop.isna().sum()}, "
          f"min={pop.min():,.0f}, max={pop.max():,.0f}, total={pop.sum():,.0f}")

# ── COUNTY unique count ───────────────────────────────────────────────────────
print("\n── County name check ─────────────────────────────────────────")
if "COUNTY" in svi_raw.columns:
    print(f"  Unique COUNTY names : {svi_raw['COUNTY'].nunique()}")
    print(f"  Sample county names : {svi_raw['COUNTY'].head(10).tolist()}")

print("\n── DONE 03a ──────────────────────────────────────────────────")
