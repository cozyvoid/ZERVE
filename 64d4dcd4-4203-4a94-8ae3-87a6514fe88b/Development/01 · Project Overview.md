# California Healthcare Access Priority Explorer

## Objective
Identify California counties where **high social vulnerability** overlaps with **limited primary-care physician capacity**, to support resource-planning and funding discussions.

## Intended Audience
Public-health program managers · Healthcare network planners · Nonprofit funding organizations · County health administrators

## Data Sources
| # | File | Source | Vintage |
|---|------|---------|---------|
| 1 | `cdc_svi_ca_county_2022.csv` | CDC/ATSDR Social Vulnerability Index | 2022 (2018–2022 ACS) |
| 2 | `cdc_svi_2022_data_dictionary_tract_county_zcta.pdf` | CDC/ATSDR SVI documentation | 2022 |
| 3 | `hrsa_ahrf_ca_county_primary_care_physicians_population_2022.xlsx` | HRSA Area Health Resources File | 2022 |
| 4 | `hrsa_primary_care_hpsa_national_2026-06-25.csv` | HRSA HPSA designations | Current (downloaded 2026-06-25) |
| 5 | `hrsa_hpsa_data_dictionary_2026-06-25.xlsx` | HRSA HPSA data dictionary | 2026-06-25 |

## Analytical Ground Rules
- All raw datasets are preserved; cleaned copies are separate objects.
- `STCNTY` from SVI is the preferred join key; all FIPS codes are 5-character zero-padded strings.
- SVI values of `-999` are treated as missing, not zero.
- The core historical analysis uses **2022** SVI and AHRF data only.
- The 2026 HPSA file is treated as a **current-status indicator**, not a 2022 data point.
- Provider rates are **recalculated** from raw counts; the supplied rate is used only as a validation check.
- HPSA rows are **filtered and aggregated** at the county level; raw row counts are not used as severity measures.
- Geographic/population HPSAs and facility HPSAs are kept as **separate indicators**.

## Responsible Use Statement
> This analysis is a **portfolio demonstration** of reproducible public-health data methods.
> Results are descriptive and exploratory — they do **not** constitute official shortage designations,
> resource-allocation recommendations, or clinical policy guidance.
> No causal claims are made. All limitations are documented in section 14.

## Milestone Scope (Current)
**Milestone 1 — Audit only.** Sections 01–02 (overview + documentation) and 03–04 (raw inspection + quality audit) are complete. Sections 05–14 (cleaning, joining, scoring, visualizations, dashboard) are proposed but not yet implemented.
