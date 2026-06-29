# 09 · Exploratory Analysis Overview

## Unit of Analysis
Each row is one **California county** (n = 58).

## Primary Historical Period
**2022** — CDC/ATSDR SVI (ACS 2018–2022 vintage) and HRSA AHRF primary-care physician counts and population estimates (Census 2022 vintage).

## Outcome of Interest
**Primary-care physicians per 10,000 residents** (`primary_care_physicians_per_10000`), calculated from the 2022 AHRF physician count and AHRF Census population.

## Principal Vulnerability Measure
**Overall SVI percentile** (`svi_overall` = `RPL_THEMES`), a California-specific composite ranking on [0, 1] where higher values indicate greater social vulnerability. Four sub-theme percentiles (`svi_socioeconomic`, `svi_household_characteristics`, `svi_racial_ethnic_minority`, `svi_housing_transportation`) are examined separately.

## Role of Current HPSA Data
The 2026-06-25 HRSA HPSA snapshot (`current_*` fields) is used **only as an external descriptive overlay and comparison group**. It reflects current federal shortage-area designations and is **not folded into any measure labeled as 2022**, nor is it used to construct a composite score.

## Analytical Framing
This analysis is **ecological and descriptive**. Observations are counties, not individuals. All associations reported are observational; no causal claims are made. Medians used as reference thresholds are **exploratory conveniences**, not official policy cutoffs. Results are intended to support further investigation and resource-planning discussion, not to serve as an official resource-allocation formula.
