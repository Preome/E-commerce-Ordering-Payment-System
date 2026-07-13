import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadProducts(); }, []);

  const loadProducts = async (params = {}) => {
    try {
      setLoading(true);
      const res = await productAPI.list(params);
      setProducts(res.data.results || res.data);
    } catch (err) {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadProducts({ search });
  };

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>Products</h2>
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
        <div className="grid">
          {products.map((product) => (
            <Link key={product.id} to={`/products/${product.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="card product-card">
                <div style={{ height: 200, background: '#eee', borderRadius: 5, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {product.image_url ? <img src={product.image_url} alt={product.name} /> : <span style={{ color: '#999' }}>No Image</span>}
                </div>
                <h3 style={{ marginTop: 10, fontSize: '1rem' }}>{product.name}</h3>
                <p style={{ color: '#666', fontSize: '0.85rem' }}>{product.category_name}</p>
                <p style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#0f3460' }}>${product.price}</p>
                <p style={{ fontSize: '0.85rem', color: product.stock > 0 ? '#27ae60' : '#e74c3c' }}>
                  {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
