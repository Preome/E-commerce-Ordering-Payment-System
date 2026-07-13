import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Register() {
  const [form, setForm] = useState({
    email: '', username: '', first_name: '', last_name: '',
    password: '', password_confirm: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form);
      toast.success('Welcome to E-Shop!');
      navigate('/products');
    } catch (err) {
      const data = err.response?.data;
      if (data?.error) {
        setError(Object.values(data.error).flat().join(' '));
      } else {
        setError('Registration failed');
      }
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
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 16px', fontSize: '1.5rem', color: 'white'
            }}>&#9997;&#65039;</div>
          </div>
          <h2>Create Account</h2>
          <p className="auth-subtitle">Join E-Shop today</p>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div className="form-group">
                <label>First Name</label>
                <input type="text" name="first_name" value={form.first_name}
                  onChange={handleChange} placeholder="John" />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input type="text" name="last_name" value={form.last_name}
                  onChange={handleChange} placeholder="Doe" />
              </div>
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" name="email" value={form.email}
                onChange={handleChange} placeholder="you@example.com" required />
            </div>
            <div className="form-group">
              <label>Username</label>
              <input type="text" name="username" value={form.username}
                onChange={handleChange} placeholder="johndoe" required />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" name="password" value={form.password}
                onChange={handleChange} placeholder="Min 8 characters" required />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" name="password_confirm" value={form.password_confirm}
                onChange={handleChange} placeholder="Repeat password" required />
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
                  <span className="spinner" /> Creating account...
                </span>
              ) : 'Create Account'}
            </button>
          </form>
          <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
