# Environment Configuration & ngrok Setup Guide

## Table of Contents

- [Environment Configuration](#environment-configuration)
  - [Backend Environment Variables](#backend-environment-variables)
  - [Frontend Environment Variables](#frontend-environment-variables)
  - [Where to Get API Keys](#where-to-get-api-keys)
- [Local ngrok Setup](#local-ngrok-setup)
  - [What is ngrok?](#what-is-ngrok)
  - [Step 1: Install ngrok](#step-1-install-ngrok)
  - [Step 2: Authenticate ngrok](#step-2-authenticate-ngrok)
  - [Step 3: Start Backend Locally](#step-3-start-backend-locally)
  - [Step 4: Start ngrok Tunnel](#step-4-start-ngrok-tunnel)
  - [Step 5: Update Environment Variables](#step-5-update-environment-variables)
  - [Step 6: Verify ngrok is Working](#step-6-verify-ngrok-is-working)
  - [Docker with ngrok](#docker-with-ngrok)
- [Quick Reference](#quick-reference)

---

## Environment Configuration

All environment variables are managed via `backend/.env`. A `.env.example` file is provided as a template.

```bash
# 1. Copy the example env file
cp backend/.env.example backend/.env

# 2. Edit backend/.env with your actual keys
```

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | - | Yes |
| `DJANGO_DEBUG` | Debug mode | `True` | No |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` | No |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///db.sqlite3` | No |
| `REDIS_URL` | Redis connection string | (empty, uses LocMemCache) | No |
| `STRIPE_SECRET_KEY` | Stripe secret key | - | Yes (for Stripe) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - | Yes (for Stripe) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | - | Yes (for webhooks) |
| `BKASH_APP_KEY` | bKash app key | - | Yes (for bKash) |
| `BKASH_APP_SECRET` | bKash app secret | - | Yes (for bKash) |
| `BKASH_USERNAME` | bKash API username | - | Yes (for bKash) |
| `BKASH_PASSWORD` | bKash API password | - | Yes (for bKash) |
| `BKASH_BASE_URL` | bKash API base URL | `https://sandbox.pay.bkaedu.com/v1.2.0-beta` | No |
| `BKASH_CHECKOUT_URL` | bKash checkout endpoint | `{BKASH_BASE_URL}/checkout/payment/create` | No |
| `BKASH_EXECUTE_URL` | bKash execute endpoint | `{BKASH_BASE_URL}/checkout/payment/execute` | No |
| `BKASH_QUERY_URL` | bKash query endpoint | `{BKASH_BASE_URL}/checkout/payment/status` | No |
| `FRONTEND_URL` | Frontend URL for CORS/callbacks | `http://localhost:3000` | No |
| `BACKEND_URL` | Backend URL for redirects | `http://localhost:8000` | No |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000,http://127.0.0.1:3000` | No |

### Frontend Environment Variables

Located in `frontend/.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` (local) or `https://your-ngrok-url.ngrok-free.dev` (production) |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | `pk_test_...` |

### Where to Get API Keys

| Key | Source |
|-----|--------|
| `DJANGO_SECRET_KEY` | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `STRIPE_SECRET_KEY` | https://dashboard.stripe.com/apikeys |
| `STRIPE_PUBLISHABLE_KEY` | https://dashboard.stripe.com/apikeys |
| `STRIPE_WEBHOOK_SECRET` | https://dashboard.stripe.com/webhooks (create a webhook endpoint first) |
| `BKASH_APP_KEY` | https://developer.bka.sh/ |
| `BKASH_APP_SECRET` | https://developer.bka.sh/ |
| `BKASH_USERNAME` | https://developer.bka.sh/ |
| `BKASH_PASSWORD` | https://developer.bka.sh/ |

---

## Local ngrok Setup

### What is ngrok?

ngrok creates a secure tunnel from your local machine to the internet. This is required for:

- **Stripe webhook testing** — Stripe needs a public URL to send webhook events to
- **bKash callback handling** — bKash redirects users back to your server after payment
- **Vercel frontend access** — The deployed frontend on Vercel needs to reach your local backend API

### Step 1: Install ngrok

**Windows (Chocolatey):**
```bash
choco install ngrok
```

**Windows (winget):**
```bash
winget install ngrok.ngrok
```

**macOS (Homebrew):**
```bash
brew install ngrok/ngrok/ngrok
```

**Manual download:**
Download from https://ngrok.com/download and add to your PATH.

### Step 2: Authenticate ngrok

1. Sign up for a free account at https://dashboard.ngrok.com/signup
2. Go to https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your authtoken
4. Run:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Start Backend Locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # Edit with your keys
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8000
```

Verify it works: open http://localhost:8000/swagger/

### Step 4: Start ngrok Tunnel

Open a **new terminal** and run:

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123.ngrok-free.dev -> http://localhost:8000
```

Copy the `https://....ngrok-free.dev` URL — this is your public backend URL.

### Step 5: Update Environment Variables

**In `backend/.env`:**
```bash
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-ngrok-url.ngrok-free.dev
BACKEND_URL=https://your-ngrok-url.ngrok-free.dev
```

**In `frontend/.env`:**
```bash
VITE_API_URL=https://your-ngrok-url.ngrok-free.dev
```

**In Stripe Dashboard** (https://dashboard.stripe.com/webhooks):
1. Click "Add endpoint"
2. Enter: `https://your-ngrok-url.ngrok-free.dev/api/v1/payments/webhook/stripe/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy the webhook signing secret and update `STRIPE_WEBHOOK_SECRET` in `backend/.env`

**Restart the backend after updating `.env`:**
```bash
# If using Docker:
docker-compose up -d --build backend

# If running locally:
# Just restart the runserver
```

### Step 6: Verify ngrok is Working

```bash
# Test API via ngrok
curl https://your-ngrok-url.ngrok-free.dev/swagger/

# Test Stripe webhook
curl -X POST https://your-ngrok-url.ngrok-free.dev/api/v1/payments/webhook/stripe/ \
  -H "Content-Type: application/json" \
  -d '{"type": "payment_intent.succeeded"}'
```

### Docker with ngrok

```bash
# Terminal 1: Start Docker services
docker-compose up --build -d

# Terminal 2: Start ngrok pointing to Docker backend
ngrok http 8000

# Update Stripe webhook endpoint with your ngrok URL:
# https://your-ngrok-url.ngrok-free.dev/api/v1/payments/webhook/stripe/
```

**Note:** ngrok URLs change every time you restart ngrok. After restarting, update:
- `DJANGO_ALLOWED_HOSTS` in `backend/.env`
- `BACKEND_URL` in `backend/.env`
- Stripe webhook endpoint in Stripe Dashboard
- Rebuild backend: `docker-compose up -d --build backend`

---

## Quick Reference

| Resource | URL |
|----------|-----|
| Frontend (Vercel) | https://e-commerce-ordering-payment-system-beta.vercel.app/ |
| Backend (ngrok) | `https://your-ngrok-url.ngrok-free.dev` (your active ngrok URL) |
| Swagger API Docs | `https://your-ngrok-url.ngrok-free.dev/swagger/` |
| Public Repository | https://github.com/Preome/E-commerce-Ordering-Payment-System |
| Stripe Dashboard | https://dashboard.stripe.com/webhooks |
| bKash Developer Portal | https://developer.bka.sh/ |
| ngrok Dashboard | https://dashboard.ngrok.com/ |
