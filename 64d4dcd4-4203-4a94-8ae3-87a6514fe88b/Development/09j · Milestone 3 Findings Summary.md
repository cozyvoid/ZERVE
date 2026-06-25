# 09j · Milestone 3 Findings Summary

**Unit of analysis:** 58 California counties · **Period:** 2022 (SVI + AHRF) · **Current HPSA overlay:** 2026-06-25  
*All findings are descriptive and ecological. No causal claims are made.*

---

## Major descriptive findings

**1. Physician access is highly right-skewed and driven by a few large urban counties.**  
Median physician rate: **7.9 per 10,000** residents (range: 0–24.2). San Francisco (24.2) and Marin (18.2) are extreme upper outliers. Alpine and Sierra Counties have **zero** primary-care physicians — valid data points for genuinely isolated rural counties, not errors. Physician counts are even more skewed; Los Angeles (9,736 PCPs) has more than the bottom ~45 counties combined.

**2. The SVI–physician access association is weak at the composite level but moderate for specific themes.**  
Overall SVI and physician rate: Spearman r = **−0.31** (p = 0.017, *weak*). The socioeconomic theme (r = −0.53) and household-characteristics theme (r = −0.47) show **moderate** negative associations — meaning counties ranking higher on poverty, unemployment, and housing-cost burden, or on age and disability burden, tend to have fewer physicians. The racial/ethnic-minority and housing/transportation themes show **negligible** correlation with physician rates. Excluding Alpine and Sierra strengthens the overall SVI correlation to moderate (r = −0.42), confirming that small zero-physician counties partially attenuate the overall pattern.

**3. 18 counties (31%) fall in the high-vulnerability / low-access quadrant, representing ~6.5 million Californians (17% of the state).**  
This quadrant (Q1) includes both large mid-sized counties — Riverside (2.5M), San Joaquin (793k), Stanislaus (551k) — and intensely vulnerable smaller counties — Imperial (SVI = 1.00), Merced (0.98), Kern (0.97). Five counties meet **all five** exploratory scarcity conditions: Imperial, Merced, Kern, Kings, and Lake.

**4. County population is a strong Spearman predictor of physician count (r = 0.61), but the Pearson correlation is only 0.25 — a material divergence.**  
This confirms that the population–access relationship is non-linear: larger counties tend to have more physicians, but not proportionally more. Using raw physician counts without rate adjustment would severely penalise small rural counties.

**5. SVI vulnerability profiles differ substantially across counties — no single theme dominates.**  
Socioeconomic status is the dominant SVI theme for 18 counties; racial/ethnic minority status for 17; housing/transportation for 13; household characteristics for 10. San Bernardino and Los Angeles are dominated by racial/ethnic-minority status, while Imperial and Merced are dominated by socioeconomic factors. County vulnerability cannot be reduced to a single dimension.

---

## Counties and patterns warranting closer review

| County | SVI | PCPs/10k | HPSA | Notable |
|---|---|---|---|---|
| Imperial | 1.000 | 2.74 | Yes | Highest SVI in CA; very low access |
| Merced | 0.983 | 5.38 | Yes | 2nd highest SVI; 5 conditions met |
| Kern | 0.965 | 5.55 | Yes | Top-quartile SVI; 5 conditions met |
| Kings | 0.895 | 4.77 | Yes | High SVI; bottom-quartile rate; 5 conditions |
| Lake | 0.754 | 4.69 | Yes | Meets all 5 exploratory conditions |
| Glenn | 0.667 | 1.41 | Yes | Extremely low physician rate; rural |
| Colusa | 0.684 | 3.19 | No | High SVI, very low rate, no HPSA — warrants investigation |
| Yuba | 0.789 | 2.97 | No | High SVI, low rate, no active HPSA |
| Riverside | 0.614 | 6.58 | Yes | Q1 county with 2.5M residents — largest affected population |

*This is an exploratory identification table — not a ranked priority list.*

---

## SVI–provider access association: **Weak at composite level; moderate for socioeconomic theme**

The composite SVI and physician rate have a statistically significant but weak relationship. The socioeconomic sub-theme is a substantially stronger predictor. This suggests that poverty, unemployment, and housing-cost burden co-locate more reliably with physician scarcity than composite vulnerability alone. However, many high-SVI counties have adequate physician rates (Q2), particularly urban counties where vulnerability is driven by racial/ethnic-minority composition rather than provider scarcity.

---

## HPSA alignment with physician scarcity: **Partial, with notable exceptions**

HPSA-designated counties have lower median physician rates (7.7 vs 9.8/10k) and substantially higher median SVI (0.64 vs 0.30), consistent with the program's targeting intent. However, 11 counties with active HPSAs fall in Q2 (high SVI, above-median physician rate), likely because their HPSAs reflect population-specific or sub-county shortages rather than county-wide scarcity. Colusa and Yuba — both Q1 counties — have no active geo/population HPSA despite meeting two or more scarcity conditions.

**Facility HPSA (57/58 counties) provides no differentiation** at the county level and should not enter the final prioritization formula.

---

## Variables suitable for a later transparent priority score

| Variable | Source | Rationale |
|---|---|---|
| `primary_care_physicians_per_10000` | AHRF 2022 | Core access outcome |
| `svi_overall` | CDC SVI 2022 (CA-specific) | Composite vulnerability |
| `svi_socioeconomic` | CDC SVI 2022 | Strongest theme-level predictor |
| `svi_household_characteristics` | CDC SVI 2022 | Second strongest theme correlate |
| `has_current_geo_population_hpsa` | HRSA HPSA 2026 | Current-status external overlay |
| `current_geo_population_max_score` | HRSA HPSA 2026 | Severity overlay (keep separate from 2022 score) |

---

## Variables that should remain descriptive only

| Variable | Reason |
|---|---|
| `svi_racial_ethnic_minority` | Negligible correlation with physician rate; important context but needs domain justification before scoring |
| `svi_housing_transportation` | Same — negligible empirical correlation |
| `has_current_facility_hpsa` | 57/58 counties; no useful differentiation |
| `current_facility_hpsa_count` | Same |
| Population (AHRF or SVI) | Context variable; whether to weight by population should be an explicit program decision |

---

## Key limitations and unresolved questions

1. **n = 58** — all statistics have wide uncertainty at this sample size. Even "significant" correlations (n=58) are fragile.
2. **Physician undercounting** — AMA-sourced AHRF counts may miss salaried providers at FQHCs, IHS sites, and RHCs. Rural shortage counties may be worse than reported.
3. **SVI ties** — CA-specific ranking produces many ties at 0.0, 0.25, 0.50, 0.75, 1.0 (quartile boundaries). Aggregation effects may create artificial clustering.
4. **HPSA temporal mismatch** — 2026 snapshot vs 2022 data. Designations, withdrawals, and score updates between 2022 and 2026 may create apparent mismatches.
5. **Rate instability for tiny counties** — Alpine (pop 1,190) and Sierra (pop 3,217): one physician entering or leaving changes the rate by 8–84 per 10,000. Rates should not be taken at face value for these counties.
6. **Ecological fallacy** — county-level patterns do not guarantee individual-level access barriers. Large, heterogeneous counties (Los Angeles, San Diego) may contain both highly resourced areas and deep shortage pockets.
7. **No time-trend data** — this analysis cannot determine whether access gaps are improving or worsening.

---

*Milestone 3 complete. All required variables — `descriptive_summary`, `county_quadrants`, `correlation_summary`, `hpsa_group_summary`, `county_dominant_svi_theme`, `exploratory_review_conditions`, `milestone3_findings` — are exported and verified. No priority score, sensitivity analysis, or dashboard has been built. Awaiting approval before proceeding to Milestone 4.*
