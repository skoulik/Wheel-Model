"""Monte Carlo simulator of the wheel, and the independent check on model.py.

Simulates the exact mechanics of Parts I-II on a common GBM price path, with
each lot's call strike frozen at its entry level: a put sold on the cadence
grid, assignment when it finishes in the money, and a covered call rewritten
every tau_c until the lot is called away. None of the analytic machinery is
used here -- the depth walk, the first passage and Little's law of `model.py`
are what this is meant to test -- so agreement between the two is evidence
rather than arithmetic.

`--scenario validate` is that comparison, component by component, from the
assignment rate through to the economic excess return. The other scenarios are
exploratory, and show what the analytic core cannot:

  * the emergent depth distribution of standing inventory (length-biased
    toward slow, deep layers),
  * correlated exits on the common path (a recovery flushes whole strata),
  * the shape of the holding-time distribution, fast lane to trapped tail,
  * dead-strata formation under crash-then-flatline stress.

Dividends under the total-return convention: mu is the asset's TOTAL expected
return, the price drifts at mu - delta, held lots accrue delta_net =
delta*(1 - withholding) per year of holding (reported as a separate Track A
line), and option pricing/probabilities use the dividend-yield Black-Scholes
generalization. delta = 0 reproduces the no-dividend model exactly. The
carry-vs-recovery trade-off: carry pays on held lots, but the depth drift
nu = mu - delta - sigma^2/2 shrinks with delta, so lots recycle slower and
inventory grows; nu > 0 is the stability boundary.

The cadence/tenor split is built in: cadence T >= tau_p, defaulting to
T = tau_p, the article's running example.

Stdlib only.  Run:  python code/wheel_sim.py  [--scenario base|dividends|stress|sweep|validate|all]
"""

import argparse
import heapq
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from math import exp, log, sqrt

from model import (Config, N, bs_call, bs_put, entry_law, expected_drop,
                   k_star_drift, pmap)
import random

# Event priorities at equal timestamps: settle expiring options first, then
# sample state and sell the next put.
PUTEXP, CALLEXP, SALE = 0, 1, 2

DEPTH_EDGES = [0.0, 0.02, 0.04, 0.07, 0.10, 0.15, 0.22, 0.35, float("inf")]
KM_HORIZONS_M = [3, 6, 9, 12, 24, 36, 60, 120]


@dataclass
class Regime:
    start: float
    mu: float
    sigma: float


@dataclass
class Params:
    p_star: float = 0.20
    tau_p: float = 1 / 52      # one week, matching model.Config
    n: int = 4                 # tau_c = n * tau_p = 4 weeks
    cadence: float = None      # T >= tau_p; None -> T = tau_p
    r: float = 0.05
    margin: float = 0.20
    mu: float = 0.07           # TOTAL expected return; price drifts at mu - delta
    sigma: float = 0.20
    delta: float = 0.0         # gross dividend yield
    withhold: float = 0.15     # withholding tax fraction on dividends
    iv_spread: float = 0.0     # sigma_iv = regime sigma + spread (0 = no VRP)
    years: float = 30.0
    paths: int = 200
    seed: int = 20260722
    regimes: list = None

    def __post_init__(self):
        if self.cadence is None:
            self.cadence = self.tau_p
        if self.regimes is None:
            self.regimes = [Regime(0.0, self.mu, self.sigma)]
        self.tau_c = self.n * self.tau_p
        self.delta_net = self.delta * (1 - self.withhold)
        self._starts = [rg.start for rg in self.regimes]


class Lot:
    __slots__ = ("entry", "strike", "basis", "x", "periods")

    def __init__(self, entry, strike, basis):
        self.entry = entry
        self.strike = strike
        self.basis = basis
        self.x = 0.0        # depth ln(K_c/S) at the current call's sale
        self.periods = 0    # call periods run so far


class Agg:
    """Statistics accumulated across all paths of one scenario."""

    def __init__(self):
        self.puts = 0
        self.assigned = 0
        self.d_sum = 0.0
        self.exits = 0
        self.prem_put = 0.0        # spot-normalized, summed
        self.prem_call = 0.0
        self.dividends = 0.0       # spot-normalized net dividend carry
        self.inv_hist = Counter()  # inventory level at cadence dates
        self.cap_sum = 0.0
        self.cap_n = 0
        # Economic ledger (the no-arbitrage-consistent one): inventory carried
        # at market value, the mark loss booked at acquisition, the upside
        # given away booked at call-away.  All spot-normalized when they occur.
        self.mvcap_sum = 0.0
        self.acq_loss = 0.0
        self.giveaway = 0.0
        self.inv_by_idx = Counter()    # for time profiles (stress scenario)
        self.cap_by_idx = Counter()
        self.n_by_idx = Counter()
        self.durations = []        # (months, completed?) per lot
        self.period_hist = Counter()   # call periods per *completed* lot
        self.batch_hist = Counter()    # simultaneous exits per exit date
        # depth bins: [lot-periods, exits, sum q_theory, sum x]
        self.bins = [[0, 0, 0.0, 0.0] for _ in DEPTH_EDGES[:-1]]

    def record_call_period(self, x, exited, mu, sigma, tau_c):
        b = self.bins[bisect_right(DEPTH_EDGES, x) - 1]
        q_th = N(((mu - sigma**2 / 2) * tau_c - x) / (sigma * sqrt(tau_c)))
        b[0] += 1
        b[1] += 1 if exited else 0
        b[2] += q_th
        b[3] += x


def regime_at(P, t):
    return P.regimes[max(0, bisect_right(P._starts, t + 1e-12) - 1)]


def advance(S, t0, t1, P, rng):
    """Exact GBM step from t0 to t1, split at regime boundaries."""
    if t1 - t0 <= 1e-12:
        return S
    i = max(0, bisect_right(P._starts, t0 + 1e-12) - 1)
    a = t0
    while a < t1 - 1e-12:
        b = t1 if i + 1 >= len(P._starts) else min(t1, P._starts[i + 1])
        rg = P.regimes[i]
        dt = b - a
        S *= exp((rg.mu - P.delta - rg.sigma**2 / 2) * dt
                 + rg.sigma * sqrt(dt) * rng.gauss(0.0, 1.0))
        a = b
        i += 1
    return S


def run_path(P, rng, agg):
    S, t = 1.0, 0.0
    heap = []
    seq = 0

    def push(te, prio, data):
        nonlocal seq
        heapq.heappush(heap, (te, prio, seq, data))
        seq += 1

    push(0.0, SALE, None)
    lots = []
    exits_at = Counter()

    while heap:
        te, prio, _, data = heapq.heappop(heap)
        agg.dividends += len(lots) * P.delta_net * (min(te, P.years) - t)
        if te > P.years + 1e-9:
            break
        S = advance(S, t, te, P, rng)
        t = te
        rg = regime_at(P, t)
        sig_iv = rg.sigma + P.iv_spread

        if prio == SALE:
            # Sample state at the cadence grid (after same-date settlements).
            idx = round(t / P.cadence)
            agg.inv_hist[len(lots)] += 1
            agg.inv_by_idx[idx] += len(lots)
            agg.n_by_idx[idx] += 1
            # Sell the put.  The strike dial is a real-world assignment
            # probability (the model's one measure), so k* inverts the
            # P-world probability; the premium is a quote, priced at IV.
            kf = k_star_drift(P.p_star, P.tau_p, rg.sigma, rg.mu - P.delta)
            K = kf * S
            c_p = S * bs_put(kf, P.tau_p, sig_iv, P.r, P.delta)
            agg.puts += 1
            agg.prem_put += c_p / S
            capital = P.margin * K + sum(l.basis for l in lots)
            agg.cap_sum += capital / S
            agg.cap_by_idx[idx] += capital / S
            agg.cap_n += 1
            agg.mvcap_sum += P.margin * kf + len(lots)
            push(t + P.tau_p, PUTEXP, (K, S, c_p))
            if t + P.cadence <= P.years + 1e-9:
                push(t + P.cadence, SALE, None)

        elif prio == PUTEXP:
            K, S_sale, c_p = data
            if S < K:
                agg.assigned += 1
                agg.d_sum += 1 - S / S_sale
                agg.acq_loss += (K - S) / S      # paid K for something worth S
                lot = Lot(entry=t, strike=K, basis=K - c_p)
                lots.append(lot)
                # Sell the first covered call at the frozen strike.
                c_c = bs_call(S, K, P.tau_c, sig_iv, P.r, P.delta)
                agg.prem_call += c_c / S
                lot.x = log(K / S)
                push(t + P.tau_c, CALLEXP, lot)

        else:  # CALLEXP
            lot = data
            lot.periods += 1
            exited = S >= lot.strike
            agg.record_call_period(lot.x, exited, rg.mu - P.delta, rg.sigma, P.tau_c)
            if exited:
                agg.exits += 1
                agg.giveaway += (S - lot.strike) / S   # delivered below market
                lots.remove(lot)
                agg.durations.append((round((t - lot.entry) * 12, 6), True))
                agg.period_hist[lot.periods] += 1
                exits_at[round(t, 9)] += 1
            else:
                c_c = bs_call(S, lot.strike, P.tau_c, sig_iv, P.r, P.delta)
                agg.prem_call += c_c / S
                lot.x = log(lot.strike / S)
                push(t + P.tau_c, CALLEXP, lot)

    for lot in lots:  # censored at the horizon
        agg.durations.append((round((P.years - lot.entry) * 12, 6), False))
    for cnt in exits_at.values():
        agg.batch_hist[cnt] += 1


def simulate(P):
    rng = random.Random(P.seed)
    agg = Agg()
    for _ in range(P.paths):
        run_path(P, rng, agg)
    return agg


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------

def km_survival(durations, horizons_m):
    """Kaplan-Meier survival of lot holding time (months), with censoring."""
    ds = sorted(durations)
    curve, surv, at_risk, i = [], 1.0, len(ds), 0
    while i < len(ds):
        tt = ds[i][0]
        ev = cen = 0
        while i < len(ds) and ds[i][0] == tt:
            if ds[i][1]:
                ev += 1
            else:
                cen += 1
            i += 1
        if ev:
            surv *= 1 - ev / at_risk
            curve.append((tt, surv))
        at_risk -= ev + cen
    out = []
    for h in horizons_m:
        s = 1.0
        for tt, sv in curve:
            if tt <= h:
                s = sv
            else:
                break
        out.append(s)
    return out


def as_config(P, label="sim"):
    """The analytic Config matching a simulator Params."""
    return Config(p_star=P.p_star, tau_p=P.tau_p, n=P.n, cadence=P.cadence,
                  r=P.r, mu=P.mu, sigma=P.sigma, delta=P.delta,
                  withhold=P.withhold, iv_spread=P.iv_spread,
                  margin=P.margin, label=label)


def closed_forms(P):
    """The analytic core's entry-side predictions for this configuration.

    Closed forms only -- strike, assignment probability, expected drop and
    expected entry depth -- so they cost nothing and give `report` a reference
    column without running the depth walk. Everything downstream of entry
    needs the walk, and that comparison is `--scenario validate`.

    Single-regime only: `Config` has one mu and one sigma, so there is no
    honest reference for the stress scenario and `report` prints none.
    """
    C = as_config(P)
    k, p_real, mean_x0, _ = entry_law(C, "P")
    return {"k": k, "p_real": p_real, "E[d]": expected_drop(C, "P"),
            "E[x0]": mean_x0}


def report(P, agg, name):
    M = closed_forms(P) if len(P.regimes) == 1 else None
    line = "=" * 72
    print(f"\n{line}\nScenario: {name}   "
          f"({P.paths} paths x {P.years:g}y, tau_p={P.tau_p:.4f}, "
          f"T={P.cadence:.4f}, n={P.n}, p*={P.p_star:g}, seed={P.seed})")
    for rg in P.regimes:
        print(f"  regime from t={rg.start:>5.2f}y: mu={rg.mu:+.3f} (total), "
              f"sigma={rg.sigma:.2f}, nu={rg.mu - P.delta - rg.sigma**2 / 2:+.3f}")
    if P.delta:
        print(f"  dividends: delta={P.delta:.3f} gross, withholding {P.withhold:.0%}, "
              f"delta_net={P.delta_net:.4f}")
    print(line)

    if M:
        print("\n-- Analytic core, entry side (model.py closed forms) --")
        print(f"  k*={M['k']:.4f}  p_real={M['p_real']:.3f}  "
              f"E[d]={M['E[d]']:.3f}  E[x0]={M['E[x0]']:.4f}")
    else:
        print("\n-- No analytic reference: the core assumes a single regime --")
    print("  (the full component-by-component comparison is --scenario validate)")

    n_samples = sum(agg.inv_hist.values())
    mean_I = sum(k * v for k, v in agg.inv_hist.items()) / n_samples
    p_emp = agg.assigned / agg.puts
    mean_d = agg.d_sum / max(1, agg.assigned)
    periods_per_path = n_samples / P.paths
    exits_per_period = agg.exits / n_samples
    eff_qp = exits_per_period / mean_I if mean_I > 0 else float("nan")
    run_emp = (agg.prem_put + agg.prem_call) / agg.puts
    div_emp = agg.dividends / agg.puts
    cap_emp = agg.cap_sum / agg.cap_n
    ann = (run_emp + div_emp) / P.cadence
    excess = (ann - P.r * cap_emp) / cap_emp

    ref_p = f"   (model {M['p_real']:.3f})" if M else ""
    ref_d = f"   (model {M['E[d]']:.3f})" if M else ""
    print("\n-- Simulated (layered system on the common path) --")
    print(f"  assignment rate = {p_emp:.3f}{ref_p}")
    print(f"  mean d at assignment = {mean_d:.3f}{ref_d}")
    print(f"  mean inventory  = {mean_I:.2f}")
    pi0_emp = agg.inv_hist[0] / n_samples
    print(f"  P(I=0)          = {pi0_emp:.3f}   "
          f"(Poisson at same mean {exp(-mean_I):.3f})")
    var_I = sum((k - mean_I) ** 2 * v for k, v in agg.inv_hist.items()) / n_samples
    print(f"  Var(I)/Mean(I)  = {var_I / mean_I:.2f}   (Poisson: 1.00)")
    print(f"  effective q_p   = {eff_qp:.3f}")
    print(f"  run rate/period = {run_emp:.4f}")
    if P.delta:
        print(f"  dividends/period= {div_emp:.4f}")
    print(f"  capital (avg)   = {cap_emp:.2f}")
    print(f"  annualized: income {ann:.3f} "
          f"(premiums {run_emp / P.cadence:.3f} + dividends {div_emp / P.cadence:.3f}), "
          f"excess over risk-free {excess:+.3f}/yr on capital")

    completed = sorted(m for m, c in agg.durations if c)
    censored = [m for m, c in agg.durations if not c]
    print("\n-- Holding times --")
    print(f"  lots: {len(agg.durations)} total, {len(completed)} completed, "
          f"{len(censored)} censored at horizon")
    if completed:
        med = completed[len(completed) // 2]
        p90 = completed[int(len(completed) * 0.9)]
        print(f"  completed: median {med:.1f} mo, p90 {p90:.1f} mo, max {completed[-1]:.1f} mo")
    surv = km_survival(agg.durations, KM_HORIZONS_M)
    hdr = "".join(f"{h:>7}" for h in KM_HORIZONS_M)
    row = "".join(f"{s:>7.3f}" for s in surv)
    print(f"  KM survival (months):{hdr}\n"
          f"                       {row}")
    if agg.exits:
        tot = sum(agg.period_hist.values())
        shares = "  ".join(f"{j}: {agg.period_hist[j] / tot:.3f}"
                           for j in range(1, 7))
        tail = sum(v for k_, v in agg.period_hist.items() if k_ > 6) / tot
        print(f"  call periods per completed lot:\n"
              f"    {shares}  >6: {tail:.3f}")

    if len(P.regimes) == 1:
        print("\n-- Depth structure of call periods (x = ln(K_c/S) at call sale) --")
        print("    bin           lot-periods   exit rate   q(x) theory   mean x")
        for lo, hi, b in zip(DEPTH_EDGES, DEPTH_EDGES[1:], agg.bins):
            if b[0] == 0:
                continue
            hi_s = f"{hi:.2f}" if hi != float("inf") else " inf"
            print(f"    [{lo:.2f},{hi_s})   {b[0]:>9}      {b[1] / b[0]:.3f}       "
                  f"{b[2] / b[0]:.3f}        {b[3] / b[0]:.3f}")
        tot_per = sum(b[0] for b in agg.bins)
        mean_q_inv = sum(b[2] for b in agg.bins) / tot_per
        mean_x = sum(b[3] for b in agg.bins) / tot_per
        print(f"  inventory-weighted mean q(x) = {mean_q_inv:.3f}")
        print(f"  inventory-weighted mean depth = {mean_x:.3f}  vs  entry depth "
              f"E[x0] = {M['E[x0]']:.3f}")

    multi = sum(v for k_, v in agg.batch_hist.items() if k_ >= 2)
    tot_ev = sum(agg.batch_hist.values())
    if tot_ev:
        mx = max(agg.batch_hist)
        print("\n-- Exit clustering (lots called away on the same date) --")
        print(f"  exit dates: {tot_ev}; with >=2 simultaneous exits: "
              f"{multi / tot_ev:.3f}; largest batch: {mx}")


def report_time_profile(P, agg, checkpoints):
    print("\n-- Time profile (mean over paths) --")
    print("    t(y)   mean I   mean capital")
    for y in checkpoints:
        idx = round(y / P.cadence)
        if agg.n_by_idx[idx] == 0:
            continue
        n_ = agg.n_by_idx[idx]
        print(f"   {y:>5.2f}   {agg.inv_by_idx[idx] / n_:>6.2f}   "
              f"{agg.cap_by_idx[idx] / n_:>8.2f}")


# ----------------------------------------------------------------------
# Scenarios
# ----------------------------------------------------------------------

def _sweep_row(P):
    """One row of the dividend sweep: its own simulation.  A pmap worker.

    Each row seeds its own generator from P.seed, so the row is the same
    whether the sweep runs on one core or on all of them.
    """
    agg = simulate(P)
    n_samples = sum(agg.inv_hist.values())
    mean_I = sum(k * v for k, v in agg.inv_hist.items()) / n_samples
    cap = agg.cap_sum / agg.cap_n
    prem = (agg.prem_put + agg.prem_call) / agg.puts
    div = agg.dividends / agg.puts
    excess = ((prem + div) / P.cadence - P.r * cap) / cap
    return mean_I, cap, prem, div, excess


def dividend_sweep(args):
    """Carry-vs-recovery trade-off: sweep the gross yield at fixed total return.

    The 'alt' row holds the PRICE drift at 7% instead (total return 9.5%) --
    the convention we argue against, included as a sensitivity check.
    """
    print("\n" + "=" * 72)
    print("Dividend sweep (30y, total-return convention, withholding 15%)")
    print("=" * 72)
    print("     delta     nu   mean I   capital   prem/T   div/T   excess/yr")
    rows = [("0.0%", 0.07, 0.000), ("1.0%", 0.07, 0.010), ("2.5%", 0.07, 0.025),
            ("4.0%", 0.07, 0.040), ("6.0%", 0.07, 0.060), ("alt 2.5%", 0.095, 0.025)]
    params = [Params(years=30.0, paths=args.paths or 200, seed=args.seed,
                     mu=mu, delta=delta) for _, mu, delta in rows]
    for (label, mu, delta), P, r in zip(rows, params, pmap(_sweep_row, params)):
        mean_I, cap, prem, div, excess = r
        nu = mu - delta - P.sigma**2 / 2
        print(f"  {label:>8} {nu:+.3f}   {mean_I:>6.2f}   "
              f"{cap:>7.2f}   {prem:.4f}  {div:.4f}   {excess:+.4f}")
    print("  (alt row: price drift held at 7%, i.e. total return 9.5% -- the")
    print("   stacked convention, shown as a sensitivity check only)")


def validate(args):
    """Simulation vs. the analytic core, component by component."""
    import model
    for label, ps in (("Standard", 0.20), ("Conservative", 0.10)):
        P = Params(p_star=ps, delta=0.025, years=30.0,
                   paths=args.paths or 200, seed=args.seed)
        agg = simulate(P)
        C = as_config(P, label)
        occ = model.occupation(C, "P")
        a = model.economics(C, "P", occ, horizon=P.years)

        n_samples = sum(agg.inv_hist.values())
        per_yr = 1.0 / (agg.puts * P.cadence)
        sim = {
            "assignment rate": agg.assigned / agg.puts,
            "E[d]": agg.d_sum / max(1, agg.assigned),
            "E[I]": sum(k * v for k, v in agg.inv_hist.items()) / n_samples,
            "cost capital": agg.cap_sum / agg.cap_n,
            "market capital": agg.mvcap_sum / agg.cap_n,
            "premiums/yr": (agg.prem_put + agg.prem_call) * per_yr,
            "dividends/yr": agg.dividends / (agg.puts * P.cadence),
            "acq loss/yr": agg.acq_loss * per_yr,
            "call-away loss/yr": agg.giveaway * per_yr,
        }
        ana = {
            "assignment rate": a["p_real"], "E[d]": a["E[d]"], "E[I]": a["I"],
            "cost capital": a["capital"], "market capital": a["mv_capital"],
            "premiums/yr": a["premiums"], "dividends/yr": a["dividends"],
            "acq loss/yr": a["acq_loss"],
            "call-away loss/yr": a["call_away_loss"],
        }
        sim_pnl = (sim["premiums/yr"] + sim["dividends/yr"]
                   + sim["E[I]"] * (P.mu - P.delta)
                   - sim["acq loss/yr"] - sim["call-away loss/yr"])
        sim["economic excess/yr"] = ((sim_pnl - P.r * sim["market capital"])
                                     / sim["market capital"])
        ana["economic excess/yr"] = a["econ_excess"]

        print(f"\n{'=' * 72}\nVALIDATION: {label}  ({P.paths} paths x "
              f"{P.years:g}y, seed {P.seed})\n{'=' * 72}")
        print(f"{'quantity':>20} {'simulated':>12} {'analytic':>12} {'rel.diff':>10}")
        for key in sim:
            s, v = sim[key], ana[key]
            rel = (s - v) / abs(v) if v else float("nan")
            print(f"{key:>20} {s:>12.4f} {v:>12.4f} {rel:>+9.1%}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scenario", default="all",
                    choices=["base", "dividends", "stress", "sweep",
                             "validate", "all"])
    ap.add_argument("--paths", type=int, default=None)
    ap.add_argument("--seed", type=int, default=20260722)
    args = ap.parse_args()

    if args.scenario == "validate":
        validate(args)
        return

    if args.scenario in ("base", "all"):
        P = Params(years=30.0, paths=args.paths or 200, seed=args.seed)
        report(P, simulate(P), "base (article running example: p*=20%, weekly puts / 4-week calls)")

    if args.scenario in ("dividends", "all"):
        P = Params(years=30.0, paths=args.paths or 200, seed=args.seed, delta=0.025)
        report(P, simulate(P), "base + dividends (delta=2.5%, total-return convention)")

    if args.scenario in ("sweep", "all"):
        dividend_sweep(args)

    if args.scenario in ("stress", "all"):
        # Crash-then-flatline: 2y calm, 3-month crash (expected log-drop 30%),
        # 3y flatline (mu=0), then calm again. IV assumed to track regime sigma,
        # so the p* strike policy responds to the vol spike (k* drops).
        P = Params(
            years=10.0, paths=args.paths or 300, seed=args.seed,
            regimes=[
                Regime(0.00, 0.07, 0.20),
                Regime(2.00, log(0.7) / 0.25, 0.35),
                Regime(2.25, 0.00, 0.20),
                Regime(5.25, 0.07, 0.20),
            ],
        )
        agg = simulate(P)
        report(P, agg, "crash-then-flatline stress")
        report_time_profile(
            P, agg,
            [1.0, 2.0, 2.25, 2.5, 3.0, 4.0, 5.0, 5.25, 6.0, 7.0, 8.0, 10.0])


if __name__ == "__main__":
    main()
