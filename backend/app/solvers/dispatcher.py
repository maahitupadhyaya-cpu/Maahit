"""Routes a SolveRequest to the correct solver module and normalizes the
returned dict into the API's SolveResponse shape.

Adding a new math domain later only requires: (1) a new module in
`app/solvers/` exposing a `solve(problem: str) -> dict` function, and
(2) registering it in CATEGORY_SOLVERS below.
"""
from __future__ import annotations

from typing import Any, Dict

from . import calculus, differential_equations, linear_algebra, optimization, probability, statistics
from .utils import figure_to_spec

CATEGORY_SOLVERS = {
    "calculus": calculus.solve,
    "differential_equations": differential_equations.solve,
    "linear_algebra": linear_algebra.solve,
    "optimization": optimization.solve,
    "statistics": statistics.solve,
    "probability": probability.solve,
}

CATEGORY_LABELS = {
    "calculus": "Calculus",
    "differential_equations": "Differential Equations",
    "linear_algebra": "Linear Algebra",
    "optimization": "Optimization",
    "statistics": "Statistics",
    "probability": "Probability",
}


class UnknownCategoryError(ValueError):
    pass


def dispatch(category: str, problem: str) -> Dict[str, Any]:
    solver = CATEGORY_SOLVERS.get(category)
    if solver is None:
        raise UnknownCategoryError(
            f"Unknown category '{category}'. Valid options: {', '.join(CATEGORY_SOLVERS)}"
        )
    result = solver(problem)

    plot_spec = None
    fig = result.get("plot")
    if fig is not None:
        plot_spec = figure_to_spec(fig, caption=result.get("plot_caption"))

    steps = [
        {"title": s["title"], "description": s.get("description", ""), "latex": s.get("latex")}
        for s in result.get("steps", [])
    ]

    title = f"% LaTeXify solution — {CATEGORY_LABELS.get(category, category)}"
    body_lines = [title, "\\begin{align*}"]
    for s in steps:
        if s.get("latex"):
            body_lines.append(f"    {s['latex']} \\\\")
    body_lines.append("\\end{align*}")
    body_lines.append("")
    body_lines.append("% Final result")
    body_lines.append(result.get("final_latex", ""))
    full_latex = "\n".join(body_lines)

    return {
        "category": category,
        "subtype": result.get("subtype", "general"),
        "input_echo": problem,
        "summary": result.get("summary", ""),
        "steps": steps,
        "latex": full_latex,
        "plot": plot_spec,
        "warnings": result.get("warnings", []),
    }
