# Price, quantity or both: derivation and calibration

Code: `model/hybrid_design.py` (all numbers below are printed by it).

## 1. Why one instrument is not enough (Weitzman 1974)

Let aggregate digital-euro holdings be `q`. Marginal benefit `MB(q) = b0 + θ − b q`, marginal social cost `MC(q) = c0 + c q`, demand shock `θ` with variance `σ²`.

- Quantity rule (cap at the expected optimum): expected loss `σ² / (2(b + c))`.
- Price rule (rate at the expected optimum): holdings move with `θ`, expected loss `σ² c² / (2 b² (b + c))`.
- Advantage of prices over quantities:

      Δ = σ² (b − c) / (2 b²)

  **Prices win when the benefit curve is steeper (b > c); quantities win when the cost curve is steeper (c > b).**

For the digital euro both cases occur along the same curve:

| Region of holdings | Benefit slope | Cost slope | Better instrument |
|---|---|---|---|
| Small payment balances | steep (people need money to pay) | flat (absorbed by banks) | price, set at zero |
| Store-of-value balances | flat (a substitute for deposits) | flat at `e` | price, set at the cost `−e` |
| Beyond bank liquidity buffers | flat | vertical (a run) | quantity, a hard cap |

The demand shock is largest exactly in a crisis (flight to safety), when the cost curve is vertical, so the cap does its work there. Roberts & Spence (1976) show that a price schedule combined with a quantity ceiling dominates either instrument on its own. For the digital euro this means **tiered remuneration with a cap**.

## 2. Three segments of marginal cost → three instruments

Let the aggregate outflow from deposits be `X`. Its marginal social cost is

    MC(X) = 0      for X ≤ X0      (banks absorb it at no cost)
          = e      for X0 < X ≤ L  (deposit funding replaced at extra cost e)
          = ∞      for X > L       (liquidity buffers exhausted)

Decentralising the planner's optimum gives one instrument per segment:

1. **Free tier `M1`**: zero rate on the first `M1`, chosen so that payment holdings use exactly the free capacity:
   `N · E[min(t, M1)] = X0`, where `t` is a person's desired holding.
2. **Pigouvian tier-2 rate `−e`**: holders of balances above `M1` pay the marginal cost they impose.
   Under Baumol–Tobin demand `m ∝ s^{-1/2}`, tier-2 balances shrink by `K = √(r_D / (r_D + e))`.
3. **Hard cap `M̄`**: crisis outflow stays within tolerance,
   `N · E[min(d, M̄)] = θ · D`, where `d` is a person's sight deposit, `D` is total retail sight deposits, and `θ` is the tolerated outflow share.

## 3. Data

| Item | Value | Source |
|---|---|---|
| Sight deposits per person | median €2,000, mean €13,100 | ECB WP 2980 (Lambert et al. 2024), SPACE survey |
| Desired digital-euro holdings | median €560, mean €3,220; 80% below €3,000 | ECB WP 2980, deposit-like case |
| Flight-to-safety outflow | €156bn at a €500 limit, €699bn at €3,000 (8.2% of retail sight deposits) | ECB technical data on holding limits, 9 Oct 2025 |
| Digitalisation inflow to deposits by 2034 | €127bn | same |
| Main refinancing rate | 2.65% (from 16 Sep 2026) | ECB key rates |
| Household overnight deposit rate | 0.26% (Apr 2026) | ECB MIR statistics |
| Aggregate LCR | 156.7% (Q3 2025) | ECB supervisory banking statistics |
| Household overnight deposits | €5.4tn (Dec 2025) | ECB |
| All deposits swapped, no limit | ≈ €5tn of reserves needed | Meller & Soons (2023) |

**Fit.** Lognormal distributions from the survey medians and means; population `N` fitted to the two ECB outflow figures.
Result: `N = 360m`, which matches the 2026 euro-area population (359.6m). The model reproduces €156bn at €500 and gives €648bn at €3,000 (ECB: €699bn). It also gives €1,086 as average holdings under a €3,000 cap (paper: €1,100) and 18% of people wanting more than €3,000 (paper: 20%).

## 4. Calibrated design

- `e = MRO − r_D = 2.65% − 0.26% = 2.39%`, an upper bound on the bank's cost of replacing deposit funding. Tier-2 balances shrink by `K = 0.31`.
- **Free tier**: with `X0 = €127bn` (the digitalisation inflow, so banks end up no worse off than today), `M1 ≈ €510`.
  Sensitivity: `X0` of €100bn / €200bn / €300bn gives `M1` of €370 / €960 / €1,840.
- **Tier-2 rate**: `−2.4%`.
- **Cap by crisis tolerance**: `θ` of 5% / 7.6% / 10% gives `M̄` of €1,690 / €3,000 / €4,520.

### Design comparison

| Design | Normal times: holdings | Users constrained | Negative rates: outflow | Crisis: outflow |
|---|---|---|---|---|
| Cap only (0%, €3,000) | €391bn | 18.5% | €648bn | €648bn |
| Price only (tier €510, −2.4%) | €450bn | 0% | €158bn | **€4.7tn** |
| Hybrid (tier €510, −2.4%, cap €3,000) | €280bn | 7.3% | €158bn | €648bn |

The hybrid gets the cap's crisis protection and the price's protection when rates are negative. It also constrains fewer users than the cap alone, because tier-2 demand shrinks.

### Countercyclical cap
Tolerance scales with the banks' liquidity surplus: `θ_t = θ_0 · (LCR_t − 1) / (LCR_0 − 1)`, anchored at €3,000 for today's 157%.

| Aggregate LCR | 130% | 145% | 157% | 170% | 185% |
|---|---|---|---|---|---|
| Cap | €1,280 | €2,170 | €3,000 | €4,100 | €5,560 |

## 5. Caveats
- `e` is the private cost of replacing deposit funding; the social cost may be lower if central-bank pass-through funding keeps lending intact (Brunnermeier & Niepelt 2019; Helmich 2026).
- The negative-rate column assumes deposit rates ≤ 0 make every zero-rate euro preferable to a deposit.
- The LCR scaling rule is illustrative; the actual tolerance should come from bank-level stress tests.
