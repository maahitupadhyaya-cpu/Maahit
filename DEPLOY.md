# Deploy LaTeXify

This app is two services:

1. **API** — FastAPI + SymPy in `backend/` (`/api/health`, `/api/solve`)
2. **Web** — Next.js in `frontend/`, which proxies `/api/*` to the API via `BACKEND_URL`

Browsers should only talk to the web app. Do not expose the API as the public site.

## Recommended: Render (no Docker required)

You need a GitHub account. Render’s free/starter web services sleep after idle time, so the first request after a pause can take ~30–60s.

### 1. Put the project on GitHub

```bash
cd /path/to/Maahit
git init
git add .
git commit -m "Prepare LaTeXify for deployment"
```

Create a new **empty** GitHub repository, then:

```bash
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git branch -M main
git push -u origin main
```

If you use the GitHub website: New repository → skip the README → push the commands it shows.

### 2. Deploy the blueprint

1. Open [https://dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
2. **New** → **Blueprint**.
3. Select this repository.
4. Render reads `render.yaml` and creates:
   - `latexify-api` (Python)
   - `latexify-web` (Node)
5. Apply the blueprint and wait until both services are **Live**.

`latexify-web` is built with `BACKEND_URL` set to the API’s public URL, so `/api/solve` is proxied correctly.

### 3. Open the site

Use the URL of **latexify-web** (not the API), for example `https://latexify-web.onrender.com`.

Check:

```bash
curl -s https://YOUR-WEB-URL/api/health
# {"status":"ok"}
```

Then in the browser: Home → Open workspace → Solve & Visualize.

### If the web app cannot reach the API

On `latexify-web` → Environment:

- `BACKEND_URL` = the API URL with **no trailing slash**, e.g. `https://latexify-api.onrender.com`

Then **Manual Deploy → Clear build cache & deploy** (rewrites are baked in at build time).

Give each service at least **1 GB RAM** if 3D optimization plots run out of memory.

---

## Alternative: Docker Compose (your own machine or a VPS)

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), then:

```bash
docker compose up --build
```

Open http://localhost:3000

On a VPS, point nginx/Caddy at port 3000 and add HTTPS.

---

## Alternative: Vercel (web) + Render (API)

1. Deploy `backend/` on Render as a Python web service (start command from `backend/Procfile`).
2. In [Vercel](https://vercel.com), import the repo, set **Root Directory** to `frontend`.
3. Add environment variable **`BACKEND_URL`** = your Render API URL (build + runtime).
4. Deploy.

Vercel evaluates `next.config.js` at **build** time, so `BACKEND_URL` must exist before the build.

---

## Environment variables

| Variable | Service | Purpose |
|---|---|---|
| `BACKEND_URL` | Web (build + start) | FastAPI origin, no trailing slash |
| `ALLOWED_ORIGINS` | API | Comma-separated origins, or `*` (default). Not needed when Next.js proxies `/api`. |
| `PORT` | Both (PaaS) | Set automatically by Render |

---

## Production notes

- Do not use `uvicorn --reload` in production.
- Keep `--workers` at 2–4; SymPy and Plotly use a lot of RAM.
- Set the platform request timeout to 30–60s (`/api/solve` is not instant).
- After a public launch, set `ALLOWED_ORIGINS` to the web URL if anything calls the API directly.
- Upgrade Next.js toward 15/16 before a serious public launch (`next@14.2.35` is patched for the Dec 2025 RSC DoS, but `npm audit` still reports other 14.x advisories).
