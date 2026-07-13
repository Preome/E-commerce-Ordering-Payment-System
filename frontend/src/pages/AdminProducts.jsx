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
    if (!window.confirm(`Delete "${name}"? This will deactivate it.`)) return;
    try {
      await productAPI.delete(id);
      toast.success('Product deactivated');
      setProducts(products.map(p => p.id === id ? { ...p, status: 'inactive' } : p));
    } catch {
      toast.error('Failed to delete product');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2>Admin - Products</h2>
        <Link to="/admin/products/new" className="btn btn-primary">+ Add Product</Link>
      </div>

      <form onSubmit={handleSearch} style={{ marginBottom: 20, display: 'flex', gap: 10 }}>
        <input
          type="text" placeholder="Search products..."
          value={search} onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, padding: '10px', border: '1px solid #ddd', borderRadius: 5 }}
        />
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.sku}</td>
                <td>${product.price}</td>
                <td>{product.stock}</td>
                <td>
                  <span className={`badge badge-${product.status === 'active' ? 'active' : 'inactive'}`}>
                    {product.status}
                  </span>
                </td>
                <td className="actions-cell">
                  <Link to={`/products/${product.id}`} className="btn btn-sm">View</Link>
                  <Link to={`/admin/products/${product.id}/edit`} className="btn btn-sm btn-primary">Edit</Link>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(product.id, product.name)}>Delete</button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr><td colSpan="6" style={{ textAlign: 'center' }}>No products found</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
