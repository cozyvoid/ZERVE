# Final Findings and Responsible Use

> **Scope of this milestone:** Exploratory county-level prioritization framework for California.  
> All scores are relative to California's 58 counties and do not represent official resource-allocation decisions.  
> Data sources: CDC SVI 2022, HRSA AHRF 2022, HRSA HPSA snapshot 2026-06-25.

---

## 1. Counties consistently ranked highly across all four scenarios

**Imperial County** ranks **#1 under every scenario** (balanced score 0.974) — the only county with zero rank movement. Its extreme provider scarcity (2.74 physicians / 10k, among the lowest in the state) combined with the highest overall SVI in California (1.000) produces this unambiguous result regardless of weighting.

**Three counties are in the top 5 under all four scenarios:** Imperial, Kings, and Merced.  
**Nine counties appear in the top 10 under all four scenarios:** Imperial, Merced, Kings, Yuba, Glenn, Kern, Tulare, Lake, and Colusa.  
**Ten counties remain in the top quartile under all four scenarios: Imperial, Merced, Kings, Yuba, Glenn, Kern, Tulare, Lake, Colusa, and Madera.
---

## 2. Counties whose ranks depend heavily on the weighting choice

**Thirteen counties show a rank range ≥ 10 across scenarios**, meaning their placement shifts by 10 or more positions depending on whether provider scarcity or social vulnerability is weighted higher:

| County | Rank range | Pattern |
|---|---|---|
| Alpine, Sierra | 19 | High scarcity but moderate SVI; rank rises sharply in access-focused scenarios |
| Monterey | 17 | Strong racial/ethnic minority SVI not captured in empirical-theme scenario |
| Fresno | 16 | Moderate on both dimensions; sensitive to balance point |
| Calaveras, Santa Barbara | 15 | Flip between mid-tier positions |
| Los Angeles | 14 | Large population, moderate scores; Equity scenario pushes it higher |

Planners should treat these counties as requiring individual review rather than relying on a single rank.

---

## 3. Scenario agreement and divergence

All four scenarios are **highly correlated** (all Spearman r > 0.89, p < 0.001). The **top-10 Jaccard similarity is 0.82–1.00**: the balanced, equity, and empirical-theme scenarios share an **identical top-10 county set**; the access-focused scenario shares 9 of 10 with each of the others.

**Practical conclusion:** The three scenarios using `svi_overall` produce materially similar conclusions for the top tier. The main divergence is in the middle of the ranking, where the access-focused scenario elevates counties with extreme physician scarcity but moderate SVI (Glenn, Yuba) relative to counties with high SVI but moderate scarcity.

---

## 4. Empirical-theme scenario vs overall-SVI scenarios

The empirical-theme scenario (50% provider scarcity + 30% socioeconomic SVI + 20% household SVI) produces rankings very similar to the balanced and equity-focused scenarios (Spearman r ≥ 0.96 with both). It **does not materially change the top-10 composition** — the same core counties appear at the top. The scenario's main effect is to slightly de-emphasize the racial/ethnic minority and housing/transportation SVI dimensions relative to the overall composite. 

> ⚠ The empirical correlation between those sub-themes and physician rates was observed in a single cross-section of 58 counties. This is not sufficient evidence to treat the empirical-theme scenario as a more valid formula. It is retained as a robustness check only.

---

## 5. Residents represented in higher-priority counties

| Tier | Counties | Population | % of CA |
|---|---|---|---|
| Top 5 (balanced) | 5 | 1,622,126 | 4.2% |
| Top 10 (balanced) | 10 | 2,378,370 | 6.1% |
| Top quartile (balanced) | 14 | 2,517,621 | 6.5% |
| Current geo/pop HPSA designated | 34 | 27,878,795 | 71.4% |

The county-count framing identifies predominantly **smaller, rural, and agricultural counties** in the top tier. The population framing shows these counties are home to about 2.4–2.5 million residents. Population is retained as a separate planning dimension rather than entering the score, so that small rural counties with extreme need are not displaced by large urban counties with moderate scores.

---

## 6. HPSA alignment with historical score

**Category A (high historical priority + current HPSA):** 10 counties — the majority of the top quartile is HPSA-designated, indicating general alignment.

**Category B (high historical priority, NO current geo/pop HPSA):** 4 counties — **Yuba, Colusa, Madera, and Lassen**. These counties score in the top 14 historically but lack an active geographic/population HPSA. This warrants closer attention, though possible explanations include: sub-county provider distribution that satisfies HPSA adequacy criteria at the designation level; different provider types included in HPSA criteria beyond AHRF physician count; near-threshold positions; or the 4-year gap between the 2022 data and the 2026 HPSA snapshot.

**Category C (current HPSA, lower historical priority):** 24 counties — these designations likely reflect sub-county geographic areas, specific population-group HPSAs (e.g. migrant workers, low-income populations), or earlier designation criteria. They should not be dismissed; they indicate the HPSA system captures dimensions the county-level physician-count measure does not.

---

## 7. Zero-provider rural counties

**Alpine and Sierra counties** both have zero recorded primary-care physicians in 2022. They receive the **highest possible provider_scarcity value (0.991)** — tied by construction since the rank-based method assigns average ranks. Their balanced scores place them at ranks 14 and 22 respectively, reflecting their moderate overall SVI scores (0.474 and 0.482). They appear in the top quartile under the access-focused scenario (ranks 14 and 15) but move lower under equity-focused weighting.

> Planning note: with populations of ~1,190 and ~3,217, these counties are micro-populations. Resource-planning conclusions for these counties should be informed by context (proximity to neighboring counties, travel time to care, telehealth capacity) that is not captured in this county-level framework.

---

## 8. Population remains separate from the primary score

Incorporating population into the score would systematically elevate large counties (Los Angeles, Riverside, San Bernardino) above the rural/agricultural counties that dominate the top tier on the access-scarcity and vulnerability dimensions. The 2×2 planning classification in Block 15 distinguishes **intensity of need** from **scale of impact** without blending the two into a single number. Kern (rank 3, pop 916k), Tulare (rank 6, pop 478k), and Riverside (rank 23, pop 2.5M) are the primary "higher need / larger population" counties warranting attention at scale.

---

## 9. Scoring framework limitations

The following limitations apply to all four scenarios and must be understood before using this framework to inform planning decisions:

1. **Relative, not absolute:** Scores rank counties within California only. A county ranked #14 may still have substantial unmet need.
2. **County-level ecological analysis:** Within-county variation in provider distribution, access, and vulnerability is not captured. Rural pockets within large counties may be underserved even if the county-level rate appears adequate.
3. **Physician count only:** The AHRF measure counts primary-care physicians. Nurse practitioners, physician assistants, federally qualified health centers (FQHCs), rural health clinics, and telehealth providers are not reflected.
4. **No appointment availability:** A physician being counted does not imply they accept new patients, accept Medicaid/Medi-Cal, or have available appointment capacity.
5. **No cross-county travel:** Residents in border counties may access providers in adjacent counties; this is not modeled.
6. **Single data vintage:** 2022 data. Provider availability and population vulnerability change over time.
7. **Ecological fallacy risk:** County-level associations between SVI and physician rates do not imply that the most vulnerable individuals within a county are the ones experiencing the greatest access barriers.
8. **HPSA temporal gap:** The HPSA comparison uses a 2026 snapshot against 2022 historical data. Designation changes between 2022 and 2026 affect the alignment analysis.
9. **Weighting is arbitrary:** The 50/50, 65/35, and 35/65 weight splits are illustrative. No empirical test can determine the "correct" weight from this data alone.

---

## 10. Responsible use

> This framework is an **exploratory analytical tool** intended to support further investigation and planning conversations. It is **not** a validated clinical instrument, an official shortage-area determination, a funding formula, or a causal model of healthcare access. Rankings should be used to **identify areas for closer review**, not to automatically allocate resources or override local knowledge and program-specific criteria.

**milestone4_findings** is documented in the analytical blocks above across `county_priority_scores`, `scenario_rankings`, `rank_stability_summary`, `balanced_priority_results`, `population_impact_context`, and `hpsa_alignment_summary`.
