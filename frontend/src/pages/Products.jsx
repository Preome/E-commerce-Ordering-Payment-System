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

  return (
    <div className="page-wrapper">
      <div className="section-header">
        <h2>Products</h2>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          {products.length} item{products.length !== 1 ? 's' : ''}
        </span>
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
        <div className="grid">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="card" style={{ padding: 0 }}>
              <div className="skeleton" style={{ height: 220 }} />
              <div style={{ padding: 18 }}>
                <div className="skeleton" style={{ height: 16, width: '70%', marginBottom: 10 }} />
                <div className="skeleton" style={{ height: 12, width: '40%', marginBottom: 12 }} />
                <div className="skeleton" style={{ height: 20, width: '30%' }} />
              </div>
            </div>
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">&#128269;</div>
          <h3>No products found</h3>
          <p>Try adjusting your search terms</p>
        </div>
      ) : (
        <div className="grid">
          {products.map((product, idx) => (
            <Link
              key={product.id}
              to={`/products/${product.id}`}
              className="animate-in"
              style={{ textDecoration: 'none', color: 'inherit', animationDelay: `${idx * 0.05}s`, opacity: 0 }}
            >
              <div className="card product-card card-interactive">
                <div className="product-image-wrap">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.name} className="product-image" />
                  ) : (
                    <div style={{
                      height: 220,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: 'linear-gradient(135deg, #e0e7ff, #f0f9ff)',
                      color: 'var(--text-muted)', fontSize: '2.5rem'
                    }}>
                      &#128247;
                    </div>
                  )}
                  <div className="product-image-overlay">
                    <span>View Details</span>
                  </div>
                </div>
                <div className="product-info">
                  <h3>{product.name}</h3>
                  <p className="product-category">{product.category_name || 'Uncategorized'}</p>
                  <p className="product-price">${product.price}</p>
                  <p className="product-stock" style={{ color: product.stock > 0 ? 'var(--success)' : 'var(--danger)' }}>
                    {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
