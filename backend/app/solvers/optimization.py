"""Optimization solver: unconstrained (and simple equality-constrained via
Lagrange multipliers) extrema of single- and multi-variable functions."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import numpy as np
import plotly.graph_objects as go
import sympy as sp

from .utils import ProblemParseError, clean_text, latex, parse_expression, safe_lambdify


def _extract_function(text: str):
    m = re.search(r"[a-zA-Z]\s*\(([^)]*)\)\s*=\s*(.+)", text)
    if m:
        var_names = [v.strip() for v in m.group(1).split(",") if v.strip()]
        expr_str = m.group(2)
    else:
        var_names = []
        expr_str = text
    expr_str = re.sub(r"(?i)^(minimi[sz]e|maximi[sz]e|optimi[sz]e|find the (minimum|maximum) of|find (minimum|maximum) of)\s*", "", expr_str)
    expr_str = re.split(r"(?i)\bsubject to\b", expr_str)[0].strip().strip(".")
    if not var_names:
        pre = re.sub(r"(?i)subject to.*", "", expr_str)
    expr = parse_expression(expr_str, extra_symbols=var_names)
    variables = [sp.Symbol(v) for v in var_names] if var_names else sorted(expr.free_symbols, key=str)
    if not variables:
        raise ProblemParseError("Could not determine the variable(s) of the objective function.")
    return expr, variables


def _extract_constraint(text: str, variables: List[sp.Symbol]):
    m = re.search(r"(?i)subject to\s+(.+)", text)
    if not m:
        return None
    cons_str = m.group(1).strip().strip(".")
    if "=" not in cons_str:
        return None
    lhs_str, rhs_str = cons_str.split("=", 1)
    var_names = [str(v) for v in variables]
    lhs = parse_expression(lhs_str, extra_symbols=var_names)
    rhs = parse_expression(rhs_str, extra_symbols=var_names)
    return sp.Eq(lhs, rhs)


def solve(problem: str) -> Dict[str, Any]:
    text = clean_text(problem)
    is_max = bool(re.search(r"(?i)maximi[sz]e|maximum", text))
    expr, variables = _extract_function(text)
    constraint = _extract_constraint(text, variables)

    steps: List[Dict[str, Any]] = [
        {"title": "Objective function", "description": f"{'Maximize' if is_max else 'Minimize'} f({', '.join(map(str, variables))}).",
         "latex": f"f({', '.join(latex(v) for v in variables)}) = {latex(expr)}"},
    ]
    warnings: List[str] = []

    if constraint is not None:
        lam = sp.Symbol("lambda")
        g = constraint.lhs - constraint.rhs
        L = expr - lam * g
        steps.append({"title": "Set up the Lagrangian", "description": "Introduce a multiplier λ for the constraint g=0.",
                       "latex": f"\\mathcal{{L}} = {latex(expr)} - \\lambda\\left({latex(g)}\\right)"})
        grad_eqs = [sp.diff(L, v) for v in variables] + [g]
        unknowns = variables + [lam]
        sols = sp.solve(grad_eqs, unknowns, dict=True)
        if not sols:
            raise ProblemParseError("Could not find critical points satisfying the constraint.")
        eqs_latex = r" \\ ".join(f"\\partial \\mathcal{{L}}/\\partial {latex(v)} = {latex(eq)} = 0" for v, eq in zip(unknowns, grad_eqs))
        steps.append({"title": "Solve the system ∇L = 0", "description": "Stationary points of the Lagrangian.",
                       "latex": eqs_latex})
        candidates = []
        for s in sols:
            point = {v: s[v] for v in variables if v in s}
            if len(point) == len(variables):
                val = expr.subs(point)
                candidates.append((point, val))
        if not candidates:
            raise ProblemParseError("No valid critical points found for the constrained problem.")
        best = max(candidates, key=lambda c: c[1]) if is_max else min(candidates, key=lambda c: c[1])
        point, val = best
        point_str = ", ".join(f"{latex(v)} = {latex(val_)}" for v, val_ in point.items())
        final_latex = f"{point_str} \\quad\\Rightarrow\\quad f = {latex(val)}"
        steps.append({"title": "Evaluate candidates and pick the extremum", "description": "Compare f at all critical points.",
                       "latex": final_latex})
        summary = f"Constrained {'maximum' if is_max else 'minimum'} at {point}, f = {val}"
        fig = _plot_constrained(expr, g, variables, point) if len(variables) == 2 else None
        plot_caption = "Objective surface with constraint curve and optimum" if fig else None
        return {
            "subtype": "constrained", "summary": summary, "steps": steps, "final_latex": final_latex,
            "plot": fig, "plot_caption": plot_caption, "warnings": warnings,
        }

    grad = [sp.diff(expr, v) for v in variables]
    grad_latex = r" \\ ".join(f"\\frac{{\\partial f}}{{\\partial {latex(v)}}} = {latex(g)}" for v, g in zip(variables, grad))
    steps.append({"title": "Compute the gradient", "description": "Partial derivative with respect to each variable.",
                   "latex": grad_latex})

    crit_sols = sp.solve(grad, variables, dict=True)
    if not crit_sols:
        raise ProblemParseError("Could not find critical points (∇f = 0 has no closed-form solution).")
    steps.append({"title": "Set gradient to zero and solve", "description": "Find candidate critical points.",
                   "latex": r" \\ ".join(f"{latex(g)} = 0" for g in grad)})

    n = len(variables)
    H = sp.hessian(expr, variables)
    results = []
    for s in crit_sols:
        point = tuple(s.get(v, v) for v in variables)
        Hp = H.subs(s)
        f_val = expr.subs(s)
        classification = _classify_point(Hp, n)
        results.append({"point": s, "value": f_val, "hessian": Hp, "classification": classification})

    if n == 1:
        v = variables[0]
        lines = []
        for r in results:
            fpp = H[0, 0].subs(r["point"])
            lines.append(f"f''({latex(r['point'][v])}) = {latex(fpp)} \\Rightarrow \\text{{{r['classification']}}}")
        steps.append({"title": "Second derivative test", "description": "Sign of f'' classifies each critical point.",
                       "latex": r" \\ ".join(lines)})
    else:
        lines = []
        for r in results:
            lines.append(f"H = {latex(r['hessian'])} \\Rightarrow \\text{{{r['classification']}}}")
        steps.append({"title": "Second-order (Hessian) test", "description": "Definiteness of the Hessian classifies each point.",
                       "latex": r" \\ ".join(lines)})

    desired = "maximum" if is_max else "minimum"
    matching = [r for r in results if desired in r["classification"]]
    chosen = matching[0] if matching else results[0]
    if not matching:
        warnings.append(f"No critical point was classified as a {desired}; showing the closest stationary point found.")

    point_str = ", ".join(f"{latex(v)} = {latex(chosen['point'].get(v, v))}" for v in variables)
    final_latex = f"{point_str} \\quad\\Rightarrow\\quad f_{{{desired}}} = {latex(chosen['value'])}"
    steps.append({"title": "Conclusion", "description": f"Optimal point and {desired} value.", "latex": final_latex})

    summary = f"{desired.capitalize()} at {chosen['point']}, f = {chosen['value']}"
    fig = _plot_objective(expr, variables, [r["point"] for r in results], chosen["point"])
    plot_caption = "Objective function with critical point(s) marked"

    return {
        "subtype": "unconstrained", "summary": summary, "steps": steps, "final_latex": final_latex,
        "plot": fig, "plot_caption": plot_caption, "warnings": warnings,
    }


def _classify_point(H, n: int) -> str:
    if n == 1:
        val = H[0, 0] if hasattr(H, "shape") else H
        if val > 0:
            return "local minimum"
        if val < 0:
            return "local maximum"
        return "inconclusive (saddle/degenerate)"
    try:
        eigs = list(H.eigenvals().keys())
        eigs_f = [complex(sp.N(e)) for e in eigs]
        if all(e.real > 1e-9 for e in eigs_f):
            return "local minimum"
        if all(e.real < -1e-9 for e in eigs_f):
            return "local maximum"
        return "saddle point"
    except Exception:
        return "inconclusive"


def _plot_objective(expr, variables, all_points, chosen_point) -> Optional[go.Figure]:
    try:
        if len(variables) == 1:
            v = variables[0]
            f = safe_lambdify(expr, [v])
            center = float(chosen_point.get(v, 0)) if chosen_point else 0.0
            xs = np.linspace(center - 10, center + 10, 400)
            ys = np.array([f(t) for t in xs], dtype=float)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line=dict(color="#4f46e5", width=3)))
            for p in all_points:
                px = float(p.get(v, 0))
                fig.add_trace(go.Scatter(x=[px], y=[float(f(px))], mode="markers", name=f"critical point x={px:.3g}",
                                          marker=dict(size=12, color="#f97316")))
            fig.update_layout(title="Objective function f(x)", xaxis_title=str(v), yaxis_title="f(x)",
                               template="plotly_white", legend=dict(orientation="h", y=-0.2))
            return fig
        elif len(variables) == 2:
            v1, v2 = variables
            f = safe_lambdify(expr, [v1, v2])
            cx = float(chosen_point.get(v1, 0)) if chosen_point else 0.0
            cy = float(chosen_point.get(v2, 0)) if chosen_point else 0.0
            xs = np.linspace(cx - 8, cx + 8, 60)
            ys = np.linspace(cy - 8, cy + 8, 60)
            X, Y = np.meshgrid(xs, ys)
            Z = np.array(f(X, Y), dtype=float)
            fig = go.Figure(data=[go.Surface(x=xs, y=ys, z=Z, colorscale="Viridis", opacity=0.9)])
            for p in all_points:
                px, py = float(p.get(v1, 0)), float(p.get(v2, 0))
                pz = float(f(px, py))
                fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[pz], mode="markers",
                                            marker=dict(size=6, color="#f97316"), name="critical point"))
            fig.update_layout(title="Objective surface f(x, y)", template="plotly_white",
                               scene=dict(xaxis_title=str(v1), yaxis_title=str(v2), zaxis_title="f"))
            return fig
    except Exception:
        return None
    return None


def _plot_constrained(expr, g, variables, point) -> Optional[go.Figure]:
    try:
        v1, v2 = variables
        f = safe_lambdify(expr, [v1, v2])
        gfun = safe_lambdify(g, [v1, v2])
        cx, cy = float(point.get(v1, 0)), float(point.get(v2, 0))
        xs = np.linspace(cx - 8, cx + 8, 200)
        ys = np.linspace(cy - 8, cy + 8, 200)
        X, Y = np.meshgrid(xs, ys)
        Z = np.array(f(X, Y), dtype=float)
        G = np.array(gfun(X, Y), dtype=float)
        fig = go.Figure()
        fig.add_trace(go.Contour(x=xs, y=ys, z=Z, colorscale="Viridis", name="f(x,y)", opacity=0.85))
        fig.add_trace(go.Contour(x=xs, y=ys, z=G, contours=dict(start=0, end=0, size=1, coloring="lines"),
                                  line=dict(color="white", width=3), showscale=False, name="constraint g=0"))
        fig.add_trace(go.Scatter(x=[cx], y=[cy], mode="markers", marker=dict(size=14, color="#f97316", symbol="star"),
                                  name="optimum"))
        fig.update_layout(title="Constrained optimization: f contours with constraint curve",
                           xaxis_title=str(v1), yaxis_title=str(v2), template="plotly_white")
        return fig
    except Exception:
        return None
