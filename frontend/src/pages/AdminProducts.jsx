import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => { loadProducts(); }, []);

  const loadProducts = async (params = {}) => {
    try {
      setLoading(true);
      const res = await productAPI.list({ status: 'all', ...params });
      setProducts(res.data.results || res.data);
    } catch {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadProducts({ search });
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Deactivate "${name}"?`)) return;
    try {
      await productAPI.delete(id);
      toast.success('Product deactivated');
      setProducts(products.map(p => p.id === id ? { ...p, status: 'inactive' } : p));
    } catch {
      toast.error('Failed to deactivate product');
    }
  };

  return (
    <div className="page-wrapper">
      <div className="section-header">
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Product Management</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: 4 }}>
            {products.length} product{products.length !== 1 ? 's' : ''} total
          </p>
        </div>
        <Link to="/admin/products/new" className="btn btn-primary">
          + New Product
        </Link>
      </div>

      <form onSubmit={handleSearch} className="search-bar">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      {loading ? (
        <div className="card">
          <div className="skeleton" style={{ height: 400 }} />
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="admin-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{
                        width: 40, height: 40, borderRadius: 'var(--radius-sm)',
                        background: 'linear-gradient(135deg, #e0e7ff, #f0f9ff)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '1rem', flexShrink: 0, overflow: 'hidden'
                      }}>
                        {product.image_url ? (
                          <img src={product.image_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>&#128247;</span>
                        )}
                      </div>
                      <span style={{ fontWeight: 600 }}>{product.name}</span>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{product.sku}</td>
                  <td style={{ fontWeight: 600 }}>${product.price}</td>
                  <td>
                    <span style={{
                      fontWeight: 600,
                      color: product.stock > 0 ? 'var(--success)' : 'var(--danger)'
                    }}>
                      {product.stock}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${product.status === 'active' ? 'badge-success' : 'badge-danger'}`}>
                      {product.status}
                    </span>
                  </td>
                  <td>
                    <div className="actions-cell" style={{ justifyContent: 'flex-end' }}>
                      <Link to={`/products/${product.id}`} className="btn btn-sm btn-secondary">View</Link>
                      <Link to={`/admin/products/${product.id}/edit`} className="btn btn-sm btn-primary">Edit</Link>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(product.id, product.name)}>
                        Deactivate
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr><td colSpan="6" style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
                  No products found
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
