import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Palette (Zerve design system) ─────────────────────────────────────────────
BG   = "#1D1D20"; TXT  = "#fbfbff"; TXTS = "#909094"
BLUE = "#A1C9F4"; ORG  = "#FFB482"; GRN  = "#8DE5A1"
COR  = "#FF9F9B"; LAV  = "#D0BBFF"; YLW  = "#ffd400"
TEAL = "#1F77B4"; PRP  = "#9467BD"

def _style(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(TXTS)
    ax.tick_params(colors=TXT, labelsize=8)
    ax.xaxis.label.set_color(TXT)
    ax.yaxis.label.set_color(TXT)
    ax.title.set_color(TXT)

bpr = balanced_priority_results.copy().sort_values("rank_balanced")

# Merge all 4 scenario scores into bpr from county_priority_scores (join on county_name)
_SCEN_COLS = ["priority_balanced", "priority_access_focused",
              "priority_equity_focused", "priority_empirical_themes"]
bpr = bpr.merge(
    county_priority_scores[["county_name"] + _SCEN_COLS],
    on="county_name", how="left", suffixes=("", "_cps")
)
# Use _cps columns where the original is missing
for _c in _SCEN_COLS:
    if _c + "_cps" in bpr.columns:
        bpr[_c] = bpr[_c].combine_first(bpr[_c + "_cps"])
        bpr.drop(columns=[_c + "_cps"], inplace=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — HORIZONTAL RANKED BAR CHART: Top 15 counties, balanced scenario
# ═══════════════════════════════════════════════════════════════════════════════
top15  = bpr.head(15).sort_values("priority_balanced")
_names  = [n.replace(" County", "") for n in top15["county_name"]]
_scores = top15["priority_balanced"].values
_hpsa   = top15["has_current_geo_population_hpsa"].values
_colors = [GRN if h else ORG for h in _hpsa]
_ranks  = top15["rank_balanced"].values

fig1, ax1 = plt.subplots(figsize=(9, 6))
bars = ax1.barh(_names, _scores, color=_colors, height=0.65, edgecolor="none")
for bar, score, rank in zip(bars, _scores, _ranks):
    ax1.text(score + 0.005, bar.get_y() + bar.get_height() / 2,
             f"{score:.3f}  (#{rank})",
             va="center", ha="left", color=TXT, fontsize=7.5)
ax1.set_xlim(0, 1.12)
ax1.set_xlabel("Balanced Priority Score  [0–1, exploratory]", color=TXT)
ax1.set_title(
    "Top 15 Counties — Balanced Priority Score (Exploratory)\n"
    "50% Provider Scarcity  +  50% Overall SVI  |  2022 data", color=TXT)
ax1.axvline(0.5, color=TXTS, linewidth=0.7, linestyle="--")
ax1.text(0.502, -0.6, "Score = 0.5", color=TXTS, fontsize=7)
p1 = mpatches.Patch(color=GRN, label="Current geo/pop HPSA")
p2 = mpatches.Patch(color=ORG, label="No current geo/pop HPSA")
ax1.legend(handles=[p1, p2], fontsize=8, facecolor=BG,
           labelcolor=TXT, edgecolor=TXTS, loc="lower right")
for sp in ["top", "right"]:
    ax1.spines[sp].set_visible(False)
ax1.grid(axis="x", color=TXTS, alpha=0.18, linewidth=0.6)
ax1.grid(axis="y", visible=False)
_style(fig1, ax1)
fig1.tight_layout()
plt.close("all")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — SCENARIO-COMPARISON VISUALIZATION: Top 15 × 4 scenarios (grouped bars)
# ═══════════════════════════════════════════════════════════════════════════════
_SCEN_NAMES  = ["Balanced", "Access-focused", "Equity-focused", "Empirical themes"]
_SCEN_COLORS = [BLUE, ORG, GRN, LAV]

# Top-15 by balanced rank; reverse so rank 1 at top
_sc15 = bpr.head(15).sort_values("rank_balanced", ascending=False).reset_index(drop=True)
_cn15 = [n.replace(" County", "") for n in _sc15["county_name"]]
_n15  = len(_sc15)
_bar_h = 0.18
_y_base = np.arange(_n15)

fig2, ax2 = plt.subplots(figsize=(11, 7.5))
fig2.patch.set_facecolor(BG)
ax2.set_facecolor(BG)

for j, (col, lbl, clr) in enumerate(zip(_SCEN_COLS, _SCEN_NAMES, _SCEN_COLORS)):
    _offset = (_bar_h + 0.02) * (j - 1.5)
    _vals   = _sc15[col].values
    ax2.barh(_y_base + _offset, _vals, height=_bar_h, color=clr, alpha=0.88,
             edgecolor="none", label=lbl)

ax2.set_yticks(_y_base)
ax2.set_yticklabels(_cn15, fontsize=8.5, color=TXT)
ax2.set_xlabel("Priority Score  [0–1, exploratory]", color=TXT, fontsize=9)
ax2.set_title(
    "Scenario Comparison — Top 15 Counties Across All Four Weighting Scenarios\n"
    "Grouped bars: each county shows four scores (one per scenario). Width = score.",
    color=TXT, fontsize=10)
ax2.set_xlim(0, 1.05)
ax2.axvline(0.5, color=TXTS, linewidth=0.7, linestyle="--")
ax2.text(0.502, -0.7, "0.5", color=TXTS, fontsize=7)
ax2.legend(fontsize=8, facecolor=BG, labelcolor=TXT, edgecolor=TXTS,
           loc="lower right", ncol=2)
for sp in ["top", "right"]:
    ax2.spines[sp].set_visible(False)
ax2.spines["bottom"].set_color(TXTS)
ax2.spines["left"].set_color(TXTS)
ax2.grid(axis="x", color=TXTS, alpha=0.15, linewidth=0.6)
ax2.grid(axis="y", visible=False)
ax2.tick_params(colors=TXT)
fig2.tight_layout()
plt.close("all")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — BUMP/RANK-MOVEMENT CHART: Top 20 by mean rank across scenarios
# ═══════════════════════════════════════════════════════════════════════════════
ps_full = county_priority_scores.copy()
ps_full = ps_full.merge(rank_stability_summary[["county_fips", "rank_mean"]], on="county_fips")
top20   = ps_full.nsmallest(20, "rank_mean")

SCEN_LABELS    = ["Balanced", "Access-\nFocused", "Equity-\nFocused", "Empirical\nThemes"]
RANK_COLS_LIST = ["rank_balanced", "rank_access_focused",
                  "rank_equity_focused", "rank_empirical_themes"]

fig3, ax3 = plt.subplots(figsize=(9, 7))
fig3.patch.set_facecolor(BG)
ax3.set_facecolor(BG)
_cmap = plt.cm.get_cmap("tab20", len(top20))

for idx, (_, row) in enumerate(top20.iterrows()):
    ranks = [row[c] for c in RANK_COLS_LIST]
    short = row["county_name"].replace(" County", "")
    ax3.plot(range(4), ranks, marker="o", markersize=5,
             color=_cmap(idx), alpha=0.85, linewidth=1.5)
    ax3.text(-0.08, ranks[0], short, ha="right", va="center",
             color=_cmap(idx), fontsize=6.5)
    ax3.text(3.08, ranks[3], short, ha="left", va="center",
             color=_cmap(idx), fontsize=6.5)

ax3.set_xticks(range(4))
ax3.set_xticklabels(SCEN_LABELS, fontsize=9, color=TXT)
ax3.invert_yaxis()
ax3.set_ylabel("Rank  (1 = highest exploratory priority)", color=TXT)
ax3.set_title(
    "Rank Movement Across Scenarios — Top 20 Counties by Mean Rank\n"
    "(Exploratory — all four weighting scenarios)", color=TXT)
ax3.axhline(14, color=TXTS, linewidth=0.6, linestyle="--")
ax3.text(0.01, 14.5, "Top quartile boundary", color=TXTS, fontsize=7)
ax3.set_xlim(-1.2, 4.2)
ax3.tick_params(colors=TXT)
for spine in ax3.spines.values():
    spine.set_color(TXTS)
ax3.grid(axis="y", color=TXTS, alpha=0.12, linewidth=0.5)
ax3.grid(axis="x", visible=False)
fig3.tight_layout()
plt.close("all")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — SCATTERPLOT: Balanced priority score vs county population
# ═══════════════════════════════════════════════════════════════════════════════
_pop_raw = bpr["ahrf_population_2022"].values
_scr     = bpr["priority_balanced"].values
_hpsa_f  = bpr["has_current_geo_population_hpsa"].values
_pop_log = np.log10(np.maximum(_pop_raw, 1))

LABEL_SET4 = {"Imperial County", "Kern County", "Merced County",
              "Los Angeles County", "San Francisco County", "Marin County",
              "Alpine County", "Sierra County", "Glenn County", "Riverside County"}

fig4, ax4 = plt.subplots(figsize=(9, 6))
fig4.patch.set_facecolor(BG)
ax4.set_facecolor(BG)
ax4.scatter(_pop_log[_hpsa_f],  _scr[_hpsa_f],  s=55, c=GRN, alpha=0.80,
            edgecolors="none", label="Current geo/pop HPSA", zorder=3)
ax4.scatter(_pop_log[~_hpsa_f], _scr[~_hpsa_f], s=55, c=ORG, alpha=0.80,
            edgecolors="none", label="No current HPSA", zorder=3)

for _, row in bpr.iterrows():
    if row["county_name"] in LABEL_SET4:
        short = row["county_name"].replace(" County", "")
        ax4.annotate(short,
                     (np.log10(max(row["ahrf_population_2022"], 1)), row["priority_balanced"]),
                     fontsize=6.5, color=TXT, xytext=(5, 3), textcoords="offset points")

_tick_vals4 = [1e3, 1e4, 1e5, 1e6, 1e7]
ax4.set_xticks([np.log10(v) for v in _tick_vals4])
ax4.set_xticklabels(["1K", "10K", "100K", "1M", "10M"], fontsize=8)
ax4.set_xlabel("County Population — AHRF 2022 (log scale)", color=TXT)
ax4.set_ylabel("Balanced Priority Score (Exploratory)", color=TXT)
ax4.set_title(
    "Balanced Priority Score vs County Population\n"
    "Color = HPSA status  |  No strong population-score relationship by design",
    color=TXT)
ax4.axhline(bpr["priority_balanced"].median(), color=TXTS, linewidth=0.7, linestyle="--")
ax4.text(3.05, bpr["priority_balanced"].median() + 0.01, "Median score", color=TXTS, fontsize=7)
ax4.legend(fontsize=8, facecolor=BG, labelcolor=TXT, edgecolor=TXTS)
for sp in ["top", "right"]:
    ax4.spines[sp].set_visible(False)
ax4.spines["bottom"].set_color(TXTS)
ax4.spines["left"].set_color(TXTS)
ax4.tick_params(colors=TXT)
ax4.grid(color=TXTS, alpha=0.12, linewidth=0.5)
fig4.tight_layout()
plt.close("all")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — BOXPLOT: Balanced score distribution by HPSA group
# ═══════════════════════════════════════════════════════════════════════════════
_hpsa_yes_scores = bpr.loc[ bpr["has_current_geo_population_hpsa"], "priority_balanced"].values
_hpsa_no_scores  = bpr.loc[~bpr["has_current_geo_population_hpsa"], "priority_balanced"].values

fig5, ax5 = plt.subplots(figsize=(7, 5.5))
fig5.patch.set_facecolor(BG)
ax5.set_facecolor(BG)
bp = ax5.boxplot(
    [_hpsa_yes_scores, _hpsa_no_scores],
    patch_artist=True, widths=0.45,
    medianprops=dict(color=YLW, linewidth=2),
    boxprops=dict(linewidth=1.2),
    whiskerprops=dict(color=TXTS), capprops=dict(color=TXTS),
    flierprops=dict(marker="o", color=ORG, markersize=5, alpha=0.7)
)
bp["boxes"][0].set_facecolor(GRN);  bp["boxes"][0].set_alpha(0.7)
bp["boxes"][1].set_facecolor(ORG);  bp["boxes"][1].set_alpha(0.7)
ax5.set_xticks([1, 2])
ax5.set_xticklabels(
    [f"Geo/Pop HPSA\n(n={len(_hpsa_yes_scores)})",
     f"No Geo/Pop HPSA\n(n={len(_hpsa_no_scores)})"],
    fontsize=9
)
ax5.set_ylabel("Balanced Priority Score (Exploratory)", color=TXT)
ax5.set_title(
    "Balanced Score Distribution by Current Geo/Pop HPSA Status\n"
    "Current HPSA = 2026 snapshot; score = 2022 historical data",
    color=TXT)
ax5.set_ylim(0, 1.05)
for spine in ax5.spines.values():
    spine.set_color(TXTS)
ax5.tick_params(colors=TXT)
ax5.grid(axis="y", color=TXTS, alpha=0.15, linewidth=0.5)
ax5.grid(axis="x", visible=False)
fig5.tight_layout()
plt.close("all")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — SCATTERPLOT: Provider scarcity vs SVI; balanced score as color
# ═══════════════════════════════════════════════════════════════════════════════
_ps6  = bpr["provider_scarcity"].values
_svi6 = bpr["svi_overall"].values
_sc6  = bpr["priority_balanced"].values

LABEL6 = {"Imperial County", "Kern County", "Merced County", "Glenn County",
           "Yuba County", "Colusa County", "Alpine County", "Sierra County",
           "San Francisco County", "Marin County"}

fig6, ax6 = plt.subplots(figsize=(9, 6.5))
fig6.patch.set_facecolor(BG)
ax6.set_facecolor(BG)
sc = ax6.scatter(_ps6, _svi6, c=_sc6, s=60, cmap="YlOrRd", alpha=0.85,
                 vmin=0, vmax=1, edgecolors="none")
cbar = fig6.colorbar(sc, ax=ax6, pad=0.02)
cbar.set_label("Balanced Priority Score (Exploratory)", color=TXT, fontsize=9)
cbar.ax.yaxis.set_tick_params(color=TXT)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TXT, fontsize=8)
cbar.outline.set_edgecolor(TXTS)

for _, row in bpr.iterrows():
    if row["county_name"] in LABEL6:
        short = row["county_name"].replace(" County", "")
        ax6.annotate(short, (row["provider_scarcity"], row["svi_overall"]),
                     fontsize=6.5, color=TXT, xytext=(4, 3), textcoords="offset points")

med_ps  = bpr["provider_scarcity"].median()
med_svi = bpr["svi_overall"].median()
ax6.axvline(med_ps,  color=TXTS, linewidth=0.8, linestyle="--")
ax6.axhline(med_svi, color=TXTS, linewidth=0.8, linestyle="--")
ax6.text(med_ps + 0.01, 0.03, "Median\nscarcity", color=TXTS, fontsize=6.5)
ax6.text(0.02, med_svi + 0.02, "Median SVI", color=TXTS, fontsize=6.5)
ax6.set_xlabel("Provider Scarcity Percentile  [0=most available · 1=most scarce]", color=TXT)
ax6.set_ylabel("Overall SVI Percentile  [0=lowest · 1=highest vulnerability]", color=TXT)
ax6.set_title(
    "Provider Scarcity vs Social Vulnerability\n"
    "Color = Balanced Priority Score  |  Exploratory",
    color=TXT)
for sp in ["top", "right"]:
    ax6.spines[sp].set_visible(False)
ax6.spines["bottom"].set_color(TXTS)
ax6.spines["left"].set_color(TXTS)
ax6.tick_params(colors=TXT)
ax6.grid(color=TXTS, alpha=0.12, linewidth=0.5)
fig6.tight_layout()
plt.close("all")

print("=" * 60)
print("17 · ALL 6 VISUALIZATIONS RENDERED")
print("=" * 60)
print("  fig1 — Horizontal ranked bar chart: top-15 balanced score")
print("  fig2 — Scenario-comparison grouped bar: top-15 × 4 scenarios")
print("  fig3 — Bump/rank-movement chart: top-20 by mean rank")
print("  fig4 — Scatterplot: balanced score vs population")
print("  fig5 — Boxplot: score distribution by HPSA group")
print("  fig6 — Scatterplot: provider scarcity vs SVI (color = priority score)")
print("\n  ⚠  All charts label scores as EXPLORATORY.")
print("  ⚠  HPSA status reflects 2026 current snapshot, not 2022 data.")
