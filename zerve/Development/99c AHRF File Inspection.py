"""
Section 03 — Raw File Inspection
Block 03b: HRSA AHRF California County Primary Care Physicians 2022

FINDINGS (from raw scan):
  - Sheet: 'AHRF Geo Data' (only sheet)
  - Row 0: blank
  - Row 1: data.HRSA.gov source URLs (5 cells)
  - Row 2: filter description string
  - Row 3: REAL COLUMN HEADERS  ← header=3
  - Rows 4–61: 58 California county data rows
  - Rows 62–63: blank
  - Row 64: "Note: Blank cells indicate that data are not available."
"""
import pandas as pd
import numpy as np

AHRF_PATH = "california_healthcare_access/hrsa_ahrf_ca_county_primary_care_physicians_population_2022.xlsx"
HEADER_ROW = 3   # 0-indexed; confirmed by raw scan above

# ── Load with correct header row ──────────────────────────────────────────────
ahrf_raw = pd.read_excel(AHRF_PATH, sheet_name="AHRF Geo Data", header=HEADER_ROW)

print("=" * 60)
print("FILE: hrsa_ahrf_ca_county_primary_care_physicians_population_2022.xlsx")
print(f"Sheet: 'AHRF Geo Data'  |  Header row (0-indexed): {HEADER_ROW}")
print("=" * 60)
print(f"Raw shape (before footer removal): {ahrf_raw.shape}")
print(f"\nColumn names:\n  {ahrf_raw.columns.tolist()}")

# ── Remove blank footer rows and explanatory note ─────────────────────────────
# Row 64 raw = "Note: Blank cells..." → appears as an extra row in ahrf_raw
# Drop fully-blank rows, then drop any row where the first column starts with "Note:"
ahrf_raw_clean = ahrf_raw.dropna(how="all").copy()
# Identify and drop the explanatory note row
note_mask = ahrf_raw_clean.iloc[:, 0].astype(str).str.startswith("Note:")
if note_mask.any():
    print(f"\nFooter note found — dropping {note_mask.sum()} row(s):")
    print(f"  {ahrf_raw_clean.loc[note_mask].iloc[:, 0].tolist()}")
    ahrf_raw_clean = ahrf_raw_clean[~note_mask]

print(f"\nShape after removing blank rows + note: {ahrf_raw_clean.shape}")
print(f"\n── All rows ──────────────────────────────────────────────────")
print(ahrf_raw_clean.to_string())

# ── Summary statistics ─────────────────────────────────────────────────────────
print(f"\n── Data types ────────────────────────────────────────────────")
print(ahrf_raw_clean.dtypes)

print(f"\n── Null / missing counts ─────────────────────────────────────")
print(ahrf_raw_clean.isnull().sum())

print(f"\n── Numeric summary ───────────────────────────────────────────")
# Rename columns for easy reference
col_map = {
    ahrf_raw_clean.columns[0]: "county_label",
    ahrf_raw_clean.columns[1]: "pc_physicians_2022",
    ahrf_raw_clean.columns[2]: "population_2022",
    ahrf_raw_clean.columns[3]: "rate_per_100k",
    ahrf_raw_clean.columns[4]: "source"
}
ahrf_display = ahrf_raw_clean.rename(columns=col_map)
print(ahrf_display[["pc_physicians_2022","population_2022","rate_per_100k"]].describe())

print(f"\n── Unique county count ───────────────────────────────────────")
print(f"  {ahrf_raw_clean.shape[0]} county rows (expected 58 for California)")

print(f"\n── Counties with 0 physicians ────────────────────────────────")
zero_md = ahrf_raw_clean[ahrf_raw_clean.iloc[:,1] == 0]
print(zero_md.iloc[:,[0,1,2,3]].to_string())

print(f"\n── Source field unique values ────────────────────────────────")
print(ahrf_raw_clean.iloc[:,4].unique())

print("\n── DONE 03b ──────────────────────────────────────────────────")
