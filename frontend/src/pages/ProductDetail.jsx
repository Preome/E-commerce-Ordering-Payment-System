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
      const res = await productAPI.get(id);
      setProduct(res.data);
      const recRes = await productAPI.getRecommendations(id);
      setRecommendations(recRes.data.recommendations || []);
    } catch (err) {
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

  if (loading) return <p>Loading...</p>;
  if (!product) return <p>Product not found</p>;

  return (
    <div>
      <div className="card" style={{ display: 'flex', gap: 30, padding: 30 }}>
        <div style={{ flex: 1, background: '#eee', borderRadius: 8, minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {product.image_url ? <img src={product.image_url} alt={product.name} style={{ maxWidth: '100%', borderRadius: 8 }} /> : <span>No Image</span>}
        </div>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '1.8rem' }}>{product.name}</h1>
          <p style={{ color: '#666', margin: '5px 0' }}>SKU: {product.sku}</p>
          <p style={{ color: '#666' }}>Category: {product.category_name || 'N/A'}</p>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0f3460', margin: '15px 0' }}>${product.price}</p>
          <p style={{ color: product.stock > 0 ? '#27ae60' : '#e74c3c', marginBottom: 15 }}>
            {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
          </p>
          <p style={{ marginBottom: 20, lineHeight: 1.6 }}>{product.description}</p>

          {product.stock > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 15 }}>
              <label>Qty:</label>
              <input
                type="number" min="1" max={product.stock}
                value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                style={{ width: 70, padding: 8, border: '1px solid #ddd', borderRadius: 5 }}
              />
            </div>
          )}

          {user ? (
            <button className="btn btn-primary" onClick={addToCart} disabled={product.stock === 0}>
              Add to Cart
            </button>
          ) : (
            <button className="btn btn-primary" onClick={() => navigate('/login')}>
              Login to Purchase
            </button>
          )}
        </div>
      </div>

      {recommendations.length > 0 && (
        <div style={{ marginTop: 30 }}>
          <h3>Related Products</h3>
          <div className="grid" style={{ marginTop: 15 }}>
            {recommendations.map((rec) => (
              <div key={rec.id} className="card" style={{ cursor: 'pointer' }} onClick={() => { navigate(`/products/${rec.id}`); window.location.reload(); }}>
                <h4>{rec.name}</h4>
                <p style={{ fontWeight: 'bold', color: '#0f3460' }}>${rec.price}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
