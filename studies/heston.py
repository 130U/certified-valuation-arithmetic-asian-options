"""Heston calculations in binary64: simulated dispersion and Fourier proxy values.

Two tools.

`conditional_paths` simulates what is left of a path once the independent
stock noise before the first fixing has been integrated out: the shape
a_1, ..., a_n of the fixings and the volatility sigma of the common factor.
Call prices, proxy values and the cost of the kink are then smooth functions
of (a, g, sigma), so their sample means carry no payoff kink.

`proxy_spread_value` evaluates the proxy-exercise value of a call spread by
transform inversion, under the continuous model (exact Riccati flow) and under
the Euler kernel without projection (explicit Euler steps of the same Riccati
equation).  With the inversion design of the paper's Appendix C it reproduces
the finite sums of the certified package to the last printed digits of binary64.

Nothing here is a certificate; the proved intervals are in `code/`.
"""
import math

import numpy as np
from scipy.special import ndtr


def conditional_paths(paths, fixing_steps, h, S0, r, kappa, vbar, xi, rho, v0, seed, chunk=1 << 15):
    """Return (a, I1): shapes a_i (paths x n) and first-period integrated variance.

    Absorbed Euler with step h; `fixing_steps` are the step indices of the fixings.
    Conditional on the returned quantities, S(t_i) = a_i exp(U) with
    U ~ N(0, (1 - rho^2) I1).
    """
    rng = np.random.default_rng(seed)
    n, first, last = len(fixing_steps), fixing_steps[0], fixing_steps[-1]
    s = math.sqrt(1.0 - rho * rho)
    a = np.empty((paths, n))
    I1 = np.empty(paths)
    done = 0
    while done < paths:
        m = min(chunk, paths - done)
        V = np.full(m, float(v0))
        logp = np.zeros(m)
        acc = np.zeros(m)
        k = 0
        for j in range(last):
            G = rng.standard_normal(m)
            sq = np.sqrt(V * h)
            logp += (r - 0.5 * V) * h + rho * sq * G
            if j < first:
                acc += V * h
            else:
                logp += s * sq * rng.standard_normal(m)
            V = np.maximum((1.0 - kappa * h) * V + kappa * vbar * h + xi * sq * G, 0.0)
            if j + 1 == fixing_steps[k]:
                a[done:done + m, k] = S0 * np.exp(logp)
                k += 1
        I1[done:done + m] = acc
        done += m
    return a, I1


def coupled_levels(paths, levels, n, dt, S0, r, kappa, vbar, xi, rho, v0, seed, chunk=1 << 14):
    """Absorbed Euler at several step sizes driven by the same Brownian increments.

    `levels` are steps per fixing interval, each dividing the last; the n fixings
    are dt apart, the first at time dt.  Yields, chunk by chunk, a list with one
    pair (a, I1) per level.
    """
    fine = levels[-1]
    ratios = [fine // m for m in levels]
    assert all(fine % m == 0 for m in levels)
    rng = np.random.default_rng(seed)
    s = math.sqrt(1.0 - rho * rho)
    hf = dt / fine
    done = 0
    while done < paths:
        m = min(chunk, paths - done)
        V = [np.full(m, float(v0)) for _ in levels]
        logp = [np.zeros(m) for _ in levels]
        I1 = [np.zeros(m) for _ in levels]
        dW = [np.zeros(m) for _ in levels]
        dB = [np.zeros(m) for _ in levels]
        a = [np.empty((m, n)) for _ in levels]
        for j in range(n * fine):
            w = rng.standard_normal(m) * math.sqrt(hf)
            b = rng.standard_normal(m) * math.sqrt(hf) if j >= fine else None
            for l, ratio in enumerate(ratios):
                dW[l] += w
                if b is not None:
                    dB[l] += b
                if (j + 1) % ratio:
                    continue
                h = hf * ratio
                root = np.sqrt(V[l])
                logp[l] += (r - 0.5 * V[l]) * h + rho * root * dW[l]
                if j < fine:
                    I1[l] += V[l] * h
                else:
                    logp[l] += s * root * dB[l]
                V[l] = np.maximum((1.0 - kappa * h) * V[l] + kappa * vbar * h + xi * root * dW[l], 0.0)
                dW[l][:] = 0.0
                dB[l][:] = 0.0
                if (j + 1) % fine == 0:
                    a[l][:, (j + 1) // fine - 1] = S0 * np.exp(logp[l])
        yield [(a[l], I1[l]) for l in range(len(levels))]
        done += m


def conditional_call(a, sigma, K):
    """E[(a e^U - K)^+] for U ~ N(0, sigma^2): the conditional call of Proposition 3.2."""
    d = np.log(a / K) / sigma
    return a * np.exp(0.5 * sigma * sigma) * ndtr(d + sigma) - K * ndtr(d)


def conditional_proxy(a, b, sigma, K):
    """E[(a e^U - K) 1{b e^U > K}]: exercise decided by the proxy b e^U."""
    d = np.log(b / K) / sigma
    return a * np.exp(0.5 * sigma * sigma) * ndtr(d + sigma) - K * ndtr(d)


def mean_se(x):
    x = np.asarray(x, dtype=float)
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x)))


# ---------------------------------------------------------------------------
# Transform inversion for the proxy value of a call spread
# ---------------------------------------------------------------------------

def _riccati_exact(A, B, q, dt, r, kappa, vbar, xi, rho, pieces=8):
    """Advance exp(A + B v) backward over an interval of length dt with stock loading q."""
    alpha, d = 0.5 * xi * xi, kappa * vbar
    kq = kappa - rho * xi * q
    D = np.sqrt(kq * kq - 2.0 * xi * xi * 0.5 * (q * q - q))
    t = dt / pieces
    ch, sh = np.cosh(0.5 * D * t), np.sinh(0.5 * D * t)
    for _ in range(pieces):
        c = (kq - 2.0 * alpha * B) / D
        den = ch + c * sh
        A = A + r * q * t + d * (0.5 * kq * t - np.log(den)) / alpha
        B = kq / (2.0 * alpha) - (0.5 * D * (sh + c * ch) / den) / alpha
    return A, B


def _riccati_euler(A, B, q, steps, h, r, kappa, vbar, xi, rho):
    """The same interval under the Euler kernel: explicit Euler steps of the Riccati system."""
    alpha, d = 0.5 * xi * xi, kappa * vbar
    kq, gq = kappa - rho * xi * q, 0.5 * (q * q - q)
    for _ in range(steps):
        A, B = A + h * (r * q + d * B), B + h * (alpha * B * B - kq * B + gq)
    return A, B


def proxy_spread_value(S0, r, kappa, vbar, xi, rho, v0, fixing_times, K1, K2, scale,
                       euler_steps_per_interval=None, damping=0.5, du=0.2, N=640):
    """Discounted E[psi(cG) + (A - cG) 1{K1 < cG <= K2}] by damped inversion.

    `fixing_times` must be equally spaced starting one interval after time zero.
    With `euler_steps_per_interval` set, the transforms are those of the Euler
    kernel without projection; otherwise those of the continuous model.
    """
    n = len(fixing_times)
    dt = fixing_times[0]
    T = fixing_times[-1]
    z = damping + 1j * du * np.arange(N + 1)
    wts = np.ones(N + 1)
    wts[0] = 0.5
    y1, y2 = math.log(K1 / (scale * S0)), math.log(K2 / (scale * S0))
    # rows: profile 0 is E exp(-z Y); profile i is E exp(Z_i - z Y), with Y = mean of the Z_j
    A = np.zeros((n + 1, N + 1), dtype=complex)
    B = np.zeros((n + 1, N + 1), dtype=complex)
    for k in range(n, 0, -1):                       # interval (t_{k-1}, t_k]
        q = np.empty((n + 1, N + 1), dtype=complex)
        q[:] = -z * (n - k + 1) / n
        for i in range(k, n + 1):
            q[i] += 1.0
        if euler_steps_per_interval:
            A, B = _riccati_euler(A, B, q, euler_steps_per_interval, dt / euler_steps_per_interval,
                                  r, kappa, vbar, xi, rho)
        else:
            A, B = _riccati_exact(A, B, q, dt, r, kappa, vbar, xi, rho)
    transforms = np.exp(A + B * v0)
    front = math.exp(-r * T) * du * wts / (math.pi * z)
    coef0 = front * (K1 * np.exp(z * y1) - K2 * np.exp(z * y2))
    coefA = front * (S0 / n) * (np.exp(z * y2) - np.exp(z * y1))
    total = (coef0 * transforms[0]).real.sum() + (coefA * transforms[1:].sum(axis=0)).real.sum()
    return math.exp(-r * T) * (K2 - K1) + float(total)
