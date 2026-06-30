"""
Raw File Inspection
Block 03d: Documentation files — targeted field lookups
  - hrsa_hpsa_data_dictionary_2026-06-25.xlsx
  - cdc_svi_2022_data_dictionary_tract_county_zcta.pdf
"""
import pandas as pd
import os

HPSA_DICT_PATH = "california_healthcare_access/hrsa_hpsa_data_dictionary_2026-06-25.xlsx"
SVI_PDF_PATH   = "california_healthcare_access/cdc_svi_2022_data_dictionary_tract_county_zcta.pdf"

pd.set_option("display.max_colwidth", 600)
pd.set_option("display.width", 250)

# ── Load HPSA metadata sheet ───────────────────────────────────────────────────
meta = pd.read_excel(HPSA_DICT_PATH, sheet_name="DD_HPSA_METADATA_VX", header=0)

# Write every field entry to a string buffer, then print at the end
_lines = []
_lines.append("=" * 70)
_lines.append("HPSA DATA DICTIONARY — All 100 field entries")
_lines.append("=" * 70)

for _i, _r in meta.iterrows():
    _name  = str(_r.get("Attribute Name", "")).strip()
    _defn  = str(_r.get("Definition", "")).strip()
    _valid = str(_r.get("Valid Values", "")).strip()
    _biz   = str(_r.get("Business Rule / Format", "")).strip()
    _dtype = str(_r.get("Data Type", "")).strip()
    _phys  = str(_r.get("Physical Column Name", "")).strip()
    if _name and _name != "nan":
        _lines.append(f"\n[{_i:>3}] {_name}  [{_dtype}]  phys={_phys}")
        if _valid and _valid != "nan":
            _lines.append(f"  VALID: {_valid[:600]}")
        if _defn and _defn != "nan":
            _lines.append(f"  DEFN : {_defn[:500]}")
        if _biz and _biz != "nan":
            _lines.append(f"  BIZ  : {_biz[:400]}")

print("\n".join(_lines))

# ── SVI PDF ────────────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("SVI PDF — full text extraction")
print(f"Size: {os.path.getsize(SVI_PDF_PATH):,} bytes")
print(f"{'='*70}")

_pdf = ""
try:
    from pypdf import PdfReader
    _r = PdfReader(SVI_PDF_PATH)
    print(f"pypdf: {len(_r.pages)} pages")
    for _p in _r.pages:
        _pdf += (_p.extract_text() or "") + "\n"
    print(f"Extracted {len(_pdf):,} chars\n")
    # Print the full text — the PDF is a data dictionary, likely concise
    # Limit to first 40000 chars to stay within output budget
    print(_pdf[:40000])
except ImportError:
    try:
        from pdfminer.high_level import extract_text as _ext
        _pdf = _ext(SVI_PDF_PATH) or ""
        print(f"pdfminer: {len(_pdf):,} chars\n")
        print(_pdf[:40000])
    except ImportError:
        print("No PDF library (pypdf/pdfminer) installed.")

print("\n── DONE 03d ──────────────────────────────────────────────────")
