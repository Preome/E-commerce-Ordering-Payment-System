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
        confirmParams: {
          return_url: window.location.origin + '/orders',
        },
        redirect: 'if_required',
      });

      if (error) {
        toast.error(error.message || 'Payment failed');
      } else {
        try {
          await paymentAPI.confirm({ order_id: orderId, provider: 'stripe' });
        } catch {}
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
      <button
        type="submit"
        className="btn btn-primary"
        disabled={!stripe || processing}
        style={{ marginTop: 15, padding: '12px 30px', width: '100%' }}
      >
        {processing ? 'Processing...' : 'Pay Now'}
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
        items: cart.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
      });

      const order = res.data.order;
      setOrderId(order.id);
      toast.success('Order placed! Initiating payment...');

      const checkoutRes = await orderAPI.checkout(order.id, { provider, currency: provider === 'bkash' ? 'bdt' : 'usd' });

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
      <div style={{ maxWidth: 500, margin: '0 auto' }}>
        <h2 style={{ marginBottom: 20 }}>Complete Payment</h2>
        <div className="card">
          <p style={{ marginBottom: 15, color: '#666' }}>
            Order Total: <strong>${total.toFixed(2)}</strong>
          </p>
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
    <div>
      <h2 style={{ marginBottom: 20 }}>Shopping Cart</h2>
      {cart.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p>Your cart is empty</p>
          <button className="btn btn-primary" onClick={() => navigate('/products')} style={{ marginTop: 15 }}>
            Browse Products
          </button>
        </div>
      ) : (
        <>
          {cart.map((item, index) => (
            <div key={index} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4>{item.name}</h4>
                <p style={{ color: '#666' }}>${item.price} each</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <input
                  type="number" min="1" value={item.quantity}
                  onChange={(e) => updateQuantity(index, parseInt(e.target.value) || 1)}
                  style={{ width: 60, padding: 5, textAlign: 'center', border: '1px solid #ddd', borderRadius: 5 }}
                />
                <span style={{ fontWeight: 'bold', minWidth: 80 }}>${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
                <button onClick={() => removeItem(index)} style={{ background: 'none', border: 'none', color: '#e74c3c', cursor: 'pointer', fontSize: '1.2rem' }}>
                  &times;
                </button>
              </div>
            </div>
          ))}
          <div className="card" style={{ textAlign: 'right', fontSize: '1.3rem' }}>
            <strong>Total: ${total.toFixed(2)}</strong>
          </div>

          <div className="card" style={{ marginTop: 15 }}>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: 10 }}>Payment Method</label>
            <div style={{ display: 'flex', gap: 15 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input type="radio" name="provider" value="stripe" checked={provider === 'stripe'} onChange={() => setProvider('stripe')} />
                Stripe (Card)
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input type="radio" name="provider" value="bkash" checked={provider === 'bkash'} onChange={() => setProvider('bkash')} />
                bKash
              </label>
            </div>
          </div>

          <button className="btn btn-primary" onClick={placeOrder} disabled={loading} style={{ marginTop: 15, padding: '12px 30px' }}>
            {loading ? 'Processing...' : 'Place Order & Pay'}
          </button>
        </>
      )}
    </div>
  );
}
