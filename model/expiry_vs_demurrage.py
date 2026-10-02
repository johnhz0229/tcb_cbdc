"""Hard expiry vs continuous demurrage for programmable money.

Per-unit value V of a token. Holders search for useful spending at intensity
kappa (cost kappa^2 / 2a per unit balance per day); a useful purchase is worth
1 per unit. A "junk" outlet (low-value goods / dumping on a secondary market)
is always available and is worth phi < 1 per unit. r is the time discount rate.

Hard expiry (tau = T - t remaining):
    dV/dtau = -r V + a (1 - V)^2 / 2,   V(0) = phi   (remaining balance dumped at T)
Demurrage lambda (stationary):
    (r + lambda) V = a (1 - V)^2 / 2
In both cases optimal velocity is kappa* = a (1 - V); for small r + lambda the
stationary case gives kappa* ~ sqrt(2 a (r + lambda)), a Baumol-Tobin-type
square-root rule.

Comparison: lambda is calibrated so that demurrage delivers the same average
velocity over [0, T] as the expiring voucher.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = 0.04 / 365      # discount rate per day (~4%/yr)
A = 0.2             # search-efficiency parameter
PHI = 0.5           # value of junk spending per unit
T = 30              # voucher lifetime, days (default for the figure)
DT = 0.01


def expiry_value(tau_grid):
    sol = solve_ivp(lambda tau, v: -R * v + A * (1 - v) ** 2 / 2,
                    (0, tau_grid[-1]), [PHI], t_eval=tau_grid, rtol=1e-10, atol=1e-12)
    return sol.y[0]


def demurrage_value(lam):
    # positive root of (r+lam) V = a (1-V)^2 / 2 lying in (0, 1)
    f = lambda v: (R + lam) * v - A * (1 - v) ** 2 / 2
    return max(brentq(f, 0.0, 1.0), PHI)


def simulate_expiry(T=T):
    t = np.arange(0, T + DT, DT)
    v = expiry_value(T - t[::-1])[::-1]          # V as a function of calendar time
    kappa = A * (1 - v)
    m = np.exp(-np.concatenate([[0], np.cumsum(kappa[:-1] * DT)]))
    useful = kappa * m                            # spending flow on useful goods
    dumped_at_T = m[-1]                           # mass point at T
    return t, v, kappa, m, useful, dumped_at_T


def simulate_demurrage(lam, horizon):
    t = np.arange(0, horizon + DT, DT)
    v = demurrage_value(lam)
    kappa = A * (1 - v)
    m = np.exp(-(kappa + lam) * t)
    useful = kappa * m
    return t, v, kappa, m, useful


def compare(T):
    t_e, v_e, k_e, m_e, s_e, dump = simulate_expiry(T)
    k_avg = np.mean(k_e)
    lam = brentq(lambda l: A * (1 - demurrage_value(l)) - k_avg, 0.0, 1.0)
    t_d, v_d, k_d, m_d, s_d = simulate_demurrage(lam, T)
    return dict(T=T, lam=lam, useful_e=np.sum(s_e) * DT, dump=dump, junk_loss=(1 - PHI) * dump,
                peak_ratio=k_e[-1] / k_e[0], v_min=v_e.min(), v_max=v_e.max(),
                useful_d=np.sum(s_d) * DT, left_d=m_d[-1], burned_d=1 - m_d[-1] - np.sum(s_d) * DT,
                v_d=v_d, k_d=k_d), (t_e, v_e, k_e, s_e, t_d, v_d, k_d, s_d)


def main():
    global PHI, A
    print("T  | expiry: useful  junk-dump  junk-loss  kappa_T/kappa_0  V range   "
          "| demurrage (same avg velocity): lambda/yr  useful  burned  still held  V")
    for horizon in (7, 14, 30, 90):
        c, _ = compare(horizon)
        print(f"{horizon:<3}| {c['useful_e']:.3f}  {c['dump']:.3f}  {c['junk_loss']:.3f}  {c['peak_ratio']:.1f}"
              f"  {c['v_min']:.2f}-{c['v_max']:.2f} | {c['lam'] * 365:7.0%}  {c['useful_d']:.3f}"
              f"  {c['burned_d']:.3f}  {c['left_d']:.3f}  {c['v_d']:.3f}")

    print("\nmonetary-policy-scale demurrage (no expiry): velocity relative to lambda = 0")
    k0 = A * (1 - demurrage_value(0.0))
    for lam_yr in (0.005, 0.01, 0.02, 0.03, 0.05):
        k = A * (1 - demurrage_value(lam_yr / 365))
        print(f"  lambda = {lam_yr:.1%}/yr: velocity x{k / k0:.2f}"
              f"  (sqrt rule predicts x{np.sqrt((R + lam_yr / 365) / R):.2f})")

    print("\nsensitivity at T = 30 days (junk value phi, search efficiency a)")
    base = (PHI, A)
    for phi, a in ((0.3, 0.2), (0.5, 0.2), (0.7, 0.2), (0.5, 0.1), (0.5, 0.4)):
        PHI, A = phi, a
        c, _ = compare(30)
        print(f"  phi={phi:.1f} a={a:.1f}: expiry useful {c['useful_e']:.2f}, dumped {c['dump']:.2f},"
              f" waste {c['junk_loss']:.2f}, V {c['v_min']:.2f}-{c['v_max']:.2f} | demurrage lambda"
              f" {c['lam'] * 365:.0%}/yr, useful {c['useful_d']:.2f}, burned {c['burned_d']:.2f}")
    PHI, A = base

    c, (t_e, v_e, k_e, s_e, t_d, v_d, k_d, s_d) = compare(T)
    plt.rcParams.update({"font.size": 12})
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.9))
    ax[0].plot(t_e, k_e, label="expiry date")
    ax[0].axhline(k_d, color="C1", label=f"decay, λ={c['lam']*365:.0%}/yr")
    ax[0].annotate(f"{c['dump']:.0%} of issuance\ndumped at φ on day T", xy=(T, k_e[-1]),
                   xytext=(T * 0.05, k_e[-1] * 0.9), arrowprops=dict(arrowstyle="->"))
    ax[0].set(title="Velocity κ(t)", xlabel="day")
    ax[0].legend(loc="lower right", fontsize=11)
    ax[1].plot(t_e, s_e, label="expiry date")
    ax[1].plot(t_d, s_d, label="continuous decay")
    ax[1].set(title="Useful spending (share/day)", xlabel="day")
    ax[1].legend(fontsize=11)
    ax[2].plot(t_e, v_e, label="expiry date")
    ax[2].axhline(v_d, color="C1", label="continuous decay")
    ax[2].axhline(PHI, color="grey", ls="--", label="junk value φ")
    ax[2].set(title="Value of one unit V(t)", xlabel="day", ylim=(0.4, 1.02))
    ax[2].legend(fontsize=11)
    fig.tight_layout()
    fig.savefig("figures/expiry_vs_demurrage.png", dpi=150)
    fig.savefig("figures/expiry_vs_demurrage.pdf")


if __name__ == "__main__":
    main()
