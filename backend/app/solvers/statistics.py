"""Descriptive statistics solver: mean, median, mode, variance, std, quartiles."""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import plotly.graph_objects as go
import sympy as sp

from .utils import clean_text, latex, parse_number_list


def solve(problem: str) -> Dict[str, Any]:
    text = clean_text(problem)
    data = parse_number_list(text)
    values = [sp.nsimplify(v) for v in data]
    n = len(values)
    if n == 0:
        raise ValueError("No data points found.")

    mean = sp.nsimplify(sum(values)) / n
    sorted_vals = sorted(values, key=lambda v: float(v))
    if n % 2 == 1:
        median = sorted_vals[n // 2]
    else:
        median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

    freq: Dict[Any, int] = {}
    for v in values:
        freq[v] = freq.get(v, 0) + 1
    max_freq = max(freq.values())
    modes = [k for k, c in freq.items() if c == max_freq] if max_freq > 1 else []

    sq_dev = [(v - mean) ** 2 for v in values]
    pop_var = sp.nsimplify(sum(sq_dev)) / n
    sample_var = sp.nsimplify(sum(sq_dev)) / (n - 1) if n > 1 else sp.Integer(0)
    pop_std = sp.sqrt(pop_var)
    sample_std = sp.sqrt(sample_var)
    data_min, data_max = sorted_vals[0], sorted_vals[-1]
    data_range = data_max - data_min

    def _percentile(p: float) -> sp.Number:
        arr = np.array([float(v) for v in sorted_vals])
        return sp.nsimplify(float(np.percentile(arr, p)))

    q1, q2, q3 = _percentile(25), _percentile(50), _percentile(75)
    iqr = q3 - q1

    values_latex = ", ".join(latex(v) for v in values)
    steps: List[Dict[str, Any]] = [
        {"title": "Data set", "description": f"n = {n} observations.", "latex": f"X = \\{{{values_latex}\\}}"},
        {
            "title": "Mean",
            "description": "Sum of all values divided by the count.",
            "latex": f"\\bar{{X}} = \\frac{{1}}{{n}}\\sum_{{i=1}}^{{n}} x_i = \\frac{{{latex(sum(values))}}}{{{n}}} = {latex(mean)} \\approx {float(mean):.4f}",
        },
        {
            "title": "Median",
            "description": "Middle value of the sorted data (average of two middle values if n is even).",
            "latex": f"\\text{{median}} = {latex(median)}",
        },
        {
            "title": "Mode",
            "description": "Most frequently occurring value(s).",
            "latex": ("\\text{mode} = " + ", ".join(latex(m) for m in modes)) if modes else "\\text{no repeated value (no unique mode)}",
        },
        {
            "title": "Variance",
            "description": "Average squared deviation from the mean (population and sample versions).",
            "latex": (
                f"\\sigma^2 = \\frac{{1}}{{n}}\\sum (x_i-\\bar{{X}})^2 = {latex(pop_var)} \\approx {float(pop_var):.4f} "
                f"\\qquad s^2 = \\frac{{1}}{{n-1}}\\sum (x_i-\\bar{{X}})^2 = {latex(sample_var)} \\approx {float(sample_var):.4f}"
            ),
        },
        {
            "title": "Standard deviation",
            "description": "Square root of variance.",
            "latex": f"\\sigma = {latex(pop_std)} \\approx {float(pop_std):.4f} \\qquad s = {latex(sample_std)} \\approx {float(sample_std):.4f}",
        },
        {
            "title": "Range & quartiles",
            "description": "Spread of the data.",
            "latex": f"\\text{{range}} = {latex(data_range)}, \\quad Q_1={latex(q1)},\\ Q_2={latex(q2)},\\ Q_3={latex(q3)},\\quad IQR = {latex(iqr)}",
        },
    ]

    final_latex = (
        f"\\bar{{X}} = {float(mean):.4f}, \\quad \\sigma = {float(pop_std):.4f}, \\quad "
        f"s = {float(sample_std):.4f}, \\quad \\text{{median}} = {latex(median)}"
    )
    summary = f"mean={float(mean):.4f}, median={float(median):.4f}, std={float(pop_std):.4f}, n={n}"

    fig = _plot_distribution(values, float(mean), float(pop_std))

    return {
        "subtype": "descriptive",
        "summary": summary,
        "steps": steps,
        "final_latex": final_latex,
        "plot": fig,
        "plot_caption": "Histogram with mean/std overlay and box plot",
        "warnings": [],
    }


def _plot_distribution(values, mean: float, std: float) -> go.Figure:
    arr = np.array([float(v) for v in values])
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=arr, name="data", marker_color="#4f46e5", opacity=0.75,
                                nbinsx=min(20, max(5, len(arr) // 2 or 1)), yaxis="y"))
    fig.add_vline(x=mean, line=dict(color="#f97316", width=3, dash="dash"), annotation_text="mean")
    if std > 0:
        xs = np.linspace(arr.min() - std, arr.max() + std, 200)
        pdf = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mean) / std) ** 2)
        pdf_scaled = pdf * len(arr) * (arr.max() - arr.min() + 1e-9) / 10
        fig.add_trace(go.Scatter(x=xs, y=pdf_scaled, mode="lines", name="normal fit (scaled)",
                                  line=dict(color="#16a34a", width=3)))
    fig.update_layout(title="Data distribution", xaxis_title="value", yaxis_title="frequency",
                       template="plotly_white", legend=dict(orientation="h", y=-0.2), bargap=0.05)
    return fig
