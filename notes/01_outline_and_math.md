# Use It or Lose It? — outline and model notes

## 0. Verified facts

- European Commission proposal for a Regulation on the establishment of the digital euro (28 June 2023),
  **Art. 16(8): "The digital euro shall not bear interest."**
- As of 30 Sep 2026: Council position adopted 19 Dec 2025, Parliament position July 2026, trilogues running
  (13 Jul, 10 Sep, 30 Sep 2026), aim to conclude by end-2026. Both sides want a holding limit; they disagree
  on who sets it. Range under discussion: about €1,500–3,000.
- ECB deposit facility rate was −0.50% from Sep 2019 to Jul 2022.
- The ECB commits to keeping cash.

## 1. Storyline (slide titles, 20 minutes)

1. Use it or lose it? (0:30)
2. Money with an expiry date gets spent, and fast. (1:30)
3. A digital euro could build the same pressure into money itself, by an expiry date or by continuous decay. (1:30)
4. To compare them, take a holder who searches for good uses of money and can always dump it at a loss. (2:00)
5. An expiry date pushes out more spending, but ends in a fire sale and splits money into vintages. (2:00)
6. Continuous decay keeps every euro equal, and it is nothing more than a negative interest rate. (2:00)
7. As a rate, decay is far too weak to replicate a voucher: money can carry a rate, not a stimulus programme. (1:45)
8. So the real question is the digital euro's interest rate, and the draft regulation fixes it at zero. (1:15)
9. A zero-rate digital euro is cash without storage costs, which lifts the lower bound back to zero. (2:30)
10. A negative digital-euro rate can win that space back, but no more while cash still exists. (2:00)
11. The best design keeps zero as the default and lets balances above a threshold decay when policy rates turn negative. (2:00)
12. The digital euro should be able to bear interest: only as decay, and only when rates are negative. (1:00)

## 2. Expiry vs demurrage: model and results

Code: `model/expiry_vs_demurrage.py`. Figure: `figures/expiry_vs_demurrage.{pdf,png}`.

### 2.1 Setup
- Per-unit token value `V`. Holders search for useful purchases with intensity `κ`, cost `κ²/(2a)` per unit balance per day. A useful purchase is worth 1.
- A junk outlet (low-value goods, dumping on a secondary market) is always available at `φ < 1`.
- Discount rate `r`.

**Hard expiry** (remaining time `τ = T − t`):

    dV/dτ = −rV + a(1−V)²/2,   V(0) = φ   (unspent balance is dumped at φ on day T)

**Demurrage** at rate `λ` (stationary):

    (r + λ) V = a(1−V)²/2

In both regimes optimal velocity is `κ* = a(1 − V)`.

### 2.2 Analytical result: square-root rule
For small `r + λ`, demurrage gives `κ* ≈ √(2a(r + λ))`: **velocity has elasticity 1/2 with respect to the holding cost**, the Baumol–Tobin elasticity.

| λ (p.a.) | 0.5% | 1% | 2% | 3% | 5% |
|---|---|---|---|---|---|
| Velocity multiplier (r = 4%) | 1.06 | 1.12 | 1.22 | 1.32 | 1.49 |

### 2.3 Equal-average-velocity comparison (a = 0.2, φ = 0.5, r = 4%)

| T | Expiry: useful | dumped | waste (1−φ)·dumped | κ_T/κ_0 | value range | Demurrage: λ p.a. | useful | burned | value |
|---|---|---|---|---|---|---|---|---|---|
| 7 d | 45% | 55% | 27% | 1.3 | 0.50–0.63 | 1172% | 41% | 15% | 0.57 |
| 14 d | 66% | 35% | 17% | 1.7 | 0.50–0.71 | 842% | 58% | 17% | 0.62 |
| 30 d | 84% | 16% | 8% | 2.5 | 0.50–0.80 | 489% | 73% | 16% | 0.69 |
| 90 d | 97% | 3% | 2% | 5.3 | 0.50–0.91 | 161% | 88% | 10% | 0.81 |

Sensitivity at T = 30 (φ ∈ {0.3, 0.5, 0.7}, a ∈ {0.1, 0.2, 0.4}): matching λ is 211%–833% p.a.; expiry always front-loads more and always wastes 3%–16% of issuance.

### 2.4 Interpretation — correcting the original intuition

**"Hard expiry is a disaster, demurrage dominates" does not hold.** Expiry delivers *more* useful spending within T, because it forces the whole balance out, while demurrage burns part of it.

What survives robustly:
1. **Real waste.** Expiry causes junk spending at T, a social loss of (1−φ)·dumped (up to 27% of issuance). Demurrage's burned balances are a transfer to the issuer; with V > φ there is no junk spending.
2. **Singleness of money.** An expiring token's value depends on its vintage; units are no longer fungible. Under demurrage all units have the same value.
3. **Velocity path.** Expiry: rising velocity and a mass point at T. Demurrage: constant. With convex search costs velocity is *finite* (bounded by a(1−φ)); "velocity → ∞" only holds with linear costs.
4. **Is it a rate?** Demurrage is stationary and applies to the whole stock: it is the rate i = −λ. Expiry cannot apply to the whole money stock without vintages: it is a fiscal-programme tool.

Magnitude: voucher-strength velocity needs 160%–1,200% p.a. demurrage; policy-sized rates move velocity by 6%–32%. Two to three orders of magnitude.

## 3. Lower-bound argument

Deposit-rate floor from the best central-bank outside option `j` (rate `i_j`, holding cost `c_j`):

    r_D ≥ max_j { i_j − c_j }

- Cash: floor −c_cash (the ELB).
- Digital euro under Art. 16(8): floor 0 on balances up to the limit M̄ — **hardens the lower bound**.
- Digital euro at −λ: floor max{−λ, −c_cash} ≥ −c_cash.

Asymmetry: zero remuneration raises the floor from −c_cash to 0; negative remuneration cannot push it below −c_cash while cash exists. Going deeper needs cash reform (Agarwal–Kimball crawling cash/reserve exchange rate).

Disintermediation pressure from a zero-rate digital euro peaks in negative-rate regimes; zero remuneration and the holding limit are a package.

## 4. Policy proposal (for discussion)
Keep i_DE = 0 by default. If DFR < 0, balances above a tier threshold M₁ < M̄ pay max{DFR, −c̄}, implemented as continuous demurrage, never as expiry.

## 5. Open items
- Calibrate a and φ from voucher redemption and resale-discount data.
- Estimate c_cash from the 2019–22 pass-through to large deposits.
- General-equilibrium extension (prices, output).
