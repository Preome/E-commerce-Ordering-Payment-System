import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { orderAPI, paymentAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_placeholder');

function StripeForm({ clientSecret, paymentId, orderId, onSuccess }) {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setProcessing(true);
    try {
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: { return_url: window.location.origin + '/orders' },
        redirect: 'if_required',
      });

      if (error) {
        toast.error(error.message || 'Payment failed');
      } else {
        try { await paymentAPI.confirm({ order_id: orderId, provider: 'stripe' }); } catch {}
        toast.success('Payment successful!');
        onSuccess();
      }
    } catch {
      toast.error('Payment confirmation failed');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button type="submit" className="btn btn-primary btn-lg" disabled={!stripe || processing}
        style={{ marginTop: 20, width: '100%' }}>
        {processing ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="spinner" /> Processing...
          </span>
        ) : 'Pay Now'}
      </button>
    </form>
  );
}

export default function Cart() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('stripe');
  const [paymentData, setPaymentData] = useState(null);
  const [orderId, setOrderId] = useState(null);

  useEffect(() => {
    setCart(JSON.parse(localStorage.getItem('cart') || '[]'));
  }, []);

  const updateQuantity = (index, qty) => {
    const updated = [...cart];
    updated[index].quantity = Math.max(1, qty);
    setCart(updated);
    localStorage.setItem('cart', JSON.stringify(updated));
  };

  const removeItem = (index) => {
    const updated = cart.filter((_, i) => i !== index);
    setCart(updated);
    localStorage.setItem('cart', JSON.stringify(updated));
  };

  const total = cart.reduce((sum, item) => sum + parseFloat(item.price) * item.quantity, 0);

  const placeOrder = async () => {
    if (!user) { navigate('/login'); return; }
    if (cart.length === 0) { toast.error('Cart is empty'); return; }

    setLoading(true);
    try {
      const res = await orderAPI.create({
        items: cart.map(item => ({ product_id: item.product_id, quantity: item.quantity })),
      });
      const order = res.data.order;
      setOrderId(order.id);
      toast.success('Order placed! Initiating payment...');

      const checkoutRes = await orderAPI.checkout(order.id, {
        provider, currency: provider === 'bkash' ? 'bdt' : 'usd'
      });

      if (checkoutRes.data.success) {
        const pd = checkoutRes.data.payment_data;
        if (provider === 'stripe') {
          setPaymentData(pd);
        } else if (provider === 'bkash' && pd.bkash_url) {
          localStorage.removeItem('cart');
          window.location.href = pd.bkash_url;
          return;
        }
      } else {
        toast.error(checkoutRes.data.error || 'Payment initiation failed');
      }
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.items || 'Order failed';
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = () => {
    localStorage.removeItem('cart');
    setCart([]);
    setPaymentData(null);
    navigate('/orders');
  };

  if (paymentData && paymentData.client_secret) {
    return (
      <div className="page-wrapper" style={{ maxWidth: 560, margin: '0 auto' }}>
        <div className="card animate-in" style={{ padding: 40 }}>
          <div style={{ textAlign: 'center', marginBottom: 28 }}>
            <div style={{
              width: 60, height: 60, borderRadius: '50%', background: 'var(--primary-50)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 16px', fontSize: '1.5rem'
            }}>&#128179;</div>
            <h2 style={{ fontSize: '1.4rem', marginBottom: 4 }}>Complete Payment</h2>
            <p style={{ color: 'var(--text-secondary)' }}>
              Order Total: <strong style={{ color: 'var(--text)' }}>${total.toFixed(2)}</strong>
            </p>
          </div>
          <Elements stripe={stripePromise} options={{ clientSecret: paymentData.client_secret }}>
            <StripeForm
              clientSecret={paymentData.client_secret}
              paymentId={paymentData.payment_id}
              orderId={orderId}
              onSuccess={handlePaymentSuccess}
            />
          </Elements>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: 28 }}>Shopping Cart</h2>

      {cart.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">&#128722;</div>
            <h3>Your cart is empty</h3>
            <p>Add some products to get started</p>
            <button className="btn btn-primary" onClick={() => navigate('/products')}>
              Browse Products
            </button>
          </div>
        </div>
      ) : (
        <div className="cart-layout">
          <div>
            {cart.map((item, index) => (
              <div key={index} className="card animate-in"
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', animationDelay: `${index * 0.05}s`, opacity: 0 }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 2 }}>{item.name}</h4>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>${item.price} each</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', border: '2px solid var(--border)',
                    borderRadius: 'var(--radius-sm)', overflow: 'hidden'
                  }}>
                    <button onClick={() => updateQuantity(index, item.quantity - 1)}
                      style={{ padding: '6px 10px', border: 'none', background: 'var(--bg)', cursor: 'pointer', fontWeight: 600 }}>
                      -
                    </button>
                    <span style={{ padding: '6px 12px', fontWeight: 600, fontSize: '0.9rem' }}>{item.quantity}</span>
                    <button onClick={() => updateQuantity(index, item.quantity + 1)}
                      style={{ padding: '6px 10px', border: 'none', background: 'var(--bg)', cursor: 'pointer', fontWeight: 600 }}>
                      +
                    </button>
                  </div>
                  <span style={{ fontWeight: 700, minWidth: 80, textAlign: 'right', color: 'var(--primary)' }}>
                    ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                  </span>
                  <button onClick={() => removeItem(index)}
                    style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '1.2rem', padding: 4 }}>
                    &#10005;
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div>
            <div className="card cart-summary animate-in" style={{ padding: 28 }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 20 }}>Order Summary</h3>
              <div className="summary-row">
                <span style={{ color: 'var(--text-secondary)' }}>Subtotal ({cart.reduce((s, i) => s + i.quantity, 0)} items)</span>
                <span style={{ fontWeight: 600 }}>${total.toFixed(2)}</span>
              </div>
              <div className="summary-row">
                <span style={{ color: 'var(--text-secondary)' }}>Shipping</span>
                <span style={{ fontWeight: 600, color: 'var(--success)' }}>Free</span>
              </div>
              <div className="summary-row total">
                <span>Total</span>
                <span style={{ color: 'var(--primary)' }}>${total.toFixed(2)}</span>
              </div>

              <div style={{ marginTop: 24 }}>
                <label style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: 12, display: 'block' }}>Payment Method</label>
                <div className="payment-methods">
                  <div className={`payment-method ${provider === 'stripe' ? 'active' : ''}`}
                    onClick={() => setProvider('stripe')}>
                    <div className="payment-method-icon" style={{ background: '#eef2ff', color: '#635bff' }}>S</div>
                    <div className="payment-method-info">
                      <h4>Stripe</h4>
                      <p>Credit/Debit Card</p>
                    </div>
                  </div>
                  <div className={`payment-method ${provider === 'bkash' ? 'active' : ''}`}
                    onClick={() => setProvider('bkash')}>
                    <div className="payment-method-icon" style={{ background: '#fce7f3', color: '#be185d' }}>bK</div>
                    <div className="payment-method-info">
                      <h4>bKash</h4>
                      <p>Mobile Payment</p>
                    </div>
                  </div>
                </div>
              </div>

              <button className="btn btn-primary btn-lg" onClick={placeOrder} disabled={loading}
                style={{ marginTop: 24, width: '100%' }}>
                {loading ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
                    <span className="spinner" /> Processing...
                  </span>
                ) : 'Place Order & Pay'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
