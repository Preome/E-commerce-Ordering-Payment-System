# Backend - E-Commerce Ordering & Payment System

Django REST Framework backend for managing users, products, orders, and payments with Stripe and bKash integration.

## Tech Stack

- **Framework**: Django 4.2.30 + DRF 3.15.2
- **Database**: PostgreSQL 15 (Docker) / SQLite3 (local dev)
- **Cache**: Redis 7 (Docker) / LocMemCache (local dev)
- **Auth**: Token-based (DRF TokenAuthentication)
- **API Docs**: Swagger/ReDoc via drf-yasg
- **Payments**: Stripe SDK 15.3.0 + bKash Tokenized Checkout v1.2.0-beta

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL (or use SQLite for dev)
- Redis (optional, falls back to in-memory cache)

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys
```

### Database Setup

```bash
# Run migrations
python manage.py migrate

# Seed admin user + sample products
python manage.py seed_data

# Create superuser (if needed)
python manage.py createsuperuser
```

### Start Server

```bash
python manage.py runserver
# Available at http://localhost:8000
# Swagger at http://localhost:8000/swagger/
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `DJANGO_DEBUG` | No | Debug mode (default: `True`) |
| `DATABASE_URL` | No | Postgres URL (default: SQLite) |
| `REDIS_URL` | No | Redis URL (default: LocMemCache) |
| `STRIPE_SECRET_KEY` | For Stripe | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | For Stripe | Stripe publishable key |
| `STRIPE_WEBHOOK_SECRET` | For Stripe | Webhook signing secret |
| `BKASH_APP_KEY` | For bKash | bKash app key |
| `BKASH_APP_SECRET` | For bKash | bKash app secret |
| `BKASH_USERNAME` | For bKash | bKash API username |
| `BKASH_PASSWORD` | For bKash | bKash API password |
| `BKASH_BASE_URL` | For bKash | bKash API base URL |
| `BKASH_CHECKOUT_URL` | For bKash | Checkout endpoint |
| `BKASH_EXECUTE_URL` | For bKash | Execute endpoint |
| `BKASH_QUERY_URL` | For bKash | Query endpoint |
| `FRONTEND_URL` | No | Frontend URL for CORS (default: `http://localhost:3000`) |
| `BACKEND_URL` | No | Backend URL for callbacks |

## Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── db.sqlite3
├── logs/
├── ecommerce_backend/         # Project config
│   ├── settings.py            # Main settings
│   ├── test_settings.py       # Test settings (SQLite in-memory)
│   ├── urls.py                # Root URL routing
│   ├── exceptions.py          # Custom exception handler
│   └── wsgi.py
├── users/                     # User management app
│   ├── models.py              # User (AbstractUser), UserDAO
│   ├── serializers.py         # Register, Login, Profile serializers
│   ├── views.py               # Register, Login, Profile views
│   ├── urls.py
│   ├── tests.py               # Unit tests
│   └── management/commands/
│       └── seed_data.py       # Seeder command
├── products/                  # Product & Category app
│   ├── models.py              # Product, Category, CategoryHierarchy
│   ├── serializers.py
│   ├── views.py               # CRUD + hierarchy + recommendations
│   ├── urls.py
│   └── tests.py
├── orders/                    # Order management app
│   ├── models.py              # Order, OrderItem, OrderManager
│   ├── serializers.py
│   ├── views.py               # CRUD + checkout + cancel
│   ├── urls.py
│   └── tests.py
├── payments/                  # Payment system app
│   ├── models.py              # Payment model, PaymentManager
│   ├── strategy.py            # Strategy Pattern (ABC + Context)
│   ├── stripe_provider.py     # Stripe integration
│   ├── bkash_provider.py      # bKash integration
│   ├── views.py               # Webhook handlers, confirm, verify
│   ├── urls.py
│   └── tests.py
└── tests/                     # API integration tests
    ├── test_auth.py
    ├── test_products.py
    ├── test_orders.py
    └── test_payments.py
```

## Running Tests

```bash
# All tests
python manage.py test

# By app
python manage.py test users
python manage.py test products
python manage.py test orders
python manage.py test payments

# API integration tests
python manage.py test tests

# Verbose output
python manage.py test --verbosity=2
```

### Test Settings

Tests use `test_settings.py` which configures:
- SQLite in-memory database
- LocMemCache
- Disabled throttling
- Separate test environment

## Seeder

```bash
# Seed default data
python manage.py seed_data

# Clear and re-seed
python manage.py seed_data --clear
```

### Seeded Data

| Entity | Data |
|--------|------|
| Admin | `admin@example.com` / `admin123!` (is_staff, is_superuser) |
| User | `user@example.com` / `user123!` |
| Categories | Electronics, Clothing, Home & Kitchen, Books, Sports + 6 subcategories |
| Products | 10 sample products (iPhone, Samsung, MacBook, Dell, Sony, T-Shirt, Dress, Cookware, Python Book, Yoga Mat) |

## Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

Docker services:
- `db`: PostgreSQL 15 (port 5432)
- `redis`: Redis 7 (port 6379)
- `backend`: Django + Gunicorn (port 8000)

The backend container automatically runs migrations and seeds data on startup.

## API Endpoints

### Users
- `POST /api/v1/users/register/` - Register
- `POST /api/v1/users/login/` - Login
- `GET/PATCH /api/v1/users/profile/` - Profile
- `GET /api/v1/users/my-orders/` - User orders
- `GET /api/v1/users/my-payments/` - User payments

### Products
- `GET/POST /api/v1/products/` - List/Create
- `GET/PUT/PATCH/DELETE /api/v1/products/{id}/` - Detail/Update/Delete
- `GET/POST /api/v1/products/categories/` - Categories
- `GET /api/v1/products/categories/hierarchy/` - DFS tree
- `GET /api/v1/products/{id}/recommendations/` - Related products

### Orders
- `GET/POST /api/v1/orders/` - List/Create
- `GET /api/v1/orders/{id}/` - Detail
- `POST /api/v1/orders/{id}/cancel/` - Cancel
- `POST /api/v1/orders/{id}/checkout/` - Initiate payment

### Payments
- `GET /api/v1/payments/` - List
- `GET /api/v1/payments/{id}/` - Detail
- `POST /api/v1/payments/confirm/` - Confirm
- `GET /api/v1/payments/{id}/verify/` - Verify
- `POST /api/v1/payments/webhook/stripe/` - Stripe webhook
- `POST /api/v1/payments/webhook/bkash/` - bKash webhook
- `POST /api/v1/payments/bkash/callback/` - bKash callback

## Key Design Decisions

### OOP Classes
- **User**: Extends `AbstractUser` with UUID PK, email-based auth, DAO pattern
- **Product**: Stock management with `reduce_stock()`/`increase_stock()`, soft-delete via status
- **Order**: Calculates totals, manages lifecycle (pending -> paid -> canceled)
- **Payment**: Provider-agnostic with raw response storage

### Strategy Pattern
`payments/strategy.py` defines `PaymentProvider` (ABC) and `PaymentProcessor` (Context). Providers are registered at app startup in `payments/apps.py`.

### DFS + Caching
`CategoryHierarchy.dfs_traverse()` walks the category tree recursively. Results cached in Redis (1 hour TTL). Cache invalidated on category mutations.

### Data Validation
- DRF serializers with field-level validation
- Django model validators (MinValueValidator, EmailValidator)
- Unique constraints on email, SKU, transaction_id
- Password confirmation on registration
