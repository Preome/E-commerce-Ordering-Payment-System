# Frontend - E-Commerce Ordering & Payment System

React SPA for browsing products, managing cart, placing orders, and paying via Stripe or bKash.

## Tech Stack

- React 18.2
- Vite 5
- React Router 6
- Axios (API client)
- Stripe Elements (`@stripe/react-stripe-js`, `@stripe/stripe-js`)
- React Hot Toast (notifications)

## Setup

### Prerequisites

- Node.js 18+
- npm

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Copy or create `.env`:

```
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

### Start Dev Server

```bash
npm run dev
# Available at http://localhost:3000
```

Vite proxies `/api` requests to `http://localhost:8000` (configured in `vite.config.js`).

### Build for Production

```bash
npm run build
# Output in dist/
```

## Project Structure

```
frontend/
├── package.json
├── vite.config.js
├── index.html
├── .env
└── src/
    ├── main.jsx                 # Entry point
    ├── App.jsx                  # Router + routes
    ├── index.css                # Global styles
    ├── context/
    │   └── AuthContext.jsx      # Auth state management
    ├── services/
    │   └── api.js               # Axios interceptors + API modules
    ├── components/
    │   ├── Navbar.jsx           # Navigation bar
    │   └── AdminRoute.jsx       # Admin route guard
    └── pages/
        ├── Home.jsx             # Landing page
        ├── Login.jsx            # Login form
        ├── Register.jsx         # Registration form
        ├── Products.jsx         # Product listing + search
        ├── ProductDetail.jsx    # Product detail + add to cart
        ├── Cart.jsx             # Cart + Stripe/bKash checkout
        ├── Orders.jsx           # Order list + cancel + retry
        ├── Payments.jsx         # Payment history
        ├── AdminProducts.jsx    # Admin product management
        └── AdminProductForm.jsx # Admin create/edit product
```

## Pages

| Page | Route | Auth | Description |
|------|-------|------|-------------|
| Home | `/` | No | Landing page |
| Login | `/login` | No | Email + password login |
| Register | `/register` | No | User registration |
| Products | `/products` | No | Browse + search products |
| Product Detail | `/products/:id` | No | Product info + add to cart |
| Cart | `/cart` | Yes | Review cart + checkout |
| Orders | `/orders` | Yes | Order history + cancel/retry |
| Payments | `/payments` | Yes | Payment history |
| Admin Products | `/admin/products` | Admin | CRUD products |
| Admin Product Form | `/admin/products/new`, `/admin/products/:id/edit` | Admin | Create/edit product |

## Authentication

- Token stored in `localStorage` as `token`
- User data stored in `localStorage` as `user`
- Axios interceptor attaches `Token <key>` header to all requests
- 401 responses clear storage and redirect to `/login`
- Admin pages require `is_staff = true`

## Payment Integration

### Stripe Checkout (in Cart page)
- Stripe Elements card input
- Creates PaymentIntent via backend
- Confirms payment client-side
- Redirects to order confirmation

### bKash Checkout (in Cart page)
- Redirects to bKash payment URL
- User completes payment on bKash
- Callback redirects back to orders page

## Deployment (Vercel)

1. Push to GitHub
2. Import repository in Vercel
3. Set environment variable:
   - `VITE_API_URL` = your backend URL (e.g., `https://your-backend.ngrok.io`)
   - `VITE_STRIPE_PUBLISHABLE_KEY` = your Stripe publishable key
4. Deploy

Vercel will auto-detect Vite and configure the build command (`vite build`) and output directory (`dist`).
