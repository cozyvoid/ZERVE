import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BG = "#1D1D20"; TXT = "#fbfbff"; TXTS = "#909094"
LAV = "#D0BBFF"; GRN = "#8DE5A1"; COR = "#FF9F9B"; ORG = "#FFB482"
YLW = "#ffd400"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "text.color": TXT, "axes.labelcolor": TXT,
    "xtick.color": TXT, "ytick.color": TXT,
    "axes.edgecolor": TXTS, "grid.color": TXTS,
    "grid.alpha": 0.25,
})

df = ca_county_healthcare_access_joined.copy()

# ── Theme columns and display labels ─────────────────────────────────────────
THEME_COLS = [
    "svi_socioeconomic",
    "svi_household_characteristics",
    "svi_racial_ethnic_minority",
    "svi_housing_transportation",
]
THEME_LABELS = {
    "svi_socioeconomic":             "Socioeconomic",
    "svi_household_characteristics": "Household Char.",
    "svi_racial_ethnic_minority":    "Racial/Ethnic Minority",
    "svi_housing_transportation":    "Housing & Transport",
}
THEME_COLORS = {
    "svi_socioeconomic":             LAV,
    "svi_household_characteristics": GRN,
    "svi_racial_ethnic_minority":    COR,
    "svi_housing_transportation":    ORG,
}

# ── Identify dominant theme per county ────────────────────────────────────────
# Dominant = highest percentile among the four themes.
# Important: this does NOT recreate svi_overall (which is a composite rank).
# It identifies the single dimension on which the county ranks highest.
df["dominant_svi_theme"] = df[THEME_COLS].idxmax(axis=1).map(THEME_LABELS)

county_dominant_svi_theme = df[[
    "county_fips", "county_name",
    "svi_overall",
    "svi_socioeconomic", "svi_household_characteristics",
    "svi_racial_ethnic_minority", "svi_housing_transportation",
    "dominant_svi_theme",
]].copy().sort_values("svi_overall", ascending=False)

# ── Count by dominant theme ───────────────────────────────────────────────────
theme_counts = county_dominant_svi_theme["dominant_svi_theme"].value_counts().reset_index()
theme_counts.columns = ["dominant_theme", "county_count"]

# ── Print summary ─────────────────────────────────────────────────────────────
print("=" * 72)
print("09f · SVI THEME ANALYSIS")
print("  Dominant theme = highest single-theme percentile per county.")
print("  NOTE: Do NOT average the four themes to recreate svi_overall.")
print("  These four sub-theme rankings are informational, not additive.")
print("=" * 72)

print("\n── Count of counties by dominant SVI theme ──────────────────────────")
print(theme_counts.to_string(index=False))

print("\n── All counties with dominant theme (sorted by svi_overall desc) ─────")
_show = county_dominant_svi_theme[
    ["county_name", "svi_overall",
     "svi_socioeconomic", "svi_household_characteristics",
     "svi_racial_ethnic_minority", "svi_housing_transportation",
     "dominant_svi_theme"]
].copy()
_show.columns = [
    "county", "svi_overall",
    "socioec", "hh_char", "race_eth", "housing_transp", "dominant_theme"
]
pd.set_option("display.float_format", "{:.3f}".format)
print(_show.to_string(index=False))

# ── Notable counties for chart ────────────────────────────────────────────────
# Top-5 by svi_overall + zero-physician counties + high-rate outliers
NOTABLE = [
    "Imperial County", "Merced County", "Fresno County",
    "Kings County", "Tulare County", "Kern County",
    "San Francisco County", "Marin County",
    "Alpine County", "Sierra County",
    "Los Angeles County",
]
notable_df = county_dominant_svi_theme[
    county_dominant_svi_theme["county_name"].isin(NOTABLE)
].copy().sort_values("svi_overall", ascending=True)
short_names = notable_df["county_name"].str.replace(" County", "", regex=False).tolist()

# ── Horizontal stacked dot / grouped bar chart ────────────────────────────────
fig_themes_notable, ax = plt.subplots(figsize=(12, 6))
fig_themes_notable.patch.set_facecolor(BG)

y_pos = np.arange(len(notable_df))
bar_h = 0.18
offsets = [-1.5, -0.5, 0.5, 1.5]

for i, (col, off) in enumerate(zip(THEME_COLS, offsets)):
    vals = notable_df[col].values
    bars = ax.barh(
        y_pos + off * bar_h, vals, height=bar_h,
        color=THEME_COLORS[col], alpha=0.82,
        label=THEME_LABELS[col]
    )

ax.set_yticks(y_pos)
ax.set_yticklabels(short_names, fontsize=8)
ax.set_xlabel("SVI theme percentile (CA-specific, 2022) — 1.0 = most vulnerable", fontsize=9)
ax.set_title(
    "SVI Theme Profiles — Notable California Counties (2022)\n"
    "Each bar shows the percentile rank on one theme; "
    "dominant theme is the longest bar per county",
    color=TXT, fontsize=10
)
ax.axvline(0.5, color=YLW, lw=1, ls="--", alpha=0.6)
ax.legend(facecolor=BG, edgecolor=TXTS, labelcolor=TXT, fontsize=8,
          loc="lower right")
ax.set_xlim(0, 1.05)
fig_themes_notable.tight_layout()
