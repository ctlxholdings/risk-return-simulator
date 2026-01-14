# EMBOUCHE MODEL BUG ANALYSIS
## Root Cause: "Trading Position" vs "Capital Loss" Logic

**Date:** 2026-01-09  
**Status:** Analysis Complete — Fix Required

---

## EXECUTIVE SUMMARY

The embouche model was incorrectly modified from a "capital loss" model (correct) to a "trading position" model (incorrect), resulting in unrealistic downside risk:

| Metric | v2.1 (Correct) | v3.1 (Broken) |
|--------|----------------|---------------|
| Embouche P10 | **-71.5%** | +5.7% |
| Model Type | Capital Loss | Trading Position |

**Root cause:** Conceptual error treating embouche like rental property (bad month = no rent, asset remains) instead of consumable livestock (animal dies = capital destroyed).

---

## THE TWO MODELS

### Model A: Capital Loss (CORRECT — v2.0/v2.1)

```
When p_loss_total triggers:
  - Calf dies → animal lost (300k)
  - Sunk costs lost (150k feed/vet/other)
  - n_units decreases by 1
  - Must buy replacement calf to continue
  
Total loss per death: 450k FCFA
Effect: Permanent capital destruction
```

**Code behavior (v2.1):**
```python
if roll < p_loss:
    losses_this_cycle += 1  # Count the death
# After cycle:
n_units -= losses_this_cycle  # Units permanently reduced
```

### Model B: Trading Position (INCORRECT — v3.1)

```
When p_loss_total triggers:
  - Cycle "fails" → no profit this cycle
  - Revenue reduced by loss amount
  - n_units stays constant
  - Same calf continues next cycle
  
Total loss per death: 450k deducted from revenue
Effect: Temporary setback, capital preserved
```

**Code behavior (v3.1):**
```python
if roll < p_loss:
    cycle_revenue -= total_position_loss  # Deduct from revenue
# n_units never decreases for embouche
```

---

## WHY MODEL B IS WRONG

### The Rental Property Analogy

Model B treats embouche like immobilier:
- Bad month → tenant doesn't pay → lose rent revenue
- Building still exists → try again next month

This works for immobilier because the asset (building) persists.

### The Reality of Embouche

Embouche is a **consumable asset**:
- Death event → calf dies → animal is gone
- Cannot "try again" with same calf
- Must purchase replacement (300k) plus restart working capital (150k)
- Total capital at risk per unit: 450k

### Numerical Impact

With Model B "trading position" logic:
- Year 1: 2 calves × 3 cycles × 20% death rate = ~1.2 death events
- Each death: deduct 450k from revenue, but keep 2 calves
- Year 2: Still have 2 calves (incorrectly)
- Compound effect: Unrealistic resilience

With Model A "capital loss" logic:
- Year 1: Same death events
- Each death: n_units reduced
- Without replacement: 0 calves possible by Year 3
- Compound effect: Realistic capital destruction

---

## ASSET TREATMENT COMPARISON

| Asset | Type | On Death | v3.1 Treatment | Correct? |
|-------|------|----------|----------------|----------|
| Immobilier | Durable | Lose building (500k), n_units-- | Capital loss | ✓ |
| Bétail | Durable | Lose cow (250k), n_units-- | Capital loss | ✓ |
| Embouche | Consumable | Lose calf (300k) + working capital (150k) | Trading position (no n_units--) | ✗ |

**Inconsistency:** Embouche uniquely treated as "position" while others use "capital loss".

---

## ORIGIN OF THE BUG

### Session: 2026-01-08-22-45-55 (v3.0→v3.1)

The fix session introduced the concept:

```python
# Line 132 comment:
# Est-ce que c'est de l'embouche? (modèle positions de trading)

# Lines 159-162 comments:
# EMBOUCHE: Modèle positions de trading avec perte sur échec
# Chaque unité = position ouverte
# Échec = perte du working capital (feed + vet + other = 150k)
# n_units reste constant (on réouvre la position)
```

**Intent:** Fix missing capital loss in embouche
**Error:** Introduced "trading position" mental model instead of using standard capital loss

---

## FILE LOCATIONS

| Version | Path | Embouche P10 |
|---------|------|--------------|
| v2.1 (correct) | /mnt/project/simulate.py | -71.5% |
| v2.1 results | /mnt/project/results.json | -71.5% |
| v3.1 (broken) | /home/claude/simulate.py | +5.7% |
| v3.1 results | /home/claude/results.json | +5.7% |

---

## RECOMMENDED FIX

**Option 1: Revert to v2.1 logic**
- Copy /mnt/project/simulate.py
- Unified treatment: all assets use n_units-- on death

**Option 2: Fix v3.1**
- Remove "trading position" concept
- Add `losses_this_cycle += 1` for embouche deaths
- Add `n_units -= losses_this_cycle` after embouche cycle
- Remove special `total_position_loss` deduction

**Validation criteria:**
- Embouche P10 should be approximately -70% to -75%
- Embouche should have highest volatility of all assets
- Order: Embouche vol > Bétail vol > Immobilier vol

---

## CHARTS AFFECTED

All charts showing embouche with reinvestment or P10/volatility metrics are incorrect in v3.1:
- Chart C (Risk-Return scatter)
- Chart D (Risk zones)
- Chart B (Wealth accumulation with reinvest)
- Chart E (Comparison with/without reinvest)
- Storytelling charts (malchanceux, ecart, chute)

The /mnt/project/ charts using v2.1 results remain correct.

---

## CONCLUSION

The embouche model bug stems from a conceptual error: applying "trading position" logic to a consumable asset. The fix is straightforward — restore standard capital loss treatment where n_units decreases when an animal dies, consistent with how immobilier and bétail are modeled.
