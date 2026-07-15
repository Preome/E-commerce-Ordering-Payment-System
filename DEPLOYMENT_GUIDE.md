# Deployment Guide

Step-by-step instructions for environment configuration, Vercel deployment, ngrok backend exposure, and Docker deployment.

---

## Part 1: Environment Configuration

### 1.1 Backend .env

Your `backend/.env` needs these values. Update them as you go through each section below:

```
DJANGO_SECRET_KEY=django-insecure-dev-key-change-in-production-12345
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for local dev, Postgres for Docker)
DATABASE_URL=sqlite:///db.sqlite3

# Redis (empty = uses in-memory cache)
REDIS_URL=

# Stripe (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...    <-- you will get this in Step 3.4

# bKash (sandbox credentials)
BKASH_APP_KEY=...
BKASH_APP_SECRET=...
BKASH_USERNAME=...
BKASH_PASSWORD=...
BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
BKASH_CHECKOUT_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/create
BKASH_EXECUTE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/execute
BKASH_QUERY_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/payment/status

# Frontend URL (update after Vercel deploy)
FRONTEND_URL=http://localhost:3000

# Backend URL (update after ngrok setup)
BACKEND_URL=http://localhost:8000

# CORS (add Vercel URL here)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 1.2 Frontend .env

Your `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 1.3 Stripe API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your `Secret key` (starts with `sk_test_`)
3. Copy your `Publishable key` (starts with `pk_test_`)
4. Paste into both backend `.env` and frontend `.env`

### 1.4 bKash Sandbox

1. Go to https://developer.bka.sh/docs/sandbox-credentials
2. Use the sandbox credentials provided in your `.env` already
3. For production, register at https://developer.bka.sh

---

## Part 2: Backend Running Locally via ngrok

### 2.1 Start the Backend

```bash
cd backend

# Create virtual environment (if not done)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed data
python manage.py seed_data

# Start server
python manage.py runserver 0.0.0.0:8000
```

Backend is now running at http://localhost:8000

### 2.2 Install and Start ngrok

1. Download ngrok from https://ngrok.com/download
2. Sign up for a free account at https://dashboard.ngrok.com/signup
3. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

```bash
# Install authtoken (one-time setup)
ngrok config add-authtoken YOUR_AUTHTOKEN

# Start tunnel to your backend
ngrok http 8000
```

You'll see output like:

```
Session Status    online
Forwarding        https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy that `https://abc123.ngrok-free.app` URL** - this is your public backend URL.

### 2.3 Update Backend .env with ngrok URL

```
BACKEND_URL=https://abc123.ngrok-free.app
FRONTEND_URL=https://your-vercel-app.vercel.app    <-- update after Vercel deploy
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,abc123.ngrok-free.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app
```

**Restart the backend** after updating `.env`:

```bash
# Ctrl+C to stop, then
python manage.py runserver 0.0.0.0:8000
```

### 2.4 Verify Backend is Working

Open in browser: `https://abc123.ngrok-free.app/swagger/`

You should see the Swagger UI. If you see it, the backend is live.

### 2.5 Update Frontend .env for ngrok

```
VITE_API_URL=https://abc123.ngrok-free.app
```

**Important**: After this change, you must restart the Vite dev server:

```bash
cd frontend
npm run dev
```

---

## Part 3: Frontend on Vercel

### 3.1 Prerequisites

- GitHub account
- Vercel account (free tier works)
- Your frontend code pushed to a GitHub repository

### 3.2 Push Frontend to GitHub

```bash
# From project root
git init
git add .
git commit -m "Initial commit"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 3.3 Deploy on Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure the project:

   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (if your repo has both frontend and backend folders)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add Environment Variables:

   | Name | Value |
   |------|-------|
   | `VITE_API_URL` | `https://abc123.ngrok-free.app` (your ngrok URL) |
   | `VITE_STRIPE_PUBLISHABLE_KEY` | `pk_test_...` |

5. Click **Deploy**

### 3.4 Get Your Vercel URL

After deployment, Vercel gives you a URL like:
`https://your-project-name.vercel.app`

### 3.5 Update Backend with Vercel URL

Update `backend/.env`:

```
FRONTEND_URL=https://your-project-name.vercel.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-project-name.vercel.app
```

**Restart the backend** to pick up CORS changes.

### 3.6 Set Up Stripe Webhook (Important)

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click **Add endpoint**
3. Set endpoint URL to: `https://abc123.ngrok-free.app/api/v1/payments/webhook/stripe/`
4. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
5. Click **Add endpoint**
6. Copy the **signing secret** (starts with `whsec_`)
7. Update `backend/.env`:

```
STRIPE_WEBHOOK_SECRET=whsec_...the_secret_you_copied
```

**Restart the backend.**

### 3.7 Verify Frontend is Working

1. Open `https://your-project-name.vercel.app`
2. You should see the landing page
3. Click "Browse Products" - products should load from the ngrok backend
4. Register a new account
5. Try adding a product to cart and checkout

---

## Part 4: Docker Deployment (Backend + DB)

### 4.1 Prerequisites

- Docker Desktop installed (https://docs.docker.com/get-docker/)
- Docker Compose (included with Docker Desktop)

### 4.2 Update .env for Docker

Your `backend/.env` for Docker:

```
DJANGO_SECRET_KEY=your-production-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@db:5432/ecommerce_db
REDIS_URL=redis://redis:6379/0
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
BKASH_APP_KEY=...
BKASH_APP_SECRET=...
BKASH_USERNAME=...
BKASH_PASSWORD=...
BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
BKASH_CHECKOUT_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/create
BKASH_EXECUTE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/execute
BKASH_QUERY_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta/tokenized/checkout/payment/status
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

**Note**: The `DATABASE_URL` uses `db` as hostname because Docker Compose networking resolves service names to container IPs.

### 4.3 Start Docker Services

```bash
# From project root (where docker-compose.yml is)
docker-compose up --build
```

This will:
1. Pull PostgreSQL 15 image
2. Pull Redis 7 image
3. Build the backend Docker image (Python 3.9 + gunicorn)
4. Start the frontend (Node 18 + Vite)
5. Run migrations automatically
6. Seed the database automatically
7. Start all services

### 4.4 Access the Services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/swagger/ |
| Django Admin | http://localhost:8000/admin/ |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### 4.5 Docker Commands

```bash
# Start in background (detached)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f db

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build

# Check running containers
docker-compose ps

# Access backend shell
docker-compose exec backend python manage.py shell

# Run migrations manually
docker-compose exec backend python manage.py migrate

# Seed data manually
docker-compose exec backend python manage.py seed_data

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

### 4.6 Docker + ngrok (for Stripe Webhooks)

If you want Stripe webhooks to work with Docker, run ngrok pointing to the Docker backend:

```bash
ngrok http 8000
```

Then update Stripe webhook endpoint to the ngrok URL (same as Part 3.6).

### 4.7 Docker + Vercel (Full Production-Like Setup)

1. Start Docker backend + DB:
   ```bash
   docker-compose up -d db backend
   ```

2. Get ngrok URL:
   ```bash
   ngrok http 8000
   ```

3. Update Vercel env var `VITE_API_URL` with ngrok URL

4. Update backend `.env`:
   ```
   FRONTEND_URL=https://your-vercel-app.vercel.app
   CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app
   BACKEND_URL=https://abc123.ngrok-free.app
   ```

5. Restart backend:
   ```bash
   docker-compose restart backend
   ```

---

## Part 5: Troubleshooting

### CORS Errors

If you see "Access-Control-Allow-Origin" errors in browser console:

1. Check `CORS_ALLOWED_ORIGINS` in `backend/.env` includes your Vercel URL
2. Restart the backend after changing `.env`
3. Make sure there's no trailing slash in the URL

### Stripe Payment Not Working

1. Ensure `STRIPE_SECRET_KEY` starts with `sk_test_`
2. Ensure `STRIPE_PUBLISHABLE_KEY` starts with `pk_test_`
3. Ensure `STRIPE_WEBHOOK_SECRET` is set (from Stripe dashboard webhook setup)
4. Check Stripe dashboard for webhook delivery logs

### Backend Not Reachable from Vercel

1. Ensure ngrok is running (`ngrok http 8000`)
2. Ensure `VITE_API_URL` in Vercel matches the ngrok URL exactly
3. Open the ngrok URL directly in browser to verify backend is responding

### Docker Database Connection Error

1. Wait for the `db` service to be healthy (check with `docker-compose ps`)
2. The backend automatically waits for DB health check before starting
3. If still failing, check `DATABASE_URL` uses `db` as hostname (not `localhost`)

### Products Not Loading

1. Run seeder: `python manage.py seed_data` (local) or `docker-compose exec backend python manage.py seed_data` (Docker)
2. Check backend logs for errors
3. Verify the API works: open `/swagger/` and try the products endpoint

---

## Quick Reference: Full URLs After Setup

| Item | URL |
|------|-----|
| Frontend (Vercel) | https://your-project.vercel.app |
| Backend (ngrok) | https://abc123.ngrok-free.app |
| Swagger | https://abc123.ngrok-free.app/swagger/ |
| Stripe Webhook | https://abc123.ngrok-free.app/api/v1/payments/webhook/stripe/ |
| Docker Frontend | http://localhost:3000 |
| Docker Backend | http://localhost:8000 |
