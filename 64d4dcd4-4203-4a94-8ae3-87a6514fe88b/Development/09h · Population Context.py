import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BG = "#1D1D20"; TXT = "#fbfbff"; TXTS = "#909094"
COR = "#FF9F9B"; BLUE = "#A1C9F4"; GRN = "#8DE5A1"; LAV = "#D0BBFF"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG,
    "text.color": TXT, "axes.labelcolor": TXT,
    "xtick.color": TXT, "ytick.color": TXT,
    "axes.edgecolor": TXTS, "grid.color": TXTS,
    "grid.alpha": 0.25,
})

df = county_quadrants.copy()   # from 09c; includes quadrant assignments
total_pop   = df["ahrf_population_2022"].sum()
total_counties = len(df)

# ── Quadrant population summary ───────────────────────────────────────────────
quad_pop = (
    df.groupby("quadrant")
    .agg(
        n_counties    = ("county_fips",         "count"),
        total_pop     = ("ahrf_population_2022", "sum"),
        median_rate   = ("primary_care_physicians_per_10000", "median"),
        median_svi    = ("svi_overall", "median"),
    )
    .reset_index()
)
quad_pop["pct_counties"] = quad_pop["n_counties"] / total_counties * 100
quad_pop["pct_population"] = quad_pop["total_pop"] / total_pop * 100
quad_pop = quad_pop.sort_values("quadrant")

# ── HPSA population summary ───────────────────────────────────────────────────
hpsa_pop_yes = df[df["has_current_geo_population_hpsa"] == True]["ahrf_population_2022"].sum()
hpsa_pop_no  = df[df["has_current_geo_population_hpsa"] == False]["ahrf_population_2022"].sum()
hpsa_cnt_yes = df["has_current_geo_population_hpsa"].sum()

# ── Print results ─────────────────────────────────────────────────────────────
print("=" * 80)
print("09h · POPULATION CONTEXT")
print(f"  Total CA population (AHRF 2022): {total_pop:>13,.0f}")
print(f"  Total counties                 : {total_counties}")
print("=" * 80)

print("\n── Quadrant breakdown: county count vs population ───────────────────────")
print(f"  {'Quadrant':<48} {'#Cty':>4}  {'%Cty':>5}  {'Population':>12}  {'%Pop':>5}  {'Med SVI':>7}  {'Med Rate':>8}")
print("  " + "-" * 96)
for _, r in quad_pop.iterrows():
    print(f"  {r['quadrant']:<48} {r['n_counties']:>4.0f}  {r['pct_counties']:>5.1f}%  "
          f"{r['total_pop']:>12,.0f}  {r['pct_population']:>5.1f}%  "
          f"{r['median_svi']:>7.3f}  {r['median_rate']:>8.2f}")

q1_row = quad_pop[quad_pop["quadrant"].str.startswith("Q1")].iloc[0]
print(f"\n── High Vulnerability / Low Provider Access (Q1) ────────────────────────")
print(f"  Counties    : {q1_row['n_counties']:.0f} ({q1_row['pct_counties']:.1f}% of 58)")
print(f"  Population  : {q1_row['total_pop']:,.0f} ({q1_row['pct_population']:.1f}% of CA)")

print(f"\n── Current geo/population HPSA population ───────────────────────────────")
print(f"  Counties with active geo/pop HPSA : {hpsa_cnt_yes} ({hpsa_cnt_yes/total_counties*100:.1f}%)")
print(f"  Population in HPSA counties       : {hpsa_pop_yes:,.0f} ({hpsa_pop_yes/total_pop*100:.1f}% of CA)")
print(f"  Population NOT in HPSA counties   : {hpsa_pop_no:,.0f} ({hpsa_pop_no/total_pop*100:.1f}% of CA)")

# ── Grouped bar chart: county % vs population % per quadrant ─────────────────
short_labels = [
    "Q1: High Vuln\nLow Access",
    "Q2: High Vuln\nHigh Access",
    "Q3: Low Vuln\nLow Access",
    "Q4: Low Vuln\nHigh Access",
]
_pct_cty = quad_pop["pct_counties"].values
_pct_pop = quad_pop["pct_population"].values
_x = np.arange(4)

fig_pop_context, ax = plt.subplots(figsize=(10, 5))
fig_pop_context.patch.set_facecolor(BG)

w = 0.35
ax.bar(_x - w/2, _pct_cty, width=w, color=BLUE, alpha=0.85, label="% of 58 counties")
ax.bar(_x + w/2, _pct_pop, width=w, color=COR,  alpha=0.85, label="% of CA population")

ax.set_xticks(_x)
ax.set_xticklabels(short_labels, fontsize=8)
ax.set_ylabel("Percentage (%)", fontsize=9)
ax.set_title(
    "Quadrant Share: County Count vs Population (2022)\n"
    "A county view and a resident view can lead to different planning conclusions",
    color=TXT, fontsize=10
)
ax.legend(facecolor=BG, edgecolor=TXTS, labelcolor=TXT, fontsize=9)
ax.axhline(25, color=TXTS, lw=0.8, ls=":", alpha=0.5)
fig_pop_context.tight_layout()

# ── Interpretation ────────────────────────────────────────────────────────────
print("""
── County-based vs resident-based planning perspectives ─────────────────────

  County-based view: each of the 58 counties carries equal weight.
  Favors attention to rural and small-population counties.
  A county like Imperial (pop ~179k) and a county like Alpine (pop ~1,190)
  are treated as equally important units of analysis.

  Resident-based view: each resident carries equal weight.
  Favors attention to large, densely populated counties.
  Q1 (High Vuln / Low Access) holds ~31% of counties but only ~28% of residents,
  because several Q1 counties are mid-sized (Riverside, San Joaquin, Stanislaus)
  rather than the most populous in the state.

  Planning implication:
  • A program focused on NUMBER OF PEOPLE affected would prioritize larger counties
    even if their provider rates are close to the median.
  • A program focused on GEOGRAPHIC COVERAGE or EQUITY ACROSS PLACES would weigh
    smaller, more isolated counties more heavily.
  • Neither view is wrong — both should be reported and the audience should decide
    which framing best matches their program goals.

  Note: Alpine and Sierra (zero-physician, tiny populations) sit in Q3 (Low Vuln)
  because their overall SVI is below the median — yet they are the most extreme
  access-gap cases by physician rate. They reinforce why no single threshold or
  view captures the full picture.
""")
