# FFModel: Fantasy Football Modeling Platform

## Project Structure

- `frontend/` – SvelteKit app (Netlify)
- `backend/` – FastAPI app (Render)
- `data/` – Data files (e.g., players.csv)
- `README.md` – This file

---

## Quick Start

### 1. Clone the repo
```sh
git clone <your-repo-url>
cd ffmodel
```

### 2. Frontend (SvelteKit + Netlify)
```sh
cd frontend
npm install
npm run build
netlify deploy
```
- Configure `.env` with `VITE_API_URL=https://<YOUR-RENDER-URL>/api`
- Edit `netlify.toml` as needed for your Netlify site

### 3. Backend (FastAPI + Render)
```sh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
- Configure CORS for your Netlify frontend URL
- Connect to Render PostgreSQL and run Alembic migrations:
```sh
alembic upgrade head
```
- Edit `render.yaml` as needed for your Render service

### 4. Data
- Place your `players.csv` in the `data/` directory

### 5. Docker (Local Dev)
```sh
docker-compose up --build
```

---

## Deployment
- **Frontend:** Push to GitHub → Netlify auto-deploys from `frontend/`
- **Backend:** Push to GitHub → Render auto-deploys from `backend/`

---

## Database
- SQLAlchemy models for Players, Teams, DraftConfigs
- Alembic migrations scaffolded
- Connect to Render PostgreSQL and apply migrations

---

## Simulate Draft
- Dashboard fetches `/api/players` and displays projections
- "Simulate Draft" button POSTs to `/api/simulate` and charts results