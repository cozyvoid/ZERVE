# Data Sources and Scope

This project combines three public healthcare and demographic data sources at the California county level.

| Data source                          | Reporting period                          | Role in the project                                                       |
| ------------------------------------ | ----------------------------------------- | ------------------------------------------------------------------------- |
| CDC/ATSDR Social Vulnerability Index | 2022, based on 2018–2022 ACS estimates    | Measures overall and theme-level social vulnerability                     |
| HRSA Area Health Resources Files     | 2022                                      | Provides primary-care physician counts and county population              |
| HRSA Primary Care HPSA data          | Current snapshot downloaded June 25, 2026 | Provides a separate comparison with current federal shortage designations |

## Analytical Scope

* **Unit of analysis:** California county
* **Counties included:** 58
* **Primary historical analysis:** 2022
* **Healthcare measure:** Primary-care physicians per 10,000 residents
* **Vulnerability measure:** Overall SVI percentile
* **External comparison:** Current geographic and population Primary Care HPSA designations

County FIPS codes are used as the authoritative geographic join key. The final analytical table contains one record for each California county.

The current HPSA data are kept separate from the 2022 priority scores because they represent a later reporting period. Population is also retained as a separate planning dimension rather than being included directly in the county priority score.
