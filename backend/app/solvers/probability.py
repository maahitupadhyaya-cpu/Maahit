"""Probability solver: binomial distribution and normal distribution queries."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import plotly.graph_objects as go
import sympy as sp
from sympy.stats import Binomial, Normal, P
from sympy.stats import cdf as sp_cdf
from sympy.stats import density as sp_density

from .utils import ProblemParseError, clean_text, latex


def _find_float(pattern: str, text: str) -> Optional[float]:
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return None
    try:
        return float(m.group(1))
    except (ValueError, IndexError):
        return None


def _binomial_bounds(text: str) -> Tuple[str, Any]:
    m = re.search(r"between\s+(\d+)\s+and\s+(\d+)", text, re.IGNORECASE)
    if m:
        return "range", (int(m.group(1)), int(m.group(2)))
    m = re.search(r"exactly\s+(\d+)", text, re.IGNORECASE)
    if m:
        return "eq", int(m.group(1))
    m = re.search(r"at least\s+(\d+)", text, re.IGNORECASE)
    if m:
        return "ge", int(m.group(1))
    m = re.search(r"at most\s+(\d+)", text, re.IGNORECASE)
    if m:
        return "le", int(m.group(1))
    m = re.search(r"more than\s+(\d+)", text, re.IGNORECASE)
    if m:
        return "gt", int(m.group(1))
    m = re.search(r"(?:less than|fewer than)\s+(\d+)", text, re.IGNORECASE)
    if m:
        return "lt", int(m.group(1))
    raise ProblemParseError("Could not determine the target event (e.g. 'exactly 3', 'at least 2', 'between 2 and 5').")


def _solve_binomial(text: str) -> Dict[str, Any]:
    n = _find_float(r"(\d+)\s*(?:coin\s*flips|flips|trials|tosses|attempts)", text)
    if n is None:
        n = _find_float(r"n\s*=\s*(\d+)", text)
    if n is None:
        raise ProblemParseError("Could not determine the number of trials (n).")
    n = int(n)

    p = _find_float(r"p\s*=\s*([\d.]+)", text)
    if p is None:
        p = _find_float(r"probability(?: of success)?\s*(?:of|is|=)\s*([\d.]+)", text)
    if p is None and "coin" in text.lower():
        p = 0.5
    if p is None:
        p = 0.5

    kind, target = _binomial_bounds(text)
    X = Binomial("X", n, sp.nsimplify(p))
    k = sp.Symbol("k", nonnegative=True, integer=True)
    pmf_expr = sp.binomial(n, k) * sp.nsimplify(p) ** k * (1 - sp.nsimplify(p)) ** (n - k)

    steps: List[Dict[str, Any]] = [
        {"title": "Model as a Binomial distribution",
         "description": f"n = {n} independent trials, success probability p = {p}.",
         "latex": f"X \\sim \\text{{Binomial}}(n={n}, p={sp.nsimplify(p)})"},
        {"title": "PMF formula", "description": "Probability of exactly k successes.",
         "latex": f"P(X=k) = \\binom{{n}}{{k}} p^k (1-p)^{{n-k}} = {latex(pmf_expr)}"},
    ]

    if kind == "eq":
        prob = P(sp.Eq(X, target))
        event_latex = f"P(X = {target})"
    elif kind == "ge":
        prob = P(X >= target)
        event_latex = f"P(X \\geq {target})"
    elif kind == "le":
        prob = P(X <= target)
        event_latex = f"P(X \\leq {target})"
    elif kind == "gt":
        prob = P(X > target)
        event_latex = f"P(X > {target})"
    elif kind == "lt":
        prob = P(X < target)
        event_latex = f"P(X < {target})"
    else:
        a, b = target
        prob = P((X >= a) & (X <= b))
        event_latex = f"P({a} \\leq X \\leq {b})"

    prob_num = sp.nsimplify(prob)
    steps.append({"title": "Evaluate the event probability", "description": "Sum the PMF over the relevant outcomes.",
                   "latex": f"{event_latex} = {latex(prob_num)} \\approx {float(prob_num):.6f}"})

    final_latex = f"{event_latex} = {latex(prob_num)} \\approx {float(prob_num):.6f}"
    summary = f"{event_latex.replace(chr(92), '')} ≈ {float(prob_num):.6f}"
    fig = _plot_binomial(n, p, kind, target)

    return {
        "subtype": "binomial", "summary": summary, "steps": steps, "final_latex": final_latex,
        "plot": fig, "plot_caption": "Binomial PMF with the requested event highlighted", "warnings": [],
    }


def _normal_bounds(text: str) -> Tuple[float, float]:
    m = re.search(r"between\s+(-?[\d.]+)\s+and\s+(-?[\d.]+)", text, re.IGNORECASE)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"(?:less than|below|under)\s+(-?[\d.]+)", text, re.IGNORECASE)
    if m:
        return float("-inf"), float(m.group(1))
    m = re.search(r"(?:greater than|above|over|more than)\s+(-?[\d.]+)", text, re.IGNORECASE)
    if m:
        return float(m.group(1)), float("inf")
    raise ProblemParseError("Could not determine the probability range (e.g. 'between 1 and 2', 'less than 5').")


def _solve_normal(text: str) -> Dict[str, Any]:
    mean = _find_float(r"mean\s*(?:=|is|of)?\s*(-?[\d.]+)", text)
    std = _find_float(r"std(?:ev|\.|\s*deviation)?\s*(?:=|is|of)?\s*([\d.]+)", text)
    if std is None:
        std = _find_float(r"variance\s*(?:=|is|of)?\s*([\d.]+)", text)
        if std is not None:
            std = std ** 0.5
    mean = mean if mean is not None else 0.0
    std = std if std is not None else 1.0

    a, b = _normal_bounds(text)
    X = Normal("X", sp.nsimplify(mean), sp.nsimplify(std))
    xsym = sp.Symbol("x")

    steps: List[Dict[str, Any]] = [
        {"title": "Model as a Normal distribution", "description": f"mean μ = {mean}, std σ = {std}.",
         "latex": f"X \\sim \\mathcal{{N}}(\\mu={mean}, \\sigma={std})"},
        {"title": "PDF formula", "description": "Probability density function.",
         "latex": f"f(x) = \\frac{{1}}{{\\sigma\\sqrt{{2\\pi}}}} e^{{-\\frac{{(x-\\mu)^2}}{{2\\sigma^2}}}}"},
    ]

    cdf_fn = sp_cdf(X)
    if a == float("-inf"):
        prob = cdf_fn(b)
        event_latex = f"P(X < {b})"
    elif b == float("inf"):
        prob = 1 - cdf_fn(a)
        event_latex = f"P(X > {a})"
    else:
        prob = cdf_fn(b) - cdf_fn(a)
        event_latex = f"P({a} < X < {b})"

    prob_val = float(sp.N(prob))
    steps.append({"title": "Evaluate using the CDF", "description": "P(a < X < b) = Φ(b) - Φ(a), standardizing with z=(x-μ)/σ.",
                   "latex": f"{event_latex} = {prob_val:.6f}"})

    final_latex = f"{event_latex} = {prob_val:.6f}"
    summary = f"{event_latex} ≈ {prob_val:.6f}"
    fig = _plot_normal(mean, std, a, b)

    return {
        "subtype": "normal", "summary": summary, "steps": steps, "final_latex": final_latex,
        "plot": fig, "plot_caption": "Normal PDF with requested probability region shaded", "warnings": [],
    }


def solve(problem: str) -> Dict[str, Any]:
    text = clean_text(problem)
    lowered = text.lower()
    if "normal" in lowered or "gaussian" in lowered:
        return _solve_normal(text)
    return _solve_binomial(text)


def _plot_binomial(n: int, p: float, kind: str, target) -> go.Figure:
    ks = np.arange(0, n + 1)
    from scipy.stats import binom
    pmf = binom.pmf(ks, n, p)
    if kind == "eq":
        highlight = ks == target
    elif kind == "ge":
        highlight = ks >= target
    elif kind == "le":
        highlight = ks <= target
    elif kind == "gt":
        highlight = ks > target
    elif kind == "lt":
        highlight = ks < target
    else:
        a, b = target
        highlight = (ks >= a) & (ks <= b)
    colors = ["#f97316" if h else "#4f46e5" for h in highlight]
    fig = go.Figure(go.Bar(x=ks, y=pmf, marker_color=colors, name="P(X=k)"))
    fig.update_layout(title=f"Binomial(n={n}, p={p}) PMF", xaxis_title="k (successes)", yaxis_title="P(X=k)",
                       template="plotly_white")
    return fig


def _plot_normal(mean: float, std: float, a: float, b: float) -> go.Figure:
    lo = mean - 4 * std
    hi = mean + 4 * std
    xs = np.linspace(lo, hi, 400)
    pdf = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mean) / std) ** 2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=pdf, mode="lines", name="f(x)", line=dict(color="#4f46e5", width=3)))
    fill_a = lo if a == float("-inf") else a
    fill_b = hi if b == float("inf") else b
    fxs = np.linspace(fill_a, fill_b, 200)
    fys = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((fxs - mean) / std) ** 2)
    fig.add_trace(go.Scatter(x=np.concatenate([fxs, fxs[::-1]]), y=np.concatenate([fys, np.zeros_like(fys)]),
                              fill="toself", fillcolor="rgba(249,115,22,0.35)", line=dict(width=0), name="P(event)"))
    fig.update_layout(title=f"Normal(μ={mean}, σ={std}) PDF", xaxis_title="x", yaxis_title="f(x)",
                       template="plotly_white", legend=dict(orientation="h", y=-0.2))
    return fig
