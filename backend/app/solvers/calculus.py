"""Calculus solver: derivatives, integrals (definite/indefinite) and limits."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import numpy as np
import plotly.graph_objects as go
import sympy as sp

from .utils import (
    ProblemParseError,
    clean_text,
    figure_to_spec,
    latex,
    parse_expression,
    safe_lambdify,
)

X = sp.Symbol("x")


def _detect_variable(text: str, default: str = "x") -> sp.Symbol:
    m = re.search(r"with respect to\s+([a-zA-Z])", text, re.IGNORECASE)
    if m:
        return sp.Symbol(m.group(1))
    m = re.search(r"\bd/d([a-zA-Z])\b", text)
    if m:
        return sp.Symbol(m.group(1))
    m = re.search(r"\bd([a-zA-Z])\b\s*$", text)
    if m and m.group(1) not in ("x",):
        return sp.Symbol(m.group(1))
    return sp.Symbol(default)


def _strip_prefixes(text: str, prefixes: List[str]) -> str:
    lowered = text.lower()
    for p in prefixes:
        if lowered.startswith(p):
            return text[len(p):].strip()
        idx = lowered.find(p)
        if idx != -1:
            return (text[:idx] + text[idx + len(p):]).strip()
    return text


def _solve_derivative(text: str) -> Dict[str, Any]:
    var = _detect_variable(text)
    body = text
    body = re.sub(r"(?i)with respect to\s+[a-zA-Z]", "", body)
    body = re.sub(r"(?i)^(differentiate|derivative of|find the derivative of|find derivative of|d/d[a-zA-Z])\s*", "", body)
    body = re.sub(r"(?i)\bd/d[a-zA-Z]\b", "", body)
    body = body.strip().strip(".")
    body = re.sub(r"^\((.*)\)$", r"\1", body)
    expr = parse_expression(body, extra_symbols=[str(var)])

    order = 1
    m = re.search(r"(\d+)(st|nd|rd|th)?\s*derivative", text, re.IGNORECASE)
    if m:
        order = int(m.group(1))
    elif re.search(r"second derivative", text, re.IGNORECASE):
        order = 2
    elif re.search(r"third derivative", text, re.IGNORECASE):
        order = 3

    steps = [
        {"title": "Original function", "description": "The function to differentiate.",
         "latex": f"f({var}) = {latex(expr)}"},
    ]

    terms = sp.Add.make_args(sp.expand(expr)) if expr.is_Add else [expr]
    if len(terms) > 1:
        term_lines = []
        running = []
        for t in terms:
            dt = sp.diff(t, var)
            term_lines.append(f"\\frac{{d}}{{d{var}}}\\left[{latex(t)}\\right] = {latex(dt)}")
            running.append(dt)
        steps.append({
            "title": "Differentiate term-by-term",
            "description": "Apply linearity of differentiation: the derivative of a sum is the sum of derivatives.",
            "latex": r" \quad ".join(term_lines),
        })
        result = sp.simplify(sum(running))
    else:
        result = expr
        for i in range(order):
            nxt = sp.diff(result, var)
            rule = _classify_rule(result)
            steps.append({
                "title": f"Apply {rule}" if i == 0 else f"Differentiate again ({rule})",
                "description": f"Differentiate with respect to {var}.",
                "latex": f"\\frac{{d}}{{d{var}}}\\left[{latex(result)}\\right] = {latex(nxt)}",
            })
            result = nxt
        result = sp.simplify(result)
        steps.append({
            "title": "Result",
            "description": "Simplified derivative.",
            "latex": f"f^{{({order})}}({var}) = {latex(result)}" if order > 1 else f"f'({var}) = {latex(result)}",
        })
        final_latex = steps[-1]["latex"]
        fig = _plot_function_and_derivative(expr, result, var)
        return {
            "subtype": "derivative",
            "summary": f"d/d{var} [{sp.pretty(expr, use_unicode=False)}] = {result}",
            "steps": steps,
            "final_latex": final_latex,
            "plot": fig,
        }

    order_final = sp.diff(expr, var, order) if order > 1 else result
    if order > 1:
        result = sp.simplify(order_final)
    deriv_symbol = f"f^{{({order})}}({var})" if order > 1 else f"f'({var})"
    final_latex = f"{deriv_symbol} = {latex(result)}"
    steps.append({"title": "Result", "description": "Sum the differentiated terms and simplify.",
                   "latex": final_latex})
    fig = _plot_function_and_derivative(expr, result, var)
    return {
        "subtype": "derivative",
        "summary": f"d/d{var} [{expr}] = {result}",
        "steps": steps,
        "final_latex": final_latex,
        "plot": fig,
    }


def _classify_rule(expr) -> str:
    if expr.is_Pow:
        return "power rule"
    if expr.is_Mul and len(expr.args) > 1 and any(a.is_Function for a in expr.args):
        return "product rule"
    if expr.is_Function and any(not a.is_Symbol and not a.is_Number for a in expr.args):
        return "chain rule"
    if expr.is_Add:
        return "sum rule"
    return "differentiation rule"


def _plot_function_and_derivative(expr, deriv, var) -> go.Figure:
    f = safe_lambdify(expr, [var])
    fprime = safe_lambdify(deriv, [var])
    xs = np.linspace(-10, 10, 400)
    try:
        ys = np.array([f(v) for v in xs], dtype=float)
    except Exception:
        ys = np.full_like(xs, np.nan)
    try:
        yps = np.array([fprime(v) for v in xs], dtype=float)
    except Exception:
        yps = np.full_like(xs, np.nan)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line=dict(color="#4f46e5", width=3)))
    fig.add_trace(go.Scatter(x=xs, y=yps, mode="lines", name="f'(x)", line=dict(color="#f97316", width=3, dash="dash")))
    fig.update_layout(
        title="Function and its derivative",
        xaxis_title=str(var), yaxis_title="value",
        template="plotly_white", legend=dict(orientation="h", y=-0.2),
    )
    return fig


def _solve_integral(text: str) -> Dict[str, Any]:
    var = _detect_variable(text)
    bounds = None
    m = re.search(r"from\s+(.+?)\s+to\s+(.+?)(?:\s+of|$)", text, re.IGNORECASE)
    body = text
    if m:
        a_str, b_str = m.group(1).strip(), m.group(2).strip()
        body = (text[:m.start()] + " " + text[m.end():]).strip()
    body = re.sub(r"(?i)^(integrate|find the integral of|find integral of|integral of|evaluate)\s*", "", body)
    body = re.sub(r"(?i)\bd[a-zA-Z]\s*$", "", body).strip()
    body = body.strip().strip(".")
    body = re.sub(r"^\((.*)\)$", r"\1", body)
    expr = parse_expression(body, extra_symbols=[str(var)])

    steps = [
        {"title": "Original integral", "description": "Set up the integral.",
         "latex": (f"\\int {latex(expr)}\\,d{var}" if not m else
                    f"\\int_{{{a_str}}}^{{{b_str}}} {latex(expr)}\\,d{var}")},
    ]

    antideriv = sp.integrate(expr, var)
    steps.append({
        "title": "Find the antiderivative",
        "description": "Apply integration rules (power rule, substitution, standard forms, etc.).",
        "latex": f"F({var}) = {latex(antideriv)} + C",
    })

    if m:
        try:
            a_val = parse_expression(a_str)
            b_val = parse_expression(b_str)
        except ProblemParseError:
            a_val, b_val = sp.sympify(a_str), sp.sympify(b_str)
        Fb = antideriv.subs(var, b_val)
        Fa = antideriv.subs(var, a_val)
        result = sp.simplify(Fb - Fa)
        steps.append({
            "title": "Apply the Fundamental Theorem of Calculus",
            "description": f"Evaluate F({b_val}) - F({a_val}).",
            "latex": f"F({latex(b_val)}) - F({latex(a_val)}) = {latex(Fb)} - {latex(Fa)} = {latex(result)}",
        })
        final_latex = f"\\int_{{{latex(a_val)}}}^{{{latex(b_val)}}} {latex(expr)}\\,d{var} = {latex(result)}"
        fig = _plot_definite_integral(expr, var, float(a_val), float(b_val))
        summary = f"Definite integral evaluates to {result}"
    else:
        result = antideriv
        final_latex = f"\\int {latex(expr)}\\,d{var} = {latex(antideriv)} + C"
        fig = _plot_indefinite_integral(expr, antideriv, var)
        summary = f"Antiderivative: {antideriv} + C"

    return {
        "subtype": "integral",
        "summary": summary,
        "steps": steps,
        "final_latex": final_latex,
        "plot": fig,
    }


def _plot_definite_integral(expr, var, a: float, b: float) -> go.Figure:
    f = safe_lambdify(expr, [var])
    pad = max(1.0, (b - a) * 0.5)
    xs = np.linspace(a - pad, b + pad, 400)
    ys = np.array([f(v) for v in xs], dtype=float)
    fill_xs = np.linspace(a, b, 200)
    fill_ys = np.array([f(v) for v in fill_xs], dtype=float)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line=dict(color="#4f46e5", width=3)))
    fig.add_trace(go.Scatter(
        x=np.concatenate([fill_xs, fill_xs[::-1]]),
        y=np.concatenate([fill_ys, np.zeros_like(fill_ys)]),
        fill="toself", fillcolor="rgba(249,115,22,0.35)", line=dict(width=0),
        name=f"Area on [{a:g}, {b:g}]",
    ))
    fig.update_layout(title="Definite integral: shaded area under f(x)",
                       xaxis_title=str(var), yaxis_title="f(x)", template="plotly_white",
                       legend=dict(orientation="h", y=-0.2))
    return fig


def _plot_indefinite_integral(expr, antideriv, var) -> go.Figure:
    f = safe_lambdify(expr, [var])
    F = safe_lambdify(antideriv, [var])
    xs = np.linspace(-10, 10, 400)
    try:
        ys = np.array([f(v) for v in xs], dtype=float)
    except Exception:
        ys = np.full_like(xs, np.nan)
    try:
        Ys = np.array([F(v) for v in xs], dtype=float)
    except Exception:
        Ys = np.full_like(xs, np.nan)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line=dict(color="#4f46e5", width=3)))
    fig.add_trace(go.Scatter(x=xs, y=Ys, mode="lines", name="F(x) (antiderivative, C=0)",
                              line=dict(color="#16a34a", width=3, dash="dash")))
    fig.update_layout(title="Function and one antiderivative",
                       xaxis_title=str(var), yaxis_title="value", template="plotly_white",
                       legend=dict(orientation="h", y=-0.2))
    return fig


def _solve_limit(text: str) -> Dict[str, Any]:
    m = re.search(r"as\s+([a-zA-Z])\s*(?:->|\u2192|approaches)\s*([^\s,]+)", text, re.IGNORECASE)
    var = sp.Symbol(m.group(1)) if m else X
    point_str = m.group(2) if m else "0"
    body = text
    if m:
        body = (text[:m.start()] + " " + text[m.end():]).strip()
    body = re.sub(r"(?i)^(limit of|find the limit of|find limit of|lim)\s*", "", body).strip()
    body = re.sub(r"(?i)\blim[_a-zA-Z0-9\->\s]*", "", body).strip()
    body = body.strip(".")
    body = re.sub(r"^\((.*)\)$", r"\1", body)

    point_str_norm = point_str.replace("infinity", "oo").replace("infty", "oo")
    point = parse_expression(point_str_norm, extra_symbols=[str(var)])
    expr = parse_expression(body, extra_symbols=[str(var)])

    steps = [
        {"title": "Original limit", "description": "Set up the limit expression.",
         "latex": f"\\lim_{{{var} \\to {latex(point)}}} {latex(expr)}"},
    ]

    direct = None
    try:
        direct = expr.subs(var, point)
        direct_simpl = sp.simplify(direct)
    except Exception:
        direct_simpl = sp.nan

    indeterminate = direct_simpl in (sp.nan, sp.zoo) or direct_simpl.has(sp.zoo) or (
        direct_simpl.is_number is False
    )
    if not indeterminate:
        steps.append({
            "title": "Direct substitution",
            "description": f"Substitute {var} = {sp.sstr(point)} directly (function is continuous there).",
            "latex": f"= {latex(direct_simpl)}",
        })
    else:
        steps.append({
            "title": "Direct substitution gives an indeterminate form",
            "description": "Direct substitution fails, so apply algebraic simplification / L'Hôpital's rule.",
            "latex": f"\\frac{{0}}{{0}} \\text{{ or }} \\frac{{\\infty}}{{\\infty}} \\Rightarrow \\text{{apply L'Hôpital / simplification}}",
        })

    result = sp.limit(expr, var, point)
    steps.append({
        "title": "Result",
        "description": "Evaluated limit.",
        "latex": f"\\lim_{{{var} \\to {latex(point)}}} {latex(expr)} = {latex(result)}",
    })
    final_latex = steps[-1]["latex"]
    fig = _plot_limit(expr, var, point, result)
    return {
        "subtype": "limit",
        "summary": f"Limit as {var} -> {point} of the expression is {result}",
        "steps": steps,
        "final_latex": final_latex,
        "plot": fig,
    }


def _plot_limit(expr, var, point, result) -> go.Figure:
    f = safe_lambdify(expr, [var])
    try:
        p = float(point)
    except (TypeError, ValueError):
        p = 0.0
    if not np.isfinite(p):
        p = 0.0
    span = 5.0
    xs = np.linspace(p - span, p + span, 400)
    ys = []
    for v in xs:
        try:
            val = f(v)
            val = float(val)
        except Exception:
            val = np.nan
        ys.append(val)
    ys = np.array(ys, dtype=float)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line=dict(color="#4f46e5", width=3)))
    try:
        r = float(result)
        fig.add_trace(go.Scatter(x=[p], y=[r], mode="markers", name="limit point",
                                  marker=dict(color="#f97316", size=12, symbol="circle-open", line=dict(width=3))))
    except (TypeError, ValueError):
        pass
    fig.update_layout(title="Behaviour of f(x) near the limit point",
                       xaxis_title=str(var), yaxis_title="f(x)", template="plotly_white",
                       legend=dict(orientation="h", y=-0.2))
    return fig


def solve(problem: str) -> Dict[str, Any]:
    text = clean_text(problem)
    lowered = text.lower()
    if re.search(r"\blim(it)?\b", lowered) and ("->" in text or "approaches" in lowered or "\u2192" in text):
        return _solve_limit(text)
    if re.search(r"\bintegr", lowered) or "\u222b" in text:
        return _solve_integral(text)
    return _solve_derivative(text)
