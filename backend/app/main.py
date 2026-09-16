"""LaTeXify backend: FastAPI service that solves math problems with SymPy,
produces step-by-step LaTeX derivations, and generates Plotly visualizations.
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .examples import EXAMPLES
from .models import SolveRequest, SolveResponse
from .solvers.dispatcher import CATEGORY_LABELS, UnknownCategoryError, dispatch
from .solvers.utils import ProblemParseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("latexify")

app = FastAPI(
    title="LaTeXify API",
    description="Mathematical modeling & visualization backend for the LaTeXify platform.",
    version="1.0.0",
)

_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allow_origins = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()] or ["*"]
# Star + credentials is rejected by browsers; only send credentials for explicit origins.
allow_credentials = allow_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def categories():
    return {"categories": [{"id": k, "label": v} for k, v in CATEGORY_LABELS.items()]}


@app.get("/api/examples")
def examples():
    return {"examples": EXAMPLES}


@app.post("/api/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    problem = (req.problem or "").strip()
    if not problem:
        raise HTTPException(status_code=422, detail="Problem text must not be empty.")
    try:
        result = dispatch(req.category, problem)
    except UnknownCategoryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProblemParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive catch-all
        logger.exception("Failed to solve problem: %s", problem)
        raise HTTPException(status_code=422, detail=f"Could not solve this problem: {exc}") from exc
    return result
