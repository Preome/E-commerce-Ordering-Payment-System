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
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(form);
      toast.success('Registration successful!');
      navigate('/products');
    } catch (err) {
      const data = err.response?.data;
      if (data?.error) {
        const msgs = Object.values(data.error).flat().join(' ');
        setError(msgs);
      } else {
        setError('Registration failed');
      }
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '40px auto' }}>
      <div className="card">
        <h2>Register</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" value={form.email} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Username</label>
            <input type="text" name="username" value={form.username} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>First Name</label>
            <input type="text" name="first_name" value={form.first_name} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Last Name</label>
            <input type="text" name="last_name" value={form.last_name} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" name="password" value={form.password} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Confirm Password</label>
            <input type="password" name="password_confirm" value={form.password_confirm} onChange={handleChange} required />
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Register</button>
        </form>
        <p style={{ marginTop: 15, textAlign: 'center' }}>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
