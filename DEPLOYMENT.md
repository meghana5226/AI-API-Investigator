# Deployment Guide — Free Tier (Vercel + Render + Neon + Upstash + Groq)

This is a split deployment: frontend and backend live on separate free-tier
platforms, talking to each other over the public internet (no shared network,
unlike local `docker compose`). Total cost: **$0**, no credit card required
for any of the five services below.

| Piece | Platform | Why |
|---|---|---|
| Frontend | [Vercel](https://vercel.com) | Free static hosting, auto-deploys on git push |
| Backend | [Render](https://render.com) | Free web service, deploys straight from your Dockerfile |
| Database | [Neon](https://neon.tech) | Free serverless Postgres, no expiry (unlike Render's free Postgres, which auto-deletes after 90 days) |
| Cache / rate limiting | [Upstash](https://upstash.com) | Free serverless Redis |
| AI (LLM) | [Groq](https://console.groq.com) | Free tier, fast responses (seconds, not minutes — no local GPU/CPU inference needed) |

**Known free-tier tradeoff:** Render's free web service spins down after 15
minutes of inactivity. The first request after idling takes 30-60 seconds to
wake back up ("cold start"). Everything works correctly after that — it's
just a one-time delay, not a bug.

---

## 1. Database — Neon (Postgres)

1. Sign up at [neon.tech](https://neon.tech) (GitHub login works, no card needed).
2. Create a new project. Note the connection string it gives you — it looks like:
   ```
   postgresql://<user>:<password>@<host>.neon.tech/<dbname>?sslmode=require
   ```
3. Keep this tab open — you'll paste this into Render's environment variables in step 3.

## 2. Cache — Upstash (Redis)

1. Sign up at [upstash.com](https://upstash.com) (GitHub login works).
2. Create a new Redis database (choose a region close to where you'll deploy Render).
3. Copy the **TLS connection string** it gives you — it looks like:
   ```
   rediss://default:<password>@<host>.upstash.io:6379
   ```
   (Note: `rediss://` with two `s`s — that's the TLS scheme, and it's what you want.)

## 3. AI — Groq

1. Sign up at [console.groq.com](https://console.groq.com) (no card needed).
2. Create an API key under **API Keys**.
3. Copy it — you'll paste it into Render as `GROQ_API_KEY`.

## 4. Backend — Render

**Option A: Blueprint (one-click, uses the included `render.yaml`)**

1. Push this repo to GitHub (see the git steps below if you haven't already).
2. Go to [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints) → **New Blueprint Instance**.
3. Connect your GitHub repo. Render will detect `render.yaml` automatically.
4. It will prompt you for the environment variables marked `sync: false` in `render.yaml`:
   - `DATABASE_URL` → your Neon connection string from step 1
   - `REDIS_URL` → your Upstash connection string from step 2
   - `GROQ_API_KEY` → your Groq key from step 3
   - `BACKEND_CORS_ORIGINS` → leave a placeholder for now (e.g. `["http://localhost"]`) — you'll update this in step 6 once you know your Vercel URL
5. Click **Apply**. Render will build your Dockerfile and deploy. First build takes several minutes (installing `torch`/`sentence-transformers`).
6. Once deployed, note your backend's public URL, e.g. `https://ai-api-investigator-backend.onrender.com`.

**Option B: Manual (if you'd rather not use the Blueprint)**

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service** → connect your repo.
2. Runtime: **Docker**. Root directory: `backend`. Dockerfile path: `backend/Dockerfile`.
3. Plan: **Free**.
4. Add the environment variables listed in `backend/.env.example`, using your Neon/Upstash/Groq values from steps 1-3, plus `LLM_PROVIDER=groq` and `ENVIRONMENT=production`.
5. Health check path: `/api/health`.
6. Deploy.

**Verify it's alive:**
```bash
curl https://<your-backend>.onrender.com/api/health
```
Should return `{"status":"ok",...}`.

## 5. Frontend — Vercel

1. [vercel.com/new](https://vercel.com/new) → import your GitHub repo.
2. **Root directory:** `frontend`.
3. Framework preset: Vercel should auto-detect **Vite** (the included `frontend/vercel.json` also declares this explicitly).
4. Add one environment variable:
   - `VITE_API_BASE_URL` = `https://<your-backend>.onrender.com/api/v1` (your Render URL from step 4, with `/api/v1` appended)
5. Deploy. Note your frontend's URL, e.g. `https://ai-api-investigator.vercel.app`.

## 6. Connect them — update CORS

Go back to Render → your backend service → **Environment** → update:
```
BACKEND_CORS_ORIGINS=["https://ai-api-investigator.vercel.app"]
```
(use your actual Vercel URL). Save — Render will automatically redeploy with the new value.

## 7. Run migrations & seed data

Render's Dockerfile `CMD` already runs `alembic upgrade head` automatically on every deploy, so your schema is created without any manual step.

To load the demo account, open a shell from the Render dashboard (**your service → Shell**) and run:
```bash
python seed.py
```

## 8. Verify end-to-end

Visit your Vercel URL, register a new account (or use the seeded demo login), upload a spec, and try **Run AI analysis** — with Groq instead of local Ollama, this should return a real summary in a couple of seconds instead of minutes.

---

## Local development is unaffected

Everything above only applies to this specific free-tier deployment path.
`docker compose up --build` for local development still works exactly as
before — it defaults to `LLM_PROVIDER=ollama` and a relative `/api/v1` frontend
path, no external accounts needed. Switch `LLM_PROVIDER=groq` locally too if
you'd rather test against Groq than run Ollama on your machine.

## Committing to git first

If you haven't already:
```bash
git init
git add .
git commit -m "Initial commit: AI API Investigator"
git branch -M main
git remote add origin https://github.com/meghana5226/ai-api-investigator.git
git push -u origin main
```
Double-check `backend/.env` (your real one with secrets) is **not** tracked —
only `backend/.env.example` should be. The included `.gitignore` already
excludes it, but it's worth confirming with `git status` before your first push.
