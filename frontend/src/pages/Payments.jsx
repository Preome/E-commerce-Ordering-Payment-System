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
    const map = {
      success: { class: 'badge-success', icon: '\u2713 ' },
      pending: { class: 'badge-warning', icon: '\u25F7 ' },
      failed: { class: 'badge-danger', icon: '\u2717 ' },
    };
    const s = map[status] || { class: 'badge-info', icon: '' };
    return <span className={`badge ${s.class}`}>{s.icon}{status}</span>;
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: 28 }}>Payment History</h2>
        <div className="card">
          <div className="skeleton" style={{ height: 300 }} />
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <div className="section-header">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Payment History</h2>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          {payments.length} payment{payments.length !== 1 ? 's' : ''}
        </span>
      </div>

      {payments.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">&#128179;</div>
            <h3>No payments yet</h3>
            <p>Your payment history will appear here</p>
          </div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="admin-table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Order</th>
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
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div className={`payment-icon ${p.provider}`}>
                        {p.provider === 'stripe' ? 'S' : 'bK'}
                      </div>
                      <span style={{ textTransform: 'capitalize', fontWeight: 500 }}>{p.provider}</span>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    #{(p.order_id || '').slice(0, 8)}...
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {p.transaction_id}
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    ${p.amount} <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{p.currency}</span>
                  </td>
                  <td>{statusBadge(p.status)}</td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {new Date(p.created_at).toLocaleString()}
                  </td>
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
        </div>
      )}
    </div>
  );
}
