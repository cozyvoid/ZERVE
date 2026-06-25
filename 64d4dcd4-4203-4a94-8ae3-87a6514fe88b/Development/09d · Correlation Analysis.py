import pandas as pd
import numpy as np
from scipy import stats

df = ca_county_healthcare_access_joined.copy()

RATE_COL = "primary_care_physicians_per_10000"

# Pairs: (x-variable, label)
PAIRS = [
    ("svi_overall",                  "Overall SVI percentile"),
    ("svi_socioeconomic",            "SVI Theme 1: Socioeconomic"),
    ("svi_household_characteristics","SVI Theme 2: Household Characteristics"),
    ("svi_racial_ethnic_minority",   "SVI Theme 3: Racial/Ethnic Minority"),
    ("svi_housing_transportation",   "SVI Theme 4: Housing & Transportation"),
    ("ahrf_population_2022",         "County population (AHRF 2022)"),
    ("current_geo_population_max_score", "Current geo/pop HPSA max score"),
]

def strength_label(r):
    """Interpret absolute correlation magnitude (Evans 1996 scale)."""
    a = abs(r)
    if a >= 0.80: return "Very strong"
    if a >= 0.60: return "Strong"
    if a >= 0.40: return "Moderate"
    if a >= 0.20: return "Weak"
    return "Negligible"

rows = []
for xcol, xlabel in PAIRS:
    pair = df[[RATE_COL, xcol]].dropna()
    n = len(pair)
    x = pair[xcol].values
    y = pair[RATE_COL].values

    r_p, p_p = stats.pearsonr(x, y)
    r_s, p_s = stats.spearmanr(x, y)

    rows.append({
        "variable":           xlabel,
        "n":                  n,
        "pearson_r":          round(r_p, 3),
        "pearson_p":          round(p_p, 4),
        "spearman_r":         round(r_s, 3),
        "spearman_p":         round(p_s, 4),
        "direction":          "positive" if r_s > 0 else "negative",
        "strength_spearman":  strength_label(r_s),
        "pearson_vs_spearman_diff": round(abs(r_p - r_s), 3),
        "material_disagreement": abs(r_p - r_s) >= 0.10,
    })

correlation_summary = pd.DataFrame(rows)

# ── Print full summary ────────────────────────────────────────────────────────
print("=" * 80)
print("09d · CORRELATION ANALYSIS — Physician Rate per 10,000 vs Selected Variables")
print("  N=58 counties (CA ecological units); Spearman preferred for robustness.")
print("  Correlation ≠ causation.")
print("=" * 80)
print()
print(f"  {'Variable':<45} {'n':>3}  {'Pearson r':>9}  {'p':>6}  {'Spearman r':>10}  {'p':>6}  {'Strength':>13}  {'|Δ|':>5}")
print("  " + "-" * 106)
for _, r in correlation_summary.iterrows():
    flag = "  ⚠ material Pearson/Spearman gap" if r["material_disagreement"] else ""
    print(f"  {r['variable']:<45} {r['n']:>3}  {r['pearson_r']:>9.3f}  "
          f"{r['pearson_p']:>6.4f}  {r['spearman_r']:>10.3f}  {r['spearman_p']:>6.4f}  "
          f"{r['strength_spearman']:>13}  {r['pearson_vs_spearman_diff']:>5.3f}{flag}")

# ── Material disagreements ────────────────────────────────────────────────────
mat = correlation_summary[correlation_summary["material_disagreement"]]
print(f"\n── Material Pearson/Spearman disagreements (|Δ| ≥ 0.10): {len(mat)} ──")
if mat.empty:
    print("  None — Pearson and Spearman are broadly consistent for all pairs.")
else:
    for _, r in mat.iterrows():
        print(f"  {r['variable']}: Pearson={r['pearson_r']}, Spearman={r['spearman_r']}")
        print("  Likely driven by non-linearity or influential outliers.")

# ── Alpine / Sierra sensitivity check ────────────────────────────────────────
print("\n── Sensitivity: exclude Alpine (pop 1,190) and Sierra (pop 3,217) ──────────")
print("  These are zero-physician, very small counties that may exert leverage.")
df_trim = df[~df["county_name"].isin(["Alpine County", "Sierra County"])]
print(f"  Sample after exclusion: {len(df_trim)} counties")
print(f"\n  {'Variable':<45} {'Full n':>6}  {'Full Sp.r':>9}  {'Trim n':>6}  {'Trim Sp.r':>9}  {'Δ Sp.r':>7}")
print("  " + "-" * 90)
for xcol, xlabel in PAIRS:
    full_pair  = df[[RATE_COL, xcol]].dropna()
    trim_pair  = df_trim[[RATE_COL, xcol]].dropna()
    r_full     = stats.spearmanr(full_pair[xcol], full_pair[RATE_COL])[0]
    r_trim     = stats.spearmanr(trim_pair[xcol], trim_pair[RATE_COL])[0]
    delta      = r_trim - r_full
    flag       = "  ← notable shift" if abs(delta) >= 0.05 else ""
    print(f"  {xlabel:<45} {len(full_pair):>6}  {r_full:>9.3f}  "
          f"{len(trim_pair):>6}  {r_trim:>9.3f}  {delta:>+7.3f}{flag}")
print("\n  Sensitivity results shown for transparency only.")
print("  Full-sample results above are the primary findings.")
print("  Alpine/Sierra are NOT removed from any downstream analysis.")
