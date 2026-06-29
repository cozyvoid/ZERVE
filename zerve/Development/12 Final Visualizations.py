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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Top 15 counties, balanced scenario
# ═══════════════════════════════════════════════════════════════════════════════
top15 = bpr.head(15).sort_values("priority_balanced")
_names = [n.replace(" County", "") for n in top15["county_name"]]
_scores = top15["priority_balanced"].values
_hpsa = top15["has_current_geo_population_hpsa"].values
_colors = [GRN if h else ORG for h in _hpsa]

fig1, ax1 = plt.subplots(figsize=(9, 6))
bars = ax1.barh(_names, _scores, color=_colors, height=0.65, edgecolor="none")
for bar, score in zip(bars, _scores):
    ax1.text(score + 0.005, bar.get_y() + bar.get_height() / 2,
             f"{score:.3f}", va="center", ha="left", color=TXT, fontsize=7.5)
ax1.set_xlim(0, 1.08)
ax1.set_xlabel("Balanced Priority Score  [0–1, exploratory]", color=TXT)
ax1.set_title("Top 15 Counties — Balanced Priority Score (Exploratory)\n"
              "50% Provider Scarcity  +  50% Overall SVI  |  2022 data", color=TXT)
ax1.axvline(0.5, color=TXTS, linewidth=0.7, linestyle="--")
ax1.text(0.502, -0.6, "Score = 0.5", color=TXTS, fontsize=7)
p1 = mpatches.Patch(color=GRN, label="Current geo/pop HPSA")
p2 = mpatches.Patch(color=ORG, label="No current geo/pop HPSA")
ax1.legend(handles=[p1, p2], fontsize=8, facecolor=BG,
           labelcolor=TXT, edgecolor=TXTS, loc="lower right")
_style(fig1, ax1)
fig1.tight_layout()

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Score-component comparison top-10
# ═══════════════════════════════════════════════════════════════════════════════
top10 = bpr.head(10).sort_values("priority_balanced")
_n10 = [n.replace(" County", "") for n in top10["county_name"]]
_ps10 = top10["provider_scarcity"].values * 0.50
_sv10 = top10["svi_overall"].values * 0.50
y10 = np.arange(len(_n10))

fig2, ax2 = plt.subplots(figsize=(9, 5.5))
ax2.barh(y10, _ps10, color=BLUE, height=0.55, label="Provider Scarcity × 0.50", edgecolor="none")
ax2.barh(y10, _sv10, left=_ps10, color=LAV, height=0.55, label="SVI Overall × 0.50", edgecolor="none")
ax2.set_yticks(y10)
ax2.set_yticklabels(_n10, fontsize=9)
ax2.set_xlabel("Component Contribution to Balanced Score", color=TXT)
ax2.set_title("Score Components — Top 10 Counties (Balanced Scenario, Exploratory)\n"
              "Stacked bars show each component's weighted contribution", color=TXT)
ax2.legend(fontsize=8, facecolor=BG, labelcolor=TXT, edgecolor=TXTS)
_style(fig2, ax2)
fig2.tight_layout()

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Rank movement across scenarios (bump chart for top 20 by mean rank)
# ═══════════════════════════════════════════════════════════════════════════════
ps_full = county_priority_scores.copy()
ps_full = ps_full.merge(rank_stability_summary[["county_fips","rank_mean"]], on="county_fips")
top20 = ps_full.nsmallest(20, "rank_mean")

SCEN_LABELS = ["Balanced", "Access-\nFocused", "Equity-\nFocused", "Empirical\nThemes"]
RANK_COLS_LIST = ["rank_balanced","rank_access_focused","rank_equity_focused","rank_empirical_themes"]

fig3, ax3 = plt.subplots(figsize=(9, 7))
cmap = plt.cm.get_cmap("tab20", len(top20))
for idx, (_, row) in enumerate(top20.iterrows()):
    ranks = [row[c] for c in RANK_COLS_LIST]
    short = row["county_name"].replace(" County", "")
    ax3.plot(range(4), ranks, marker="o", markersize=5,
             color=cmap(idx), alpha=0.85, linewidth=1.5)
    # Label at start and end
    ax3.text(-0.08, ranks[0], short, ha="right", va="center",
             color=cmap(idx), fontsize=6.5)
    ax3.text(3.08, ranks[3], short, ha="left", va="center",
             color=cmap(idx), fontsize=6.5)

ax3.set_xticks(range(4))
ax3.set_xticklabels(SCEN_LABELS, fontsize=9)
ax3.invert_yaxis()  # rank 1 at top
ax3.set_ylabel("Rank  (1 = highest exploratory priority)", color=TXT)
ax3.set_title("Rank Movement Across Scenarios — Top 20 Counties by Mean Rank\n"
              "(Exploratory — all four weighting scenarios)", color=TXT)
ax3.axhline(14, color=TXTS, linewidth=0.6, linestyle="--")
ax3.text(0.01, 14.5, "Top quartile boundary", color=TXTS, fontsize=7)
_style(fig3, ax3)
ax3.set_xlim(-1.2, 4.2)
fig3.tight_layout()

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Balanced score vs county population (bubble)
# ═══════════════════════════════════════════════════════════════════════════════
_pop  = bpr["ahrf_population_2022"].values
_scr  = bpr["priority_balanced"].values
_hpsa_flag = bpr["has_current_geo_population_hpsa"].values
_clr  = [GRN if h else ORG for h in _hpsa_flag]
_pop_log = np.log10(np.maximum(_pop, 1))
_sz = ((_pop_log - _pop_log.min()) / (_pop_log.max() - _pop_log.min()) * 220 + 30)

fig4, ax4 = plt.subplots(figsize=(9, 6))
ax4.scatter(_pop_log, _scr, s=_sz, c=_clr, alpha=0.75, edgecolors="none")
# Annotate notable counties
LABEL_SET = {"Imperial County","Kern County","Merced County","Los Angeles County",
             "San Francisco County","Marin County","Alpine County","Sierra County",
             "Glenn County","Riverside County"}
for _, row in bpr.iterrows():
    if row["county_name"] in LABEL_SET:
        short = row["county_name"].replace(" County","")
        ax4.annotate(short, (np.log10(max(row["ahrf_population_2022"],1)),
                             row["priority_balanced"]),
                     fontsize=6.5, color=TXT,
                     xytext=(5,3), textcoords="offset points")

# Pre-compute x-tick labels as strings — no FuncFormatter
_tick_vals = [1e3, 1e4, 1e5, 1e6, 1e7]
_tick_strs = ["1K", "10K", "100K", "1M", "10M"]
ax4.set_xticks([np.log10(v) for v in _tick_vals])
ax4.set_xticklabels(_tick_strs, fontsize=8)
ax4.set_xlabel("County Population — AHRF 2022 (log scale)", color=TXT)
ax4.set_ylabel("Balanced Priority Score (Exploratory)", color=TXT)
ax4.set_title("Balanced Priority Score vs County Population\n"
              "Bubble size ~ population; color = HPSA status (green = designated)", color=TXT)
ax4.axhline(bpr["priority_balanced"].median(), color=TXTS, linewidth=0.7, linestyle="--")
ax4.text(3.05, bpr["priority_balanced"].median()+0.01, "Median score", color=TXTS, fontsize=7)
p1 = mpatches.Patch(color=GRN, label="Current geo/pop HPSA")
p2 = mpatches.Patch(color=ORG, label="No current HPSA")
ax4.legend(handles=[p1,p2], fontsize=8, facecolor=BG, labelcolor=TXT, edgecolor=TXTS)
_style(fig4, ax4)
fig4.tight_layout()

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Balanced score by HPSA group (boxplot)
# ═══════════════════════════════════════════════════════════════════════════════
hpsa_yes_scores = bpr.loc[ bpr["has_current_geo_population_hpsa"], "priority_balanced"].values
hpsa_no_scores  = bpr.loc[~bpr["has_current_geo_population_hpsa"], "priority_balanced"].values

fig5, ax5 = plt.subplots(figsize=(7, 5))
bp = ax5.boxplot(
    [hpsa_yes_scores, hpsa_no_scores],
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
    [f"Geo/Pop HPSA\n(n={len(hpsa_yes_scores)})",
     f"No Geo/Pop HPSA\n(n={len(hpsa_no_scores)})"],
    fontsize=9
)
ax5.set_ylabel("Balanced Priority Score (Exploratory)", color=TXT)
ax5.set_title("Balanced Score Distribution by Current Geo/Pop HPSA Status\n"
              "Current HPSA = 2026 snapshot; score = 2022 historical data", color=TXT)
ax5.set_ylim(0, 1.05)
_style(fig5, ax5)
fig5.tight_layout()

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Provider scarcity vs SVI; balanced score as color
# ═══════════════════════════════════════════════════════════════════════════════
_ps  = bpr["provider_scarcity"].values
_svi = bpr["svi_overall"].values
_sc  = bpr["priority_balanced"].values
_pop = bpr["ahrf_population_2022"].values
_sz6 = (np.log10(np.maximum(_pop, 1)) - 3) * 25 + 20

fig6, ax6 = plt.subplots(figsize=(9, 6.5))
sc = ax6.scatter(_ps, _svi, c=_sc, s=_sz6, cmap="YlOrRd", alpha=0.85,
                 vmin=0, vmax=1, edgecolors="none")
cbar = fig6.colorbar(sc, ax=ax6, pad=0.02)
cbar.set_label("Balanced Priority Score (Exploratory)", color=TXT, fontsize=9)
cbar.ax.yaxis.set_tick_params(color=TXT)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TXT, fontsize=8)
cbar.outline.set_edgecolor(TXTS)

LABEL6 = {"Imperial County","Kern County","Merced County","Glenn County",
          "Yuba County","Colusa County","Alpine County","Sierra County",
          "San Francisco County","Marin County"}
for _, row in bpr.iterrows():
    if row["county_name"] in LABEL6:
        short = row["county_name"].replace(" County","")
        ax6.annotate(short, (row["provider_scarcity"], row["svi_overall"]),
                     fontsize=6.5, color=TXT, xytext=(4,3),
                     textcoords="offset points")

med_ps  = bpr["provider_scarcity"].median()
med_svi = bpr["svi_overall"].median()
ax6.axvline(med_ps,  color=TXTS, linewidth=0.8, linestyle="--")
ax6.axhline(med_svi, color=TXTS, linewidth=0.8, linestyle="--")
ax6.text(med_ps+0.01, 0.03, "Median\nscarcity", color=TXTS, fontsize=6.5)
ax6.text(0.02, med_svi+0.02, "Median SVI", color=TXTS, fontsize=6.5)

ax6.set_xlabel("Provider Scarcity Percentile  [0=most available · 1=most scarce]", color=TXT)
ax6.set_ylabel("Overall SVI Percentile  [0=lowest · 1=highest vulnerability]", color=TXT)
ax6.set_title("Provider Scarcity vs Social Vulnerability\n"
              "Color = Balanced Priority Score  |  Size ~ Population  |  Exploratory", color=TXT)
_style(fig6, ax6)
fig6.tight_layout()

print("=" * 60)
print("17 · ALL 6 VISUALIZATIONS RENDERED")
print("=" * 60)
print("  fig1 — Top 15 balanced bar chart")
print("  fig2 — Score component stacked bar (top 10)")
print("  fig3 — Rank movement bump chart (top 20 by mean rank)")
print("  fig4 — Score vs population bubble chart")
print("  fig5 — Score distribution by HPSA group boxplot")
print("  fig6 — Provider scarcity vs SVI, score as color")
print("\n  ⚠  All charts label scores as EXPLORATORY.")
print("  ⚠  HPSA status reflects 2026 current snapshot, not 2022 data.")
