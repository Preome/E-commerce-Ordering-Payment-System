import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="nav">
      <div className="container">
        <Link to="/" className="nav-brand">E-Shop</Link>
        <div className="nav-links">
          <Link to="/products">Products</Link>
          {user ? (
            <>
              <Link to="/cart">Cart</Link>
              <Link to="/orders">Orders</Link>
              <Link to="/payments">Payments</Link>
              {user.is_staff && <Link to="/admin/products">Admin</Link>}
              <div className="nav-user">
                <div className="nav-avatar">
                  {user.email?.[0] || 'U'}
                </div>
                <span className="nav-email">{user.email}</span>
                <button className="btn btn-sm" onClick={logout}
                  style={{ background: 'rgba(255,255,255,0.15)', color: 'white', backdropFilter: 'blur(10px)' }}>
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register" className="btn btn-sm"
                style={{ background: 'white', color: '#4f46e5', marginLeft: 4 }}>
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
