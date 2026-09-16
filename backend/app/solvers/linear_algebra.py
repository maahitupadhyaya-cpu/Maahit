"""Linear algebra solver: determinant, inverse, rank, eigen-decomposition and
solving linear systems Ax = b."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import numpy as np
import plotly.graph_objects as go
import sympy as sp

from .utils import ProblemParseError, clean_text, extract_bracketed, latex, parse_matrix


def _detect_subtype(text: str) -> str:
    t = text.lower()
    if "eigenvector" in t:
        return "eigenvectors"
    if "eigenvalue" in t or "eigen value" in t:
        return "eigenvalues"
    if re.search(r"\bdet(erminant)?\b", t):
        return "determinant"
    if "inverse" in t:
        return "inverse"
    if "rank" in t:
        return "rank"
    if "transpose" in t:
        return "transpose"
    if "solve" in t or "=" in text:
        return "solve_system"
    return "determinant"


def _parse_vector_after_equals(text: str) -> Optional[sp.Matrix]:
    if "=" not in text:
        return None
    after = text.split("=", 1)[1]
    brackets = extract_bracketed(after)
    if not brackets:
        return None
    try:
        values = sp.sympify(brackets[0])
        return sp.Matrix(values)
    except Exception:
        return None


def _fmt_matrix_latex(M: sp.Matrix) -> str:
    return latex(M)


def solve(problem: str) -> Dict[str, Any]:
    text = clean_text(problem)
    subtype = _detect_subtype(text)
    M = parse_matrix(text)
    n, m = M.shape

    steps: List[Dict[str, Any]] = [
        {"title": "Given matrix", "description": f"A {n}x{m} matrix.", "latex": f"A = {_fmt_matrix_latex(M)}"},
    ]
    warnings: List[str] = []
    fig = None
    plot_caption = None

    if subtype == "determinant":
        if n != m:
            raise ProblemParseError("Determinant requires a square matrix.")
        det = M.det()
        if n <= 3:
            steps.append({
                "title": "Cofactor expansion",
                "description": "Expand along the first row.",
                "latex": _cofactor_latex(M),
            })
        result = det
        final_latex = f"\\det(A) = {latex(result)}"
        summary = f"det(A) = {result}"

    elif subtype == "inverse":
        if n != m:
            raise ProblemParseError("Inverse requires a square matrix.")
        det = M.det()
        if det == 0:
            raise ProblemParseError("Matrix is singular (determinant = 0); it has no inverse.")
        steps.append({"title": "Compute the determinant", "description": "Required to confirm invertibility.",
                       "latex": f"\\det(A) = {latex(det)} \\neq 0"})
        inv = M.inv()
        steps.append({"title": "Compute the adjugate / inverse", "description": "A^{-1} = adj(A) / det(A).",
                       "latex": None})
        result = inv
        final_latex = f"A^{{-1}} = {_fmt_matrix_latex(inv)}"
        summary = f"A^-1 = {inv.tolist()}"

    elif subtype == "rank":
        rank = M.rank()
        rref, pivots = M.rref()
        steps.append({"title": "Row-reduce to echelon form", "description": "Compute the RREF of A.",
                       "latex": f"\\text{{rref}}(A) = {_fmt_matrix_latex(rref)}"})
        result = rank
        final_latex = f"\\text{{rank}}(A) = {rank}"
        summary = f"rank(A) = {rank}"

    elif subtype == "transpose":
        T = M.T
        result = T
        final_latex = f"A^{{T}} = {_fmt_matrix_latex(T)}"
        summary = f"A^T = {T.tolist()}"

    elif subtype == "eigenvalues":
        if n != m:
            raise ProblemParseError("Eigenvalues require a square matrix.")
        lam = sp.Symbol("lambda")
        char_poly = M.charpoly(lam).as_expr()
        steps.append({"title": "Form the characteristic polynomial",
                       "description": "det(A - λI) = 0",
                       "latex": f"\\det(A - \\lambda I) = {latex(char_poly)} = 0"})
        eigvals = M.eigenvals()
        eig_str = ", ".join(f"\\lambda = {latex(k)}" + (f"\\ (\\text{{mult. }}{v})" if v > 1 else "")
                              for k, v in eigvals.items())
        steps.append({"title": "Solve for the eigenvalues", "description": "Roots of the characteristic polynomial.",
                       "latex": eig_str})
        result = eigvals
        final_latex = eig_str
        summary = f"Eigenvalues: {list(eigvals.keys())}"
        fig = _plot_2d_transform(M) if n == 2 else _plot_eigenvalues_bar(eigvals)
        plot_caption = "Eigen-structure visualization"

    elif subtype == "eigenvectors":
        if n != m:
            raise ProblemParseError("Eigenvectors require a square matrix.")
        triples = M.eigenvects()
        lines = []
        for val, mult, vecs in triples:
            for v in vecs:
                lines.append(f"\\lambda = {latex(val)}: \\ v = {latex(v)}")
        steps.append({"title": "Solve (A - λI)v = 0 for each eigenvalue",
                       "description": "Null space of (A - λI) gives the eigenvectors.",
                       "latex": r" \\ ".join(lines)})
        result = triples
        final_latex = r" \\ ".join(lines)
        summary = "Eigenvectors computed for each eigenvalue."
        fig = _plot_2d_transform(M) if n == 2 else None
        plot_caption = "Eigenvectors shown as arrows from the origin" if n == 2 else None

    elif subtype == "solve_system":
        b = _parse_vector_after_equals(text)
        if b is None or b.shape[0] != n:
            raise ProblemParseError("Could not find a compatible vector b for A x = b (expected form: solve [[...]] x = [...]).")
        steps[0] = {"title": "Given system", "description": f"Solve A x = b for x.",
                     "latex": f"A = {_fmt_matrix_latex(M)}, \\quad b = {_fmt_matrix_latex(b)}"}
        aug = M.row_join(b)
        rref, _ = aug.rref()
        steps.append({"title": "Row-reduce the augmented matrix [A | b]",
                       "description": "Gaussian elimination to reduced row echelon form.",
                       "latex": f"[A \\mid b] \\to {_fmt_matrix_latex(rref)}"})
        try:
            xsol = M.solve(b)
            steps.append({"title": "Back-substitute", "description": "Read off the unique solution.", "latex": None})
            final_latex = f"x = {_fmt_matrix_latex(xsol)}"
            summary = f"x = {xsol.tolist()}"
            fig = _plot_2x2_system(M, b, xsol) if n == 2 and m == 2 else None
            plot_caption = "Intersection of the two lines is the solution" if fig is not None else None
        except Exception:
            sol_vars = sp.symbols(f"x1:{m + 1}")
            xvec = sp.Matrix(sol_vars)
            sols = sp.linsolve((M, b), *sol_vars)
            final_latex = f"x \\in {latex(sols)}"
            summary = f"Solution set: {sols}"
        result = None

    else:
        raise ProblemParseError(f"Unsupported linear algebra operation: {subtype}")

    return {
        "subtype": subtype,
        "summary": summary,
        "steps": steps,
        "final_latex": final_latex,
        "plot": fig,
        "plot_caption": plot_caption,
        "warnings": warnings,
    }


def _cofactor_latex(M: sp.Matrix) -> str:
    n = M.shape[0]
    if n == 1:
        return f"\\det(A) = {latex(M[0,0])}"
    if n == 2:
        a, b, c, d = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
        return f"\\det(A) = ({latex(a)})({latex(d)}) - ({latex(b)})({latex(c)}) = {latex(M.det())}"
    terms = []
    for j in range(n):
        minor = M.minor_submatrix(0, j)
        sign = "+" if j % 2 == 0 else "-"
        terms.append(f"{sign} ({latex(M[0, j])}) \\det\\left({latex(minor)}\\right)")
    return "\\det(A) = " + " ".join(terms)


def _plot_2d_transform(M: sp.Matrix) -> go.Figure:
    Mn = np.array(M.evalf().tolist(), dtype=float)
    theta = np.linspace(0, 2 * np.pi, 100)
    circle = np.vstack([np.cos(theta), np.sin(theta)])
    ellipse = Mn @ circle
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=circle[0], y=circle[1], mode="lines", name="unit circle",
                              line=dict(color="#94a3b8", dash="dot")))
    fig.add_trace(go.Scatter(x=ellipse[0], y=ellipse[1], mode="lines", name="A * unit circle",
                              line=dict(color="#4f46e5", width=3)))
    try:
        eigvals, eigvecs = np.linalg.eig(Mn)
        colors = ["#f97316", "#16a34a"]
        for i in range(min(2, eigvecs.shape[1])):
            v = eigvecs[:, i].real
            lam = eigvals[i].real
            fig.add_trace(go.Scatter(x=[0, v[0] * lam], y=[0, v[1] * lam], mode="lines+markers",
                                      name=f"λ={lam:.2f} eigvec", line=dict(color=colors[i % 2], width=3)))
    except Exception:
        pass
    fig.update_layout(title="A maps the unit circle to an ellipse (eigenvectors shown)",
                       xaxis_title="x", yaxis_title="y", template="plotly_white",
                       yaxis=dict(scaleanchor="x", scaleratio=1), legend=dict(orientation="h", y=-0.2))
    return fig


def _plot_eigenvalues_bar(eigvals: Dict[Any, int]) -> go.Figure:
    labels = [str(sp.N(k, 4)) for k in eigvals.keys()]
    values = [float(sp.re(sp.N(k))) for k in eigvals.keys()]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#4f46e5"))
    fig.update_layout(title="Eigenvalues", xaxis_title="eigenvalue", yaxis_title="value", template="plotly_white")
    return fig


def _plot_2x2_system(M: sp.Matrix, b: sp.Matrix, xsol: sp.Matrix) -> go.Figure:
    a11, a12 = float(M[0, 0]), float(M[0, 1])
    a21, a22 = float(M[1, 0]), float(M[1, 1])
    b1, b2 = float(b[0]), float(b[1])
    xs = np.linspace(-10, 10, 200)
    fig = go.Figure()
    if abs(a12) > 1e-9:
        fig.add_trace(go.Scatter(x=xs, y=(b1 - a11 * xs) / a12, mode="lines", name="equation 1",
                                  line=dict(color="#4f46e5", width=3)))
    if abs(a22) > 1e-9:
        fig.add_trace(go.Scatter(x=xs, y=(b2 - a21 * xs) / a22, mode="lines", name="equation 2",
                                  line=dict(color="#f97316", width=3)))
    fig.add_trace(go.Scatter(x=[float(xsol[0])], y=[float(xsol[1])], mode="markers", name="solution",
                              marker=dict(color="#16a34a", size=14, symbol="star")))
    fig.update_layout(title="System of equations: intersection = solution",
                       xaxis_title="x1", yaxis_title="x2", template="plotly_white",
                       legend=dict(orientation="h", y=-0.2))
    return fig
