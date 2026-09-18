/**
 * Invoice — printable invoice page with full line-item breakdown.
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import API from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  ArrowLeft, Printer, Download, Wrench, IndianRupee,
  Calendar, User, FileText, CheckCircle
} from 'lucide-react'

export default function Invoice() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [invoice, setInvoice] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    API.get(`/invoices/${id}/`)
      .then((res) => setInvoice(res.data))
      .catch(() => {
        // Try by booking ID
        API.get(`/bookings/${id}/invoice/`)
          .then((res) => setInvoice(res.data))
          .catch(() => {})
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingSpinner text="Loading invoice..." />

  if (!invoice) {
    return (
      <div className="page-container text-center py-20">
        <p className="text-lg text-white mb-2">Invoice not found</p>
        <button onClick={() => navigate(-1)} className="text-blue-400 hover:underline text-sm">Go back</button>
      </div>
    )
  }

  return (
    <div className="relative">
      <div className="page-container max-w-2xl mx-auto">
        {/* Actions */}
        <div className="flex items-center justify-between mb-6 no-print">
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white">
            <ArrowLeft size={16} /> Back
          </button>
          <button onClick={() => window.print()} className="btn-secondary flex items-center gap-2">
            <Printer size={16} /> Print Invoice
          </button>
        </div>

        {/* Invoice Card */}
        <div className="glass-card-static p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-8 pb-6" style={{ borderBottom: '1px solid var(--glass-border)' }}>
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl">
                <Wrench size={22} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">SevaConnect</h1>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>AI-Powered Service Platform</p>
              </div>
            </div>
            <div className="text-right">
              <h2 className="text-lg font-bold text-gradient">INVOICE</h2>
              <p className="text-sm text-white font-mono">{invoice.invoice_number}</p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                <Calendar size={11} className="inline mr-1" />
                {invoice.created_at ? new Date(invoice.created_at).toLocaleDateString('en-IN') : 'N/A'}
              </p>
            </div>
          </div>

          {/* Service Info */}
          <div className="mb-6">
            <p className="text-xs font-medium mb-1" style={{ color: 'var(--text-muted)' }}>Service</p>
            <p className="text-white font-semibold">{invoice.service_name || 'Service'}</p>
          </div>

          {/* Line Items */}
          <div className="mb-6">
            <div className="grid grid-cols-12 gap-2 text-xs font-medium pb-2 mb-2" style={{ color: 'var(--text-muted)', borderBottom: '1px solid var(--glass-border)' }}>
              <div className="col-span-6">Description</div>
              <div className="col-span-2 text-center">Qty</div>
              <div className="col-span-2 text-right">Rate</div>
              <div className="col-span-2 text-right">Amount</div>
            </div>

            {(invoice.items || []).map((item, i) => (
              <div key={i} className="grid grid-cols-12 gap-2 text-sm py-2" style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                <div className="col-span-6 text-white">{item.description}</div>
                <div className="col-span-2 text-center" style={{ color: 'var(--text-muted)' }}>{item.quantity || '-'}</div>
                <div className="col-span-2 text-right" style={{ color: 'var(--text-muted)' }}>
                  {item.unit_price ? `₹${item.unit_price}` : '-'}
                </div>
                <div className="col-span-2 text-right text-white font-medium">₹{item.amount || 0}</div>
              </div>
            ))}
          </div>

          {/* Totals */}
          <div className="pt-4" style={{ borderTop: '2px solid var(--glass-border)' }}>
            <div className="flex justify-between text-sm mb-1">
              <span style={{ color: 'var(--text-muted)' }}>Subtotal</span>
              <span className="text-white">₹{invoice.subtotal || 0}</span>
            </div>
            <div className="flex justify-between text-lg font-bold mt-2 pt-2" style={{ borderTop: '1px solid var(--glass-border)' }}>
              <span className="text-white">Total</span>
              <span className="text-gradient">₹{invoice.total || 0}</span>
            </div>
          </div>

          {/* Payment Status */}
          <div className="mt-6 pt-4 flex items-center justify-between" style={{ borderTop: '1px solid var(--glass-border)' }}>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Payment Status</span>
            {invoice.payment_status === 'paid' ? (
              <span className="badge-green badge flex items-center gap-1.5">
                <CheckCircle size={13} /> Paid
              </span>
            ) : (
              <span className="badge-yellow badge">Unpaid</span>
            )}
          </div>

          {/* Footer */}
          <div className="mt-8 pt-4 text-center text-xs" style={{ borderTop: '1px solid var(--glass-border)', color: 'var(--text-muted)' }}>
            <p>Thank you for choosing SevaConnect!</p>
            <p className="mt-1">support@sevaconnect.in • +91 98765 43210</p>
          </div>
        </div>
      </div>
    </div>
  )
}
