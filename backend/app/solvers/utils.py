"""Shared helpers used by every solver module: parsing, LaTeX rendering and
Plotly figure serialization.

Keeping this logic in one place means new solver modules (added later, e.g.
AI-based explanations or new math domains) can reuse the same safe-parsing
and plotting primitives instead of re-implementing them.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

import plotly.graph_objects as go
import plotly.utils as plotly_utils
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    standard_transformations,
    auto_symbol,
    auto_number,
)


class ProblemParseError(ValueError):
    """Raised when a user's problem text cannot be understood."""


# ---------------------------------------------------------------------------
# Expression parsing
# ---------------------------------------------------------------------------

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# A generous namespace of functions/constants students commonly use.
_SAFE_NAMESPACE: Dict[str, Any] = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt,
    "Abs": sp.Abs, "abs": sp.Abs,
    "pi": sp.pi, "e": sp.E, "E": sp.E, "oo": sp.oo, "infinity": sp.oo,
    "factorial": sp.factorial, "binomial": sp.binomial,
}


def clean_text(text: str) -> str:
    text = text.strip()
    text = text.replace("\u2212", "-")  # unicode minus
    text = text.replace("\u00d7", "*")  # multiplication sign
    text = text.replace("÷", "/")
    return text


def parse_expression(text: str, extra_symbols: Optional[Sequence[str]] = None):
    """Safely parse a math expression string into a SymPy expression."""
    text = clean_text(text)
    if not text:
        raise ProblemParseError("Empty expression.")
    namespace = dict(_SAFE_NAMESPACE)
    if extra_symbols:
        for s in extra_symbols:
            namespace.setdefault(s, sp.Symbol(s))
    try:
        expr = sp.sympify(text, locals=namespace, evaluate=True)
    except Exception:
        try:
            from sympy.parsing.sympy_parser import parse_expr
            expr = parse_expr(text, local_dict=namespace, transformations=_TRANSFORMATIONS)
        except Exception as exc:  # pragma: no cover - defensive
            raise ProblemParseError(f"Could not parse expression: '{text}'") from exc
    return expr


def extract_bracketed(text: str, open_char: str = "[", close_char: str = "]") -> List[str]:
    """Return all balanced-bracket substrings (handles nested brackets, e.g. matrices)."""
    results = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == open_char:
            if depth == 0:
                start = i
            depth += 1
        elif ch == close_char:
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    results.append(text[start:i + 1])
                    start = None
    return results


def parse_matrix(text: str) -> sp.Matrix:
    """Parse a matrix literal like '[[1,2],[3,4]]' into a sympy Matrix."""
    candidates = extract_bracketed(text)
    if not candidates:
        raise ProblemParseError("No matrix (e.g. [[1,2],[3,4]]) found in input.")
    # Prefer a candidate that looks like a nested list.
    matrix_str = None
    for c in candidates:
        if "[[" in c.replace(" ", ""):
            matrix_str = c
            break
    if matrix_str is None:
        matrix_str = candidates[0]
    try:
        rows = sp.sympify(matrix_str)
        mat = sp.Matrix(rows)
    except Exception as exc:
        raise ProblemParseError(f"Could not parse matrix from '{matrix_str}'") from exc
    return mat


def parse_number_list(text: str) -> List[sp.Number]:
    candidates = extract_bracketed(text)
    if not candidates:
        # fall back: comma separated numbers without brackets
        nums = re.findall(r"-?\d+\.?\d*", text)
        if not nums:
            raise ProblemParseError("No numeric list found in input, e.g. [1,2,3].")
        return [sp.Float(n) if "." in n else sp.Integer(n) for n in nums]
    data_str = candidates[0]
    try:
        values = sp.sympify(data_str)
        return [sp.nsimplify(v) for v in values]
    except Exception as exc:
        raise ProblemParseError(f"Could not parse numeric list from '{data_str}'") from exc


def find_number(pattern: str, text: str, default: Optional[float] = None, group: int = 1) -> Optional[float]:
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return default
    try:
        return float(m.group(group))
    except (ValueError, IndexError):
        return default


# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------

def latex(expr) -> str:
    return sp.latex(expr)


def build_latex_document(title: str, steps: List[Dict[str, str]], final_latex: str) -> str:
    """Compose a clean, copy-pasteable LaTeX snippet (not a full standalone
    document by default, but valid within one) summarising the solution."""
    lines = [
        f"% {title}",
        "\\begin{align*}",
    ]
    for step in steps:
        step_latex = step.get("latex")
        if step_latex:
            lines.append(f"    {step_latex} \\\\")
    lines.append("\\end{align*}")
    lines.append("")
    lines.append("% Final result")
    lines.append(final_latex)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plotly helpers
# ---------------------------------------------------------------------------

def figure_to_spec(fig: "go.Figure", caption: Optional[str] = None) -> Dict[str, Any]:
    """Convert a Plotly figure into a JSON-safe dict {data, layout, caption}."""
    raw = json.loads(json.dumps(fig.to_plotly_json(), cls=plotly_utils.PlotlyJSONEncoder))
    return {"data": raw.get("data", []), "layout": raw.get("layout", {}), "caption": caption}


def safe_lambdify(expr, symbols: Sequence[sp.Symbol]):
    return sp.lambdify(symbols, expr, modules=["numpy"])


def sample_range(lo: float, hi: float, n: int = 400) -> List[float]:
    import numpy as np
    if lo == hi:
        lo, hi = lo - 5, hi + 5
    return list(np.linspace(lo, hi, n))
