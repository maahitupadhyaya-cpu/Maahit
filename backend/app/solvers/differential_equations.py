"""Ordinary differential equation solver built on sympy.dsolve."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import plotly.graph_objects as go
import sympy as sp

from .utils import ProblemParseError, clean_text, latex, safe_lambdify

x = sp.Symbol("x")
y = sp.Function("y")

_HINT_DESCRIPTIONS = {
    "separable": "Separable equation: variables can be separated onto each side and integrated.",
    "1st_linear": "First-order linear ODE: solved via an integrating factor.",
    "Bernoulli": "Bernoulli equation: reduced to a linear ODE via substitution.",
    "nth_linear_constant_coeff_homogeneous": "Linear homogeneous ODE with constant coefficients: solved via the characteristic equation.",
    "nth_linear_constant_coeff_undetermined_coefficients": "Linear ODE with constant coefficients: solved using the method of undetermined coefficients.",
    "nth_linear_constant_coeff_variation_of_parameters": "Linear ODE with constant coefficients: solved using variation of parameters.",
    "1st_exact": "Exact equation: an implicit potential function exists whose differential equals the ODE.",
    "1st_homogeneous_coeff_best": "Homogeneous-coefficient ODE, solved via a substitution y = vx.",
}


def _extract_ics(text: str) -> Tuple[Dict[Any, Any], str]:
    ics: Dict[Any, Any] = {}
    pattern = re.compile(r"y(\'{0,2})\s*\(\s*(-?\d+\.?\d*)\s*\)\s*=\s*(-?\d+\.?\d*)")
    spans = []
    for m in pattern.finditer(text):
        primes = len(m.group(1))
        x0 = sp.nsimplify(m.group(2))
        val = sp.nsimplify(m.group(3))
        if primes == 0:
            ics[y(x0)] = val
        else:
            ics[sp.Derivative(y(x), x, primes).subs(x, x0)] = val
        spans.append(m.span())
    cleaned = text
    for start, end in sorted(spans, reverse=True):
        cleaned = cleaned[:start] + " " + cleaned[end:]
    cleaned = re.sub(r"^[\s,;]+|[\s,;]+$", "", cleaned)
    cleaned = re.sub(r",\s*,", ",", cleaned)
    return ics, cleaned


def _normalize_ode_text(text: str) -> str:
    t = text
    t = re.sub(r"(?i)^(solve|find the solution of|find solution of|find y\(x\) such that)\s*", "", t).strip()
    t = re.sub(r"d\^?\s*3\s*y\s*/\s*d\s*x\^?\s*3", "Derivative(y(x),x,3)", t, flags=re.IGNORECASE)
    t = re.sub(r"d\^?\s*2\s*y\s*/\s*d\s*x\^?\s*2", "Derivative(y(x),x,2)", t, flags=re.IGNORECASE)
    t = re.sub(r"dy\s*/\s*dx", "Derivative(y(x),x)", t, flags=re.IGNORECASE)
    t = t.replace("y'''", "Derivative(y(x),x,3)")
    t = t.replace("y''", "Derivative(y(x),x,2)")
    t = re.sub(r"y'(?!')", "Derivative(y(x),x)", t)
    t = re.sub(r"\by\b(?!\()", "y(x)", t)
    return t


def _build_equation(ode_text: str) -> sp.Eq:
    if "=" not in ode_text:
        raise ProblemParseError("ODE must contain an '=' sign, e.g. y'' - y = 0")
    lhs_str, rhs_str = ode_text.split("=", 1)
    locals_dict = {
        "y": y, "x": x, "Derivative": sp.Derivative,
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp,
        "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "E": sp.E, "pi": sp.pi,
    }
    try:
        lhs = sp.sympify(lhs_str.strip(), locals=locals_dict)
        rhs = sp.sympify(rhs_str.strip() or "0", locals=locals_dict)
    except Exception as exc:
        raise ProblemParseError(f"Could not parse ODE: '{ode_text}'") from exc
    return sp.Eq(lhs, rhs)


def _characteristic_equation_steps(eq: sp.Eq) -> Optional[Dict[str, str]]:
    """Best-effort extraction of the characteristic polynomial for linear,
    constant-coefficient homogeneous ODEs. Returns None if not applicable."""
    try:
        expr = eq.lhs - eq.rhs
        expr = sp.expand(expr)
        max_order = 0
        for d in expr.atoms(sp.Derivative):
            if d.expr == y(x):
                max_order = max(max_order, d.derivative_count)
        if max_order == 0:
            return None
        r = sp.Symbol("r")
        poly_expr = expr
        for k in range(max_order, 0, -1):
            poly_expr = poly_expr.subs(sp.Derivative(y(x), x, k), r ** k)
        poly_expr = poly_expr.subs(y(x), 1)
        if poly_expr.free_symbols - {r}:
            return None  # not constant-coefficient
        poly = sp.Poly(poly_expr, r)
        roots = sp.roots(poly)
        roots_str = ", ".join(f"r = {latex(k)}" + (f" (mult. {v})" if v > 1 else "") for k, v in roots.items())
        return {
            "title": "Form the characteristic equation",
            "description": "Substitute y = e^{rx} so each derivative becomes a power of r.",
            "latex": f"{latex(poly.as_expr())} = 0 \\quad\\Rightarrow\\quad {roots_str}",
        }
    except Exception:
        return None


def _plot_solution(sol_rhs, ics_present: bool, warnings: List[str]) -> Optional[go.Figure]:
    free = sorted((s for s in sol_rhs.free_symbols if s != x), key=str)
    fig = go.Figure()
    xs = np.linspace(-5, 5, 400)
    try:
        if not free:
            f = safe_lambdify(sol_rhs, [x])
            ys = np.array([f(v) for v in xs], dtype=float)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="y(x)", line=dict(color="#4f46e5", width=3)))
        elif len(free) == 1 and not ics_present:
            c = free[0]
            warnings.append(f"No initial conditions given: plotted a family of curves for different {c} values.")
            colors = ["#4f46e5", "#16a34a", "#f97316", "#dc2626", "#0ea5e9"]
            for i, cval in enumerate([-2, -1, 1, 2]):
                f = safe_lambdify(sol_rhs.subs(c, cval), [x])
                ys = np.array([f(v) for v in xs], dtype=float)
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"{c}={cval}",
                                          line=dict(color=colors[i % len(colors)], width=2.5)))
        else:
            subs_map = {c: 1 for c in free}
            warnings.append(
                "Arbitrary constants (" + ", ".join(str(c) for c in free) +
                ") were set to 1 purely for visualization; no initial conditions fully pinned them down."
            )
            f = safe_lambdify(sol_rhs.subs(subs_map), [x])
            ys = np.array([f(v) for v in xs], dtype=float)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="y(x) (constants=1)",
                                      line=dict(color="#4f46e5", width=3)))
        fig.update_layout(title="Solution curve y(x)", xaxis_title="x", yaxis_title="y",
                           template="plotly_white", legend=dict(orientation="h", y=-0.2))
        return fig
    except Exception:
        return None


def solve(problem: str) -> Dict[str, Any]:
    text = clean_text(problem)
    ics, remaining = _extract_ics(text)
    ode_text = _normalize_ode_text(remaining)
    eq = _build_equation(ode_text)

    warnings: List[str] = []
    steps = [
        {"title": "Original differential equation", "description": "Rewritten with explicit derivative notation.",
         "latex": latex(eq)},
    ]

    try:
        hints = sp.classify_ode(eq, y(x))
    except Exception:
        hints = ()
    primary_hint = hints[0] if hints else None
    if primary_hint:
        desc = _HINT_DESCRIPTIONS.get(primary_hint, f"Solved using the '{primary_hint}' method.")
        steps.append({"title": "Classify the ODE", "description": desc, "latex": None})

    char_step = _characteristic_equation_steps(eq)
    if char_step:
        steps.append(char_step)

    try:
        sol = sp.dsolve(eq, y(x), ics=ics if ics else None)
    except Exception:
        try:
            sol = sp.dsolve(eq, y(x))
            if ics:
                warnings.append("Could not apply the given initial conditions automatically; showing the general solution.")
        except Exception as exc:
            raise ProblemParseError(f"SymPy could not solve this ODE: {exc}") from exc

    if isinstance(sol, list):
        sol = sol[0]
        warnings.append("Multiple solution branches were found; showing the first one.")

    steps.append({
        "title": "General solution" if not ics else "Solve for the constants and write the particular solution",
        "description": "Solve the ODE (SymPy's dsolve).",
        "latex": latex(sol),
    })

    final_latex = latex(sol)
    fig = _plot_solution(sol.rhs, bool(ics), warnings)

    return {
        "subtype": "ode",
        "summary": f"Solved via {primary_hint or 'symbolic integration'}: {sp.sstr(sol)}",
        "steps": steps,
        "final_latex": final_latex,
        "plot": fig,
        "plot_caption": "Solution curve(s) of the ODE",
        "warnings": warnings,
    }
