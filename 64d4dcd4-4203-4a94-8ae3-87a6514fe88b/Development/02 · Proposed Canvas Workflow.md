# Proposed Canvas Workflow — All 14 Sections

> **Milestone 1 scope:** Sections 01–04 are implemented. Sections 05–14 are proposed below — not yet built.
> Review this plan before proceeding to cleaning, joining, scoring, or visualization blocks.

---

## 01 · Project Overview *(implemented)*

**Block type:** MARKDOWN  
**Purpose:** Static reference header — project objective, audience, data sources, analytical rules, responsible-use statement.  
**Outputs:** None (documentation only).

---

## 02 · Source Documentation *(implemented)*

**Block types:** PYTHON · MARKDOWN  
**Purpose:** Working data dictionary (27 fields across SVI, AHRF, HPSA); proposed workflow roadmap (this block).  
**Outputs:** `wdd` — working data dictionary DataFrame.

---

## 03 · Raw File Inspection *(implemented)*

**Block types:** PYTHON × 4  
| Block | File | Key findings |
|-------|------|--------------|
| 03a | SVI CSV | 58 rows × 158 cols; no -999; all 5-char STCNTY |
| 03b | AHRF XLSX | Header row=3; 58 rows; 2 zero-physician counties |
| 03c | HPSA CSV | 79K national / 8,245 CA rows; 1,436 unique HPSA IDs |
| 03d | Documentation | HPSA dict (100 fields); SVI PDF extracted |

**Outputs:** `svi_raw`, `ahrf_raw_clean`, `hpsa_raw`, `hpsa_ca`, `meta`

---

## 04 · Data Quality Audit *(implemented)*

**Block type:** PYTHON  
**Purpose:** Structured audit — per-file shapes, nulls, -999 checks, duplicate analysis, FIPS candidates, geographic coverage, join-key recommendation, unresolved flags.  
**Outputs:** Printed audit report (no new variables exported).

---

## 05 · SVI Cleaning

**Block type:** PYTHON  
**Dependencies:** 03a output (`svi_raw`)  
**Transformations:**
- Cast `STCNTY` and `FIPS` as `str.zfill(5)` — verify they are identical.
- Numeric-cast all `RPL_` and `E_` columns.
- Replace `-999` with `np.nan` (none currently present, but guard against future re-runs).
- Select only the ~15 fields needed: `STCNTY`, `COUNTY`, `E_TOTPOP`, `RPL_THEMES`, `RPL_THEME1–4` plus any `F_` flag columns used as sensitivity checks.
- Assert: 58 rows, 0 nulls in key fields, all STCNTY start with `'06'`.

**Outputs:** `svi_clean` — 58 rows × ~10 cols

---

## 06 · AHRF Cleaning

**Block type:** PYTHON  
**Dependencies:** 03b output (`ahrf_raw_clean`)  
**Transformations:**
- Rename columns to `county_label`, `pc_physicians_2022`, `population_2022`, `rate_per_100k`, `source`.
- Parse county FIPS: strip `', CA'` from `county_label` → match normalized name to SVI `COUNTY` → assign `STCNTY`.
- Validate all 58 counties matched (assert zero unmatched rows).
- Calculate `pc_per_10k = (pc_physicians_2022 / population_2022) * 10_000`.
- Cross-check: verify `pc_per_10k * 10` ≈ `rate_per_100k` (tolerance ±0.5 per 100k).
- Flag counties with 0 physicians (`is_zero_md = True` for Alpine, Sierra).

**Outputs:** `ahrf_clean` — 58 rows × ~7 cols, includes `STCNTY`, `pc_per_10k`, `is_zero_md`

---

## 07 · HPSA Filtering and Aggregation

**Block type:** PYTHON  
**Dependencies:** 03c output (`hpsa_ca`)  
**Transformations:**
- Filter to `HPSA Discipline Class == 'Primary Care'` and `Primary State Abbreviation == 'CA'`.
- Classify rows: `desig_group = 'Geo/Pop'` | `'Facility'` | `'Other'` (from Designation Type).
- Filter to `HPSA Status == 'Designated'` for active shortage indicators.
- Zero-pad `Common State County FIPS Code` to 5 chars.
- Aggregate to county level (one row per `STCNTY`):
  - `has_geo_pop_hpsa`: 1 if any active Geo/Pop designation, else 0.
  - `has_facility_hpsa`: 1 if any active Facility designation, else 0.
  - `max_hpsa_score`: max `HPSA Score` across active Geo/Pop rows (use `max()`).
  - `n_active_designations`: count of distinct active HPSA IDs (Geo/Pop only).
  - `total_underserved_pop`: sum of `HPSA Estimated Underserved Population` (Geo/Pop, non-null only; flag counties where this is entirely null).
- Note in comments: `Proposed For Withdrawal` and `Withdrawn` rows are excluded.
- ⚠ Document that `has_facility_hpsa = 1` does NOT imply the whole county is a shortage area.

**Outputs:** `hpsa_county` — ≤58 rows × ~6 cols (counties with no HPSA data will be absent; fill with 0/NaN after join)

---

## 08 · County Join and Validation

**Block type:** PYTHON  
**Dependencies:** `svi_clean`, `ahrf_clean`, `hpsa_county`  
**Transformations:**
- Left-join `svi_clean` ↔ `ahrf_clean` on `STCNTY` (engineered in 06).
- Left-join result ↔ `hpsa_county` on `STCNTY` — fill missing HPSA columns with 0 / NaN.
- Assert: final table has exactly 58 rows.
- Print join diagnostics: any unmatched STCNTY values in either direction.
- Check for population mismatch between `E_TOTPOP` (SVI) and `population_2022` (AHRF): flag counties where `abs(E_TOTPOP - population_2022) / population_2022 > 0.10`.
- Document any blending decisions as inline comments.

**Outputs:** `county_master` — 58 rows, all key metrics aligned by STCNTY

---

## 09 · Exploratory Analysis

**Block types:** PYTHON × 2–3  
**Dependencies:** `county_master`  
**Analyses:**
- Distributions: histograms of `RPL_THEMES`, `pc_per_10k`, `max_hpsa_score`.
- Scatter: `RPL_THEMES` vs `pc_per_10k` (color-coded by `has_geo_pop_hpsa`).
- Correlation matrix across all key metrics.
- Descriptive table: top 10 and bottom 10 counties by each metric.
- Note population outliers (very small counties: Alpine, Sierra, Modoc, Trinity, etc.).

**Outputs:** `eda_corr_matrix`, exploratory figures

---

## 10 · Provider Scarcity Measure

**Block type:** PYTHON  
**Dependencies:** `county_master`  
**Transformations:**
- Primary measure: `pc_per_10k` (physicians per 10,000 residents) recalculated from AHRF.
- Classify counties: `scarcity_tier` = `'Critical'` (< 5 per 10k) | `'Limited'` (5–10) | `'Adequate'` (> 10).
  - Thresholds are illustrative reference points, not official standards.
- Cross-tabulate `scarcity_tier` with `has_geo_pop_hpsa` to show HPSA alignment.
- Document discordant cases: counties where physician rate is low but no active HPSA, or vice versa.

**Outputs:** `county_master` updated with `scarcity_tier`; summary tables

---

## 11 · Priority Score and Sensitivity Analysis

**Block type:** PYTHON  
**Dependencies:** `county_master` with `scarcity_tier`  
**Transformations:**
- Construct a simple composite score:
  `priority_score = w1 × RPL_THEMES_rank + w2 × scarcity_rank`
  where ranks are within-CA percentiles and default weights are `w1 = 0.5, w2 = 0.5`.
- Parameterize weights so they can be changed without rewriting code.
- Run sensitivity analysis: vary `w1` from 0.3 to 0.7 in steps of 0.1; show how top-10 county list changes.
- Annotate all disclaimers: score is a heuristic ordering tool, not an official designation.
- ⚠ Do NOT blend 2026 HPSA data directly into the score labeled as '2022'. HPSA is a supplemental comparison column only.

**Outputs:** `county_scored` — 58 rows with `priority_score`, `priority_rank`, sensitivity table

---

## 12 · Visualizations

**Block types:** PYTHON × 3–4  
**Dependencies:** `county_scored`  
**Charts (one figure per block):**
1. **Quadrant scatter** — `RPL_THEMES` (x) vs `pc_per_10k` (y); highlight top-priority counties; label outliers.
2. **Ranked bar chart** — top 20 counties by `priority_score`; color-coded by `scarcity_tier`.
3. **HPSA comparison strip** — county-level `max_hpsa_score` vs `pc_per_10k`, separated by `has_geo_pop_hpsa`.
4. **Sensitivity heat map** — which counties remain in the top 15 across all weight scenarios.

**Design:** Zerve color scheme (dark background `#1D1D20`, palette `#A1C9F4 / #FFB482 / #8DE5A1`). No `FuncFormatter`. Pre-compute all tick labels.

**Outputs:** Named figure variables (`quadrant_fig`, `ranked_bar_fig`, `hpsa_compare_fig`, `sensitivity_fig`)

---

## 13 · Interactive Dashboard

**Block type / Script:** Streamlit deployment script  
**Dependencies:** `county_scored`, figure variables  
**Features:**
- County-selector sidebar.
- Sliders for SVI / scarcity weight adjustment (live priority-score recalculation).
- Four-panel chart layout (quadrant, bar, HPSA strip, sensitivity).
- Data table with download button.
- Responsible-use disclaimer banner.

**Outputs:** Deployed Streamlit app URL

---

## 14 · Findings, Limitations, and Responsible Use

**Block type:** MARKDOWN  
**Purpose:** Final documentation block covering:
- Summary of top-priority counties and what the data supports.
- Data vintage mismatches (ACS 2018–22 vs Census 2022 vs HPSA 2026).
- Known data gaps (AHRF no-FIPS issue, HPSA underserved-pop nulls, facility vs geographic HPSA conflation risk).
- What the analysis cannot claim (causation, completeness, official shortage status).
- Suggested next steps for a program manager or funder.
- Citation block for all five source files.

**Outputs:** None (documentation only).

---

## Dependency Map

```
03a (svi_raw) ──────────────────────────────────── 05 (svi_clean) ─────┐
03b (ahrf_raw_clean) ────────────────────────────── 06 (ahrf_clean) ────┤──► 08 (county_master)
03c (hpsa_ca) ──────────────────────────────────── 07 (hpsa_county) ───┘
                                                                         │
                                    09 (EDA) ◄───────────────────────────┤
                                    10 (scarcity) ◄──────────────────────┤
                                    11 (scoring) ◄───────────────────────┘
                                    12 (viz) ◄── 11
                                    13 (dashboard) ◄── 12 + 11
                                    14 (findings) ◄── 11
```
