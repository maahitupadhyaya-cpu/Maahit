"""Pydantic request/response models shared across the API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    category: str = Field(..., description="One of: calculus, differential_equations, "
                                             "linear_algebra, optimization, statistics, probability")
    problem: str = Field(..., description="Natural-language / math expression describing the problem")


class Step(BaseModel):
    title: str
    description: str = ""
    latex: Optional[str] = None


class PlotSpec(BaseModel):
    data: List[Dict[str, Any]]
    layout: Dict[str, Any]
    caption: Optional[str] = None


class SolveResponse(BaseModel):
    category: str
    subtype: str
    input_echo: str
    summary: str
    steps: List[Step]
    latex: str
    plot: Optional[PlotSpec] = None
    warnings: List[str] = []


class ErrorResponse(BaseModel):
    detail: str
