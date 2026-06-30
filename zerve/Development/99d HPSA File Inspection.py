"""
Raw File Inspection
supports Block 03d: HRSA Primary Care HPSA National File (downloaded 2026-06-25)
"""
import pandas as pd
import numpy as np

HPSA_PATH = "california_healthcare_access/hrsa_primary_care_hpsa_national_2026-06-25.csv"

# ── Load full file ─────────────────────────────────────────────────────────────
hpsa_raw = pd.read_csv(HPSA_PATH, dtype=str, low_memory=False)

print("=" * 60)
print("FILE: hrsa_primary_care_hpsa_national_2026-06-25.csv")
print("=" * 60)
print(f"Shape (national): {hpsa_raw.shape[0]:,} rows × {hpsa_raw.shape[1]} columns")
print(f"Column count: {len(hpsa_raw.columns)}")

# ── California subset ──────────────────────────────────────────────────────────
hpsa_ca = hpsa_raw[hpsa_raw["Primary State Abbreviation"] == "CA"].copy()
print(f"\nCA rows: {len(hpsa_ca):,}")

# ── Key field presence ────────────────────────────────────────────────────────
key_fields = [
    "HPSA ID", "Designation Type", "HPSA Discipline Class", "HPSA Score",
    "Primary State Abbreviation", "HPSA Status",
    "Common State County FIPS Code", "Common County Name",
    "HPSA Designation Date", "HPSA Designation Last Update Date",
    "HPSA Estimated Served Population", "HPSA Estimated Underserved Population",
    "Rural Status", "HPSA Component Type Description"
]
print("\n── Required field presence ───────────────────────────────────")
for f in key_fields:
    print(f"  {'✓' if f in hpsa_ca.columns else '✗'} {f}")

# ── Also note the two FIPS-like columns ──────────────────────────────────────
fips_candidates = [c for c in hpsa_ca.columns if "fips" in c.lower() or "FIPS" in c]
print(f"\n── FIPS-like columns found: {fips_candidates}")

# ── Value counts — Designation Type ──────────────────────────────────────────
print("\n── Designation Type (CA, all rows) ───────────────────────────")
print(hpsa_ca["Designation Type"].value_counts(dropna=False).to_string())

# ── Designation Type grouping (geo/pop vs facility) ──────────────────────────
geo_pop_types = {"Geographic HPSA", "HPSA Population", "High Needs Geographic HPSA"}
facility_types = {
    "Rural Health Clinic", "Federally Qualified Health Center",
    "Indian Health Service, Tribal Health, and Urban Indian Health Organizations",
    "Federally Qualified Health Center Look A Like",
    "Correctional Facility", "Other Facility"
}
hpsa_ca["_desig_group"] = hpsa_ca["Designation Type"].apply(
    lambda x: "Geo/Population" if x in geo_pop_types
              else ("Facility" if x in facility_types else "Other/Unknown")
)
print("\n── Designation group summary (CA) ────────────────────────────")
print(hpsa_ca["_desig_group"].value_counts().to_string())

# ── HPSA Discipline Class ──────────────────────────────────────────────────────
print("\n── HPSA Discipline Class (CA) ────────────────────────────────")
print(hpsa_ca["HPSA Discipline Class"].value_counts(dropna=False).to_string())

# ── HPSA Status ──────────────────────────────────────────────────────────────
print("\n── HPSA Status (CA) ─────────────────────────────────────────")
print(hpsa_ca["HPSA Status"].value_counts(dropna=False).to_string())

# ── HPSA Component Type Description ──────────────────────────────────────────
print("\n── HPSA Component Type Description (CA) ─────────────────────")
print(hpsa_ca["HPSA Component Type Description"].value_counts(dropna=False).to_string())

# ── Rural Status ──────────────────────────────────────────────────────────────
print("\n── Rural Status (CA) ────────────────────────────────────────")
print(hpsa_ca["Rural Status"].value_counts(dropna=False).to_string())

# ── HPSA Score ────────────────────────────────────────────────────────────────
print("\n── HPSA Score statistics (CA, all designations) ─────────────")
_score = pd.to_numeric(hpsa_ca["HPSA Score"], errors="coerce")
print(f"  n={_score.notna().sum():,}  nulls={_score.isna().sum():,}")
print(f"  min={_score.min()}, max={_score.max()}, mean={_score.mean():.2f}, "
      f"median={_score.median()}")

# ── HPSA Score — Designated/Active only ──────────────────────────────────────
_active = hpsa_ca[hpsa_ca["HPSA Status"] == "Designated"]
_score_active = pd.to_numeric(_active["HPSA Score"], errors="coerce")
print(f"\n── HPSA Score — Designated rows only (CA) ────────────────────")
print(f"  n={_score_active.notna().sum():,}  nulls={_score_active.isna().sum():,}")
if _score_active.notna().any():
    print(f"  min={_score_active.min()}, max={_score_active.max()}, "
          f"mean={_score_active.mean():.2f}, median={_score_active.median()}")

# ── Common State County FIPS Code ────────────────────────────────────────────
print("\n── Common State County FIPS Code (CA) ───────────────────────")
_fips = hpsa_ca["Common State County FIPS Code"].dropna()
print(f"  Non-null : {len(_fips):,}  |  Null: {hpsa_ca['Common State County FIPS Code'].isna().sum():,}")
print(f"  Unique   : {_fips.nunique()}")
print(f"  Char-length dist : {_fips.str.len().value_counts().to_dict()}")
print(f"  Sample (10): {_fips.unique()[:10].tolist()}")

# Confirm it is 5-char (state+county)
all_5 = (_fips.str.len() == 5).all()
print(f"  All 5-char: {all_5}")

# ── Duplicate HPSA ID analysis ────────────────────────────────────────────────
print("\n── HPSA ID duplicate analysis (CA) ──────────────────────────")
total = len(hpsa_ca)
unique = hpsa_ca["HPSA ID"].nunique()
print(f"  Total CA rows  : {total:,}")
print(f"  Unique HPSA IDs: {unique:,}")
print(f"  Rows with dup ID: {total - unique:,}")
# Rows per HPSA ID distribution
id_counts = hpsa_ca["HPSA ID"].value_counts()
print(f"\n  Rows-per-HPSA-ID distribution:")
print(id_counts.value_counts().sort_index().to_string())
print(f"\n  Top 5 most-repeated HPSA IDs:")
print(id_counts.head(5).to_string())

# Why duplicates? Often same HPSA spans multiple counties → one row per county
print(f"\n  Why duplicates? Same HPSA ID across multiple counties:")
if total - unique > 0:
    sample_dup_id = id_counts.index[0]
    sample_rows = hpsa_ca[hpsa_ca["HPSA ID"] == sample_dup_id][
        ["HPSA ID","HPSA Name","Designation Type","HPSA Status",
         "Common County Name","Common State County FIPS Code"]
    ]
    print(sample_rows.to_string())

# ── Null counts for all required fields (CA) ─────────────────────────────────
print("\n── Null / missing counts for required fields (CA) ─────────────")
for f in key_fields:
    if f in hpsa_ca.columns:
        n_null = hpsa_ca[f].isna().sum()
        print(f"  {f:<55} nulls={n_null:>5,}")

# ── Estimated Underserved Population ─────────────────────────────────────────
print("\n── Estimated Underserved Population (CA) ─────────────────────")
_usp = pd.to_numeric(hpsa_ca["HPSA Estimated Underserved Population"], errors="coerce")
print(f"  n={_usp.notna().sum():,}  nulls={_usp.isna().sum():,}")
print(f"  min={_usp.min():.0f}, max={_usp.max():,.0f}, sum={_usp.sum():,.0f}")

# ── Unique counties covered by CA HPSA rows ──────────────────────────────────
print("\n── Unique counties covered in CA HPSA ────────────────────────")
print(f"  Unique Common County Name : {hpsa_ca['Common County Name'].nunique()}")
print(f"  Unique FIPS               : {hpsa_ca['Common State County FIPS Code'].nunique()}")

# ── Designated rows only — county coverage ────────────────────────────────────
_desig_geo_pop = hpsa_ca[
    (hpsa_ca["HPSA Status"] == "Designated") &
    (hpsa_ca["_desig_group"] == "Geo/Population")
]
print(f"\n── Designated Geo/Pop HPSA rows (CA) ────────────────────────")
print(f"  Rows: {len(_desig_geo_pop):,}")
print(f"  Unique counties: {_desig_geo_pop['Common State County FIPS Code'].nunique()}")

_desig_fac = hpsa_ca[
    (hpsa_ca["HPSA Status"] == "Designated") &
    (hpsa_ca["_desig_group"] == "Facility")
]
print(f"\n── Designated Facility HPSA rows (CA) ───────────────────────")
print(f"  Rows: {len(_desig_fac):,}")
print(f"  Unique counties: {_desig_fac['Common State County FIPS Code'].nunique()}")

print("\n── DONE 03c ──────────────────────────────────────────────────")
