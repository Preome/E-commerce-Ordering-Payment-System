import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function ProductDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProduct();
  }, [id]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const res = await productAPI.get(id);
      setProduct(res.data);
      const recRes = await productAPI.getRecommendations(id);
      setRecommendations(recRes.data.recommendations || []);
    } catch {
      toast.error('Product not found');
    } finally {
      setLoading(false);
    }
  };

  const addToCart = () => {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const existing = cart.findIndex(item => item.product_id === id);
    if (existing >= 0) {
      cart[existing].quantity += quantity;
    } else {
      cart.push({
        product_id: id,
        name: product.name,
        price: product.price,
        quantity,
      });
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    toast.success('Added to cart!');
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="card" style={{ display: 'flex', gap: 40, padding: 30 }}>
          <div className="skeleton" style={{ flex: 1, minHeight: 350, borderRadius: 12 }} />
          <div style={{ flex: 1 }}>
            <div className="skeleton" style={{ height: 32, width: '60%', marginBottom: 12 }} />
            <div className="skeleton" style={{ height: 16, width: '30%', marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 40, width: '25%', marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 16, width: '100%', marginBottom: 8 }} />
            <div className="skeleton" style={{ height: 16, width: '80%' }} />
          </div>
        </div>
      </div>
    );
  }

  if (!product) return <div className="page-wrapper"><p>Product not found</p></div>;

  return (
    <div className="page-wrapper">
      <div className="card animate-in" style={{ display: 'flex', gap: 40, padding: 30 }}>
        <div style={{
          flex: 1, background: 'linear-gradient(135deg, #e0e7ff, #f0f9ff)',
          borderRadius: 12, minHeight: 350,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          overflow: 'hidden'
        }}>
          {product.image_url ? (
            <img src={product.image_url} alt={product.name}
              style={{ maxWidth: '100%', maxHeight: 400, borderRadius: 8, objectFit: 'contain' }} />
          ) : (
            <span style={{ fontSize: '3rem', color: 'var(--text-muted)' }}>&#128247;</span>
          )}
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {product.category_name && (
            <span className="badge badge-primary" style={{ alignSelf: 'flex-start', marginBottom: 12 }}>
              {product.category_name}
            </span>
          )}
          <h1 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.5px', marginBottom: 4 }}>
            {product.name}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>
            SKU: {product.sku}
          </p>
          <p style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: 8 }}>
            ${product.price}
          </p>
          <p style={{
            color: product.stock > 0 ? 'var(--success)' : 'var(--danger)',
            fontWeight: 600, marginBottom: 20, fontSize: '0.9rem',
            display: 'flex', alignItems: 'center', gap: 6
          }}>
            <span style={{
              width: 8, height: 8, borderRadius: '50%',
              background: product.stock > 0 ? 'var(--success)' : 'var(--danger)',
              display: 'inline-block'
            }} />
            {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
          </p>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 28 }}>
            {product.description}
          </p>

          {product.stock > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
              <label style={{ fontWeight: 600, fontSize: '0.9rem' }}>Quantity</label>
              <div style={{
                display: 'flex', alignItems: 'center', border: '2px solid var(--border)',
                borderRadius: 'var(--radius-sm)', overflow: 'hidden'
              }}>
                <button onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  style={{ padding: '8px 14px', border: 'none', background: 'var(--bg)', cursor: 'pointer', fontSize: '1rem', fontWeight: 600 }}>
                  -
                </button>
                <span style={{ padding: '8px 18px', fontWeight: 600 }}>{quantity}</span>
                <button onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                  style={{ padding: '8px 14px', border: 'none', background: 'var(--bg)', cursor: 'pointer', fontSize: '1rem', fontWeight: 600 }}>
                  +
                </button>
              </div>
            </div>
          )}

          {user ? (
            <button className="btn btn-primary btn-lg" onClick={addToCart} disabled={product.stock === 0}
              style={{ alignSelf: 'flex-start' }}>
              {product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
            </button>
          ) : (
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/login')}
              style={{ alignSelf: 'flex-start' }}>
              Login to Purchase
            </button>
          )}
        </div>
      </div>

      {recommendations.length > 0 && (
        <div style={{ marginTop: 40 }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 20 }}>Related Products</h3>
          <div className="grid">
            {recommendations.map((rec) => (
              <div key={rec.id} className="card card-interactive" style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/products/${rec.id}`)}>
                <h4 style={{ fontSize: '1rem', marginBottom: 6 }}>{rec.name}</h4>
                <p style={{ fontWeight: 700, color: 'var(--primary)', fontSize: '1.1rem' }}>${rec.price}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
