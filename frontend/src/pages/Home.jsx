import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div>
      <div className="hero">
        <div className="hero-content container">
          <h1 className="animate-in">Discover Amazing Products</h1>
          <p className="animate-in animate-in-delay-1">
            Shop the latest electronics, clothing, and accessories with secure payments
            via Stripe and bKash.
          </p>
          <Link to="/products" className="btn animate-in animate-in-delay-2">
            Browse Products
          </Link>
          <div className="hero-features animate-in animate-in-delay-3">
            <div className="hero-feature">
              <div className="hero-feature-icon">&#128722;</div>
              <p>Easy Ordering</p>
            </div>
            <div className="hero-feature">
              <div className="hero-feature-icon">&#128274;</div>
              <p>Secure Payment</p>
            </div>
            <div className="hero-feature">
              <div className="hero-feature-icon">&#9889;</div>
              <p>Instant Delivery</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
