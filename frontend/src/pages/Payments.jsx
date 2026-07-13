import { useState, useEffect } from 'react';
import { paymentAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function Payments() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadPayments(); }, []);

  const loadPayments = async () => {
    try {
      const res = await paymentAPI.list();
      setPayments(res.data.results || res.data);
    } catch {
      toast.error('Failed to load payments');
    } finally {
      setLoading(false);
    }
  };

  const verifyPayment = async (id) => {
    try {
      const res = await paymentAPI.verify(id);
      const status = res.data.verification?.status || 'unknown';
      toast.success(`Verified: ${status}`);
      loadPayments();
    } catch {
      toast.error('Verification failed');
    }
  };

  const statusBadge = (status) => {
    const colors = { success: '#27ae60', pending: '#f39c12', failed: '#e74c3c' };
    return (
      <span className="badge" style={{ background: colors[status] || '#666', color: 'white' }}>
        {status}
      </span>
    );
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>Payment History</h2>
      {payments.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p>No payments yet</p>
        </div>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Provider</th>
              <th>Transaction ID</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id}>
                <td>#{(p.order_id || '').slice(0, 8)}...</td>
                <td style={{ textTransform: 'capitalize' }}>{p.provider}</td>
                <td style={{ fontSize: '0.8rem', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.transaction_id}</td>
                <td>${p.amount} {p.currency}</td>
                <td>{statusBadge(p.status)}</td>
                <td>{new Date(p.created_at).toLocaleString()}</td>
                <td>
                  {p.status === 'pending' && (
                    <button className="btn btn-sm btn-primary" onClick={() => verifyPayment(p.id)}>
                      Verify
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
