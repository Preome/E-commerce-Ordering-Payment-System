import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { productAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function AdminProductForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: '', sku: '', description: '', price: '',
    stock: '', status: 'active', category: '', image_url: '',
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    productAPI.getCategories().then(res => {
      setCategories(res.data.categories || res.data.results || res.data);
    }).catch(() => {});
    if (isEdit) {
      productAPI.get(id).then(res => {
        const p = res.data;
        setForm({
          name: p.name, sku: p.sku, description: p.description || '',
          price: p.price, stock: p.stock, status: p.status,
          category: p.category || '', image_url: p.image_url || '',
        });
      }).catch(() => toast.error('Failed to load product'));
    }
  }, [id, isEdit]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const validate = () => {
    const errs = {};
    if (!form.name.trim()) errs.name = 'Name is required';
    if (!form.sku.trim()) errs.sku = 'SKU is required';
    if (!form.price || parseFloat(form.price) <= 0) errs.price = 'Price must be greater than 0';
    if (form.stock === '' || parseInt(form.stock) < 0) errs.stock = 'Stock must be 0 or more';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const data = {
        ...form,
        price: parseFloat(form.price),
        stock: parseInt(form.stock),
        category: form.category || null,
        image_url: form.image_url || '',
      };

      if (isEdit) {
        await productAPI.update(id, data);
        toast.success('Product updated successfully');
      } else {
        await productAPI.create(data);
        toast.success('Product created successfully');
      }
      navigate('/admin/products');
    } catch (err) {
      if (err.response?.data) {
        const apiErrors = err.response.data;
        const fieldErrors = {};
        Object.keys(apiErrors).forEach(key => {
          fieldErrors[key] = Array.isArray(apiErrors[key]) ? apiErrors[key][0] : apiErrors[key];
        });
        setErrors(fieldErrors);
      } else {
        toast.error('Failed to save product');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper" style={{ maxWidth: 720 }}>
      <div className="section-header">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700 }}>
          {isEdit ? 'Edit Product' : 'New Product'}
        </h2>
      </div>

      <div className="card animate-in">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Product Name *</label>
            <input name="name" value={form.name} onChange={handleChange}
              placeholder="e.g. Wireless Headphones" />
            {errors.name && <span className="error">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label>SKU *</label>
            <input name="sku" value={form.sku} onChange={handleChange}
              placeholder="e.g. WH-1000XM5" />
            {errors.sku && <span className="error">{errors.sku}</span>}
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={form.description} onChange={handleChange}
              rows="4" placeholder="Product description..." />
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Price *</label>
              <input name="price" type="number" step="0.01" min="0.01" value={form.price}
                onChange={handleChange} placeholder="0.00" />
              {errors.price && <span className="error">{errors.price}</span>}
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Stock *</label>
              <input name="stock" type="number" min="0" value={form.stock}
                onChange={handleChange} placeholder="0" />
              {errors.stock && <span className="error">{errors.stock}</span>}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Status</label>
              <select name="status" value={form.status} onChange={handleChange}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Category</label>
              <select name="category" value={form.category} onChange={handleChange}>
                <option value="">No category</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Image URL</label>
            <input name="image_url" value={form.image_url} onChange={handleChange}
              placeholder="https://example.com/image.jpg" />
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
            <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
              {loading ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="spinner" /> Saving...
                </span>
              ) : isEdit ? 'Update Product' : 'Create Product'}
            </button>
            <button type="button" className="btn btn-secondary btn-lg" onClick={() => navigate('/admin/products')}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
