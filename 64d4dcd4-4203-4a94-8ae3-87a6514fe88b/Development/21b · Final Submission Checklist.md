# Final Submission Checklist — California Healthcare Access Priority Explorer

Use this checklist before submitting to HackerEarth. Each item has a short note explaining what to verify.

---

## A · Deployment and access

- [ ] **Application link opens without errors**
  Open the Zerve preview or production URL in a private browser tab to confirm it loads cleanly from a cold start.

- [ ] **Project / canvas access settings are correct**
  Confirm the canvas and dashboard are shared at the access level required by the competition (view-only for judges, if applicable).

- [ ] **Deployment is synced after any upstream canvas rerun**
  If any canvas block was re-run after the last deployment sync, open the Deployments panel and sync the preview so the app picks up the latest variables.

- [ ] **Final deployment URL is copied correctly**
  Paste the URL into the submission form exactly — no trailing spaces, no shortened links that may expire.

---

## B · Dashboard functionality

- [ ] **All five tabs render without errors**
  Click through Overview → County Explorer → Scenario Comparison → HPSA Alignment → Methodology & Limitations and confirm each tab loads.

- [ ] **County selector returns correct county profiles**
  Test at least three counties: Imperial (rank 1), Alpine or Sierra (zero-physician note), and a mid-ranked county such as Fresno.

- [ ] **Custom weight slider enforces 100% sum**
  Move the Provider Scarcity slider and confirm the SVI weight updates automatically to keep the total at 100%.

- [ ] **Custom scoring does not overwrite preset results**
  Navigate away from the custom scenario and back to Balanced — confirm the balanced scores and ranks are unchanged.

- [ ] **Zero-physician counties remain visible and correctly flagged**
  Search for Alpine County and Sierra County. Confirm both show the zero-physician note and their validated provider-scarcity value.

- [ ] **Alpine and Sierra show tied provider-scarcity values (≈ 0.991)**
  Verify in the County Explorer that both counties display the same provider-scarcity percentile.

- [ ] **Responsible-use statement is visible on every tab**
  Scroll each tab to confirm the exploratory-tool disclaimer appears.

- [ ] **Source years are clearly labeled throughout**
  Confirm SVI columns are labeled 2022, physician data are labeled 2022, and HPSA columns carry the "current (2026)" label or equivalent.

---

## C · Submission form content

- [ ] **Title matches exactly:** `California Healthcare Access Priority Explorer`

- [ ] **Project description is complete and accurate**
  Use the longer description from Section 2 of the submission package. Confirm quantitative values (58 counties, 4 scenarios, 30 validation checks) match the canvas outputs.

- [ ] **Application-form answers match the dashboard**
  Check that every specific number or county name cited in the form answers (e.g. Imperial ranked #1, top-10 Jaccard > 0.82, max HPSA score = 19) appears consistently in the dashboard.

- [ ] **No causal language or unsupported claims**
  Review all form answers for phrases like "improves healthcare outcomes," "proves shortage," or "most underserved." Replace with "warrants closer review" or "the analysis found."

---

## D · Content and data quality

- [ ] **No private or confidential information is included**
  Confirm no local file paths, API keys, internal usernames, or non-public data appear in any block output, dashboard display, or submission text.

- [ ] **Raw local file paths are not exposed**
  Verify that canvas block outputs reference relative paths (e.g. `/files/...`) and not absolute local machine paths.

- [ ] **No 2026 HPSA field is incorporated into any 2022 score**
  Confirm in the HPSA Alignment tab and Methodology tab that HPSA data are described as a separate current-status comparison.

---

## E · Final review

- [ ] **Spelling and grammar are reviewed**
  Read the project description, problem statement, and all five tab texts for typos, inconsistent capitalization, and grammatical errors.

- [ ] **Final screenshots are readable**
  If screenshots are required by the submission form, verify they are taken at sufficient resolution and all axis labels, county names, and score values are legible.

---

*All 37 canvas blocks, 5 dashboard tabs, 22 Milestone 4 validation checks, and 30 deployment validation checks have been completed and confirmed. This checklist covers submission-readiness only—no analytical changes should be made after this point.*
