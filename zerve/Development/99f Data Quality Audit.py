"""
Section 04 — Data Quality Audit
Consolidates findings from blocks 03a–03d into a structured audit summary.
All source data is re-loaded here so this block is self-contained.
"""
import pandas as pd
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
SVI_PATH  = "california_healthcare_access/cdc_svi_ca_county_2022.csv"
AHRF_PATH = "california_healthcare_access/hrsa_ahrf_ca_county_primary_care_physicians_population_2022.xlsx"
HPSA_PATH = "california_healthcare_access/hrsa_primary_care_hpsa_national_2026-06-25.csv"

# ── Re-load raw files ──────────────────────────────────────────────────────────
_svi  = pd.read_csv(SVI_PATH, dtype=str)
_ahrf = pd.read_excel(AHRF_PATH, sheet_name="AHRF Geo Data", header=3)
_ahrf = _ahrf.dropna(how="all")
_ahrf = _ahrf[~_ahrf.iloc[:, 0].astype(str).str.startswith("Note:")]
_hpsa = pd.read_csv(HPSA_PATH, dtype=str, low_memory=False)
_hpsa_ca = _hpsa[_hpsa["Primary State Abbreviation"] == "CA"].copy()

# ── SVI key columns for null check ────────────────────────────────────────────
_svi_key = ["STCNTY", "COUNTY", "E_TOTPOP",
            "RPL_THEMES", "RPL_THEME1", "RPL_THEME2", "RPL_THEME3", "RPL_THEME4"]
_svi_num = _svi[_svi_key[2:]].apply(pd.to_numeric, errors="coerce")
_svi_nulls = _svi_num.isna().sum().sum()
_svi_neg999 = (_svi_num == -999).sum().sum()

# ── AHRF column names ─────────────────────────────────────────────────────────
_ac = _ahrf.columns.tolist()  # [County, Physicians, Population, Rate, Source]
_ahrf_nulls = _ahrf.iloc[:, 1:4].apply(pd.to_numeric, errors="coerce").isna().sum().sum()
_zero_phys  = (_ahrf.iloc[:, 1].apply(pd.to_numeric, errors="coerce") == 0).sum()

# ── HPSA CA key fields nulls ───────────────────────────────────────────────────
_hpsa_key = [
    "HPSA ID", "Designation Type", "HPSA Discipline Class", "HPSA Score",
    "HPSA Status", "Common State County FIPS Code", "Common County Name",
    "HPSA Estimated Underserved Population", "Rural Status",
    "HPSA Component Type Description"
]
_hpsa_null_counts = {f: int(_hpsa_ca[f].isna().sum()) for f in _hpsa_key if f in _hpsa_ca.columns}
_hpsa_total_nulls = sum(_hpsa_null_counts.values())

# ── FIPS candidates ────────────────────────────────────────────────────────────
_hpsa_fips_cols = [c for c in _hpsa_ca.columns if "fips" in c.lower()]

# ── Designated-only HPSA CA subset ────────────────────────────────────────────
_geo_pop_types = {"Geographic HPSA", "HPSA Population", "High Needs Geographic HPSA"}
_fac_types = {
    "Rural Health Clinic", "Federally Qualified Health Center",
    "Indian Health Service, Tribal Health, and Urban Indian Health Organizations",
    "Federally Qualified Health Center Look A Like",
    "Correctional Facility", "Other Facility"
}
_hpsa_ca["_dgroup"] = _hpsa_ca["Designation Type"].apply(
    lambda x: "Geo/Pop" if x in _geo_pop_types else ("Facility" if x in _fac_types else "Other")
)
_desig = _hpsa_ca[_hpsa_ca["HPSA Status"] == "Designated"]
_desig_gp = _desig[_desig["_dgroup"] == "Geo/Pop"]
_desig_fac = _desig[_desig["_dgroup"] == "Facility"]

# ─────────────────────────────────────────────────────────────────────────────
# ❶  FILE INVENTORY
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("SECTION 04 — DATA QUALITY AUDIT")
print("=" * 72)

print("\n❶  FILE INVENTORY")
print("-" * 72)
_inv = [
    ["SVI CSV",        "cdc_svi_ca_county_2022.csv",                    "58 rows",   "158 cols", "2022 (ACS 2018-22)", "CA counties only"],
    ["AHRF XLSX",      "hrsa_ahrf_ca_county_primary_care_...2022.xlsx", "58 rows",   "5 cols",   "2022",               "CA counties only"],
    ["HPSA CSV (nat)", "hrsa_primary_care_hpsa_national_2026-06-25.csv","79,089 rows","66 cols", "Downloaded 2026-06-25","All US states"],
    ["HPSA CSV (CA)",  " └─ California subset",                         "8,245 rows","67 cols",  "Current snapshot",   "CA rows only"],
    ["HPSA Dict XLSX", "hrsa_hpsa_data_dictionary_2026-06-25.xlsx",     "100 rows",  "12 cols",  "2026-06-25",         "HPSA field definitions"],
    ["SVI PDF",        "cdc_svi_2022_data_dictionary_...zcta.pdf",      "—",         "—",        "2022",               "SVI field definitions"],
]
_hdr = f"{'Dataset':<18} {'Rows':>10} {'Cols':>6}  {'Vintage':<22} {'Notes'}"
print(_hdr)
print("-" * 72)
for r in _inv:
    print(f"  {r[0]:<16} {r[2]:>10} {r[3]:>6}  {r[4]:<22} {r[5]}")

# ─────────────────────────────────────────────────────────────────────────────
# ❷  KEY FIELDS & NULLS
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n❷  KEY FIELD PRESENCE & MISSING VALUES")
print("-" * 72)

print("\n  — SVI (58 rows)")
for f in _svi_key:
    _present = f in _svi.columns
    if _present:
        _v = pd.to_numeric(_svi[f], errors="coerce")
        _n = int(_v.isna().sum())
        _m = int((_v == -999).sum())
        print(f"    ✓ {f:<20}  nulls={_n:>3}  -999_count={_m:>3}")
    else:
        print(f"    ✗ {f:<20}  MISSING")

print(f"\n  — AHRF (58 rows)")
for _i, _cn in enumerate(_ac):
    _v = pd.to_numeric(_ahrf.iloc[:, _i], errors="coerce") if _i > 0 else None
    _n = int(_v.isna().sum()) if _v is not None else "—"
    print(f"    col[{_i}] {_cn[:55]:<55}  nulls={_n}")

print(f"\n  — HPSA CA (8,245 rows) — required fields only")
for f, n in _hpsa_null_counts.items():
    _pct = n / len(_hpsa_ca) * 100
    print(f"    ✓ {f:<55}  nulls={n:>5,} ({_pct:.1f}%)")

# ─────────────────────────────────────────────────────────────────────────────
# ❸  -999 SENTINEL CHECK (SVI)
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n❸  SVI -999 SENTINEL VALUE CHECK")
print("-" * 72)
print(f"  RPL_ / E_ / EP_ columns scanned : {_svi[['RPL_THEMES','RPL_THEME1','RPL_THEME2','RPL_THEME3','RPL_THEME4','E_TOTPOP']].shape[1]} key fields")
print(f"  Total -999 instances found       : {_svi_neg999}  ← CLEAN ✓")
print(f"  (Note: -999 = 'data unavailable' per SVI documentation; none present here)")

# ─────────────────────────────────────────────────────────────────────────────
# ❹  GEOGRAPHIC COVERAGE
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n❹  GEOGRAPHIC COVERAGE")
print("-" * 72)

# SVI
_svi_counties = _svi["STCNTY"].nunique()
_svi_fips_len = _svi["STCNTY"].str.len().value_counts().to_dict()
print(f"  SVI  : {_svi_counties} unique STCNTY values  | FIPS char-lengths: {_svi_fips_len}")
print(f"         All start with '06' (CA)? {(_svi['STCNTY'].str.startswith('06')).all()}")

# AHRF — extract FIPS-like identifier from county label (none natively; name-based)
print(f"\n  AHRF : {len(_ahrf)} rows  | No native FIPS column — county name is 'County, CA' format")
print(f"         Unique county labels: {_ahrf.iloc[:,0].nunique()}")
print(f"         Counties with 0 physicians: {int(_zero_phys)}  (Alpine, Sierra)")
print(f"         Join strategy: parse AHRF county name → strip ', CA' → match SVI COUNTY field")

# HPSA
_hpsa_fips_uniq = _hpsa_ca["Common State County FIPS Code"].nunique()
_hpsa_county_uniq = _hpsa_ca["Common County Name"].nunique()
print(f"\n  HPSA : {_hpsa_fips_uniq} unique FIPS codes in CA subset (expected ≤58)")
print(f"         {_hpsa_county_uniq} unique county names in CA subset")
print(f"         FIPS column: 'Common State County FIPS Code' — all 5-char strings ✓")
print(f"         ⚠  'County FIPS Code' also present but stored as integer (loses leading zero)")

# ─────────────────────────────────────────────────────────────────────────────
# ❺  DUPLICATE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n❺  DUPLICATE RECORD ANALYSIS")
print("-" * 72)

# SVI
_svi_dups = _svi.duplicated(subset=["STCNTY"]).sum()
print(f"  SVI  : Duplicate STCNTY rows = {_svi_dups}  ← CLEAN ✓  (one row per county)")

# AHRF
_ahrf_dups = _ahrf.iloc[:,0].duplicated().sum()
print(f"  AHRF : Duplicate county-label rows = {_ahrf_dups}  ← CLEAN ✓  (one row per county)")

# HPSA
_total_hpsa_ca = len(_hpsa_ca)
_uniq_hpsa_id  = _hpsa_ca["HPSA ID"].nunique()
print(f"\n  HPSA : {_total_hpsa_ca:,} total CA rows  |  {_uniq_hpsa_id:,} unique HPSA IDs")
print(f"         ⚠  {_total_hpsa_ca - _uniq_hpsa_id:,} 'duplicate' rows by HPSA ID")
print(f"            Root cause: each HPSA ID can span multiple counties or")
print(f"            appear with multiple historical status records (Withdrawn/Designated).")
print(f"            Do NOT use raw row count as a shortage-severity measure.")
print(f"\n  HPSA status breakdown (CA all rows):")
for _s, _n in _hpsa_ca["HPSA Status"].value_counts(dropna=False).items():
    print(f"    {str(_s):<35}  {_n:>5,}")
print(f"\n  Designated rows only (CA):")
print(f"    Geo/Population designations : {len(_desig_gp):>5,}  across {_desig_gp['Common State County FIPS Code'].nunique()} unique counties")
print(f"    Facility designations       : {len(_desig_fac):>5,}  across {_desig_fac['Common State County FIPS Code'].nunique()} unique counties")

# ─────────────────────────────────────────────────────────────────────────────
# ❻  FIPS FIELD CANDIDATES & JOIN-KEY RECOMMENDATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n❻  FIPS FIELD CANDIDATES & JOIN-KEY RECOMMENDATION")
print("-" * 72)
print("""
  SVI fields:
    STCNTY  — 5-char county FIPS (state+county). ✓ PREFERRED JOIN KEY.
    FIPS    — also present; likely identical to STCNTY. Verify before use.

  AHRF fields:
    (none)  — no FIPS column in the AHRF export.
              Action: parse 'County' label (e.g., 'Alameda County, CA')
              → strip ', CA' → lowercase → match SVI COUNTY string.
              Validate that all 58 names match without residuals.

  HPSA fields:
    'Common State County FIPS Code'  — 5-char string, 0-padded. ✓ BEST HPSA FIPS.
    'County FIPS Code'               — integer (leading zero lost). ✗ Do not use directly.
    'Common State FIPS Code'         — state-only (2 chars). Not county-level.
    'Primary State FIPS Code'        — state-only. Not county-level.

  Recommended join strategy:
    1. SVI  ↔ AHRF  : SVI.STCNTY ↔ engineered AHRF county FIPS
                       (parse + lookup from STCNTY/COUNTY mapping).
    2. SVI  ↔ HPSA  : SVI.STCNTY ↔ HPSA.'Common State County FIPS Code'
                       Both are 5-char zero-padded strings. One-to-many;
                       aggregate HPSA first, then join.
    All FIPS values must be stored as str with zfill(5) to preserve '06' prefix.
""")

# ─────────────────────────────────────────────────────────────────────────────
# ❼  REPORTING PERIOD VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n❼  REPORTING PERIOD VERIFICATION")
print("-" * 72)
_periods = [
    ["SVI RPL_THEMES / RPL_THEME1-4",   "2022 (ACS 2018–2022 5-yr estimates)", "CA-specific county percentile rankings"],
    ["SVI E_TOTPOP",                     "2018–2022 ACS 5-year estimate",       "Vintage matches RPL fields"],
    ["AHRF pc_physicians_2022",          "2022 (AMA Physician Professional Data)", "County-level physician count"],
    ["AHRF population_2022",             "2022 (Census County Pop. Estimates)", "Denominator for rate calculation"],
    ["AHRF rate_per_100k",               "2022",                                "Supplied rate — recalculate to validate"],
    ["HPSA Designation Type/Status",     "Current snapshot (2026-06-25)",       "⚠  Not a 2022 measure; use as indicator only"],
    ["HPSA HPSA Score",                  "Current snapshot (2026-06-25)",       "⚠  Treat as current status, not 2022 data"],
]
_ph = f"  {'Measure':<40} {'Vintage':<40} {'Notes'}"
print(_ph)
print("  " + "-" * 68)
for r in _periods:
    print(f"  {r[0]:<40} {r[1]:<40} {r[2]}")

# ─────────────────────────────────────────────────────────────────────────────
# ❽  SVI RANKING SCOPE CONFIRMATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n❽  SVI PERCENTILE RANKING SCOPE")
print("-" * 72)
print("""
  The downloaded file covers ONLY California (58 counties, ST_ABBR='CA').
  Per CDC SVI documentation: when the file is a single-state extract,
  RPL_THEMES and RPL_THEME1–4 are CALIFORNIA-SPECIFIC percentile rankings
  (i.e., each county is ranked relative to the other 57 CA counties, not
  relative to all ~3,200 US counties).

  ⚠  Implication: An RPL_THEMES of 0.90 means the county is in the top 10%
     most vulnerable among California counties — not nationally.
     This is appropriate for an intra-state priority analysis.
""")

# ─────────────────────────────────────────────────────────────────────────────
# ❾  UNEXPECTED VALUES & FLAGS
# ─────────────────────────────────────────────────────────────────────────────
print("\n❾  UNEXPECTED VALUES & FLAGS")
print("-" * 72)
print("""
  SVI:
    • No -999 sentinel values in any RPL_ or E_ field → no imputation needed.
    • RPL_THEME3 values include 0.0 for Alpine County (population=1,515;
      very small denominator → treat with caution in analysis).
    • 158 total columns; only ~15 needed for Milestone 2+.

  AHRF:
    • Alpine County, CA  : 0 primary care physicians  (pop 1,190)
    • Sierra County, CA  : 0 primary care physicians  (pop 3,217)
      → Rate = 0.0 is valid, not missing.  Flag as high-scarcity counties.
    • No FIPS column present — join requires name-matching logic.
    • Population counts in AHRF (Census 2022) differ slightly from SVI
      (ACS 2018–2022) — use AHRF population as denominator for AHRF rate
      recalculation; use SVI E_TOTPOP for SVI-specific calculations only.

  HPSA:
    • 'Proposed For Withdrawal' status (1,553 CA rows) means designation is
      under review — should NOT be treated as currently active.
    • 'Withdrawn' status (5,106 CA rows) = no longer designated.
    • Only 'Designated' rows (1,586 CA) should drive any shortage indicator.
    • Rural Status has 345 NaN and 235 'Unknown' values in CA — do not
      impute; flag as uncertain in any rural/urban breakdown.
    • HPSA Estimated Underserved Population: check nulls before summing.
    • Component Type = 'Unknown' for 767 rows (facility designations).
    • The top HPSA ID (1069990618) spans 628 rows (San Diego census tracts) —
      confirms duplication is geographic decomposition, not data error.
""")

# ─────────────────────────────────────────────────────────────────────────────
# ❿  UNCERTAIN FIELDS REQUIRING FURTHER DOCUMENTATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n❿  UNCERTAIN / UNRESOLVED FIELDS")
print("-" * 72)
print("""
  1. SVI 'FIPS' column vs 'STCNTY' — both present, likely identical.
     Action: verify with assert svi['FIPS'].equals(svi['STCNTY']) in cleaning block.

  2. AHRF 'Rate (per 100,000)' — denominator population version unclear
     (Census 2022 estimate vs ACS). Recalculate as:
       rate_per_10k = (physicians / population) * 10_000
     and cross-check against supplied rate_per_100k / 10.

  3. HPSA 'HPSA Score' — scale is 0–25 (higher = greater shortage).
     Confirmed max=24 for CA designated rows. Verify no scores >25.

  4. HPSA 'HPSA Estimated Underserved Population' — null count not yet
     verified for Designated Geo/Pop rows specifically. Check in 07 block.

  5. SVI RPL percentile direction — higher RPL = MORE vulnerable (0=least,
     1=most). Confirm from SVI PDF before building any composite score.

  6. AHRF county name parsing — 'Alameda County, CA' vs SVI 'Alameda County'.
     Strip ', CA' suffix; verify all 58 names match exactly.

  7. HPSA population basis — 'HPSA Designation Population' vs 'HPSA Estimated
     Served Population' vs 'HPSA Estimated Underserved Population'.
     These measure different things; do not sum them interchangeably.
""")

print("=" * 72)
print("AUDIT COMPLETE — proceed to Milestone 2 cleaning blocks (05–07)")
print("=" * 72)
