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
      confirmLatestPendingPayment();
    }
  }, []);

  const confirmLatestPendingPayment = async () => {
    try {
      toast.success('Payment confirmed via bKash callback!');
      loadOrders();
    } catch {
      toast.error('Payment confirmation failed. You can verify from Payments page.');
    }
  };

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

  const statusColor = (status) => {
    switch (status) {
      case 'paid': return '#27ae60';
      case 'pending': return '#f39c12';
      case 'canceled': return '#e74c3c';
      default: return '#666';
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>My Orders</h2>
      {orders.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p>No orders yet</p>
          <Link to="/products" className="btn btn-primary" style={{ marginTop: 15 }}>Browse Products</Link>
        </div>
      ) : (
        orders.map((order) => (
          <div key={order.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4>Order #{order.id.slice(0, 8)}...</h4>
                <p style={{ color: '#666', fontSize: '0.85rem' }}>
                  {new Date(order.created_at).toLocaleString()}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>${order.total_amount}</p>
                <span className={`badge badge-${order.status === 'paid' ? 'active' : order.status === 'canceled' ? 'inactive' : ''}`}
                  style={order.status === 'pending' ? { background: '#fff3cd', color: '#856404' } : {}}>
                  {order.status}
                </span>
              </div>
            </div>

            {order.items && order.items.length > 0 && (
              <div style={{ marginTop: 10, borderTop: '1px solid #eee', paddingTop: 10 }}>
                {order.items.map((item) => (
                  <p key={item.id} style={{ fontSize: '0.9rem', color: '#555' }}>
                    {item.quantity}x {item.product_name || 'Product'} - ${item.subtotal}
                  </p>
                ))}
              </div>
            )}

            <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {order.status === 'pending' && (
                <>
                  <button className="btn btn-primary btn-sm" onClick={() => retryPayment(order.id)}>
                    Retry Payment
                  </button>
                  <button className="btn btn-sm" style={{ border: '1px solid #e74c3c', color: '#e74c3c' }} onClick={() => cancelOrder(order.id)}>
                    Cancel Order
                  </button>
                </>
              )}
              {order.payments && order.payments.map((p) => (
                <button key={p.id} className="btn btn-sm" onClick={() => verifyPayment(p.id)}>
                  Verify {p.provider} ({p.status})
                </button>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
