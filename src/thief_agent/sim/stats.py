"""Bootstrap confidence intervals for rates and paired differences (deterministic)."""

from ..strategy.rng import make_rng


def _percentiles(samples, lo=0.025, hi=0.975):
    samples.sort()
    b = len(samples)
    return [round(samples[int(lo * b)], 4), round(samples[min(int(hi * b), b - 1)], 4)]


def rate_ci(values, boots: int = 1000, seed: int = 0):
    """Bootstrap 95% CI for the mean of 0/1 outcomes."""
    n = len(values)
    if n == 0:
        return [0.0, 0.0]
    rng = make_rng(seed)
    means = []
    for _ in range(boots):
        acc = sum(values[rng.randrange(n)] for _ in range(n))
        means.append(acc / n)
    return _percentiles(means)


def paired_diff_ci(base, cand, boots: int = 1000, seed: int = 0):
    """Bootstrap 95% CI for mean(cand - base) over the SAME scenarios (paired)."""
    diffs = [c - b for b, c in zip(base, cand, strict=True)]
    n = len(diffs)
    if n == 0:
        return [0.0, 0.0]
    rng = make_rng(seed)
    means = []
    for _ in range(boots):
        acc = sum(diffs[rng.randrange(n)] for _ in range(n))
        means.append(acc / n)
    return _percentiles(means)
