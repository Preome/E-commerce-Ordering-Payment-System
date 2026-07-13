import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/products');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card animate-in">
        <div className="card">
          <div style={{ textAlign: 'center', marginBottom: 8 }}>
            <div style={{
              width: 56, height: 56, borderRadius: 'var(--radius)',
              background: 'linear-gradient(135deg, var(--primary), var(--primary-dark))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 16px', fontSize: '1.5rem', color: 'white'
            }}>&#128274;</div>
          </div>
          <h2>Welcome back</h2>
          <p className="auth-subtitle">Sign in to your account</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
            {error && (
              <div style={{
                padding: '12px 16px', borderRadius: 'var(--radius-sm)',
                background: 'var(--danger-bg)', color: '#991b1b',
                fontSize: '0.85rem', marginBottom: 20, fontWeight: 500
              }}>
                {error}
              </div>
            )}
            <button type="submit" className="btn btn-primary" disabled={loading}
              style={{ width: '100%', padding: '13px' }}>
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
                  <span className="spinner" /> Signing in...
                </span>
              ) : 'Sign In'}
            </button>
          </form>
          <p className="auth-footer">
            Don't have an account? <Link to="/register">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
