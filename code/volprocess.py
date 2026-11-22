"""The fitted volatility process, for the simulator: step 5(b) of the moving-volatility plan.

What `volfit.py` fitted on the Aristocrats (step 4, `data/aristocrats/volfit-final.json`) and
`earnmoves.py` measured at their earnings dates (step 5(a), `earnmoves.json`), pinned here so
that the simulator (`wheel_sim.py --vol fitted`) and its pricing tables (`fairprice.py`) step
one process, and neither needs the calibration's data. Stdlib only.

**A session** is a fifth of a week, so the article's weekly put spans 5 and its four-week call
20. The fit's parameters are per session, its jump rates per 252 sessions, and they are used
as they stand; a year here is 260 sessions.

**The state** is two factors of log volatility, H = h_fast + h_slow (clipped at ±H_CLIP as in
the fit), and σ_t = σ̄·e^H is the session's diffusive sd. A session's log return is

    c_t + σ_t·z + σ̄·e^(β·H)·J + σ̄·e^(β_E·H)·Y,

z standard normal; J an unscheduled jump, up with probability λ↑/252 and exponential of
mean a↑, down with probability λ↓/252 and mean a↓, at most one a session; Y the earnings
jump, on the first session of each earnings window only, up with probability p_E and
exponential of mean a_E↑, down otherwise with mean a_E↓. The factors move with the session's
move alone:

    h′ = φ·h + share·θ·x + share′·kick·[down jump],    x = z + e^((β−1)·H)·J − κ_t,

with κ_t = 0 in the real world. Under the pricing measure κ_t = (μ − r)·Δt/σ_t: the shift of z
that moves the drift from μ − δ to r − δ (decision 4: only the stock's own diffusive risk is
priced), and h, a function of the price path, follows the shifted shocks. The earnings jump
does not enter x: volatility does not kick after earnings (step 5(a)).

**c_t** makes each session's expected gross return exactly e^(m·Δt), m the measure's price
drift: m·Δt − σ_t²/2 − ln E[e^(σ̄·e^(βH)·J)], and on an earnings session − ln E[e^(σ̄·e^(β_E·H)·Y)]
too, each conditional on H. So the forward of every option is exact, under either measure.

**σ̄** is set so that the year's total variance -- diffusion, jumps and earnings -- averages σ²
over the stationary state (`fairprice.moments` computes the averages), and the article's σ
stays the stock's whole volatility.
"""

from math import exp, log, sqrt

SESSIONS = 260                  # sessions in a year here: five a week
FIT_SESSIONS = 252              # the fit's: its jump rates are per this many
DT = 1.0 / SESSIONS
H_CLIP = 4.0
EARNINGS_EVERY = 65             # sessions between earnings dates: 13 weeks
BURN = 1300                     # sessions stepped before a path starts: five years

# Step 4's final model (volfit-final.json, distance 13.6 over 48 statistics; errors in
# volfit-final-se.json): two factors with no shocks of their own, gamma and feedback zero,
# no up-jump kick, Kou jumps with one beta for both sides.
FIT = {
    "half-life fast": 6.139274219010805,        # sessions
    "slow/fast": 16.88341094401715,
    "theta fast share": 0.7061418857964165,
    "kick fast share": 0.6948226539970196,      # volfit's "gamma fast share"
    "theta": -0.02876249714854998,
    "lambda up": 1.3626499911752408,            # a year of FIT_SESSIONS
    "a up": 1.7740796544471,
    "lambda down": 6.342404448900048,
    "a down": 2.0175687652063647,
    "beta": 0.582210206561832,
    "kick down": 0.6312946216490363,
}

# Step 5(a)'s earnings law in the model's units (earnmoves.json "model units": the law
# whose fit on fake samples of the fitted model reproduces the data's).
EARN = {
    "p up": 0.5232870388018941,
    "a up": 4.726524536350869,
    "a down": 5.218412016866676,
    "beta E": 0.24995465986074433,
}


class Process:
    """The fitted process at one scale. `jumps` and `earnings` switch those parts off, for
    attribution; `sig_bar` is σ̄, set by `fairprice` from the stationary averages."""

    def __init__(self, sig_bar, jumps=True, earnings=True, earn_feedback=None):
        """`earn_feedback`, (c0, c1) or None: an earnings term in h, after Ederington and
        Lee — on an earnings session h falls c0 for the expected part and rises c1 per unit
        of surprise beyond the typical move, split between the factors as the down-jump
        kick is (`earnmoves.feedback_dh`, which fits it). Off in the model; on only to
        measure what leaving it out costs the wheel (`wheel_sim.py --scenario earnterm`)."""
        f = FIT
        self.sig_bar = sig_bar
        self.jumps, self.earnings = jumps, earnings
        self.efb = earn_feedback
        self.kf_share = f["kick fast share"]
        self.ey = EARN["p up"] * EARN["a up"] + (1 - EARN["p up"]) * EARN["a down"]
        self.phi_f = 0.5 ** (1.0 / f["half-life fast"])
        self.phi_s = 0.5 ** (1.0 / (f["half-life fast"] * f["slow/fast"]))
        self.th_f = f["theta fast share"] * f["theta"]
        self.th_s = (1.0 - f["theta fast share"]) * f["theta"]
        self.k_f = f["kick fast share"] * f["kick down"] if jumps else 0.0
        self.k_s = (1.0 - f["kick fast share"]) * f["kick down"] if jumps else 0.0
        self.pu = f["lambda up"] / FIT_SESSIONS if jumps else 0.0
        self.pd = f["lambda down"] / FIT_SESSIONS if jumps else 0.0
        self.au, self.ad, self.beta = f["a up"], f["a down"], f["beta"]
        self.pe, self.aeu, self.aed, self.be = (EARN["p up"], EARN["a up"],
                                                EARN["a down"], EARN["beta E"])

    def log_jump_mgf(self, H):
        """ln E[e^(σ̄·e^(βH)·J)] for one session at state H."""
        if not self.jumps:
            return 0.0
        s = self.sig_bar * exp(self.beta * H)
        return log(1.0 - self.pu - self.pd + self.pu / (1.0 - s * self.au)
                   + self.pd / (1.0 + s * self.ad))

    def log_earn_mgf(self, H):
        """ln E[e^(σ̄·e^(β_E·H)·Y)] for an earnings session at state H."""
        s = self.sig_bar * exp(self.be * H)
        return log(self.pe / (1.0 - s * self.aeu) + (1.0 - self.pe) / (1.0 + s * self.aed))

    def step(self, logS, hf, hs, m, excess, earn, rng):
        """One session from (log S, h_fast, h_slow): the new triple. m is the price drift of
        the measure (μ − δ, or r − δ); `excess` is (μ − r)·Δt under the pricing measure and 0
        in the real world; `earn` marks an earnings session. Draws what the session needs
        and hands it to `advance`."""
        z = rng.gauss(0.0, 1.0)
        u = rng.random()
        w = rng.expovariate(1.0) if u < self.pu + self.pd else 0.0
        if earn and self.earnings:
            ue, we = rng.random(), rng.expovariate(1.0)
        else:
            ue = we = 0.0
        return self.advance(logS, hf, hs, m, excess, earn, z, u, w, ue, we)

    def advance(self, logS, hf, hs, m, excess, earn, z, u, w, ue, we):
        """`step` given its draws: z standard normal, u uniform (which jump, if any), w unit
        exponential (its size), ue and we the same for the earnings jump. `fairprice`
        steps the same arithmetic on arrays, and its check runs both on one set of draws."""
        H = hf + hs
        H = H_CLIP if H > H_CLIP else -H_CLIP if H < -H_CLIP else H
        sd = self.sig_bar * exp(H)
        ret = m * DT - 0.5 * sd * sd + sd * z
        x = z - excess / sd
        down = False
        if self.jumps:
            ret -= self.log_jump_mgf(H)
            if u < self.pu:
                J = self.au * w
            elif u < self.pu + self.pd:
                J = -self.ad * w
                down = True
            else:
                J = 0.0
            if J:
                sj = self.sig_bar * exp(self.beta * H)
                ret += sj * J
                x += sj * J / sd
        if earn and self.earnings:
            se = self.sig_bar * exp(self.be * H)
            Y = (self.aeu if ue < self.pe else -self.aed) * we
            ret += se * Y - self.log_earn_mgf(H)
        hf = self.phi_f * hf + self.th_f * x + (self.k_f if down else 0.0)
        hs = self.phi_s * hs + self.th_s * x + (self.k_s if down else 0.0)
        if earn and self.earnings and self.efb:
            dh = -self.efb[0] + self.efb[1] * max(abs(Y) / self.ey - 1.0, 0.0)
            hf += self.kf_share * dh
            hs += (1.0 - self.kf_share) * dh
        return logS + ret, hf, hs

    def annual_vol(self, hf, hs):
        """The diffusive volatility ruling now, annualized -- for reporting only."""
        H = max(-H_CLIP, min(H_CLIP, hf + hs))
        return self.sig_bar * exp(H) * sqrt(SESSIONS)


class Tables:
    """Fair prices at the state, read from `fairprice`'s tables: log implied volatility on
    a grid of the two factors (and, for the call, standardized moneyness), interpolated
    linearly in each. Phase j > 0: earnings fall on the j-th session of the option's life;
    0: none in it."""

    def __init__(self, data):
        self.data = data
        self.hf0, self.dhf, self.nf = data["hf"][0], data["hf"][1] - data["hf"][0], len(data["hf"])
        self.hs0, self.dhs, self.ns = data["hs"][0], data["hs"][1] - data["hs"][0], len(data["hs"])
        self.u0, self.du, self.nu = data["u"][0], data["u"][1] - data["u"][0], len(data["u"])
        self.put_logk = data["put"]["logk"]         # [phase][i][j]
        self.put_lniv = data["put"]["lniv"]
        self.call_lniv = {int(t): g for t, g in data["call"]["lniv"].items()}
        # ...each [phase][i][j][k], by the sessions of the call's life left
        self.u_scale = data["u scale"]              # x / u: the run's sigma * sqrt(tau_c)
        self.sig_bar = data["sig bar"]

    @staticmethod
    def _axis(v, v0, dv, n):
        """Linear: (first node, weight of the second), clamped to the grid."""
        a = (v - v0) / dv
        if a <= 0.0:
            return 0, 0.0
        if a >= n - 1:
            return n - 2, 1.0
        i = int(a)
        return i, a - i

    @staticmethod
    def _cubic(v, v0, dv, n):
        """Four-point Lagrange: (first node, its four weights), clamped to the grid. Log
        implied volatility is convex in the state, so linear interpolation would price
        every option off a node a little high; cubic takes that error from about 0.1% to
        nothing measurable (`fairprice --check`)."""
        a = min(max((v - v0) / dv, 0.0), n - 1.0)
        i = min(max(int(a) - 1, 0), n - 4)
        t = a - i
        return i, (-(t - 1) * (t - 2) * (t - 3) / 6, t * (t - 2) * (t - 3) / 2,
                   -t * (t - 1) * (t - 3) / 2, t * (t - 1) * (t - 2) / 6)

    def _bicubic(self, grid, hf, hs):
        i, wi = self._cubic(hf, self.hf0, self.dhf, self.nf)
        j, wj = self._cubic(hs, self.hs0, self.dhs, self.ns)
        v = 0.0
        for a in range(4):
            row = grid[i + a]
            v += wi[a] * (wj[0] * row[j] + wj[1] * row[j + 1] + wj[2] * row[j + 2]
                          + wj[3] * row[j + 3])
        return v

    def put(self, hf, hs, phase):
        """(strike / spot, implied volatility) of the put at the dial p*."""
        return (exp(self._bicubic(self.put_logk[phase], hf, hs)),
                exp(self._bicubic(self.put_lniv[phase], hf, hs)))

    def call_iv(self, hf, hs, phase, x, sessions=20):
        """Implied volatility of the call at depth x = ln(K/S) with `sessions` of its life
        left (20 is tau_c): cubic in the state, linear in the standardized depth."""
        i, wi = self._cubic(hf, self.hf0, self.dhf, self.nf)
        j, wj = self._cubic(hs, self.hs0, self.dhs, self.ns)
        k, c = self._axis(x / self.u_scale, self.u0, self.du, self.nu)
        g = self.call_lniv[sessions][phase]
        v = 0.0
        for a in range(4):
            ga = g[i + a]
            for b in range(4):
                row = ga[j + b]
                v += wi[a] * wj[b] * ((1 - c) * row[k] + c * row[k + 1])
        return exp(v)

    @staticmethod
    def _cubic_slope(v, v0, dv, n):
        """The four Lagrange weights' derivatives in v, as `_cubic` places them."""
        a = min(max((v - v0) / dv, 0.0), n - 1.0)
        i = min(max(int(a) - 1, 0), n - 4)
        t = a - i
        return i, (-((t - 2) * (t - 3) + (t - 1) * (t - 3) + (t - 1) * (t - 2)) / 6 / dv,
                   ((t - 2) * (t - 3) + t * (t - 3) + t * (t - 2)) / 2 / dv,
                   -((t - 1) * (t - 3) + t * (t - 3) + t * (t - 1)) / 2 / dv,
                   ((t - 1) * (t - 2) + t * (t - 2) + t * (t - 1)) / 6 / dv)

    def call_iv_grad(self, hf, hs, phase, x, sessions=20):
        """(iv, d iv/d h_fast, d iv/d h_slow, d iv/d x) of `call_iv`, for an option's
        delta through both its channels."""
        i, wi = self._cubic(hf, self.hf0, self.dhf, self.nf)
        _, di = self._cubic_slope(hf, self.hf0, self.dhf, self.nf)
        j, wj = self._cubic(hs, self.hs0, self.dhs, self.ns)
        _, dj = self._cubic_slope(hs, self.hs0, self.dhs, self.ns)
        k, c = self._axis(x / self.u_scale, self.u0, self.du, self.nu)
        g = self.call_lniv[sessions][phase]
        v = vf = vs = vx = 0.0
        for a in range(4):
            ga = g[i + a]
            for b in range(4):
                row = ga[j + b]
                lin = (1 - c) * row[k] + c * row[k + 1]
                slope = (row[k + 1] - row[k]) / (self.du * self.u_scale)
                v += wi[a] * wj[b] * lin
                vf += di[a] * wj[b] * lin
                vs += wi[a] * dj[b] * lin
                vx += wi[a] * wj[b] * slope
        iv = exp(v)
        return iv, iv * vf, iv * vs, iv * vx
