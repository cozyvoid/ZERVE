"""
21 · FINAL PROJECT-SUBMISSION PACKAGE
California Healthcare Access Priority Explorer
All text is sourced from validated Milestone 1-5 outputs.
No scores, rankings, or source data are altered here.
"""

import textwrap

DIVIDER = "\n" + "=" * 80 + "\n"
THIN    = "\n" + "-" * 80 + "\n"

# ─── helper ──────────────────────────────────────────────────────────────────
def section(title, body):
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)
    print(textwrap.dedent(body).strip())


# ══════════════════════════════════════════════════════════════════════════════
# 1 · CONCISE PROJECT SUMMARY  (~75-100 words)
# ══════════════════════════════════════════════════════════════════════════════
concise_summary = """\
Primary-care physician shortages and social vulnerability rarely appear in the same
planning tool. This project integrates three public data sources—the CDC/ATSDR 2022
Social Vulnerability Index, HRSA AHRF 2022 physician-workforce data, and current
HRSA Primary Care HPSA designations—across all 58 California counties. Using Python,
SQL, and validated percentile-ranking methods, it produces four transparent
prioritization scenarios, tests ranking stability under different planning weights,
and delivers an interactive five-tab Streamlit dashboard. The result is an exploratory,
reproducible decision-support tool designed to identify counties that warrant closer
review—not to allocate resources automatically.
"""

section("1 · CONCISE PROJECT SUMMARY  (~75–100 words)", concise_summary)


# ══════════════════════════════════════════════════════════════════════════════
# 2 · LONGER PROJECT DESCRIPTION  (~200-300 words)
# ══════════════════════════════════════════════════════════════════════════════
longer_description = """\
Public-health program managers and healthcare network planners often have to make
resource decisions—grant targeting, workforce recruitment, network expansion—without
a single clear picture of where social vulnerability and limited physician access
overlap. This project builds that picture for California's 58 counties.

The analysis integrates three public datasets: the CDC/ATSDR 2022 Social Vulnerability
Index (SVI), which provides a composite and four sub-theme percentile measure of
community resilience; the HRSA Area Health Resources File (AHRF) 2022 primary-care
physician counts and population denominators; and a current-snapshot HRSA Primary Care
Health Professional Shortage Area (HPSA) file downloaded June 25, 2026. The HPSA data
are treated as a present-day external comparison rather than a 2022 historical measure.

Data cleaning resolved two non-trivial challenges: a nonstandard multi-row Excel header
in the AHRF workbook (correct header at row 3) required careful inspection before
import; and county identifiers needed standardization across three sources with no
shared numeric FIPS column in the AHRF file, requiring an exact name-match strategy
to inherit FIPS codes from the SVI dataset. All 58 county matches were confirmed
exact—no fuzzy matching was used.

The core analytical measures are physicians per 10,000 residents (2022 AHRF denominator)
and a rank-based provider-scarcity percentile that prevents extreme raw rates in
micro-population counties from dominating the score. Four scoring scenarios—balanced
(50/50), access-focused (65/35), equity-focused (35/65), and an empirical-theme
sensitivity scenario—were computed and tested for stability using Spearman rank
correlations (all pairs r > 0.89) and top-10 Jaccard overlap.

Population is retained as a separate planning dimension rather than a scoring component,
so that sparsely populated rural counties and densely populated urban counties receive
independent analytical attention. A five-tab Streamlit application delivers the full
analysis—county profiles, scenario comparison, HPSA alignment, and methodology—in a
format accessible to nontechnical stakeholders. All 30 deployment validation checks
passed before submission.

The project is explicitly framed as exploratory and reproducible. It makes no causal
claims and should not be used as an automatic resource-allocation formula.
"""

section("2 · LONGER PROJECT DESCRIPTION  (~200–300 words)", longer_description)


# ══════════════════════════════════════════════════════════════════════════════
# 3 · PROBLEM STATEMENT
# ══════════════════════════════════════════════════════════════════════════════
problem_statement = """\
Primary-care access in California is uneven, but the dimensions of that unevenness
tell different stories depending on what you measure. Raw physician counts favor large
counties. Physician-to-population rates can be unstable in micro-population counties.
Formal shortage designations (HPSAs) reflect current administrative criteria that may
not fully capture historical patterns, sub-county boundaries, or population-group
distinctions. Social vulnerability captures community-level resilience but does not
directly measure provider supply.

No single measure answers the question that planners actually face: which counties
show the strongest overlap between high social vulnerability and limited primary-care
physician availability, and how stable are those conclusions under different planning
priorities?

This project addresses that question by building a transparent, reproducible
county-level framework that combines 2022 SVI and physician data, compares results
across four weighting scenarios, evaluates ranking stability, and uses current HPSA
designations as a separate external reference—producing an exploratory, auditable
decision-support tool rather than a definitive allocation model.
"""

section("3 · PROBLEM STATEMENT", problem_statement)


# ══════════════════════════════════════════════════════════════════════════════
# 4 · METHODOLOGY SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
methodology_summary = """\
The workflow proceeded in five structured milestones, each reviewed before the next
began.

Milestone 1 — Audit
  · Inspected five uploaded files: CDC SVI CSV, HRSA AHRF XLSX, HRSA HPSA CSV,
    and two metadata/dictionary files (HPSA XLSX, SVI PDF).
  · Documented file dimensions, sheet names, field types, missingness, duplicates,
    FIPS formats, and reporting periods.
  · Identified the AHRF header at Excel row 3, confirmed Common State County FIPS Code
    as the safe HPSA join key, and flagged HPSA Withdrawn/Proposed rows requiring
    filtering.

Milestone 2 — Cleaning and Joining
  · Preserved all raw dataframes; created separate cleaned copies.
  · Standardized county names using a shared function; inherited FIPS from SVI via
    exact name matching—58 of 58 matched, zero fuzzy matches used.
  · Replaced SVI sentinel values (-999 → NaN); confirmed none were present.
  · Calculated physicians per 10,000 residents and recalculated the per-100k rate
    as a cross-validation check (max difference: 0.005—pure rounding).
  · Filtered HPSA data to CA + Designated + Primary Care; classified designations
    as geographic/population or facility; aggregated by distinct HPSA ID to the
    county level. Intentionally did not sum estimated underserved populations due to
    potential overlap between designation areas.
  · Joined the three cleaned tables via left joins on county_fips; confirmed 58 rows,
    22 columns, and zero unmatched records.

Milestone 3 — Exploratory Analysis
  · Produced descriptive statistics for 11 key fields.
  · Visualized physician-rate and SVI distributions; identified Alpine and Sierra
    (zero physicians) and San Francisco and Marin (very high rates) as contextually
    important extremes.
  · Computed Pearson and Spearman correlations; found the overall SVI–rate association
    weak (Spearman r = –0.31), but the socioeconomic sub-theme moderate (r = –0.53).
  · Created a 2×2 quadrant table (median thresholds); 18 counties fell in Q1
    (high vulnerability / low access), representing ~6.5 million residents.
  · Identified facility HPSA designation (present in 57 of 58 counties) as
    non-differentiating at the county level.

Milestone 4 — Scoring and Sensitivity
  · Transformed physician availability to a rank-based provider-scarcity percentile
    [0, 1] to prevent micro-population outliers from dominating.
  · Computed four scenarios: balanced (0.50/0.50), access-focused (0.65/0.35),
    equity-focused (0.35/0.65), and empirical-theme (0.50 scarcity + 0.30
    socioeconomic SVI + 0.20 household SVI).
  · Evaluated stability: all pairwise Spearman rank correlations exceeded 0.89;
    balanced, equity-focused, and empirical-theme scenarios shared an identical top-10
    set; access-focused diverged most by emphasising raw scarcity.
  · Compared 2022 historical scores with current HPSA status: 10 of 14 top-quartile
    counties have an active geo/population HPSA; four (Yuba, Colusa, Mariposa,
    Trinity) do not.
  · All 22 Milestone 4 validation checks passed. These checks confirm code correctness
    and internal consistency; they do not constitute external policy or clinical
    validation of the framework.

Milestone 5 — Dashboard Deployment
  · Built a five-tab Streamlit application loading all validated canvas variables
    via zerve.variable().
  · Tabs: Overview, County Explorer, Scenario Comparison, HPSA Alignment, and
    Methodology & Limitations.
  · Custom scenario slider enforces 100% weight sum; custom scores are computed
    dynamically without overwriting precomputed results.
  · All 30 deployment validation checks passed.
"""

section("4 · METHODOLOGY SUMMARY", methodology_summary)


# ══════════════════════════════════════════════════════════════════════════════
# 5 · TECHNICAL-SKILLS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
technical_skills = """\
Languages and libraries
  · Python (pandas, NumPy, SciPy, matplotlib, openpyxl, pypdf/pdfminer)
  · SQL (left joins, aggregations, CTEs via DuckDB/pandasql inside Zerve blocks)
  · Streamlit (multi-tab app, dynamic widgets, custom weight validation)

Data engineering
  · Reading nonstandard Excel headers (header= parameter, footer detection)
  · Zero-padded FIPS string preservation with dtype=str and .str.zfill(5)
  · Sentinel-value detection and replacement (-999 → NaN) without silent imputation
  · Exact string-match county-name joining; no fuzzy matching
  · Multi-source left-join validation and unmatched-record reporting

Feature engineering and statistics
  · Rank-based percentile normalization to limit outlier leverage
  · Percentile reversal to create a scarcity measure from an availability rank
  · Pearson and Spearman correlation analysis with p-values and sensitivity checks
  · Four transparent linear-combination scoring scenarios with weight validation
  · Spearman rank correlation and Jaccard similarity for stability measurement
  · 2×2 planning classification (need × population)

Data quality and validation
  · Field-level data profiling (type, range, missingness, duplicates, sentinel values)
  · Cross-validation of computed rates against supplied rates
  · Assertion-style validation blocks at every milestone
  · Explicit temporal separation of 2022 historical data and 2026 HPSA snapshot

Deployment and documentation
  · Zerve canvas with 37 modular, dependency-ordered blocks
  · Streamlit deployment via zerve.variable() (keyword-argument data loading)
  · Stakeholder-readable visualizations using Zerve design system palette
  · In-code comments, working data dictionary, and milestone findings markdown blocks
  · Responsible-use framing and limitation disclosures in both canvas and dashboard
"""

section("5 · TECHNICAL-SKILLS SUMMARY", technical_skills)


# ══════════════════════════════════════════════════════════════════════════════
# 6 · KEY FINDINGS
# ══════════════════════════════════════════════════════════════════════════════
key_findings = """\
The following findings are drawn directly from validated Milestone 3 and 4 outputs.
All statements describe associations in the 2022 county-level data; they are not
causal claims.

1. Imperial County showed the highest exploratory priority under all four scoring
   scenarios (balanced score ≈ 0.974), with the highest SVI in California and one of
   the lowest physician rates. Its rank was stable at #1 with zero movement across
   scenarios.

2. Imperial, Kings, and Merced appeared in the top five under every scenario.
   Nine counties appeared in the top ten under all four scenarios: Imperial, Kings,
   Merced, Yuba, Glenn, Kern, Tulare, Lake, and Colusa.

3. Scenario agreement was high. All pairwise Spearman rank correlations exceeded
   0.89. The balanced, equity-focused, and empirical-theme scenarios produced the
   same top-10 county set. The access-focused scenario diverged most by placing
   greater weight on counties with the most severe physician scarcity, elevating
   Glenn and Yuba.

4. The top-10 counties represented approximately 2.4 million residents—about 6.1%
   of California's total AHRF 2022 population—confirming that higher-priority counties
   by this measure tend to be smaller and rural rather than the most populous parts of
   the state.

5. Fourteen counties fell in the top quartile of the balanced score. Ten of those
   14 had an active current geographic/population HPSA designation, suggesting general
   alignment between the 2022 historical analysis and current federal shortage status.
   Four top-quartile counties—Yuba, Colusa, Mariposa, and Trinity—did not have a
   current geo/population HPSA and may warrant closer review.

6. The overall SVI–physician-rate correlation was weak at the composite level
   (Spearman r = –0.31), but the socioeconomic sub-theme showed a moderate
   association (r = –0.53) and household characteristics a moderate association
   (r = –0.47). The racial/ethnic-minority and housing/transportation themes showed
   negligible correlation with the physician rate, which informed the decision to
   use svi_overall rather than theme subscores as the primary vulnerability component.

7. Alpine and Sierra counties retained valid zero physician counts throughout. Their
   moderate SVI scores meant they did not automatically dominate equity-focused
   rankings; they received tied provider-scarcity values of 0.991.

8. Facility HPSA designation was present in 57 of 58 counties and offered
   no meaningful county-level differentiation. It was excluded from all scoring
   scenarios.
"""

section("6 · KEY FINDINGS", key_findings)


# ══════════════════════════════════════════════════════════════════════════════
# 7 · ZERVE AND AI-AGENT USAGE EXPLANATION
# ══════════════════════════════════════════════════════════════════════════════
zerve_ai_usage = """\
Platform usage — Zerve
  The project was built entirely within Zerve's notebook environment. The platform
  provided:
  · Shared filesystem for file upload and persistent storage across blocks.
  · Modular Python, SQL, and Markdown blocks with explicit dependency edges, so each
    cleaning, analysis, and visualization step ran in a reproducible, auditable order.
  · A dependency-aware execution graph that prevented downstream blocks from running
    on stale upstream data.
  · The zerve.variable() loading mechanism, which allowed the Streamlit deployment
    script to access all validated canvas variables without reprocessing source files.
  · Iterative milestone planning: each milestone was reviewed and approved before the
    next began, creating a natural checkpoint structure.

AI-agent assistance
  Zerve's AI agent accelerated several parts of the workflow:
  · Initial workflow scaffolding—proposing a 14-section canvas structure matched to
    the project requirements.
  · Code drafting for each block, including data loading, cleaning transformations,
    rate calculations, correlation analysis, and scoring formulas.
  · Validation-block creation—writing assertion-style checks after every major step
    so errors surfaced immediately rather than propagating forward.
  · Documentation—working data dictionary, milestone findings summaries, and the
    application README.
  · Dashboard organization—structuring the five-tab Streamlit application and wiring
    the dynamic custom-weight slider.

Human review and analytical decisions
  The AI agent did not independently establish the validity of the analysis. The
  following decisions and corrections were made through active human review:
  · Verifying column definitions against the HPSA metadata workbook and SVI PDF
    rather than inferring them from field names alone.
  · Requiring FIPS codes to be read as strings with dtype=str throughout, and
    confirming zero-padding was preserved at every join step.
  · Prohibiting fuzzy county name matching; requiring exact one-to-one matches and
    displaying any exception before accepting it.
  · Distinguishing geographic/population HPSAs from facility HPSAs and rejecting
    the use of raw HPSA row counts as a shortage severity measure.
  · Deciding not to sum HPSA estimated underserved populations at the county level
    because overlapping designation boundaries could not be ruled out.
  · Explicitly keeping current 2026 HPSA data outside the 2022 historical score,
    enforcing a clear temporal boundary throughout the canvas and dashboard.
  · Selecting scoring formulas and weight values; choosing rank-based normalization
    over raw-rate normalization to limit outlier leverage.
  · Reviewing all printed validation outputs at each milestone before approving
    continuation.
  · Manually testing the deployed dashboard across all five tabs and verifying that
    Alpine and Sierra displayed correctly, custom weights summed to 100%, and the
    responsible-use statement appeared on every page.
"""

section("7 · ZERVE AND AI-AGENT USAGE EXPLANATION", zerve_ai_usage)


# ══════════════════════════════════════════════════════════════════════════════
# 8 · CHALLENGES AND LEARNING REFLECTION  (~150-200 words)
# ══════════════════════════════════════════════════════════════════════════════
challenges_learning = """\
Several challenges required more careful thought than I initially expected.

The AHRF Excel workbook had three rows of title and filter-description text before the
actual column headers, so naively reading the file produced columns named Unnamed:0
through Unnamed:4. Inspecting the raw file first and identifying the correct header row
taught me to never assume a spreadsheet starts where I expect it to.

Preserving zero-padded FIPS codes through every join was a recurring discipline. It was
easy to let pandas silently read "06001" as the integer 6001 and lose the leading zero.
Reading all ID columns with dtype=str from the very first load—and asserting format at
every step—became a consistent habit.

The HPSA file was the most complex dataset. With over 79,000 national rows, multiple
records per HPSA ID, a mix of active and withdrawn designations, and facility versus
geographic types, the temptation to simply count rows as a shortage measure was real.
Learning to filter to Designated + Primary Care, count distinct HPSA IDs, and classify
designation types before any aggregation was one of the most valuable methodological
lessons of the project.

Deciding not to include population in the primary score was also harder than it sounds.
A population-weighted score would have pulled focus toward Los Angeles and Riverside,
which are clearly important but represent a different kind of planning challenge than
Imperial or Glenn. Separating need intensity from impact scale made the framework more
honest.

Finally, converting a multi-block notebook analysis into a coherent five-tab Streamlit
application taught me to think about the user's path through the data—not just whether
the numbers were correct, but whether a nontechnical stakeholder could understand what
they were looking at and why it mattered.
"""

section("8 · CHALLENGES AND LEARNING REFLECTION  (~150–200 words)", challenges_learning)


# ══════════════════════════════════════════════════════════════════════════════
# 9 · LIMITATIONS AND RESPONSIBLE USE
# ══════════════════════════════════════════════════════════════════════════════
limitations = """\
Analytical limitations
  · The analysis is ecological: all measures are county-level aggregates. Findings
    cannot be attributed to any individual or sub-county area.
  · No within-county variation is captured. A county with a moderate physician rate
    may still have concentrated access barriers in rural sub-regions.
  · Physician counts are based on the AHRF primary-care extract and do not capture
    nurse practitioners, physician assistants, community health workers, or other
    primary-care professionals who may partially offset physician scarcity.
  · No adjustment is made for physician workload, panel capacity, or full-time
    equivalents. A small number of high-volume providers may serve more patients
    than the count implies.
  · Appointment availability, patient-provider language match, insurance network
    participation, and Medicaid acceptance rates are not measured.
  · Cross-county travel is not modeled. Residents in one county may routinely access
    care in a neighboring county.
  · Telehealth availability and utilization are not included.
  · Very small counties (Alpine, Sierra, Colusa, Mariposa, Trinity, and others) can
    produce volatile per-capita rates when a single provider joins or leaves. Rank-based
    normalization reduces but does not eliminate this sensitivity.

Scoring and ranking limitations
  · The SVI is a relative percentile within California counties. A high SVI rank
    indicates higher relative vulnerability compared to other California counties, not
    an absolute measure of deprivation.
  · The four weighting scenarios represent different policy perspectives, not
    empirically optimal allocations. No scenario has been externally validated for
    resource-allocation purposes.
  · The HPSA comparison uses a 2026 snapshot against 2022 historical data. Some
    designations may have changed since 2022, and some counties may have received or
    lost designations that would alter the alignment analysis.
  · Counties with tied scores should not be treated as substantively different from
    each other.

Responsible use
  This tool is designed to identify counties that warrant closer review by
  public-health planners, funding organizations, or healthcare network analysts. It
  should not be used to automatically allocate resources, determine staffing levels,
  prioritize grant awards, or substitute for on-the-ground community-needs assessments.
  Any planning decision should incorporate local knowledge, qualitative input from
  community stakeholders, and data sources beyond what is represented here.
"""

section("9 · LIMITATIONS AND RESPONSIBLE USE", limitations)


# ══════════════════════════════════════════════════════════════════════════════
# 10 · PORTFOLIO DESCRIPTION
# ══════════════════════════════════════════════════════════════════════════════
portfolio = """\
One-sentence version
  "Built a reproducible county-level healthcare-access prioritization framework for
  California using three public data sources, four transparent scoring scenarios, and
  a deployed Streamlit decision-support dashboard."

50-word version
  This project integrates CDC SVI, HRSA physician workforce, and HRSA HPSA data across
  all 58 California counties to identify where social vulnerability and limited
  primary-care access overlap. Four weighting scenarios are tested for ranking
  stability, population context is analyzed separately from scores, and results are
  delivered through a five-tab interactive Streamlit dashboard.

Résumé-ready project entry
  California Healthcare Access Priority Explorer  |  Python · SQL · Streamlit · Zerve

  · Integrated three public healthcare and demographic datasets (CDC SVI 2022, HRSA
    AHRF 2022, HRSA HPSA 2026) across all 58 California counties; validated 58 exact
    county FIPS matches with zero fuzzy joining.
  · Engineered a rank-based provider-scarcity percentile and created four transparent
    prioritization scenarios; confirmed ranking stability with pairwise Spearman
    correlations (all r > 0.89) and top-10 Jaccard overlap analysis.
  · Deployed a five-tab Streamlit decision-support dashboard with a custom weighting
    slider and dynamic scenario comparison; passed 30 deployment validation checks
    covering data integrity, temporal separation, and scoring reproducibility.
"""

section("10 · PORTFOLIO DESCRIPTION", portfolio)


# ══════════════════════════════════════════════════════════════════════════════
# 11 · SUGGESTED APPLICATION-FORM ANSWERS
# ══════════════════════════════════════════════════════════════════════════════

print(DIVIDER)
print("  11 · SUGGESTED APPLICATION-FORM ANSWERS")
print(DIVIDER)

answers = {

    "Project title": "California Healthcare Access Priority Explorer",

    "What did you build? (100–150 words)":
    """I built an end-to-end data analysis and decision-support tool that explores where
social vulnerability and limited primary-care physician access overlap across California's
58 counties. The project integrates three public datasets—the CDC/ATSDR 2022 Social
Vulnerability Index, HRSA 2022 primary-care physician data, and a current HRSA Primary
Care HPSA snapshot—then cleans, joins, and validates them into a single county-level
analytical table. Using rank-based normalization and four transparent weighting
scenarios, I produce exploratory priority scores and test their stability across
planning perspectives. The results are delivered through a five-tab interactive
Streamlit dashboard that allows stakeholders to explore individual counties, compare
scenarios, examine HPSA alignment, and read a plain-language methodology and
limitations guide. All 30 deployment validation checks passed before submission.""",

    "What problem does it solve? (75–125 words)":
    """Healthcare network planners and public-health program managers in California face a
common challenge: physician counts, population rates, social vulnerability scores, and
formal shortage designations each tell a different part of the same story, but rarely
appear in one place. This project addresses the question: which counties show the
strongest overlap between high social vulnerability and limited primary-care physician
availability, and how stable are those conclusions under different planning priorities?
By combining 2022 SVI and physician data into a reproducible, scenario-based
prioritization framework and comparing results against current HPSA designations, the
tool gives planners a transparent starting point for identifying counties that warrant
closer review—without making automatic allocation decisions.""",

    "What data did you use?":
    """Three public datasets:
  1. CDC/ATSDR Social Vulnerability Index 2022 — California county-level file,
     providing composite and four sub-theme SVI percentile rankings and ACS 2018–2022
     population estimates for all 58 counties.
  2. HRSA Area Health Resources File (AHRF) 2022 — California county-level export
     containing primary-care physician counts, Census 2022 population denominators,
     and a supplied physician rate per 100,000 residents.
  3. HRSA Primary Care Health Professional Shortage Area (HPSA) national file,
     downloaded June 25, 2026, filtered to California Designated Primary Care HPSAs
     and aggregated to the county level. Treated as a current-status external
     comparison, not a 2022 historical measure.""",

    "What tools and technologies did you use?":
    """Python (pandas, NumPy, SciPy, matplotlib, openpyxl, pypdf/pdfminer), SQL (left
joins and aggregations inside Zerve QUERY/Python blocks), Streamlit (five-tab
interactive application with dynamic custom scoring), and the Zerve platform for
modular notebook development, dependency-aware block execution, and canvas-to-deployment
variable loading via zerve.variable(). All code is written in plain, commented Python
with no proprietary tooling beyond Zerve itself.""",

    "What was the most challenging part?":
    """Three challenges stood out. First, the HRSA AHRF workbook had title and filter rows
above the actual column headers, so reading it naively produced entirely wrong column
names. Identifying the correct header row required inspecting the raw file before
writing any import code. Second, county identifiers had to be harmonized across three
sources with different formats—zero-padded FIPS strings, Excel integers, and free-text
county names—without any shared join key in the AHRF file. I resolved this with exact
name matching against the SVI dataset and verified every match explicitly. Third, the
HPSA file's structure—multiple records per HPSA ID, mixed Designated/Withdrawn status,
geographic versus facility designation types, and a 2026 reporting date against 2022
historical data—required careful filtering and classification before any county-level
aggregation was meaningful.""",

    "What did you learn?":
    """I learned how to structure a multi-source, multi-milestone data project so that each
step is reviewable before the next begins—a discipline the Zerve milestone approach
reinforced effectively. Working within a platform where AI assistance accelerates
drafting but requires active human review taught me to distinguish code that runs
correctly from analysis that is correctly framed. I also learned the value of
rank-based normalization for creating stable percentile scores when raw rates include
extreme outliers, and how Spearman correlation and Jaccard similarity can give a
quantitative sense of whether a ranking conclusion is robust or sensitive to weighting
assumptions. Deploying the analysis as a Streamlit application forced me to think about
explanation as much as computation—and that was one of the most useful parts of the
whole project.""",

    "How did you use Zerve's AI capabilities?":
    """Zerve's AI agent helped me scaffold the workflow, draft initial Python blocks,
generate validation code, organize the dashboard structure, and write documentation.
It significantly reduced the time I spent on boilerplate. However, the analytical
decisions—which FIPS field to use as the join key, how to classify HPSA designation
types, whether to sum estimated underserved populations at the county level, how to
handle the temporal gap between 2022 historical data and the 2026 HPSA snapshot, and
which scoring weights to apply—were my own. I reviewed every block output, corrected
constraints the agent initially missed (such as preventing facility HPSAs from entering
county-level shortage scores), and manually tested the deployed dashboard. The agent
accelerated execution; the analytical judgment remained mine.""",

    "What would you improve with more time?":
    """Several extensions would make the analysis more useful in practice:
  · Disaggregate to census-tract level to capture within-county variation in both
    SVI and provider access.
  · Include additional provider types: nurse practitioners, physician assistants,
    federally qualified health centers, and rural health clinics.
  · Add drive-time or travel-distance measures to capture whether residents in one
    county can realistically access providers in an adjacent one.
  · Incorporate insurance-network participation and Medicaid acceptance rates.
  · Replace physician headcount with full-time-equivalent measures when available.
  · Obtain historical HPSA snapshots to allow a true 2022-to-2022 comparison instead
    of a 2022-to-2026 cross-period alignment.
  · Build an automated refresh pipeline so the tool updates when HRSA releases new
    data.
  · Conduct external stakeholder testing with actual public-health program managers
    to validate whether the dashboard answers the questions they actually have.""",

    "Why is this relevant to the Data Analyst / Data Scientist role?":
    """Healthcare and social-services data are among the messiest real-world datasets a
data analyst encounters: nonstandard file structures, mismatched identifiers,
population denominators from different vintages, and administrative classification
systems that require careful interpretation. This project demonstrates that I can work
through those challenges systematically—inspecting before assuming, validating before
proceeding, and documenting decisions so they can be reviewed and reproduced. The
technical foundation—Python, SQL, feature engineering, percentile ranking, correlation
analysis, and Streamlit deployment—maps directly to the kind of work a data analyst or
data scientist performs day-to-day. And building the project on an AI-assisted platform
while maintaining analytical ownership reflects how modern data teams actually work:
using available tools to move faster, while staying responsible for the conclusions.""",
}

for q, a in answers.items():
    print(THIN)
    print(f"Q: {q}")
    print()
    print(textwrap.dedent(a).strip())
    print()


# ══════════════════════════════════════════════════════════════════════════════
# store as dict for reference
# ══════════════════════════════════════════════════════════════════════════════
submission_narrative = {
    "concise_summary":       concise_summary.strip(),
    "longer_description":    longer_description.strip(),
    "problem_statement":     problem_statement.strip(),
    "methodology_summary":   methodology_summary.strip(),
    "technical_skills":      technical_skills.strip(),
    "key_findings":          key_findings.strip(),
    "zerve_ai_usage":        zerve_ai_usage.strip(),
    "challenges_learning":   challenges_learning.strip(),
    "limitations":           limitations.strip(),
    "portfolio":             portfolio.strip(),
    "application_answers":   answers,
}

print(DIVIDER)
print(f"  submission_narrative dict created — {len(submission_narrative)} sections stored.")
print(DIVIDER)
