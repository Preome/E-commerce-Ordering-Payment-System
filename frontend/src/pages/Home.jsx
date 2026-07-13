import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div style={{ textAlign: 'center', padding: '60px 0' }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: 15 }}>Welcome to E-Shop</h1>
      <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: 30 }}>
        Your one-stop destination for electronics, clothing, and more.
      </p>
      <Link to="/products" className="btn btn-primary" style={{ fontSize: '1.1rem', padding: '15px 40px' }}>
        Browse Products
      </Link>
    </div>
  );
}
