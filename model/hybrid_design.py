"""Price, quantity or both: calibrating a tiered, capped digital euro.

Marginal social cost of moving bank deposits into digital euro has three segments:
  0      for aggregate outflow X <= X0   (absorbed by banks at no cost)
  e      for X0 < X <= L                 (deposit funding replaced at extra cost e)
  cliff  for X > L                       (bank liquidity buffers exhausted)
Each segment maps to one instrument: a free tier M1, a Pigouvian rate -e above it,
and a hard cap Mbar. All three are calibrated to euro-area data below.

Data
  Sight deposits per person: median 2,000, mean 13,100        (ECB WP 2980, SPACE survey)
  Desired digital euro holdings: median 560, mean 3,220       (ECB WP 2980, deposit-like case)
  Flight-to-safety outflows: 156bn at 500, 699bn at 3,000     (ECB technical data, Oct 2025)
  699bn = 8.2% of retail sight deposits                       (same)
  Digitalisation inflow to deposits by 2034: 127bn            (same)
  MRO 2.65% (16 Sep 2026); household overnight deposits 0.26% (ECB MIR, Apr 2026)
  Aggregate LCR 156.7% (Q3 2025)                              (ECB supervisory statistics)
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq, least_squares

# ---------- data ----------
DEP_MEDIAN, DEP_MEAN = 2_000, 13_100
WANT_MEDIAN, WANT_MEAN = 560, 3_220
FTS = {500: 156e9, 3_000: 699e9}
RETAIL_SIGHT = 699e9 / 0.082
X0 = 127e9
MRO, R_D = 0.0265, 0.0026
LCR_NOW = 1.567


def lognormal_from(median, mean):
    mu = np.log(median)
    return mu, np.sqrt(2 * np.log(mean / median))


def e_min(mu, s, m):
    """E[min(X, m)] for X lognormal(mu, s)."""
    if np.isinf(m):
        return np.exp(mu + s * s / 2)
    a = (np.log(m) - mu) / s
    return np.exp(mu + s * s / 2) * norm.cdf(a - s) + m * (1 - norm.cdf(a))


def share_above(mu, s, m):
    return 1 - norm.cdf((np.log(m) - mu) / s)


# deposits: distribution from the survey; population fitted to the two ECB outflow figures
MU_DEP, S_DEP = lognormal_from(DEP_MEDIAN, DEP_MEAN)
N = least_squares(lambda n: [n[0] * e_min(MU_DEP, S_DEP, m) / v - 1 for m, v in FTS.items()],
                  x0=[3.6e8]).x[0]
MU_W, S_W = lognormal_from(WANT_MEDIAN, WANT_MEAN)

E = MRO - R_D                       # marginal cost of replacing deposit funding
K = np.sqrt(R_D / (R_D + E))        # Baumol-Tobin shrink factor for tier-2 balances


def crisis_outflow(cap):
    return N * e_min(MU_DEP, S_DEP, cap)


def cap_for(theta):
    return brentq(lambda m: crisis_outflow(m) - theta * RETAIL_SIGHT, 1, 1e7)


def normal_holdings(m1, cap, tiered):
    """Aggregate holdings in normal times; tier-2 demand shrinks by K under the Pigouvian rate."""
    if not tiered:
        return N * e_min(MU_W, S_W, cap)
    tier1 = e_min(MU_W, S_W, m1)
    # E[(min(t, cap') - m1)^+] where cap' is the cap expressed in desired units
    cap_w = m1 + (cap - m1) / K if np.isfinite(cap) else np.inf
    tier2 = K * (e_min(MU_W, S_W, cap_w) - e_min(MU_W, S_W, m1))
    return N * (tier1 + tier2)


def constrained(m1, cap, tiered):
    if np.isinf(cap):
        return 0.0
    cap_w = m1 + (cap - m1) / K if tiered else cap
    return share_above(MU_W, S_W, cap_w)


def negative_rate_outflow(m1, cap, tiered):
    """Deposit rates <= 0: a zero-rate unit beats deposits, so balances move up to the zero-rate ceiling."""
    zero_ceiling = m1 if tiered else cap
    return N * e_min(MU_DEP, S_DEP, zero_ceiling)


def main():
    print(f"fit: deposit sigma {S_DEP:.2f}, N {N / 1e6:.0f}m "
          f"(check: 500 -> {crisis_outflow(500) / 1e9:.0f}bn, 3000 -> {crisis_outflow(3000) / 1e9:.0f}bn)")
    print(f"desired holdings sigma {S_W:.2f}; share wanting > 3,000: {share_above(MU_W, S_W, 3000):.0%}")
    print(f"e = MRO - r_D = {E:.2%}; tier-2 shrink factor K = {K:.2f}")

    m1_for = lambda x0: brentq(lambda m: N * e_min(MU_W, S_W, m) - x0, 1, 1e5)
    m1 = m1_for(X0)
    print(f"\nfree tier M1 (payments outflow = {X0 / 1e9:.0f}bn): {m1:,.0f}")
    for x0 in (100e9, 200e9, 300e9):
        print(f"  sensitivity: X0 {x0 / 1e9:.0f}bn -> M1 {m1_for(x0):,.0f}")
    print(f"Pigouvian tier-2 rate: -{E:.2%}")
    print("cap by crisis tolerance theta (share of retail sight deposits):")
    for theta in (0.05, 0.076, 0.10):
        print(f"  theta {theta:.1%}: cap {cap_for(theta):,.0f}")

    theta_now = crisis_outflow(3000) / RETAIL_SIGHT
    print(f"\ncountercyclical cap: theta scales with the LCR surplus (anchored at 3,000 today, theta {theta_now:.1%})")
    for lcr in (1.30, 1.45, LCR_NOW, 1.70, 1.85):
        theta = theta_now * (lcr - 1) / (LCR_NOW - 1)
        print(f"  LCR {lcr:.0%}: theta {theta:.1%}, cap {cap_for(theta):,.0f}")

    designs = {
        "cap only (0%, 3,000)": (3000, 3000, False),
        "price only (tier M1, -e)": (m1, np.inf, True),
        "hybrid (tier M1, -e, cap 3,000)": (m1, 3000, True),
    }
    print("\n                                  normal: holdings  constrained | negative rates | crisis")
    for name, (a, cap, tiered) in designs.items():
        print(f"  {name:32s} {normal_holdings(a, cap, tiered) / 1e9:6.0f}bn  {constrained(a, cap, tiered):6.1%}"
              f"   | {negative_rate_outflow(a, cap, tiered) / 1e9:6.0f}bn      | {crisis_outflow(cap) / 1e9:6.0f}bn")
    print(f"  (payments tolerance X0: {X0 / 1e9:.0f}bn)")


if __name__ == "__main__":
    main()
