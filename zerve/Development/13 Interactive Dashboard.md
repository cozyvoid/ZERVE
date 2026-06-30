# 13 Interactive Dashboard — Application README and Deployment Information

## Overview
An interactive Streamlit dashboard that explores where high social vulnerability and limited primary-care physician availability overlap across California's 58 counties. All results are **exploratory** — they are intended to support further investigation and resource-planning discussions, not to automatically allocate resources.

---

## Application sections and user interactions

| Tab | Section | Key interactions |
|-----|---------|-----------------| 
| **1 · Overview** | High-level KPI metrics, top-15 horizontal ranked bar chart, scatterplot, principal findings | View-only; summary statistics update from validated data |
| **2 · County Explorer** | Full county profile with scores, ranks, rates, SVI themes, HPSA status | Searchable county dropdown; all 58 counties selectable; zero-provider note for Alpine/Sierra |
| **3 · Scenario Comparison** | Top-15 scenario-comparison grouped bar chart, rank-stability bump chart, scenario agreement, county rank look-up | Select Balanced / Access-focused / Equity-focused / Empirical themes / Custom; custom weight slider auto-balances to 100% |
| **4 · HPSA Alignment** | Alignment category table, boxplot of score distribution by HPSA status, disagreement county tables | View-only; 2022 vs 2026 data clearly separated |
| **5 · Methodology & Limitations** | Data sources, core measures, scoring formulas, important distinctions, limitations, validation table | Expandable sections |

---

## Visualization methods

| Chart type | Where used | What it shows |
|------------|-----------|---------------|
| **Horizontal ranked bar chart** | Tab 1 Overview; Tab 3 Scenario Comparison | Top-15 counties ranked by balanced priority score; bars annotated with score and rank |
| **Scenario-comparison grouped bar chart** | Tab 3 Scenario Comparison | All four weighting scenarios side-by-side for the top-15 counties; reveals which counties are sensitive to weight choice |
| **Annotated heatmap** | Tab 2 County Explorer | SVI vulnerability dimensions (socioeconomic, household, racial/ethnic, housing/transport) × selected counties; dominant dimension highlighted |
| **Histograms** | Tab 1 Overview; Tab 2 County Explorer | Physician rate distribution; raw physician count distribution; county population distribution |
| **Scatterplot** | Tab 1 Overview; Tab 3 Scenario Comparison | Social vulnerability vs primary-care access (quadrant view); provider scarcity vs SVI with score as color; balanced score vs county population |
| **Boxplot** | Tab 4 HPSA Alignment | Balanced score distribution by current geo/pop HPSA status (2026 snapshot vs 2022 data) |
| **Bump/rank-movement chart** | Tab 3 Scenario Comparison | Rank trajectory of top-20 counties across all four scenarios; identifies stable vs sensitive counties |

---

## Data loaded from canvas

| Variable | Source block | Purpose |
|----------|-------------|---------|
| `balanced_priority_results` | `09 · Primary Results` | Primary county scoring and ranking table |
| `scenario_rankings` | `07 · Scenario Rankings` | Long-form 4-scenario ranking table |
| `rank_stability_summary` | `08 · Ranking-Stability` | Rank variability across scenarios |
| `population_impact_context` | `10 · Population Impact Context` | 2×2 planning classification |
| `hpsa_alignment_summary` | `11 · HPSA Alignment` | Historical score vs current HPSA comparison |
| `county_dominant_svi_theme` | `99h · SVI Theme Analysis` | Dominant vulnerability theme per county |
| `exploratory_review_conditions` | `99i · Exploratory Candidate Conditions` | Multi-condition exploratory flags |
| `county_priority_scores` | `06 · Provider-Scarcity Scenarios` | Full scoring table with all 4 scenarios |

---

## Data sources

| Source | Period | Role |
|--------|--------|------|
| CDC/ATSDR Social Vulnerability Index | 2022 (ACS 2018–2022) | SVI percentile rankings |
| HRSA Area Health Resources File (AHRF) | 2022 | Physician counts and population denominator |
| HRSA Primary Care HPSA File | 2026-06-25 snapshot | Current HPSA designation (descriptive overlay only) |

---

## Scoring formula (Balanced scenario)

```
priority_balanced = 0.50 × provider_scarcity + 0.50 × svi_overall
```

All components are relative California-county percentiles in [0, 1]. Higher = higher exploratory priority.

---

## Critical responsible-use notes

- Scores are **exploratory** and **relative** to California's 58 counties.
- The score does **not** measure actual appointment availability, travel time, insurance acceptance, or telehealth access.
- HPSA variables are from a **later reporting period** (2026) and are shown as a separate external comparison only.
- Population is **not** part of the primary score; it is a separate planning dimension.
- Tied scores should not be interpreted as substantively different.
- Rankings should identify areas for **further review**, not automatically allocate resources.

---

## Deployment details

- Framework: Streamlit
- Compute: medium
- Data: loaded at startup via `zerve.variable()` from validated Milestone 4 canvas blocks
- Preview deployment: started 2026-06-25
- Validation: 30/30 checks passed in the Technical Appendix deployment-validation block.

- **Live application:** [Open the deployed dashboard](PASTE_DEPLOYED_APP_LINK_HERE)
- **Project notebook:** [View the Zerve project](PASTE_NOTEBOOK_LINK_HERE)
