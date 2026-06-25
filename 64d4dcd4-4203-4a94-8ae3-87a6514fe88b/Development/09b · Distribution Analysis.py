import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Zerve design system ──────────────────────────────────────────────────────
BG    = "#1D1D20"
TXT   = "#fbfbff"
TXTS  = "#909094"
BLUE  = "#A1C9F4"
ORG   = "#FFB482"
GRN   = "#8DE5A1"
COR   = "#FF9F9B"
LAV   = "#D0BBFF"
YLW   = "#ffd400"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "text.color": TXT, "axes.labelcolor": TXT,
    "xtick.color": TXT, "ytick.color": TXT,
    "axes.edgecolor": TXTS, "grid.color": TXTS,
    "grid.alpha": 0.25, "axes.grid": True,
    "axes.grid.axis": "y",
})

df = ca_county_healthcare_access_joined.copy()

# ── Helper: annotate median line ────────────────────────────────────────────
def vline(ax, val, label, color=YLW):
    ax.axvline(val, color=color, lw=1.5, ls="--")
    ax.text(val + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.01, ax.get_ylim()[1] * 0.85,
            label, color=color, fontsize=8)

# ══════════════════════════════════════════════════════════════════════════════
# FIG 1 — Physician rate per 10,000
# ══════════════════════════════════════════════════════════════════════════════
fig_phys_rate, ax = plt.subplots(figsize=(9, 4))
fig_phys_rate.patch.set_facecolor(BG)

med = df["primary_care_physicians_per_10000"].median()
ax.hist(df["primary_care_physicians_per_10000"], bins=18, color=BLUE, edgecolor=BG)
ax.axvline(med, color=YLW, lw=1.5, ls="--")
ax.text(med + 0.15, ax.get_ylim()[1] * 0.88, f"Median {med:.1f}", color=YLW, fontsize=8)
ax.set_xlabel("Primary-care physicians per 10,000 residents (2022)")
ax.set_ylabel("Number of counties")
ax.set_title("Distribution: Primary-Care Physician Rate per 10,000", color=TXT, fontsize=11)
fig_phys_rate.tight_layout()

# ══════════════════════════════════════════════════════════════════════════════
# FIG 2 — Overall SVI percentile
# ══════════════════════════════════════════════════════════════════════════════
fig_svi, ax2 = plt.subplots(figsize=(9, 4))
fig_svi.patch.set_facecolor(BG)

med_svi = df["svi_overall"].median()
ax2.hist(df["svi_overall"], bins=20, color=ORG, edgecolor=BG)
ax2.axvline(med_svi, color=YLW, lw=1.5, ls="--")
ax2.text(med_svi + 0.01, ax2.get_ylim()[1] * 0.88, f"Median {med_svi:.2f}", color=YLW, fontsize=8)
ax2.set_xlabel("Overall SVI percentile (CA-specific, 2022) — 1.0 = most vulnerable")
ax2.set_ylabel("Number of counties")
ax2.set_title("Distribution: Overall Social Vulnerability Index (SVI)", color=TXT, fontsize=11)
fig_svi.tight_layout()

# ══════════════════════════════════════════════════════════════════════════════
# FIG 3 — Four SVI theme percentiles (separate panels)
# ══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "svi_socioeconomic":            ("Socioeconomic Status",        LAV),
    "svi_household_characteristics":("Household Characteristics",   GRN),
    "svi_racial_ethnic_minority":   ("Racial & Ethnic Minority",    COR),
    "svi_housing_transportation":   ("Housing & Transportation",    ORG),
}

fig_themes, axes = plt.subplots(2, 2, figsize=(12, 7))
fig_themes.patch.set_facecolor(BG)
axes = axes.flatten()

for idx, (col, (label, color)) in enumerate(THEMES.items()):
    m = df[col].median()
    axes[idx].hist(df[col], bins=15, color=color, edgecolor=BG)
    axes[idx].axvline(m, color=YLW, lw=1.5, ls="--")
    axes[idx].text(m + 0.01, axes[idx].get_ylim()[1] * 0.88,
                   f"Med {m:.2f}", color=YLW, fontsize=8)
    axes[idx].set_title(label, color=TXT, fontsize=10)
    axes[idx].set_xlabel("SVI percentile (CA-specific)", fontsize=8)
    axes[idx].set_ylabel("Counties", fontsize=8)

fig_themes.suptitle("SVI Sub-Theme Percentile Distributions (2022)", color=TXT, fontsize=12, y=1.01)
fig_themes.tight_layout()

# ══════════════════════════════════════════════════════════════════════════════
# FIG 4 — Raw physician counts (log-scaled for skew)
# ══════════════════════════════════════════════════════════════════════════════
fig_phys_count, ax4 = plt.subplots(figsize=(9, 4))
fig_phys_count.patch.set_facecolor(BG)

vals = df["primary_care_physicians_2022"]
# Use log1p so zero-physician counties appear in first bin
ax4.hist(np.log1p(vals), bins=20, color=GRN, edgecolor=BG)
med_log = np.log1p(vals.median())
ax4.axvline(med_log, color=YLW, lw=1.5, ls="--")
ax4.text(med_log + 0.05, ax4.get_ylim()[1] * 0.88,
         f"Median {vals.median():.0f} PCPs", color=YLW, fontsize=8)
# Custom tick labels at meaningful count values
tick_vals = [0, 10, 50, 200, 500, 1000, 2000, 5000, 10000]
ax4.set_xticks([np.log1p(v) for v in tick_vals])
ax4.set_xticklabels([str(v) for v in tick_vals], fontsize=8)
ax4.set_xlabel("Primary-care physician count, 2022 (log scale)")
ax4.set_ylabel("Number of counties")
ax4.set_title("Distribution: Primary-Care Physician Counts (log scale)", color=TXT, fontsize=11)
fig_phys_count.tight_layout()

# ══════════════════════════════════════════════════════════════════════════════
# FIG 5 — County population (log-scaled)
# ══════════════════════════════════════════════════════════════════════════════
fig_pop, ax5 = plt.subplots(figsize=(9, 4))
fig_pop.patch.set_facecolor(BG)

pop = df["ahrf_population_2022"]
ax5.hist(np.log10(pop), bins=20, color=COR, edgecolor=BG)
med_pop = np.log10(pop.median())
ax5.axvline(med_pop, color=YLW, lw=1.5, ls="--")
ax5.text(med_pop + 0.03, ax5.get_ylim()[1] * 0.88,
         f"Median {pop.median():,.0f}", color=YLW, fontsize=8)
pop_ticks = [1000, 5000, 20000, 50000, 200000, 500000, 1000000, 5000000, 10000000]
ax5.set_xticks([np.log10(v) for v in pop_ticks])
ax5.set_xticklabels([f"{v:,}" for v in pop_ticks], fontsize=7, rotation=30, ha="right")
ax5.set_xlabel("County population, 2022 (log scale)")
ax5.set_ylabel("Number of counties")
ax5.set_title("Distribution: County Population (log scale)", color=TXT, fontsize=11)
fig_pop.tight_layout()

# ── Printed annotations ──────────────────────────────────────────────────────
print("=" * 70)
print("09b · DISTRIBUTION ANNOTATIONS")
print("=" * 70)

# Zero-physician counties
zero_phys = df[df["primary_care_physicians_2022"] == 0]["county_name"].tolist()
print(f"\nZero-physician counties ({len(zero_phys)}): {zero_phys}")

# Unusually high physician rates (> mean + 2 SD)
_mean_r = df["primary_care_physicians_per_10000"].mean()
_std_r  = df["primary_care_physicians_per_10000"].std()
high_rate = df[df["primary_care_physicians_per_10000"] > _mean_r + 2 * _std_r][
    ["county_name", "primary_care_physicians_per_10000", "ahrf_population_2022"]]
print(f"\nUnusually HIGH physician rate (>mean+2SD = {_mean_r + 2*_std_r:.1f}/10k):")
print(high_rate.to_string(index=False))

# Unusually low physician rates (non-zero, < p25 - 0.5*IQR)
p25 = df["primary_care_physicians_per_10000"].quantile(0.25)
p75 = df["primary_care_physicians_per_10000"].quantile(0.75)
low_thresh = max(0.1, p25 - 1.5 * (p75 - p25))
low_rate = df[(df["primary_care_physicians_per_10000"] > 0) &
              (df["primary_care_physicians_per_10000"] < low_thresh)][
    ["county_name", "primary_care_physicians_per_10000", "ahrf_population_2022"]]
print(f"\nUnusually LOW physician rate (non-zero, <{low_thresh:.2f}/10k):")
if low_rate.empty:
    print("  None below IQR-based lower fence (excluding zero-physician counties listed above)")
else:
    print(low_rate.to_string(index=False))

# Small-population counties (< 10,000 AHRF pop) — rates may be unstable
small_pop = df[df["ahrf_population_2022"] < 10_000][
    ["county_name", "ahrf_population_2022", "primary_care_physicians_per_10000"]]
print(f"\nSmall-population counties (<10,000 residents) — rates may be unstable:")
print(small_pop.sort_values("ahrf_population_2022").to_string(index=False))

# Large-population counties (> 1,000,000) — may dominate statewide totals
large_pop = df[df["ahrf_population_2022"] > 1_000_000][
    ["county_name", "ahrf_population_2022", "primary_care_physicians_per_10000"]]
print(f"\nLarge-population counties (>1,000,000) — influence statewide totals:")
print(large_pop.sort_values("ahrf_population_2022", ascending=False).to_string(index=False))
