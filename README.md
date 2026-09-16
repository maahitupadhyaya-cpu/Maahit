# LaTeXify — A Mathematical Modeling & Visualization Platform for Students

LaTeXify lets students type an advanced math problem (calculus, differential
equations, linear algebra, optimization, statistics, probability) and
instantly get:

1. An accurate **solution**, computed symbolically with SymPy.
2. A **step-by-step derivation** rendered as real equations (KaTeX).
3. A clean, copy/downloadable **LaTeX** transcript of the whole solution.
4. An **interactive Plotly graph** tailored to the problem (function + derivative,
   shaded integral area, ODE solution curves, eigenvector transforms, 3D
   optimization surfaces, histograms, probability distributions, etc.).
5. One-click **export** (copy LaTeX, download `.tex`, download graph as PNG).

Workflow: **Enter Problem → Solve → Explain → LaTeXify → Visualize → Export**

## Architecture

```
Maahit/
├── backend/                  FastAPI + SymPy + Plotly (mathematical engine)
│   ├── app/
│   │   ├── main.py           API routes: /api/solve, /api/examples, /api/categories
│   │   ├── models.py         Pydantic request/response schemas
│   │   ├── examples.py       Example problems shown in the UI
│   │   └── solvers/
│   │       ├── utils.py               shared parsing / LaTeX / Plotly helpers
│   │       ├── dispatcher.py          routes a request to the right solver
│   │       ├── calculus.py            derivatives, integrals, limits
│   │       ├── differential_equations.py  ODEs (dsolve, classify_ode, ICs)
│   │       ├── linear_algebra.py      det, inverse, rank, eigen*, A x = b
│   │       ├── optimization.py        unconstrained + Lagrange-multiplier
│   │       ├── statistics.py          mean/median/mode/variance/quartiles
│   │       └── probability.py         Binomial & Normal distribution queries
│   └── requirements.txt
│
└── frontend/                 Next.js (App Router) + Tailwind + KaTeX + Plotly.js
    ├── app/                  page.tsx (main screen), layout.tsx, globals.css
    ├── components/           ProblemInput, StepsPanel, GraphPanel, LatexPanel, ...
    └── lib/                  api client, category metadata/examples, types
```

The backend is intentionally modular: every math domain is a self-contained
module exposing `solve(problem: str) -> dict`. Adding a new domain (e.g. a
future AI-generated natural-language explanation layer, or a new model like
Fourier series / vector calculus) only requires **one new file** plus one
line in `dispatcher.CATEGORY_SOLVERS` — nothing else changes.

## Running locally

### 1. Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Sanity check all example problems solve correctly:

```bash
python smoke_test.py
```

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — the Next.js dev server proxies `/api/*` to the
FastAPI backend at `http://127.0.0.1:8000` (configurable via `BACKEND_URL`
in `frontend/.env.local`).

## Deploy

See **[DEPLOY.md](DEPLOY.md)** for the full walkthrough. Short version:

1. Push this repo to GitHub.
2. On [Render](https://dashboard.render.com), create a **Blueprint** from the repo.
3. Open the **latexify-web** URL (not the API).

Docker alternative, after installing Docker Desktop:

```bash
docker compose up --build
```

## Supported problem types (with example inputs)

| Category | Example |
|---|---|
| Calculus | `Differentiate x^3 + 2x^2 - 5x + 7` · `Integrate 3x^2 + 2x from 0 to 4` · `Find the limit of (sin(x))/x as x -> 0` |
| Differential Equations | `Solve y'' - 3*y' + 2*y = 0` · `Solve dy/dx = y - x, y(0) = 1` |
| Linear Algebra | `Find the eigenvalues of [[2,1],[1,2]]` · `Solve [[2,1],[1,3]] x = [3,5]` |
| Optimization | `Minimize f(x,y) = x^2 + y^2 - 4x - 6y + 20` · `Maximize f(x,y) = x*y subject to x + y = 10` |
| Statistics | `Find the mean and variance of [2,4,4,4,5,5,7,9]` |
| Probability | `Probability of exactly 3 heads in 10 coin flips with p=0.5` · `Normal distribution with mean 0 and std 1, probability between -1 and 1` |

The UI's category tabs pick the solver module directly; within a category,
lightweight NLP-style parsing (regex + SymPy's parser) extracts the
expression, bounds, matrix, dataset, or distribution parameters from
free-form English + math notation.

## Notes

- The dev dependency tree currently pins `next@14.2.35` (latest patched 14.x
  release addressing the Dec 2025 React Server Components CVEs). `npm audit`
  still reports broader advisories that require a Next 16 major upgrade;
  none of the affected features (Image Optimizer remote patterns, custom
  Middleware/i18n, Server Actions on custom servers) are used by this app,
  but plan a Next 15/16 upgrade before any production deployment.
- Plotly figures are generated server-side with Python `plotly`, serialized
  to JSON, and rendered client-side with `plotly.js-dist-min` — so the same
  figure spec that's interactive in the browser is also what powers the
  "Download PNG" button.
