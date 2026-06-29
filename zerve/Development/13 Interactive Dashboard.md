# California Healthcare Access Priority Explorer — Application README

## Overview
An interactive Streamlit dashboard that explores where high social vulnerability and limited primary-care physician availability overlap across California's 58 counties. All results are **exploratory** — they are intended to support further investigation and resource-planning discussions, not to automatically allocate resources.

---

## Application sections and user interactions

| Tab | Section | Key interactions |
|-----|---------|-----------------|
| **1 · Overview** | High-level KPI metrics, top-15 bar chart, scatterplot, principal findings | View-only; summary statistics update from validated data |
| **2 · County Explorer** | Full county profile with scores, ranks, rates, SVI themes, HPSA status | Searchable county dropdown; all 58 counties selectable; zero-provider note for Alpine/Sierra |
| **3 · Scenario Comparison** | Top-15 by scenario, rank-stability bubble chart, scenario agreement, county rank look-up | Select Balanced / Access-focused / Equity-focused / Empirical themes / Custom; custom weight slider auto-balances to 100% |
| **4 · HPSA Alignment** | Alignment category table, score boxplot by HPSA status, disagreement county tables | View-only; 2022 vs 2026 data clearly separated |
| **5 · Methodology & Limitations** | Data sources, core measures, scoring formulas, important distinctions, limitations, validation table | Expandable sections |

---

## Data loaded from canvas

| Variable | Source block | Purpose |
|----------|-------------|---------|
| `balanced_priority_results` | `14 · Primary Results Table` | Primary county scoring and ranking table |
| `scenario_rankings` | `12 · Scenario Rankings` | Long-form 4-scenario ranking table |
| `rank_stability_summary` | `13 · Ranking-Stability Analysis` | Rank variability across scenarios |
| `population_impact_context` | `15 · Population Context` | 2×2 planning classification |
| `hpsa_alignment_summary` | `16 · HPSA Alignment Analysis` | Historical score vs current HPSA comparison |
| `county_dominant_svi_theme` | `09f · SVI Theme Analysis` | Dominant vulnerability theme per county |
| `exploratory_review_conditions` | `09g · Candidate Counties for Closer Review` | Multi-condition exploratory flags |
| `county_priority_scores` | `10 · Provider-Scarcity Measure` | Full scoring table with all 4 scenarios |

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
- Validation: 30/30 checks passed (block `20 · Dashboard Deployment Validation`)
