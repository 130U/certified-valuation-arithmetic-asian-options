"""Proxy-exercise value and kink bound in closed form under Black's model.

The fixings are S_i = F_i exp(-v^2 t_i / 2 + v W(t_i)) at 0 < t_1 < ... < t_n,
with forwards F_i = spot * exp(carry * t_i).  A is their arithmetic mean and G
their geometric mean.  For a strike K and a scale c,

    proxy value       L_c(K) = D E[(A - K) 1{cG > K}],
    cost of the kink  R_c(K) = D E[(A - K)^+] - L_c(K) >= 0,

and Theorem 3.3 of the paper bounds the cost in two ways,

    R_c(K) <= D K E[d(A / cG)] / (sigma sqrt(2 pi)),      d(x) = x - 1 - log x,
    R_c(K) <= D E[(A - cG)^2] / (2 K sigma sqrt(2 pi)),

where sigma = v sqrt(t_1) is the volatility of the return before the first
fixing.  A put has the same cost.  Every term is an elementary function of the
inputs, which are exact rationals (the model input is the variance rate v^2).
The same formulas run in binary64 and in Arb ball arithmetic; in the second
case each result is a proved enclosure of the stated real number.
"""
from fractions import Fraction
import math


class FloatOps:
    """Binary64 evaluation."""
    name = 'binary64'

    @staticmethod
    def num(q):
        return float(q)

    exp = staticmethod(math.exp)
    log = staticmethod(math.log)
    sqrt = staticmethod(math.sqrt)

    @staticmethod
    def Phi(x):
        return 0.5 * math.erfc(-x / math.sqrt(2.0))

    @staticmethod
    def pi():
        return math.pi


class BallOps:
    """Arb ball arithmetic: every value is a midpoint with a rigorous radius."""
    name = 'arb'

    def __init__(self, bits=256):
        from flint import arb, fmpq, ctx
        ctx.prec = bits
        self._arb, self._fmpq = arb, fmpq
        self.bits = bits

    def num(self, q):
        q = Fraction(q)
        return self._arb(self._fmpq(q.numerator, q.denominator))

    @staticmethod
    def exp(x):
        return x.exp()

    @staticmethod
    def log(x):
        return x.log()

    @staticmethod
    def sqrt(x):
        return x.sqrt()

    def Phi(self, x):
        return (-x / self._arb(2).sqrt()).erfc() / 2

    def pi(self):
        return self._arb.pi()


class Contract:
    """Fixing dates and Black inputs, all exact rationals."""

    def __init__(self, times, spot, variance, carry=0, rate=0):
        self.times = [Fraction(t) for t in times]
        assert self.times[0] > 0 and all(a < b for a, b in zip(self.times, self.times[1:]))
        self.spot, self.variance = Fraction(spot), Fraction(variance)
        self.carry, self.rate = Fraction(carry), Fraction(rate)
        self.n = len(self.times)

    def discount(self, ops):
        return ops.exp(ops.num(-self.rate * self.times[-1]))


def _gaussian_terms(ops, contract):
    """Means and covariances of the log fixings and of Y = log G."""
    n, times = contract.n, contract.times
    v2 = ops.num(contract.variance)
    t = [ops.num(x) for x in times]
    F = [ops.num(contract.spot) * ops.exp(ops.num(contract.carry * x)) for x in times]
    mins = [[min(a, b) for b in times] for a in times]
    gamma = [v2 * ops.num(sum(row) / n) for row in mins]            # Cov(log S_i, Y)
    sY2 = v2 * ops.num(sum(sum(row) for row in mins) / n ** 2)      # Var(Y)
    mu = [ops.log(F[i]) - v2 * t[i] / 2 for i in range(n)]          # E log S_i
    muY = sum(mu[1:], mu[0]) / n
    return {'n': n, 't': t, 'F': F, 'v2': v2, 'mins': mins,
            'gamma': gamma, 'sY2': sY2, 'sY': ops.sqrt(sY2), 'mu': mu, 'muY': muY}


def proxy_value(ops, contract, strike, scale, kind='call'):
    """D E[(A - K) 1{cG > K}] for a call, D E[(K - A) 1{cG <= K}] for a put."""
    g = _gaussian_terms(ops, contract)
    n, K = g['n'], ops.num(strike)
    k = ops.log(K / scale)
    sign = 1 if kind == 'call' else -1
    total = None
    for i in range(n):
        term = g['F'][i] * ops.Phi(sign * (g['muY'] + g['gamma'][i] - k) / g['sY'])
        total = term if total is None else total + term
    value = sign * (total / n - K * ops.Phi(sign * (g['muY'] - k) / g['sY']))
    return contract.discount(ops) * value


def dispersion_moments(ops, contract):
    """Moments of X = A/G (dimensionless) and of the pair (A, G) (price units)."""
    g = _gaussian_terms(ops, contract)
    n, v2, mins = g['n'], g['v2'], g['mins']
    m = [g['mu'][i] - g['muY'] for i in range(n)]
    w = [v2 * g['t'][i] + g['sY2'] - 2 * g['gamma'][i] for i in range(n)]
    EX = EX2 = EAA = EAG = None
    for i in range(n):
        x = ops.exp(m[i] + w[i] / 2)
        ag = g['F'][i] * ops.exp(g['muY'] + g['sY2'] / 2 + g['gamma'][i])
        EX = x if EX is None else EX + x
        EAG = ag if EAG is None else EAG + ag
        for j in range(n):
            cov = v2 * ops.num(mins[i][j]) - g['gamma'][i] - g['gamma'][j] + g['sY2']
            x2 = ops.exp(m[i] + m[j] + (w[i] + w[j]) / 2 + cov)
            aa = g['F'][i] * g['F'][j] * ops.exp(v2 * ops.num(mins[i][j]))
            EX2 = x2 if EX2 is None else EX2 + x2
            EAA = aa if EAA is None else EAA + aa
    return {'EX': EX / n, 'EX2': EX2 / n ** 2, 'EAA': EAA / n ** 2, 'EAG': EAG / n,
            'EGG': ops.exp(2 * g['muY'] + 2 * g['sY2']),
            'sigma': ops.sqrt(v2 * g['t'][0])}


def bregman_majorant(ops, EX, EX2, scale):
    """An upper bound for E[d(X/c)], using log x >= (x - 1) - (x - 1)^2 / 2 on x >= 1."""
    return EX / scale - 1 + ops.log(scale) - (EX - 1) + (EX2 - 2 * EX + 1) / 2


def kink_bounds(ops, contract, strike, scale=None):
    """Both bounds of Theorem 3.3, each at the scale that minimizes it unless one is given."""
    d = dispersion_moments(ops, contract)
    K, D = ops.num(strike), contract.discount(ops)
    peak = d['sigma'] * ops.sqrt(2 * ops.pi())
    c_log = d['EX'] if scale is None else scale
    c_quad = d['EAG'] / d['EGG'] if scale is None else scale
    log_form = D * K * bregman_majorant(ops, d['EX'], d['EX2'], c_log) / peak
    quad_form = D * (d['EAA'] - 2 * c_quad * d['EAG'] + c_quad ** 2 * d['EGG']) / (2 * K * peak)
    return {'log_form': log_form, 'quadratic_form': quad_form,
            'scale_log': c_log, 'scale_quadratic': c_quad,
            'EX': d['EX'], 'var_X': d['EX2'] - d['EX'] ** 2, 'sigma': d['sigma']}


def cubic_law(contract):
    """v^3 tau^2 / (360 sqrt(2 pi t_1)): the log-form bound per unit strike at leading order."""
    lead = float(contract.times[0])
    window = float(contract.times[-1] - contract.times[0])
    return float(contract.variance) ** 1.5 * window ** 2 / (360.0 * math.sqrt(2.0 * math.pi * lead))


def first_order_bound(contract, nodes=96):
    """(D/2) E[sd(A | G)]: the Rogers-Shi form of the classical conditioning error bound."""
    import numpy as np
    g = _gaussian_terms(FloatOps, contract)
    n = g['n']
    mu, gamma, sY2 = np.array(g['mu']), np.array(g['gamma']), g['sY2']
    cov = g['v2'] * np.array([[float(x) for x in row] for row in g['mins']]) - np.outer(gamma, gamma) / sY2
    x, wts = np.polynomial.hermite_e.hermegauss(nodes)
    total = 0.0
    for xi, wi in zip(x, wts):
        mean = np.exp(mu + gamma / math.sqrt(sY2) * xi + 0.5 * np.diag(cov))
        var = (np.outer(mean, mean) * np.expm1(cov)).sum() / n ** 2
        total += wi * math.sqrt(max(var, 0.0))
    return contract.discount(FloatOps) * 0.5 * total / math.sqrt(2.0 * math.pi)


def simulated_cost(contract, strike, scale, paths=1 << 20, seed=20261113):
    """Monte Carlo estimate of R_c(K); the first-period factor is integrated exactly on each path."""
    import numpy as np
    from scipy.special import ndtr
    rng = np.random.default_rng(seed)
    g = _gaussian_terms(FloatOps, contract)
    t, mu = np.array(g['t']), np.array(g['mu'])
    v, K, c = math.sqrt(g['v2']), float(strike), float(scale)
    sigma = v * math.sqrt(t[0])
    steps = np.sqrt(np.diff(t))
    chunk = max(1 << 12, (1 << 22) // contract.n)
    total = total_sq = 0.0
    done = 0
    while done < paths:
        m = min(chunk, paths - done)
        path = np.cumsum(rng.standard_normal((m, len(t) - 1)) * steps, axis=1)
        logs = mu + v * np.concatenate([np.zeros((m, 1)), path], axis=1)
        a = np.exp(logs).mean(axis=1)
        b = c * np.exp(logs.mean(axis=1))
        da, db = np.log(a / K) / sigma, np.log(b / K) / sigma
        growth = math.exp(0.5 * sigma ** 2)
        gap = a * growth * (ndtr(da + sigma) - ndtr(db + sigma)) - K * (ndtr(da) - ndtr(db))
        total += gap.sum()
        total_sq += (gap * gap).sum()
        done += m
    mean = total / paths
    se = math.sqrt(max(total_sq / paths - mean * mean, 0.0) / paths)
    D = contract.discount(FloatOps)
    return D * mean, D * se
