"""
Working Data Dictionary
Concise reference for every field needed across all three analytical datasets.
Built from:
  - SVI PDF documentation (2022)
  - HRSA HPSA data dictionary XLSX (2026-06-25)
  - AHRF export column headers
"""
import pandas as pd

pd.set_option("display.max_colwidth", 120)
pd.set_option("display.width", 200)

# ── Dictionary entries ─────────────────────────────────────────────────────────
# Each entry: (Dataset, Field Name, Type, Description, Known Caveats / Rules)
_entries = [

    # ── SVI ────────────────────────────────────────────────────────────────────
    ("SVI", "STCNTY",     "str(5)",   "5-digit county FIPS (state + county)",
     "Zero-padded; CA counties start with '06'. Preferred join key."),

    ("SVI", "COUNTY",     "str",      "County name (e.g., 'Alameda County')",
     "Includes ' County' suffix. Use for display only; join on STCNTY."),

    ("SVI", "ST_ABBR",    "str(2)",   "State abbreviation",
     "All rows = 'CA' in this extract."),

    ("SVI", "E_TOTPOP",   "int",      "ACS 2018–2022 5-year estimated total population",
     "Not the same as Census 2022 pop. used in AHRF. Use as SVI denominator only."),

    ("SVI", "RPL_THEMES", "float[0,1]","Overall SVI composite percentile rank",
     "CA-specific ranking (1=most vulnerable). -999 = missing (none in this file)."),

    ("SVI", "RPL_THEME1", "float[0,1]","Socioeconomic status percentile",
     "Includes poverty, unemployment, housing burden, no HS diploma, uninsured."),

    ("SVI", "RPL_THEME2", "float[0,1]","Household characteristics percentile",
     "Includes age 65+, age 17-, disability, single-parent, limited English."),

    ("SVI", "RPL_THEME3", "float[0,1]","Racial & ethnic minority status percentile",
     "Includes % minority population. Treat with caution for very small counties."),

    ("SVI", "RPL_THEME4", "float[0,1]","Housing type & transportation percentile",
     "Includes multi-unit housing, mobile homes, crowding, no vehicle, group quarters."),

    # ── AHRF ───────────────────────────────────────────────────────────────────
    ("AHRF", "County",         "str",    "County name + state abbr (e.g., 'Alameda County, CA')",
     "No native FIPS. Strip ', CA' and match to SVI.COUNTY to derive FIPS."),

    ("AHRF", "primary_care_physicians_2022", "float", "Primary care physician count (AMA 2022)",
     "0 is valid (Alpine, Sierra). Source: AMA Physician Professional Data 2022."),

    ("AHRF", "ahrf_population_2022",   "float", "Total county population (Census 2022 estimate)",
     "Differs slightly from SVI E_TOTPOP (ACS 2018-22). Use as rate denominator."),

    ("AHRF", "supplied_rate_per_100000",     "float", "Supplied rate: physicians per 100,000 residents",
     "Validation only. Recalculate: (primary_care_physicians_2022 / population_2022) * 100_000."),

    ("AHRF", "[no FIPS column]",  "—",     "FIPS must be engineered via name-matching",
     "Parse 'County, CA' → strip ', CA' → match SVI.COUNTY → join to get STCNTY."),

    # ── HPSA ───────────────────────────────────────────────────────────────────
    ("HPSA", "HPSA ID",                    "str",      "Unique identifier for an HPSA designation",
     "One ID can appear in multiple rows (multi-county HPSAs or historical rows)."),

    ("HPSA", "Designation Type",           "str",      "Classification of the shortage area",
     "Geo/Pop: 'Geographic HPSA', 'HPSA Population', 'High Needs Geographic HPSA'. "
     "Facility: 'Rural Health Clinic', 'FQHC', 'IHS/Tribal', 'FQHC Look-A-Like', "
     "'Correctional Facility', 'Other Facility'. Keep separate — facility ≠ county shortage."),

    ("HPSA", "HPSA Discipline Class",      "str",      "Healthcare discipline (always 'Primary Care' in this file)",
     "Filter to 'Primary Care' before any aggregation."),

    ("HPSA", "HPSA Score",                 "int[0,25]","Shortage severity score (higher = greater shortage)",
     "Scale: 0–25. Only meaningful for Designated rows. Use max() when aggregating to county."),

    ("HPSA", "HPSA Status",                "str",      "Current designation status",
     "Valid: 'Designated' (active), 'Withdrawn' (no longer active), "
     "'Proposed For Withdrawal' (under review). Filter to 'Designated' for active shortages."),

    ("HPSA", "Common State County FIPS Code", "str(5)", "5-char county FIPS, zero-padded",
     "Best HPSA join key to SVI. Do NOT use 'County FIPS Code' (integer, drops leading zero)."),

    ("HPSA", "Common County Name",         "str",      "County name + state (e.g., 'San Diego County, CA')",
     "Use only as a human-readable label; join on FIPS."),

    ("HPSA", "HPSA Designation Date",      "str(date)","Date the HPSA was originally designated",
     "MM/DD/YYYY format. Useful for auditing designation age."),

    ("HPSA", "HPSA Designation Last Update Date", "str(date)", "Date of most recent status update",
     "MM/DD/YYYY. More relevant than designation date for currency check."),

    ("HPSA", "HPSA Estimated Served Population", "float", "Population served within the HPSA boundary",
     "9.5% null in CA rows. Do not sum across rows without deduplication."),

    ("HPSA", "HPSA Estimated Underserved Population", "float", "Population lacking adequate primary care access",
     "9.5% null in CA rows. Only meaningful for Designated Geo/Pop rows; sum with care."),

    ("HPSA", "Rural Status",               "str",      "Rural classification of the designation",
     "Values: 'Rural', 'Non-Rural', 'Partially Rural', 'Unknown', NaN. "
     "345 nulls + 235 'Unknown' in CA — do not impute."),

    ("HPSA", "HPSA Component Type Description", "str", "Geographic unit type of the HPSA component",
     "Values: 'Census Tract', 'County Subdivision', 'Single County', 'Unknown'. "
     "'Unknown' = 767 rows (all facility designations). Component = Census Tract is most common."),
]

# ── Build DataFrame ────────────────────────────────────────────────────────────
wdd = pd.DataFrame(_entries, columns=["Dataset", "Field Name", "Type", "Description", "Caveats / Rules"])

# ── Print ──────────────────────────────────────────────────────────────────────
print("=" * 100)
print("WORKING DATA DICTIONARY — California Healthcare Access Priority Explorer")
print("Sources: CDC SVI 2022 PDF · HRSA HPSA Dict 2026-06-25 · AHRF XLSX column headers")
print("=" * 100)

for _ds in ["SVI", "AHRF", "HPSA"]:
    _sub = wdd[wdd["Dataset"] == _ds]
    print(f"\n{'─'*100}")
    print(f"  DATASET: {_ds}  ({len(_sub)} fields documented)")
    print(f"{'─'*100}")
    for _, _r in _sub.iterrows():
        print(f"\n  Field       : {_r['Field Name']}")
        print(f"  Type        : {_r['Type']}")
        print(f"  Description : {_r['Description']}")
        print(f"  Caveats     : {_r['Caveats / Rules']}")

print(f"\n{'='*100}")
print(f"Total fields documented: {len(wdd)}")
print(f"  SVI  : {(wdd['Dataset']=='SVI').sum()}")
print(f"  AHRF : {(wdd['Dataset']=='AHRF').sum()}")
print(f"  HPSA : {(wdd['Dataset']=='HPSA').sum()}")
print(f"{'='*100}")
