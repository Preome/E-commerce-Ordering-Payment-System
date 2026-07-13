import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="nav">
      <div className="container">
        <Link to="/" style={{ fontSize: '1.3rem', fontWeight: 'bold' }}>E-Shop</Link>
        <div>
          <Link to="/products">Products</Link>
          {user ? (
            <>
              {user.is_staff && <Link to="/admin/products">Admin</Link>}
              <Link to="/cart">Cart</Link>
              <Link to="/orders">Orders</Link>
              <Link to="/payments">Payments</Link>
              <span style={{ marginLeft: 15 }}>{user.email}</span>
              <button className="btn btn-primary" onClick={logout} style={{ marginLeft: 10 }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
