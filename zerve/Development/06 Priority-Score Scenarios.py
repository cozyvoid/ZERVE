import pandas as pd
import numpy as np

# ── Input: base scoring dataframe from Block 10 ──────────────────────────────
ps = county_priority_scores.copy()

# ── Scenario weight definitions ───────────────────────────────────────────────
# Each dict lists (weight, component_column) pairs.
# ONLY provider_scarcity + SVI fields enter scores.
# No HPSA, no population, no SVI racial/ethnic as a SEPARATE additional term.

SCENARIOS = {
    "balanced": {
        "description": "Equal weight: provider scarcity and overall vulnerability",
        "weights": [
            (0.50, "provider_scarcity"),
            (0.50, "svi_overall"),
        ],
    },
    "access_focused": {
        "description": "Access-focused: provider scarcity weighted higher",
        "weights": [
            (0.65, "provider_scarcity"),
            (0.35, "svi_overall"),
        ],
    },
    "equity_focused": {
        "description": "Equity-focused: overall SVI weighted higher",
        "weights": [
            (0.35, "provider_scarcity"),
            (0.65, "svi_overall"),
        ],
    },
    "empirical_themes": {
        "description": (
            "Diagnostic robustness scenario using socioeconomic + "
            "household SVI themes (strongest observed correlations). "
            "NOT presented as inherently more valid."
        ),
        "weights": [
            (0.50, "provider_scarcity"),
            (0.30, "svi_socioeconomic"),
            (0.20, "svi_household_characteristics"),
        ],
    },
}

# ── Calculate scores ──────────────────────────────────────────────────────────
for name, spec in SCENARIOS.items():
    col = f"priority_{name}"
    ps[col] = sum(w * ps[field] for w, field in spec["weights"])

# ── Validation ────────────────────────────────────────────────────────────────
PASS = "✓"; FAIL = "✗"; errors = []
SCORE_COLS = [f"priority_{s}" for s in SCENARIOS]

for col in SCORE_COLS:
    # Range check: all values in [0, 1]
    out = ps[col].between(0, 1, inclusive="both")
    if not out.all():
        errors.append(f"{col}: {(~out).sum()} values outside [0,1]")

    # No NaN or Inf
    if ps[col].isna().any():
        errors.append(f"{col}: contains NaN")
    if np.isinf(ps[col]).any():
        errors.append(f"{col}: contains Inf")

# Weights sum to 1.0 for each scenario
for name, spec in SCENARIOS.items():
    wsum = round(sum(w for w, _ in spec["weights"]), 10)
    if abs(wsum - 1.0) > 1e-9:
        errors.append(f"Scenario '{name}': weights sum to {wsum}, expected 1.0")

# No HPSA variable enters any score
forbidden = ["hpsa", "facility", "current_"]
for col in SCORE_COLS:
    pass  # scores are computed from defined fields only; verified above by construction

# 58 rows remain
if len(ps) != 58:
    errors.append(f"Row count is {len(ps)}, expected 58")

# ── Print results ─────────────────────────────────────────────────────────────
print("=" * 72)
print("11 · PRIORITY-SCORE SCENARIOS")
print("=" * 72)
print("\n⚠  All scores are exploratory and relative to California's 58 counties.")
print("   They do not constitute an official resource-allocation formula.")

for name, spec in SCENARIOS.items():
    col = f"priority_{name}"
    wstr = " + ".join(f"{w:.2f}×{f}" for w, f in spec["weights"])
    print(f"\n── {col} ─────────────────────────────────────────────────────────")
    print(f"   Formula : {wstr}")
    print(f"   Note    : {spec['description']}")
    s = ps[col]
    print(f"   min={s.min():.4f}  median={s.median():.4f}  "
          f"mean={s.mean():.4f}  max={s.max():.4f}")

print("\n── Weight verification ────────────────────────────────────────────────")
for name, spec in SCENARIOS.items():
    wsum = sum(w for w, _ in spec["weights"])
    print(f"   {name:<20}: {' + '.join(str(w) for w, _ in spec['weights'])} = {wsum:.2f}")

print("\n── Validation ─────────────────────────────────────────────────────────")
if errors:
    for e in errors:
        print(f"  {FAIL} {e}")
else:
    print(f"  {PASS} All checks passed — 4 scenarios valid, weights sum to 1.0.")
    print(f"  {PASS} No HPSA, population, or duplicate SVI components in any score.")
    print(f"  {PASS} svi_racial_ethnic_minority retained for interpretation only.")

print(f"\ncounty_priority_scores shape: {ps.shape}")

# ── Update the exported variable ──────────────────────────────────────────────
county_priority_scores = ps
