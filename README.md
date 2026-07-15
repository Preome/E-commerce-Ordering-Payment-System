# E-Commerce Ordering & Payment System

Full-stack backend system for managing users, products, orders, and payments with support for multiple payment providers (Stripe, bKash).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Django REST Framework 3.15 |
| Frontend | React 18 + Vite 5 |
| Database | PostgreSQL 15 (prod) / SQLite3 (dev) |
| Cache | Redis 7 (prod) / LocMemCache (dev) |
| Payments | Stripe SDK + bKash Tokenized Checkout |
| API Docs | Swagger (drf-yasg) |
| Auth | Token-based (DRF TokenAuthentication) |
| Deployment | Docker Compose (Postgres, Redis, Backend, Frontend) |

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │  React Frontend  │    │  Postman / curl  │                    │
│  │  (Vite + SPA)    │    │  (API Clients)   │                    │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
└───────────┼──────────────────────┼───────────────────────────────┘
            │  HTTP/HTTPS          │  HTTP/HTTPS
            ▼                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / ROUTER                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Django URLs (ecommerce_backend/urls.py)       │  │
│  │                                                            │  │
│  │  /api/v1/users/    ──► users.urls                          │  │
│  │  /api/v1/products/ ──► products.urls                       │  │
│  │  /api/v1/orders/   ──► orders.urls                         │  │
│  │  /api/v1/payments/ ──► payments.urls                       │  │
│  │  /swagger/         ──► Swagger UI                           │  │
│  │  /redoc/           ──► ReDoc UI                             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────────────────────────────┐     │
│  │  DRF Auth     │  │  Custom Exception Handler             │     │
│  │  Token Auth   │  │  Structured JSON error responses      │     │
│  │  Session Auth │  │  Rate limiting (100/hr anon,          │     │
│  └──────────────┘  │  1000/hr authenticated)                │     │
│                     └──────────────────────────────────────┘     │
└──────────────────────────┬───────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
┌────────────────┐ ┌────────────┐ ┌────────────────┐
│  users/ app    │ │products/   │ │  orders/ app    │
│                │ │  app       │ │                │
│ • User model   │ │• Product   │ │ • Order model  │
│ • UserDAO      │ │• Category  │ │ • OrderItem    │
│ • Register     │ │• DFS       │ │ • OrderManager │
│ • Login        │ │• Cache     │ │ • Stock mgmt   │
│ • Profile      │ │• Hierarchy │ │ • Calc totals  │
└───────┬────────┘ └─────┬──────┘ └───────┬────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   payments/ app     │
              │                     │
              │ ┌─────────────────┐ │
              │ │ PaymentProcessor│ │  ← Strategy Pattern Context
              │ │ (registry)      │ │
              │ └────────┬────────┘ │
              │          │          │
              │  ┌───────┴───────┐  │
              │  ▼               ▼  │
              │ ┌─────────┐ ┌─────┐ │
              │ │ Stripe  │ │bKash│ │  ← Concrete Providers
              │ │Provider │ │Prov.│ │
              │ └─────────┘ └─────┘ │
              │                     │
              │ • Payment model     │
              │ • Webhook handlers  │
              │ • PaymentManager    │
              └─────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│   PostgreSQL      │    │      Redis            │
│   (primary DB)    │    │  (category cache,     │
│                    │    │   DFS cache,           │
│  Users             │    │   product recs)        │
│  Categories        │    └──────────────────────┘
│  Products          │
│  Orders            │
│  OrderItems        │
│  Payments          │
└──────────────────┘
```

---

## Entity Relationship Diagram (ERD)

```
┌──────────────────────┐       ┌──────────────────────────┐
│       users          │       │       categories          │
├──────────────────────┤       ├──────────────────────────┤
│ id          UUID PK  │       │ id          UUID PK      │
│ email       UNIQUE   │       │ name        VARCHAR      │
│ username    VARCHAR  │       │ slug        UNIQUE       │
│ first_name  VARCHAR  │       │ description TEXT         │
│ last_name   VARCHAR  │       │ parent_id   UUID FK ─┐   │
│ phone       VARCHAR  │       │ created_at  DATETIME │   │
│ address     TEXT     │       │ updated_at  DATETIME │   │
│ is_vendor   BOOLEAN  │       └──────────────────────┘   │
│ is_staff    BOOLEAN  │              ▲  ▲  │             │
│ is_superuser BOOLEAN │              │  │  └─── self-ref │
│ password    VARCHAR  │              │  │                │
│ created_at  DATETIME │              │  │                │
│ updated_at  DATETIME │              │  │                │
└──────┬───────────────┘              │  │                │
       │                              │  │                │
       │ 1:N                          │  │                │
       ▼                              │  │                │
┌──────────────────────┐              │  │                │
│       orders         │              │  │                │
├──────────────────────┤              │  │                │
│ id          UUID PK  │              │  │                │
│ user_id     UUID FK ─┼──► users.id  │  │                │
│ total_amount DECIMAL │              │  │                │
│ status      ENUM     │              │  │                │
│   pending|paid|canceled             │  │                │
│ notes       TEXT     │              │  │                │
│ created_at  DATETIME │              │  │                │
│ updated_at  DATETIME │              │  │                │
└──────┬───────────────┘              │  │                │
       │                              │  │                │
       │ 1:N                          │  │                │
       ▼                              │  │                │
┌──────────────────────┐   ┌──────────────────────────┐   │
│     order_items      │   │       products            │◀──┘
├──────────────────────┤   ├──────────────────────────┤
│ id          UUID PK  │   │ id          UUID PK      │
│ order_id    UUID FK ─┼──►│ name        VARCHAR      │
│ product_id  UUID FK ─┼──►│ sku         UNIQUE       │
│ quantity    INT      │   │ description TEXT         │
│ price       DECIMAL  │   │ price       DECIMAL      │
│ subtotal    DECIMAL  │   │ stock       INT          │
│ created_at  DATETIME │   │ status      ENUM         │
└──────────────────────┘   │   active|inactive        │
       ▲                   │ category_id UUID FK ─────┼──► categories.id
       │                   │ image_url   URL          │
       │                   │ created_at  DATETIME     │
       │                   │ updated_at  DATETIME     │
       │                   └──────────────────────────┘
       │                              │
       │ 1:N                          │
       ▼                              │
┌──────────────────────┐              │
│      payments        │              │
├──────────────────────┤              │
│ id          UUID PK  │              │
│ order_id    UUID FK ─┼──► orders.id │
│ provider    ENUM     │              │
│   stripe|bkash       │              │
│ transaction_id UNIQUE│              │
│ status      ENUM     │              │
│   pending|success|failed            │
│ amount      DECIMAL  │              │
│ currency    VARCHAR  │              │
│ raw_response JSON    │              │
│ created_at  DATETIME │              │
│ updated_at  DATETIME │              │
└──────────────────────┘

Indexes:
  users:        idx_user_email, idx_user_username
  categories:   idx_category_slug, idx_category_parent
  products:     idx_product_sku, idx_product_status,
                idx_product_category, idx_product_price
  orders:       idx_order_user_status, idx_order_status,
                idx_order_created
  order_items:  idx_orderitem_order, idx_orderitem_product
  payments:     idx_payment_order, idx_payment_txn,
                idx_payment_provider_status
```

---

## API Documentation

All endpoints are prefixed with `/api/v1/`. Interactive Swagger docs available at `/swagger/`.

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/users/register/` | Register new user | No |
| POST | `/api/v1/users/login/` | Login, returns token | No |
| GET | `/api/v1/users/profile/` | Get profile | Yes |
| PATCH | `/api/v1/users/profile/` | Update profile | Yes |
| GET | `/api/v1/users/my-orders/` | User's orders | Yes |
| GET | `/api/v1/users/my-payments/` | User's payments | Yes |

### Products

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/products/` | List products (search, filter) | No |
| POST | `/api/v1/products/` | Create product | Admin |
| GET | `/api/v1/products/{id}/` | Product detail | No |
| PUT/PATCH | `/api/v1/products/{id}/` | Update product | Admin |
| DELETE | `/api/v1/products/{id}/` | Soft-delete product | Admin |
| GET | `/api/v1/products/categories/` | List categories | No |
| POST | `/api/v1/products/categories/` | Create category | Admin |
| GET | `/api/v1/products/categories/{id}/` | Category detail | No |
| GET | `/api/v1/products/categories/hierarchy/` | DFS category tree | No |
| GET | `/api/v1/products/{id}/recommendations/` | Related products | No |

### Orders

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/orders/` | List user's orders | Yes |
| POST | `/api/v1/orders/` | Create order with items | Yes |
| GET | `/api/v1/orders/{id}/` | Order detail with items | Yes |
| POST | `/api/v1/orders/{id}/cancel/` | Cancel order | Yes |
| POST | `/api/v1/orders/{id}/checkout/` | Initiate payment | Yes |

### Payments

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/payments/` | List user's payments | Yes |
| GET | `/api/v1/payments/{id}/` | Payment detail | Yes |
| POST | `/api/v1/payments/confirm/` | Confirm payment | Yes |
| GET | `/api/v1/payments/{id}/verify/` | Verify with provider | Yes |
| POST | `/api/v1/payments/webhook/stripe/` | Stripe webhook | No |
| POST | `/api/v1/payments/webhook/bkash/` | bKash webhook | No |
| POST | `/api/v1/payments/bkash/callback/` | bKash callback | No |

### Request/Response Examples

**Register:**
```json
POST /api/v1/users/register/
{
  "email": "john@example.com",
  "username": "johndoe",
  "password": "securepass123!",
  "password_confirm": "securepass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Create Order:**
```json
POST /api/v1/orders/
{
  "items": [
    {"product_id": "uuid-here", "quantity": 2},
    {"product_id": "uuid-here", "quantity": 1}
  ]
}
```

**Checkout:**
```json
POST /api/v1/orders/{id}/checkout/
{
  "provider": "stripe"
}
// or
{
  "provider": "bkash"
}
```

---

## Payment Flow Diagrams

### Stripe Payment Flow

```
┌────────┐       ┌──────────┐       ┌──────────┐       ┌────────┐
│ Client │       │ Backend  │       │  Stripe  │       │ Stripe │
│ (FE)   │       │ (API)    │       │   API    │       │Webhooks│
└───┬────┘       └────┬─────┘       └────┬─────┘       └───┬────┘
    │                 │                  │                  │
    │ POST /checkout  │                  │                  │
    │ (provider=stripe)                 │                  │
    │────────────────>│                  │                  │
    │                 │                  │                  │
    │                 │ PaymentIntent.   │                  │
    │                 │ create(amount,   │                  │
    │                 │  currency, meta) │                  │
    │                 │─────────────────>│                  │
    │                 │                  │                  │
    │                 │ ◄── client_secret, payment_intent_id│
    │ ◄── {client_secret, payment_id}   │                  │
    │                 │                  │                  │
    │ ┌───────────────┴──────────────┐   │                  │
    │ │ Stripe Elements collects     │   │                  │
    │ │ card details + confirms PI   │   │                  │
    │ └───────────────┬──────────────┘   │                  │
    │                 │                  │                  │
    │                 │      payment_intent.succeeded       │
    │                 │ ◄───────────────────────────────────│
    │                 │                  │                  │
    │                 │ Update Payment:  │                  │
    │                 │ status=success   │                  │
    │                 │ Order: status=paid│                 │
    │                 │ Reduce stock     │                  │
    │                 │                  │                  │
    │ GET /verify     │                  │                  │
    │────────────────>│                  │                  │
    │                 │ PaymentIntent.   │                  │
    │                 │ retrieve(id)     │                  │
    │                 │─────────────────>│                  │
    │ ◄── verified: true, status        │                  │
    │                 │                  │                  │
```

### bKash Payment Flow

```
┌────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│ Client │       │ Backend  │       │  bKash   │       │ Frontend │
│ (FE)   │       │ (API)    │       │   API    │       │Redirect  │
└───┬────┘       └────┬─────┘       └────┬─────┘       └────┬─────┘
    │                 │                  │                   │
    │ POST /checkout  │                  │                   │
    │ (provider=bkash)│                  │                   │
    │────────────────>│                  │                   │
    │                 │                  │                   │
    │                 │ Token Grant       │                   │
    │                 │ POST /token/grant │                   │
    │                 │─────────────────>│                   │
    │                 │ ◄── id_token      │                   │
    │                 │                  │                   │
    │                 │ Create Checkout   │                   │
    │                 │ POST /checkout/   │                   │
    │                 │ payment/create    │                   │
    │                 │─────────────────>│                   │
    │                 │ ◄── paymentID,    │                   │
    │                 │     bkashURL      │                   │
    │                 │                  │                   │
    │ ◄── {bkash_url, payment_id}       │                   │
    │                 │                  │                   │
    │ Redirect ─────────────────────────────────────────>│   │
    │ to bkashURL    │                  │                   │
    │                 │                  │                   │
    │                 │                  │    User completes  │
    │                 │                  │    bKash payment   │
    │                 │                  │                   │
    │                 │    Redirect to callback URL          │
    │ ◄───────────────────────────────────────────────────│
    │                 │                  │                   │
    │                 │ Execute Payment  │                   │
    │                 │ POST /execute    │                   │
    │                 │─────────────────>│                   │
    │                 │ ◄── statusCode=0000                  │
    │                 │                  │                   │
    │                 │ Update Payment:  │                   │
    │                 │ status=success   │                   │
    │                 │ Order: status=paid│                 │
    │                 │ Reduce stock     │                   │
    │                 │                  │                   │
    │ GET /verify     │                  │                   │
    │────────────────>│                  │                   │
    │                 │ Query Payment    │                   │
    │                 │ POST /status     │                   │
    │                 │─────────────────>│                   │
    │ ◄── verified: true                │                   │
```

### Order Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    ORDER LIFECYCLE                        │
│                                                          │
│   [Create Order]                                         │
│        │                                                 │
│        ▼                                                 │
│   ┌─────────┐    Checkout     ┌──────────┐               │
│   │ PENDING │ ──────────────► │ PAYMENT  │               │
│   └─────────┘                 │ INITIATED│               │
│        │                      └────┬─────┘               │
│        │                           │                     │
│        │                    ┌──────┴──────┐              │
│        │                    ▼             ▼              │
│        │              ┌──────────┐  ┌──────────┐        │
│        │              │ SUCCESS  │  │  FAILED  │        │
│        │              └────┬─────┘  └──────────┘        │
│        │                   │                             │
│        │                   ▼                             │
│        │             ┌──────────┐                        │
│        │             │   PAID   │                        │
│        │             │ - Stock  │                        │
│        │             │   reduced│                        │
│        │             └────┬─────┘                        │
│        │                  │                              │
│        │ Cancel           │                              │
│        ▼                  ▼                              │
│   ┌──────────┐    ┌──────────┐                           │
│   │ CANCELED │    │ CANCELED │ (with stock restore)      │
│   └──────────┘    └──────────┘                           │
└─────────────────────────────────────────────────────────┘
```

---

## Design Patterns & Algorithms

### Strategy Pattern (Payments)

The payment system uses the Strategy pattern to allow switching between payment providers without modifying core order logic:

```
PaymentProvider (ABC)          PaymentProcessor (Context)
├── create_payment()           ├── register_provider()
├── confirm_payment()          ├── get_provider()
├── verify_payment()           ├── create_payment()
├── process_webhook()          ├── confirm_payment()
└── get_provider_name()        └── available_providers()
        ▲
        │
├── StripePaymentProvider      Registered at app startup
└── BKashPaymentProvider       via payments/apps.py ready()
```

Adding a new provider (e.g., PayPal):
1. Create `PayPalPaymentProvider(PaymentProvider)` with 5 abstract methods
2. Register in `payments/apps.py`: `PaymentProcessor.register_provider('paypal', PayPalPaymentProvider())`
3. Add `'paypal'` to `Payment.PROVIDER_CHOICES`
4. No changes needed in Order or Checkout logic

### DFS Category Traversal

`CategoryHierarchy.dfs_traverse()` recursively walks the category tree from root nodes to leaf nodes, collecting categories with depth and product counts. Used for:

- **Category hierarchy endpoint**: `/api/v1/products/categories/hierarchy/`
- **Product recommendations**: traverses ancestor + descendant categories to find related products

### Redis Caching

| Cache Key | TTL | Description |
|-----------|-----|-------------|
| `category_tree` | 1 hour | Root categories list |
| `category_hierarchy_dfs` | 1 hour | Full DFS traversal result |
| `recommendations_{product_id}` | 30 min | Related products per product |

Cache is invalidated on category create/update/delete. Falls back to LocMemCache when Redis is unavailable.

---

## Project Structure

```
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── .env.example
│   ├── ecommerce_backend/       # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── exceptions.py
│   ├── users/                   # User management
│   │   ├── models.py            # User model + UserDAO
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── tests.py
│   ├── products/                # Product & Category management
│   │   ├── models.py            # Product, Category, CategoryHierarchy
│   │   ├── views.py
│   │   └── tests.py
│   ├── orders/                  # Order & OrderItem management
│   │   ├── models.py            # Order, OrderItem, OrderManager
│   │   ├── views.py
│   │   └── tests.py
│   ├── payments/                # Payment system
│   │   ├── models.py            # Payment model + PaymentManager
│   │   ├── strategy.py          # Strategy Pattern ABC + Context
│   │   ├── stripe_provider.py   # Stripe implementation
│   │   ├── bkash_provider.py    # bKash implementation
│   │   ├── views.py             # Webhook handlers
│   │   └── tests.py
│   └── tests/                   # API integration tests
│       ├── test_auth.py
│       ├── test_products.py
│       ├── test_orders.py
│       └── test_payments.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── context/AuthContext.jsx
        ├── services/api.js
        ├── components/
        └── pages/
```

---

## Quick Start

### With Docker (Recommended)

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env
# Edit backend/.env with your Stripe/bKash keys

# 2. Start all services
docker-compose up --build

# 3. Access
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# Swagger:   http://localhost:8000/swagger/
# Admin:     http://localhost:8000/admin/
```

### Without Docker (Development)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Default accounts seeded:
- Admin: `admin@example.com` / `admin123!`
- User: `user@example.com` / `user123!`

---

## Testing

```bash
# Backend - all tests
cd backend
python manage.py test

# Specific test modules
python manage.py test users
python manage.py test products
python manage.py test orders
python manage.py test payments
python manage.py test tests
```

### Test Coverage

| Module | Unit Tests | API Tests |
|--------|-----------|-----------|
| Users | User creation, email uniqueness, DAO operations | Register, login, profile, auth |
| Products | Model methods, SKU uniqueness, DFS traversal | CRUD, search, filter, hierarchy |
| Orders | Total calculation, stock management, lifecycle | Create, checkout, cancel |
| Payments | Model methods, strategy pattern, provider registry | Webhooks, confirm, verify |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | - |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///db.sqlite3` |
| `REDIS_URL` | Redis connection string | (empty, uses LocMemCache) |
| `STRIPE_SECRET_KEY` | Stripe secret key | - |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | - |
| `BKASH_APP_KEY` | bKash app key | - |
| `BKASH_APP_SECRET` | bKash app secret | - |
| `BKASH_USERNAME` | bKash API username | - |
| `BKASH_PASSWORD` | bKash API password | - |
| `BKASH_BASE_URL` | bKash API base URL | sandbox |
| `FRONTEND_URL` | Frontend URL for CORS/callbacks | `http://localhost:3000` |

---

## Deployment Guide

### Frontend on Vercel

1. Push frontend to GitHub
2. Connect repo to Vercel
3. Set environment variable: `VITE_API_URL=https://your-backend-url.com`
4. Deploy

### Backend with ngrok (Local Testing)

```bash
# Start backend
cd backend && python manage.py runserver 0.0.0.0:8000

# Expose via ngrok
ngrok http 8000

# Use the ngrok URL for Stripe webhook endpoint:
# https://your-ngrok-url/api/v1/payments/webhook/stripe/
```

### Docker Deployment

```bash
docker-compose up --build -d

# Check services
docker-compose ps
docker-compose logs backend
```

Services:
- `db`: PostgreSQL on port 5432
- `redis`: Redis on port 6379
- `backend`: Django/Gunicorn on port 8000
- `frontend`: Vite dev server on port 3000
