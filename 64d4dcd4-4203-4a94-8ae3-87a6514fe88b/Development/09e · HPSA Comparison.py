import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

BG = "#1D1D20"; TXT = "#fbfbff"; TXTS = "#909094"
COR = "#FF9F9B"; BLUE = "#A1C9F4"; YLW = "#ffd400"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "text.color": TXT, "axes.labelcolor": TXT,
    "xtick.color": TXT, "ytick.color": TXT,
    "axes.edgecolor": TXTS, "grid.color": TXTS,
    "grid.alpha": 0.25,
})

df = ca_county_healthcare_access_joined.copy()

# ── Geo/Population HPSA grouping ─────────────────────────────────────────────
hpsa_yes = df[df["has_current_geo_population_hpsa"] == True]
hpsa_no  = df[df["has_current_geo_population_hpsa"] == False]

def group_stats(grp, label):
    return {
        "group":                    label,
        "n_counties":               len(grp),
        "median_physicians_per_10k": grp["primary_care_physicians_per_10000"].median(),
        "median_svi_overall":       grp["svi_overall"].median(),
        "median_svi_socioeconomic": grp["svi_socioeconomic"].median(),
        "median_population":        grp["ahrf_population_2022"].median(),
        "n_zero_physician_counties": (grp["primary_care_physicians_2022"] == 0).sum(),
    }

hpsa_group_summary = pd.DataFrame([
    group_stats(hpsa_yes, "Active Geo/Pop HPSA  (n=34)"),
    group_stats(hpsa_no,  "No Active Geo/Pop HPSA  (n=24)"),
])

# ── Printed table ─────────────────────────────────────────────────────────────
print("=" * 72)
print("09e · HPSA COMPARISON — Geo/Population HPSA vs No Designation")
print("  Descriptive comparison only. HPSA status ≠ cause of scarcity.")
print("=" * 72)
print()
_t = hpsa_group_summary.set_index("group").T
print(_t.to_string())

# Mann-Whitney U for physician rate (non-parametric, small n)
_u, _p = stats.mannwhitneyu(
    hpsa_yes["primary_care_physicians_per_10000"],
    hpsa_no["primary_care_physicians_per_10000"],
    alternative="two-sided"
)
print(f"\nMann-Whitney U test (physician rate, two-sided): U={_u:.0f}, p={_p:.4f}")
print("  (Non-parametric; n=58 counties total. For descriptive context only.)")

# ── Facility HPSA note ────────────────────────────────────────────────────────
n_fac = df["has_current_facility_hpsa"].sum()
print(f"\n── Facility HPSA note ─────────────────────────────────────────────────")
print(f"  {n_fac}/58 counties have at least one active Facility HPSA designation.")
print("  Because 57 of 58 counties have a facility HPSA, this field provides")
print("  virtually no differentiation at the county level and should NOT be")
print("  used as a discriminating variable in the final prioritization formula.")
print("  Facility HPSAs indicate shortage at a specific clinic or facility, NOT")
print("  that the entire county is a primary-care shortage area.")

# ── Boxplot ───────────────────────────────────────────────────────────────────
fig_hpsa_box, axes = plt.subplots(1, 3, figsize=(13, 5))
fig_hpsa_box.patch.set_facecolor(BG)

METRICS = [
    ("primary_care_physicians_per_10000", "PCPs per 10,000 residents"),
    ("svi_overall",                       "Overall SVI percentile"),
    ("svi_socioeconomic",                 "Socioeconomic SVI percentile"),
]
COLORS  = [COR, BLUE]
LABELS  = ["Active\nGeo/Pop HPSA", "No Active\nGeo/Pop HPSA"]

for i, (col, ylabel) in enumerate(METRICS):
    grp_data = [hpsa_yes[col].values, hpsa_no[col].values]
    bp = axes[i].boxplot(
        grp_data, patch_artist=True, notch=False,
        medianprops=dict(color=YLW, linewidth=2),
        whiskerprops=dict(color=TXTS), capprops=dict(color=TXTS),
        flierprops=dict(marker="o", markerfacecolor=TXTS, markersize=4, alpha=0.6),
    )
    for patch, c in zip(bp["boxes"], COLORS):
        patch.set_facecolor(c)
        patch.set_alpha(0.75)
    axes[i].set_xticks([1, 2])
    axes[i].set_xticklabels(LABELS, fontsize=8)
    axes[i].set_ylabel(ylabel, fontsize=9)
    axes[i].set_title(ylabel, color=TXT, fontsize=9)

fig_hpsa_box.suptitle(
    "Geo/Population HPSA Comparison: Physician Rate and Vulnerability (2022)\n"
    "Descriptive comparison — HPSA status is not a causal variable",
    color=TXT, fontsize=10, y=1.01
)
fig_hpsa_box.tight_layout()
