import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { orderAPI, paymentAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    loadOrders();
    if (searchParams.get('payment') === 'done') {
      toast.success('Payment confirmed via bKash callback!');
    }
  }, []);

  const loadOrders = async () => {
    try {
      const res = await orderAPI.list();
      setOrders(res.data.results || res.data);
    } catch {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const cancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    try {
      await orderAPI.cancel(orderId);
      toast.success('Order canceled');
      loadOrders();
    } catch {
      toast.error('Failed to cancel order');
    }
  };

  const retryPayment = async (orderId) => {
    try {
      const res = await orderAPI.checkout(orderId, { provider: 'stripe', currency: 'usd' });
      if (res.data.success) {
        toast.success('Payment initiated! Redirecting...');
        loadOrders();
      }
    } catch {
      toast.error('Retry payment failed');
    }
  };

  const verifyPayment = async (paymentId) => {
    try {
      const res = await paymentAPI.verify(paymentId);
      toast.success(`Payment status: ${res.data.verification?.status || 'verified'}`);
      loadOrders();
    } catch {
      toast.error('Verification failed');
    }
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: 28 }}>My Orders</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[1,2,3].map(i => (
            <div key={i} className="card">
              <div className="skeleton" style={{ height: 20, width: '25%', marginBottom: 12 }} />
              <div className="skeleton" style={{ height: 14, width: '60%', marginBottom: 8 }} />
              <div className="skeleton" style={{ height: 14, width: '40%' }} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <div className="section-header">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700 }}>My Orders</h2>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          {orders.length} order{orders.length !== 1 ? 's' : ''}
        </span>
      </div>

      {orders.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">&#128230;</div>
            <h3>No orders yet</h3>
            <p>Start shopping to see your orders here</p>
            <Link to="/products" className="btn btn-primary">Browse Products</Link>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {orders.map((order, idx) => (
            <div key={order.id} className={`card order-card status-${order.status} animate-in`}
              style={{ animationDelay: `${idx * 0.05}s`, opacity: 0 }}>
              <div className="order-header">
                <div>
                  <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 2 }}>
                    Order #{order.id.slice(0, 8)}...
                  </h4>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {new Date(order.created_at).toLocaleString()}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text)' }}>
                    ${order.total_amount}
                  </p>
                  <span className={`badge ${
                    order.status === 'paid' ? 'badge-success' :
                    order.status === 'pending' ? 'badge-warning' :
                    order.status === 'canceled' ? 'badge-danger' : 'badge-info'
                  }`}>
                    {order.status === 'paid' && '✓ '}
                    {order.status === 'pending' && '◷ '}
                    {order.status === 'canceled' && '✕ '}
                    {order.status}
                  </span>
                </div>
              </div>

              {order.items && order.items.length > 0 && (
                <div className="order-items">
                  {order.items.map((item) => (
                    <div key={item.id} className="order-item">
                      <div className="order-item-name">
                        <span className="order-item-qty">{item.quantity}x</span>
                        {item.product_name || 'Product'}
                      </div>
                      <span style={{ fontWeight: 600 }}>${item.subtotal}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="order-actions">
                {order.status === 'pending' && (
                  <>
                    <button className="btn btn-primary btn-sm" onClick={() => retryPayment(order.id)}>
                      Retry Payment
                    </button>
                    <button className="btn btn-sm btn-secondary"
                      style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }}
                      onClick={() => cancelOrder(order.id)}>
                      Cancel
                    </button>
                  </>
                )}
                {order.payments && order.payments.map((p) => (
                  <button key={p.id} className="btn btn-sm btn-secondary"
                    onClick={() => verifyPayment(p.id)}>
                    Verify {p.provider}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
